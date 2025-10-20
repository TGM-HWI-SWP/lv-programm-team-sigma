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
    
    # Kopfzeile mit Logo-Bereich
    pdf.set_fill_color(*COLOR_HEADER)
    pdf.rect(0, 0, 210, 40, 'F')
    
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, 8, 25, 25, 'D')
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(*COLOR_HEADER)
    pdf.set_xy(15, 18)
    pdf.cell(25, 5, "LOGO", align='C')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_xy(45, 10)
    pdf.cell(0, 10, "STAMMDATENBLATT", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.set_xy(45, 22)
    pdf.cell(0, 5, "Team Sigma GmbH | Musterstraße 1 | 1010 Wien", ln=True)
    pdf.set_xy(45, 28)
    pdf.cell(0, 5, f"Erstellt am: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    
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
        ("Geschlecht:", "—", "Staatsangehörigkeit:", "Österreich"),
        ("SV-Nummer:", "—", "Telefon:", "—"),
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
        ("Straße / Hausnr.:", f"{person_like_row['PERS_STREET']} {person_like_row['PERS_HOUSENR']}".strip(), "E-Mail:", "—"),
        ("PLZ / Ort:", f"{person_like_row['PERS_ZIP']} {person_like_row['PERS_PLACE']}".strip(), "Mobil:", "—"),
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
        ("Eintrittsdatum:", person_like_row.get('EMPL_ENTRYDATE', '—') if 'EMPL_ENTRYDATE' in person_like_row.keys() else '—', "Personalnummer:", str(person_like_row.get("PERS_ID", ""))),
        ("Position:", "—", "Abteilung:", "—"),
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
    
    # Fußzeile
    pdf.set_y(285)
    pdf.set_font("Arial", '', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 3, "Team Sigma GmbH | UID: ATU12345678", align='L')
    pdf.cell(95, 3, f"Seite 1 | {datetime.date.today().strftime('%d.%m.%Y')}", align='R')
    
    return pdf.output(dest="S").encode("latin1")

def pdf_lohnzettel(employee_row, payroll_data):
    """Lohnzettel im professionellen BMD-Stil"""
    pdf = FPDF()
    pdf.add_page()
    
    # Farben
    COLOR_HEADER_BG = (41, 128, 185)
    COLOR_TABLE_HEADER = (52, 152, 219)
    COLOR_GRAY_LIGHT = (236, 240, 241)
    COLOR_TEXT_DARK = (44, 62, 80)
    COLOR_ACCENT = (46, 204, 113)
    
    # Kopfzeile
    pdf.set_fill_color(*COLOR_HEADER_BG)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_xy(10, 8)
    pdf.cell(0, 8, "Lohn- und Gehaltsabrechnung", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.set_xy(10, 18)
    pdf.cell(0, 5, "Team Sigma GmbH | Musterstraße 1 | 1010 Wien", ln=True)
    pdf.set_xy(10, 23)
    month_year = payroll_data.get('month', datetime.date.today().strftime('%Y-%m'))
    pdf.cell(0, 5, f"Abrechnungsmonat: {month_year}", ln=True)
    
    # Mitarbeiterdaten Box
    pdf.set_text_color(*COLOR_TEXT_DARK)
    y_start = 45
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.rect(10, y_start, 190, 30)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(15, y_start + 3)
    pdf.cell(0, 6, "MITARBEITER", ln=True)
    pdf.set_font("Arial", '', 10)
    name = f"{employee_row['PERS_SURNAME']} {employee_row['PERS_FIRSTNAME']}"
    addr = f"{employee_row['PERS_STREET']} {employee_row['PERS_HOUSENR']}".strip()
    place = f"{employee_row['PERS_ZIP']} {employee_row['PERS_PLACE']}".strip()
    
    pdf.set_xy(15, y_start + 11)
    pdf.cell(0, 5, f"Name: {name} | Adresse: {addr}, {place}", ln=True)
    
    # Gehaltstabelle
    y_table = y_start + 40
    col_widths = [100, 40, 50]
    
    # Header
    pdf.set_fill_color(*COLOR_TABLE_HEADER)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    headers = ["Bezüge / Abzüge", "Satz", "Betrag (EUR)"]
    x_pos = 10
    for i, header in enumerate(headers):
        pdf.set_xy(x_pos, y_table)
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        x_pos += col_widths[i]
    y_table += 8
    
    # Daten holen
    brutto = payroll_data.get("brutto")
    netto = payroll_data.get("netto")
    tax = payroll_data.get("tax")
    sv = payroll_data.get("sv")
    
    if brutto is None:
        brutto = str_to_float(employee_row.get("EMPL_BRUTTOGEHALT"), 0.0)
    if sv is None:
        sv = round(brutto * 0.1807, 2)
    if tax is None:
        tax = round(max(brutto - sv, 0) * 0.2, 2)
    if netto is None:
        netto = round(brutto - sv - tax, 2)
    
    # Brutto
    pdf.set_text_color(*COLOR_TEXT_DARK)
    pdf.set_font("Arial", '', 10)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Grundgehalt (Brutto)", border=1)
    pdf.cell(col_widths[1], 7, "", border=1)
    pdf.cell(col_widths[2], 7, f"{brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 7
    
    # Zwischensumme
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(*COLOR_GRAY_LIGHT)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Zwischensumme Brutto", border=1, fill=True)
    pdf.cell(col_widths[1], 7, "", border=1, fill=True)
    pdf.cell(col_widths[2], 7, f"{brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    y_table += 7
    
    # Abzüge
    pdf.set_font("Arial", '', 10)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Sozialversicherung", border=1)
    satz_sv = (sv / brutto * 100) if brutto > 0 else 0
    pdf.cell(col_widths[1], 7, f"{satz_sv:.1f}%", border=1, align='C')
    pdf.cell(col_widths[2], 7, f"-{sv:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 7
    
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Lohnsteuer", border=1)
    pdf.cell(col_widths[1], 7, "", border=1)
    pdf.cell(col_widths[2], 7, f"-{tax:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 7
    
    # Netto hervorgehoben
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(*COLOR_ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 9, "  AUSZAHLUNGSBETRAG (NETTO)", border=1, fill=True)
    pdf.cell(col_widths[1], 9, "", border=1, fill=True)
    pdf.cell(col_widths[2], 9, f"{netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    
    # Fußzeile
    pdf.set_y(280)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')} | Seite 1 von 1", align='C')
    
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
selected_idx = st.selectbox("Mitarbeiter auswählen", list(range(len(emp_display))), format_func=lambda i: emp_display[i] if emp_display else "—") if employees else None

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