from fpdf import FPDF
import datetime
import streamlit as st

# Einfaches Stammdatenblatt
def generate_stammdatenblatt_pdf(person_obj):
    """
    Generiert ein Stammdatenblatt-PDF für eine Person.
    
    Args:
        person_obj: Person-Objekt mit Attributen: surname, name, birthdate, street, housenr, zip, place, obj_id
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Stammdatenblatt", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {person_obj.surname} {person_obj.name}", ln=True)
    pdf.cell(0, 8, f"Geburtsdatum: {person_obj.birthdate}", ln=True)
    pdf.cell(0, 8, f"Adresse: {person_obj.street} {person_obj.housenr}", ln=True)
    pdf.cell(0, 8, f"Ort: {person_obj.zip} {person_obj.place}", ln=True)
    pdf.cell(0, 8, f"Personen-ID: {person_obj.obj_id}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')


# Vereinfachte Lohnabrechnung
def generate_real_payroll_pdf(employee_obj, brutto, netto, abrechnung_data=None):
    """
    Generiert einen Lohn- und Gehaltszettel als PDF.
    
    Args:
        employee_obj: Mitarbeiter-Objekt mit Attributen wie surname, name, birthdate, entrydate, street, housenr, zip, place
        brutto: Bruttogehalt (float)
        netto: Nettogehalt (float)
        abrechnung_data: Optional dict mit zusätzlichen Daten wie {"SV": 450.0, "Lohnsteuer": 320.0, ...}
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Lohn- und Gehaltsabrechnung", align="C", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {employee_obj.surname} {employee_obj.name}", ln=True)
    pdf.cell(0, 8, f"Geburtsdatum: {employee_obj.birthdate}", ln=True)
    pdf.cell(0, 8, f"Eintrittsdatum: {getattr(employee_obj, 'entrydate', '-')}", ln=True)
    pdf.cell(0, 8, f"Adresse: {employee_obj.street} {employee_obj.housenr}, {employee_obj.zip} {employee_obj.place}", ln=True)
    pdf.cell(0, 8, f"Abrechnungsmonat: {datetime.date.today().strftime('%m/%Y')}", ln=True)

    # Bruttobezüge
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Bruttobezüge:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(80, 8, "Grundgehalt", border=1)
    pdf.cell(40, 8, f"{brutto:.2f} EUR", border=1, ln=True)

    # Weitere Bezüge, falls vorhanden
    if abrechnung_data:
        for key in ["sonderzahlungen", "mehrstunden25", "überstunden50", "diäten", "reisekosten"]:
            betrag = abrechnung_data.get(key, 0)
            if betrag > 0:
                pdf.cell(80, 8, key, border=1)
                pdf.cell(40, 8, f"{betrag:.2f} EUR", border=1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Abzüge:", ln=True)
    pdf.set_font("Arial", size=11)

    if abrechnung_data:
        for key in ["SV", "Lohnsteuer", "Gewerkschaft"]:
            betrag = abrechnung_data.get(key, 0)
            if betrag > 0:
                pdf.cell(80, 8, key, border=1)
                pdf.cell(40, 8, f"{betrag:.2f} EUR", border=1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 8, "Nettolohn", border=1)
    pdf.cell(40, 8, f"{netto:.2f} EUR", border=1, ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')


# Einfacher Monatsbericht
def generate_monthly_summary_pdf(new_employees, total_payroll):
    """
    Generiert einen Monatsbericht als PDF.
    
    Args:
        new_employees: Liste von Mitarbeiternamen (list of str)
        total_payroll: Gesamtauszahlung (float/int)
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Monatsbericht {datetime.date.today().strftime('%B %Y')}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Neu eingestellte Mitarbeiter: {len(new_employees)}", ln=True)

    for name in new_employees:
        pdf.cell(0, 8, f"- {name}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Gesamtauszahlung: {total_payroll} EUR", ln=True)

    return pdf.output(dest='S').encode('latin1')


# Einfache Lohnabrechnung für Einzelperson
def generate_payroll_pdf(employee_name, amount):
    """
    Generiert einen einfachen Lohnzettel als PDF.
    
    Args:
        employee_name: Name des Mitarbeiters (str)
        amount: Betrag (float/int)
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Lohnzettel", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Mitarbeiter: {employee_name}", ln=True)
    pdf.cell(0, 10, f"Betrag: {amount} EUR", ln=True)
    pdf.cell(0, 10, f"Datum: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)

    return pdf.output(dest='S').encode('latin1')


# ===========================
# STREAMLIT UI - Echte Daten aus Datenbank
# ===========================
import sqlite3
from pathlib import Path

st.set_page_config(page_title="PDF-Ausgabe", page_icon="📄", layout="wide")
st.title("📄 PDF-Ausgabe")

# Datenbank-Verbindung
DB_PATH = (Path(__file__).parent.parent.parent / "Stammdaten-Projekt" / "stammdatenverwaltung.db").resolve()

def load_employees_with_persons():
    """Lädt Mitarbeiter mit zugehörigen Personendaten"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("""
            SELECT 
                m.EMPL_ID, m.PERS_ID, m.EMPL_ENTRYDATE, m.EMPL_BRUTTOGEHALT,
                p.PERS_SURNAME, p.PERS_FIRSTNAME, p.PERS_BIRTHDATE,
                IFNULL(p.PERS_STREET, '') AS PERS_STREET,
                IFNULL(p.PERS_HOUSENR, '') AS PERS_HOUSENR,
                IFNULL(p.PERS_ZIP, '') AS PERS_ZIP,
                IFNULL(p.PERS_PLACE, '') AS PERS_PLACE
            FROM MITARBEITER m
            JOIN PERSON p ON p.PERS_ID = m.PERS_ID
            ORDER BY p.PERS_SURNAME, p.PERS_FIRSTNAME
        """).fetchall()
        return rows
    except Exception as e:
        st.error(f"Fehler beim Laden der Mitarbeiter: {e}")
        return []
    finally:
        conn.close()

# Daten laden
employees = load_employees_with_persons()

if not employees:
    st.warning("⚠️ Keine Mitarbeiter in der Datenbank gefunden!")
    st.info("Bitte erstelle zunächst Personen und Mitarbeiter über die entsprechenden Seiten.")
else:
    st.success(f"✅ {len(employees)} Mitarbeiter gefunden in der Datenbank")
    
    # Mitarbeiter-Auswahl
    st.subheader("Mitarbeiter auswählen")
    
    emp_options = {f"{e['PERS_SURNAME']}, {e['PERS_FIRSTNAME']} (ID: {e['EMPL_ID']})": i 
                   for i, e in enumerate(employees)}
    
    selected_name = st.selectbox(
        "Wähle einen Mitarbeiter aus:",
        options=list(emp_options.keys()),
        key="employee_selector"
    )
    
    selected_idx = emp_options[selected_name]
    selected_employee = employees[selected_idx]
    
    # Anzeige der Mitarbeiterdaten
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name", f"{selected_employee['PERS_SURNAME']} {selected_employee['PERS_FIRSTNAME']}")
    with col2:
        st.metric("Geburtsdatum", selected_employee['PERS_BIRTHDATE'])
    with col3:
        st.metric("Eintrittsdatum", selected_employee['EMPL_ENTRYDATE'])
    
    # PDF-Generierung
    st.divider()
    st.subheader("📄 PDF-Downloads")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### Stammdatenblatt")
        st.write("Erstellt ein PDF mit allen Stammdaten des Mitarbeiters")
        
        # Erstelle ein Mock-Objekt für die Funktion
        class PersonMock:
            def __init__(self, row):
                self.surname = row['PERS_SURNAME']
                self.name = row['PERS_FIRSTNAME']
                self.birthdate = row['PERS_BIRTHDATE']
                self.street = row['PERS_STREET']
                self.housenr = row['PERS_HOUSENR']
                self.zip = row['PERS_ZIP']
                self.place = row['PERS_PLACE']
                self.obj_id = row['PERS_ID']
        
        if st.button("📄 Stammdatenblatt erstellen", key="stammdaten_btn"):
            person_obj = PersonMock(selected_employee)
            pdf_bytes = generate_stammdatenblatt_pdf(person_obj)
            st.download_button(
                "⬇️ Download Stammdatenblatt.pdf",
                data=pdf_bytes,
                file_name=f"Stammdatenblatt_{selected_employee['PERS_SURNAME']}_{selected_employee['PERS_FIRSTNAME']}.pdf",
                mime="application/pdf",
                key="download_stammdaten"
            )
    
    with col_b:
        st.markdown("### Lohnzettel")
        st.write("Erstellt einen Lohnzettel mit Gehaltsabrechnung")
        
        class EmployeeMock:
            def __init__(self, row):
                self.surname = row['PERS_SURNAME']
                self.name = row['PERS_FIRSTNAME']
                self.birthdate = row['PERS_BIRTHDATE']
                self.entrydate = row['EMPL_ENTRYDATE']
                self.street = row['PERS_STREET']
                self.housenr = row['PERS_HOUSENR']
                self.zip = row['PERS_ZIP']
                self.place = row['PERS_PLACE']
        
        if st.button("📄 Lohnzettel erstellen", key="lohnzettel_btn"):
            employee_obj = EmployeeMock(selected_employee)
            brutto = float(selected_employee['EMPL_BRUTTOGEHALT'])
            
            # Berechne Abzüge (vereinfacht)
            sv = round(brutto * 0.1807, 2)  # Sozialversicherung
            tax = round(max(brutto - sv, 0) * 0.2, 2)  # Lohnsteuer
            netto = round(brutto - sv - tax, 2)
            
            abrechnung_data = {
                "SV": sv,
                "Lohnsteuer": tax
            }
            
            pdf_bytes = generate_real_payroll_pdf(employee_obj, brutto, netto, abrechnung_data)
            st.download_button(
                "⬇️ Download Lohnzettel.pdf",
                data=pdf_bytes,
                file_name=f"Lohnzettel_{selected_employee['PERS_SURNAME']}_{selected_employee['PERS_FIRSTNAME']}.pdf",
                mime="application/pdf",
                key="download_lohnzettel"
            )

st.divider()
st.caption(f"📂 Datenbank: {DB_PATH}")
st.caption(f"📊 Status: {len(employees)} Mitarbeiter verfügbar")

