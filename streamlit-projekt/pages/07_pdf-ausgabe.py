from fpdf import FPDF
import datetime
import streamlit as st

# Einfaches Stammdatenblatt
def generate_stammdatenblatt_pdf(person_obj):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, f"Stammdatenblatt", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"Name: {person_obj.surname} {person_obj.name}", ln=True)
    pdf.cell(0, 10, f"Geburtsdatum: {person_obj.birthdate}", ln=True)
    pdf.cell(0, 10, f"Adresse: {person_obj.street} {person_obj.housenr}", ln=True)
    pdf.cell(0, 10, f"Ort: {person_obj.zip} {person_obj.place}", ln=True)
    pdf.cell(0, 10, f"Personen-ID: {person_obj.obj_id}", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')


# Vereinfachte Lohnabrechnung
def generate_real_payroll_pdf(employee_obj, brutto, netto, abrechnung_data=None):
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

    #Bruttobezüge
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Bruttobezüge:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(80, 8, "Grundgehalt", border=1)
    pdf.cell(40, 8, f"{brutto:.2f} EUR", border=1)
    pdf.ln(8)

    # Weitere Bezüge, falls vorhanden
    if abrechnung_data:
        for key in ["sonderzahlungen", "mehrstunden25", "überstunden50", "diäten", "reisekosten"]:
            betrag = abrechnung_data.get(key, 0)
            if betrag > 0:
                pdf.cell(80, 8, key, border=1)
                pdf.cell(40, 8, f"{betrag:.2f} EUR", border=1)
                pdf.ln(8)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Abzüge:", ln=True)
    pdf.set_font("Arial", size=11)

    if abrechnung_data:
        for key in ["SV", "Lohnsteuer", "Gewerkschaft"]:
            betrag = abrechnung_data.get(key, 0)
            if betrag > 0:
                pdf.cell(80, 8, key, border=1)
                pdf.cell(40, 8, f"{betrag:.2f} EUR", border=1)
                pdf.ln(8)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 8, "Nettolohn", border=1)
    pdf.cell(40, 8, f"{netto:.2f} EUR", border=1)
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')


# Einfacher Monatsbericht
def generate_monthly_summary_pdf(new_employees, total_payroll):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, f"Monatsbericht {datetime.date.today().strftime('%B %Y')}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"Neu eingestellte Mitarbeiter: {len(new_employees)}", ln=True)

    for name in new_employees:
        pdf.cell(0, 8, f"- {name}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Gesamtauszahlung: {total_payroll} EUR", ln=True)

    return pdf.output(dest='S').encode('latin1')


# Einfache Lohnabrechnung für Einzelperson
def generate_payroll_pdf(employee_name, amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, f"Lohnzettel", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"Mitarbeiter: {employee_name}", ln=True)
    pdf.cell(0, 10, f"Betrag: {amount} EUR", ln=True)
    pdf.cell(0, 10, f"Datum: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)

    return pdf.output(dest='S').encode('latin1')


# Beispielaufrufe
new_employees = ["Kilian Klein", "Luis Schultes"]
total_payroll = 5000
employee_name = "Emmanuel Amamsiugwudi"
amount = 2500

st.subheader("Automatisierte PDF-Reports")

if st.button("Monatsbericht herunterladen"):
    pdf_bytes = generate_monthly_summary_pdf(new_employees, total_payroll)
    st.download_button("Monatsbericht als PDF", pdf_bytes, file_name="Monatsbericht.pdf")

if st.button("Lohnzettel herunterladen"):
    pdf_bytes = generate_payroll_pdf(employee_name, amount)
    st.download_button("Lohnzettel als PDF", pdf_bytes, file_name="Lohnzettel.pdf")
