import sys
import sqlite3
from pathlib import Path
import datetime

import streamlit as st
from fpdf import FPDF

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

# PDF generator functions
def pdf_stammdatenblatt(person_like_row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Stammdatenblatt", ln=True)
    pdf.ln(4)
    pdf.set_font("Arial", "", 12)
    name = f"{person_like_row['PERS_SURNAME']} {person_like_row['PERS_FIRSTNAME']}"
    addr = f"{person_like_row['PERS_STREET']} {person_like_row['PERS_HOUSENR']}".strip()
    place = f"{person_like_row['PERS_ZIP']} {person_like_row['PERS_PLACE']}".strip()
    rows = [
        ("Name", name),
        ("Geburtsdatum", str(person_like_row.get("PERS_BIRTHDATE", "") or "")),
        ("Adresse", addr),
        ("Ort", place),
    ]
    for label, value in rows:
        pdf.cell(50, 8, f"{label}:", border=0)
        pdf.cell(0, 8, value, ln=True)
    pdf.ln(6)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest="S").encode("latin1")

def pdf_lohnzettel(employee_row, payroll_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Lohn- und Gehaltsabrechnung", ln=True, align="C")
    pdf.ln(2)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, "Firma: Team Sigma GmbH, Musterstraße 1, 1010 Wien", ln=True)
    pdf.cell(0, 6, f"Abrechnungsmonat: {payroll_data.get('month','-')}", ln=True)
    pdf.ln(4)
    name = f"{employee_row['PERS_SURNAME']} {employee_row['PERS_FIRSTNAME']}"
    addr = f"{employee_row['PERS_STREET']} {employee_row['PERS_HOUSENR']}".strip()
    place = f"{employee_row['PERS_ZIP']} {employee_row['PERS_PLACE']}".strip()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Mitarbeiter", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Name: {name}", ln=True)
    pdf.cell(0, 6, f"Adresse: {addr}", ln=True)
    pdf.cell(0, 6, f"Ort: {place}", ln=True)
    pdf.ln(4)
    brutto = payroll_data.get("brutto")
    netto = payroll_data.get("netto")
    tax = payroll_data.get("tax")
    sv = payroll_data.get("sv")
    if brutto is None:
        brutto = float(employee_row["EMPL_BRUTTOGEHALT"]) if "EMPL_BRUTTOGEHALT" in employee_row.keys() and employee_row["EMPL_BRUTTOGEHALT"] is not None else 0.0
    if sv is None:
        sv = round(brutto * 0.185, 2)
    if tax is None:
        tax = round(max(brutto - sv, 0) * 0.2, 2)
    if netto is None:
        netto = round(brutto - sv - tax, 2)
    def row(label, value):
        pdf.cell(80, 8, label, border=1)
        pdf.cell(0, 8, f"{value:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", "."), border=1, ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, "Bezüge/Abzüge", ln=True)
    pdf.set_font("Arial", "", 11)
    row("Bruttobezüge", brutto)
    row("Sozialversicherung", -sv)
    row("Lohnsteuer", -tax)
    pdf.set_font("Arial", "B", 11)
    row("Auszahlungsbetrag (Netto)", netto)
    pdf.ln(6)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Hinweis: Einige Beträge wurden mangels Detaildaten angenähert.", ln=True)
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