import sys
import sqlite3
from pathlib import Path
import datetime

import streamlit as st
from fpdf import FPDF

# Hilfsfunktion für sichere Float-Konvertierung
def str_to_float(value, default=0.0):
    """Konvertiert String (auch mit Komma) zu Float"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(',', '.'))
    except (ValueError, AttributeError):
        return default

# Optional project modules
try:
    from modules import dbms, person, employee, auth
except Exception:
    dbms = None
    person = None
    employee = None
    auth = None

st.set_page_config(
    page_title="Personalverwaltung - Team Sigma",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database path points to Stammdaten-Projekt
DB_PATH = (Path(__file__).parent.parent / "Stammdaten-Projekt" / "stammdatenverwaltung.db").resolve()

# SQLite helper functions
def connect_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def table_exists(conn, name):
    cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None

def columns(conn, table):
    return [r["name"] for r in conn.execute(f"PRAGMA table_info({table});")]

def first_col_like(cols, substrings, default=None):
    low = [c.lower() for c in cols]
    for sub in substrings:
        for i, c in enumerate(low):
            if sub in c:
                return cols[i]
    return default

# Data loading functions
def load_persons():
    with connect_db() as conn:
        if not table_exists(conn, "PERSON"):
            return []
        rows = conn.execute(
            "SELECT PERS_ID, PERS_SURNAME, PERS_FIRSTNAME, "
            "IFNULL(PERS_BIRTHDATE,'') AS PERS_BIRTHDATE, "
            "IFNULL(PERS_STREET,'') AS PERS_STREET, IFNULL(PERS_HOUSENR,'') AS PERS_HOUSENR, "
            "IFNULL(PERS_ZIP,'') AS PERS_ZIP, IFNULL(PERS_PLACE,'') AS PERS_PLACE "
            "FROM PERSON ORDER BY PERS_SURNAME, PERS_FIRSTNAME;"
        ).fetchall()
        return rows

def load_employees_joined():
    with connect_db() as conn:
        if not (table_exists(conn, "PERSON") and table_exists(conn, "MITARBEITER")):
            return []
        rows = conn.execute(
            "SELECT m.EMPL_ID, m.PERS_ID, m.EMPL_ENTRYDATE, m.EMPL_BRUTTOGEHALT, "
            "p.PERS_SURNAME, p.PERS_FIRSTNAME, "
            "IFNULL(p.PERS_BIRTHDATE,'') AS PERS_BIRTHDATE, "
            "IFNULL(p.PERS_STREET,'') AS PERS_STREET, IFNULL(p.PERS_HOUSENR,'') AS PERS_HOUSENR, "
            "IFNULL(p.PERS_ZIP,'') AS PERS_ZIP, IFNULL(p.PERS_PLACE,'') AS PERS_PLACE "
            "FROM MITARBEITER m "
            "JOIN PERSON p ON p.PERS_ID = m.PERS_ID "
            "ORDER BY p.PERS_SURNAME, p.PERS_FIRSTNAME;"
        ).fetchall()
        return rows

def count_payroll_current_month():
    with connect_db() as conn:
        if not table_exists(conn, "lohnverrechnung_dn"):
            return 0
        cols = columns(conn, "lohnverrechnung_dn")
        month_col = first_col_like(cols, ["monat"], None) or "lv_dn_monat"
        now = datetime.date.today()
        current_month_prefix = f"{now.year}-{now.month:02d}"
        try:
            cur = conn.execute(
                f"SELECT COUNT(*) AS c FROM lohnverrechnung_dn WHERE {month_col} LIKE ?;",
                (f"{current_month_prefix}%",),
            )
            row = cur.fetchone()
            return int(row["c"]) if row and row["c"] is not None else 0
        except sqlite3.OperationalError:
            return 0

def find_latest_payroll_for_employee(empl_id):
    with connect_db() as conn:
        if not table_exists(conn, "lohnverrechnung_dn"):
            return None, None
        cols = columns(conn, "lohnverrechnung_dn")
        col_empl = first_col_like(cols, ["empl_id", "mitarb", "employee"], None)
        col_month = first_col_like(cols, ["monat"], None)
        col_brutto = first_col_like(cols, ["brutto"], None)
        col_netto = first_col_like(cols, ["netto"], None)
        col_lstd = first_col_like(cols, ["lohnsteuer", "lst"], None)
        col_sv = first_col_like(cols, ["sv", "sozial"], None)
        if not (col_empl and col_month):
            return None, None
        sql = (
            f"SELECT * FROM lohnverrechnung_dn WHERE {col_empl} = ? "
            f"ORDER BY {col_month} DESC LIMIT 1;"
        )
        row = conn.execute(sql, (empl_id,)).fetchone()
        if not row:
            return None, None
        data = {
            "month": row[col_month] if col_month in row.keys() else "",
            "brutto": float(row[col_brutto]) if col_brutto and row[col_brutto] is not None else None,
            "netto": float(row[col_netto]) if col_netto and row[col_netto] is not None else None,
            "tax": float(row[col_lstd]) if col_lstd and row[col_lstd] is not None else None,
            "sv": float(row[col_sv]) if col_sv and row[col_sv] is not None else None,
        }
        return data, row

# PDF generator functions - VOLLSTÄNDIG OPTIMIERT FÜR A4
def pdf_stammdatenblatt(person_like_row):
    """Vollständiges Stammdatenblatt mit optimaler A4-Nutzung"""
    pdf = FPDF()
    pdf.add_page()
    
    # Farben (BMD-Stil)
    COLOR_HEADER = (41, 128, 185)
    COLOR_SECTION = (52, 152, 219)
    COLOR_LIGHT_BG = (236, 240, 241)
    COLOR_TEXT = (44, 62, 80)
    COLOR_BORDER = (189, 195, 199)
    
    # Kopfzeile
    pdf.set_fill_color(*COLOR_HEADER)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_xy(10, 10)
    pdf.cell(190, 10, "STAMMDATENBLATT", ln=True, align='C')
    pdf.set_font("Arial", '', 9)
    pdf.set_xy(10, 22)
    pdf.cell(190, 5, "Team Sigma GmbH | Wexstraße 19-23 | 1200 Wien", ln=True, align='C')
    pdf.set_xy(10, 28)
    pdf.cell(190, 5, f"Erstellt am: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True, align='C')
    
    # Name hervorgehoben
    y_pos = 50
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_xy(10, y_pos)
    name = f"{person_like_row['PERS_SURNAME']} {person_like_row['PERS_FIRSTNAME']}"
    pdf.cell(190, 10, name, border=1, fill=True, align='C')
    y_pos += 12
    
    # SEKTION 1: Personendaten
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "PERSONENDATEN", border=1, fill=True)
    y_pos += 8
    
    pdf.set_font("Arial", '', 9)
    pdf.set_draw_color(*COLOR_BORDER)
    
    person_data = [
        ("Personen-ID:", str(person_like_row.get("PERS_ID", "")), "Geburtsdatum:", str(person_like_row.get("PERS_BIRTHDATE", "") or "")),
        ("Geschlecht:", "-", "Staatsangehörigkeit:", "Österreich"),
        ("SV-Nummer:", "-", "Telefon:", "-"),
    ]
    
    for i, (l1, v1, l2, v2) in enumerate(person_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # SEKTION 2: Adressdaten
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "ADRESSDATEN", border=1, fill=True)
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    address_data = [
        ("Straße / Hausnr.:", f"{person_like_row['PERS_STREET']} {person_like_row['PERS_HOUSENR']}".strip(), "E-Mail:", "-"),
        ("PLZ / Ort:", f"{person_like_row['PERS_ZIP']} {person_like_row['PERS_PLACE']}".strip(), "Mobil:", "-"),
    ]
    
    for i, (l1, v1, l2, v2) in enumerate(address_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # SEKTION 3: Beschäftigungsdaten
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "BESCHÄFTIGUNGSDATEN", border=1, fill=True)
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    employment_data = [
        ("Eintrittsdatum:", person_like_row.get('EMPL_ENTRYDATE', '-') if 'EMPL_ENTRYDATE' in person_like_row.keys() else '-', "Personalnummer:", str(person_like_row.get("PERS_ID", ""))),
        ("Position:", "-", "Abteilung:", "-"),
        ("Beschäftigungsart:", "Vollzeit", "Lohnart:", "Monatslohn"),
    ]
    
    for i, (l1, v1, l2, v2) in enumerate(employment_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # SEKTION 4: Bankdaten
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "BANKDATEN", border=1, fill=True)
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    bank_data = [
        ("IBAN:", "AT__ ____ ____ ____ ____", "Kontoinhaber:", name),
    ]
    
    for i, (l1, v1, l2, v2) in enumerate(bank_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, l2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, v2, border=1, fill=fill)
        y_pos += 7
    
    # === SIGNATURFELD ===
    # Verschiebe Unterschriften weiter nach unten für bessere Seitennutzung
    y_pos = max(y_pos + 5, 255)  # Mindestens bei Y=255, oder tiefer falls mehr Inhalt
    
    pdf.set_draw_color(*COLOR_BORDER)
    pdf.rect(10, y_pos, 90, 20)
    pdf.rect(110, y_pos, 90, 20)
    
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.set_xy(10, y_pos + 15)
    pdf.cell(90, 5, "Unterschrift Mitarbeiter", align='C')
    pdf.set_xy(110, y_pos + 15)
    pdf.cell(90, 5, "Unterschrift Geschäftsführung", align='C')
    
    # Fußzeile
    pdf.set_y(285)
    pdf.set_font("Arial", '', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 3, "Team Sigma GmbH | UID: ATU12345678", align='L')
    pdf.cell(95, 3, f"Seite 1 | {datetime.date.today().strftime('%d.%m.%Y')}", align='R')
    
    return pdf.output(dest="S").encode("latin1")

def pdf_lohnzettel(employee_row, payroll_data):
    """BMD-Stil Lohnzettel mit 4-Spalten-Tabelle und optimiertem Layout"""
    pdf = FPDF()
    pdf.add_page()
    
    # Farben
    COLOR_HEADER = (41, 128, 185)
    COLOR_SECTION = (52, 152, 219)
    COLOR_NETTO = (46, 204, 113)
    COLOR_LIGHT_BG = (236, 240, 241)
    COLOR_TEXT = (44, 62, 80)
    COLOR_BORDER = (189, 195, 199)
    
    # Erweiterte Kopfzeile (45mm hoch)
    pdf.set_fill_color(*COLOR_HEADER)
    pdf.rect(0, 0, 210, 45, 'F')
    
    # Firmendaten
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_xy(15, 8)
    pdf.cell(0, 8, "LOHNZETTEL", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_xy(15, 18)
    pdf.cell(0, 4, "Team Sigma GmbH", ln=True)
    pdf.set_xy(15, 23)
    pdf.cell(0, 4, "Wexstraße 19-23 | 1200 Wien", ln=True)
    pdf.set_xy(15, 28)
    pdf.cell(0, 4, "Tel: +43 1 234 5678 | office@team-sigma.at", ln=True)
    pdf.set_xy(15, 33)
    pdf.cell(0, 4, "UID: ATU12345678", ln=True)
    
    # Mitarbeiterdaten - kompakt (3 Zeilen, jeweils 2 Spalten)
    y_pos = 52
    pdf.set_fill_color(*COLOR_LIGHT_BG)
    pdf.rect(10, y_pos, 190, 21, 'DF')
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Arial", 'B', 9)
    
    name = f"{employee_row['PERS_SURNAME']} {employee_row['PERS_FIRSTNAME']}"
    entry = employee_row['EMPL_ENTRYDATE'] if 'EMPL_ENTRYDATE' in employee_row.keys() else ''
    
    # Zeile 1
    pdf.set_xy(12, y_pos + 2)
    pdf.cell(50, 5, "Mitarbeiter:", ln=False)
    pdf.set_font("Arial", '', 9)
    pdf.cell(40, 5, name, ln=False)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_x(125)
    pdf.cell(30, 5, "Personen-ID:", ln=False)
    pdf.set_font("Arial", '', 9)
    pers_id = str(employee_row['PERS_ID']) if 'PERS_ID' in employee_row.keys() else ''
    pdf.cell(0, 5, pers_id)
    
    # Zeile 2
    pdf.set_xy(12, y_pos + 9)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(50, 5, "Eintrittsdatum:", ln=False)
    pdf.set_font("Arial", '', 9)
    pdf.cell(40, 5, entry, ln=False)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_x(125)
    pdf.cell(30, 5, "Abrechnungszeitraum:", ln=False)
    pdf.set_font("Arial", '', 9)
    month_year = payroll_data.get('month', datetime.date.today().strftime('%m/%Y'))
    pdf.cell(0, 5, month_year)
    
    # Zeile 3
    pdf.set_xy(12, y_pos + 16)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(50, 5, "Adresse:", ln=False)
    pdf.set_font("Arial", '', 9)
    addr = f"{employee_row['PERS_STREET']} {employee_row['PERS_HOUSENR']}, {employee_row['PERS_ZIP']} {employee_row['PERS_PLACE']}"
    pdf.cell(40, 5, addr[:35], ln=False)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_x(125)
    pdf.cell(30, 5, "Zahlungsart:", ln=False)
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, "Überweisung")
    
    y_pos += 26
    
    # 4-Spalten Tabellenkopf
    pdf.set_draw_color(*COLOR_BORDER)
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_xy(10, y_pos)
    pdf.cell(80, 7, "Bezeichnung", border=1, fill=True)
    pdf.cell(30, 7, "Menge", border=1, fill=True, align='R')
    pdf.cell(30, 7, "Satz", border=1, fill=True, align='R')
    pdf.cell(50, 7, "Betrag EUR", border=1, fill=True, align='R')
    y_pos += 7
    
    # Sektion: BRUTTOBEZÜGE
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 6, "BRUTTOBEZÜGE", border=1, fill=True)
    y_pos += 6
    
    # Daten holen
    brutto = payroll_data.get("brutto")
    if brutto is None:
        brutto_val = employee_row["EMPL_BRUTTOGEHALT"] if "EMPL_BRUTTOGEHALT" in employee_row.keys() else 0
        brutto = str_to_float(brutto_val, 0.0)
    
    brutto_items = [
        ("Grundgehalt", "1,00", "100,00%", brutto),
    ]
    
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Arial", '', 9)
    for item in brutto_items:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(10, y_pos)
        pdf.cell(80, 6, item[0], border=1, fill=True)
        pdf.cell(30, 6, item[1], border=1, fill=True, align='R')
        pdf.cell(30, 6, item[2], border=1, fill=True, align='R')
        pdf.cell(50, 6, f"{item[3]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, fill=True, align='R')
        y_pos += 6
    
    # Summe Bruttobezüge
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(*COLOR_LIGHT_BG)
    pdf.set_xy(10, y_pos)
    pdf.cell(140, 6, "Summe Bruttobezüge", border=1, fill=True, align='R')
    pdf.cell(50, 6, f"{brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, fill=True, align='R')
    y_pos += 8
    
    # Sektion: ABZÜGE
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 6, "ABZÜGE", border=1, fill=True)
    y_pos += 6
    
    # Berechnung
    sv = payroll_data.get("sv")
    if sv is None:
        sv = round(brutto * 0.1807, 2)
    tax = payroll_data.get("tax")
    if tax is None:
        tax = round(brutto * 0.20, 2)
    summe_abzuege = sv + tax
    
    abzug_items = [
        ("Sozialversicherung", "1,00", "18,07%", sv),
        ("Lohnsteuer", "1,00", "20,00%", tax),
    ]
    
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Arial", '', 9)
    for item in abzug_items:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_xy(10, y_pos)
        pdf.cell(80, 6, item[0], border=1, fill=True)
        pdf.cell(30, 6, item[1], border=1, fill=True, align='R')
        pdf.cell(30, 6, item[2], border=1, fill=True, align='R')
        pdf.cell(50, 6, f"{item[3]:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, fill=True, align='R')
        y_pos += 6
    
    # Summe Abzüge
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(*COLOR_LIGHT_BG)
    pdf.set_xy(10, y_pos)
    pdf.cell(140, 6, "Summe Abzüge", border=1, fill=True, align='R')
    pdf.cell(50, 6, f"{summe_abzuege:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, fill=True, align='R')
    y_pos += 8
    
    # NETTO - große grüne Box
    netto = payroll_data.get("netto")
    if netto is None:
        netto = brutto - summe_abzuege
    pdf.set_fill_color(*COLOR_NETTO)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_xy(10, y_pos)
    pdf.cell(140, 10, "AUSZAHLUNGSBETRAG (NETTO)", border=1, fill=True, align='R')
    pdf.cell(50, 10, f"{netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, fill=True, align='R')
    y_pos += 15
    
    # ZUSATZINFORMATIONEN
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 6, "ZUSATZINFORMATIONEN", border=1, fill=True)
    y_pos += 6
    
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_font("Arial", '', 8)
    info_text = (
        "Der Auszahlungsbetrag wird am 1. Werktag des Folgemonats auf Ihr Konto überwiesen. "
        "Bei Fragen zur Abrechnung wenden Sie sich bitte an die Personalabteilung."
    )
    pdf.set_xy(10, y_pos)
    pdf.multi_cell(190, 5, info_text, border=1, fill=True)
    
    # 3-teilige Fußzeile
    pdf.set_y(285)
    pdf.set_font("Arial", '', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(63, 3, "Team Sigma GmbH", align='L')
    pdf.cell(64, 3, "Vertraulich - Nur für den Empfänger", align='C')
    pdf.cell(63, 3, f"Seite 1 | {datetime.date.today().strftime('%d.%m.%Y')}", align='R')
    
    return pdf.output(dest="S").encode("latin1")

# Optional ORM initialization
db = None
if dbms is not None:
    try:
        db = dbms.dbms(str(DB_PATH))
        if person is not None and hasattr(person, "person") and hasattr(person.person, "initialize_db_table"):
            person.person.initialize_db_table(db)
        if employee is not None and hasattr(employee, "mitarbeiter") and hasattr(employee.mitarbeiter, "initialize_db_table"):
            employee.mitarbeiter.initialize_db_table(db)
    except Exception:
        db = None

# Authentication bypass
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True

# UI
st.title("💼 Personalverwaltungssystem - Team Sigma")

col1, col2, col3, col4 = st.columns(4)

employees = load_employees_joined()
persons = load_persons()

with col1:
    st.metric("👥 Personen", len(persons))
with col2:
    st.metric("🧑‍💼 Mitarbeiter", len(employees))
with col3:
    st.metric("💰 Abrechnungen (aktueller Monat)", count_payroll_current_month())
with col4:
    st.metric("📄 PDF-Tools", 2)

st.subheader("📄 PDF-Ausgabe")

emp_display = [f"{e['PERS_SURNAME']}, {e['PERS_FIRSTNAME']} (EMPL_ID {e['EMPL_ID']})" for e in employees]
selected_idx = st.selectbox("Mitarbeiter auswählen", list(range(len(emp_display))), format_func=lambda i: emp_display[i] if emp_display else "-") if employees else None

colA, colB = st.columns(2)

with colA:
    st.markdown("**Stammdatenblatt**")
    if employees and selected_idx is not None:
        if st.button("📄 Stammdatenblatt als PDF"):
            person_like = employees[selected_idx]
            pdf_bytes = pdf_stammdatenblatt(person_like)
            st.download_button(
                "Download Stammdatenblatt.pdf",
                data=pdf_bytes,
                file_name=f"Stammdatenblatt_{employees[selected_idx]['PERS_SURNAME']}_{employees[selected_idx]['PERS_FIRSTNAME']}.pdf",
                mime="application/pdf",
            )
    else:
        st.info("Keine Mitarbeiter in der Datenbank.")

with colB:
    st.markdown("**Lohn- und Gehaltszettel**")
    if employees and selected_idx is not None:
        empl = employees[selected_idx]
        payroll_data, _raw = find_latest_payroll_for_employee(int(empl["EMPL_ID"]))
        if payroll_data is None:
            st.warning("Keine Abrechnungsdaten gefunden. Es werden angenäherte Werte aus dem Mitarbeiterstamm verwendet.")
            payroll_data = {}
        if st.button("📄 Lohnzettel als PDF"):
            pdf_bytes = pdf_lohnzettel(empl, payroll_data)
            month_tag = (payroll_data.get("month") or datetime.date.today().strftime("%Y-%m")).replace("/", "-")
            st.download_button(
                "Download Lohnzettel.pdf",
                data=pdf_bytes,
                file_name=f"Lohnzettel_{empl['PERS_SURNAME']}_{empl['PERS_FIRSTNAME']}_{month_tag}.pdf",
                mime="application/pdf",
            )
    else:
        st.info("Keine Mitarbeiter in der Datenbank.")

st.divider()
st.caption(f"Datenbankdatei: {DB_PATH}")
st.caption("💡 Tipp: Verwende die Seitenleiste (links), um zu anderen Funktionen zu navigieren")