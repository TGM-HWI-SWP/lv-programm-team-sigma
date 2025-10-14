from fpdf import FPDF
import datetime
import streamlit as st

def generate_stammdatenblatt_pdf(person_obj):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Stammdatenblatt für {person_obj.surname} {person_obj.name}", ln=True)
    pdf.cell(0, 10, f"Geburtsdatum: {person_obj.birthdate}", ln=True)
    pdf.cell(0, 10, f"Adresse: {person_obj.street} {person_obj.housenr}, {person_obj.zip} {person_obj.place}", ln=True)
    pdf.cell(0, 10, f"PLZ/Ort: {person_obj.zip} {person_obj.place}", ln=True)
    pdf.cell(0, 10, f"ID: {person_obj.obj_id}", ln=True)
    return pdf.output(dest='S').encode('latin1')

def generate_real_payroll_pdf(employee_obj, brutto, netto, abrechnung_data=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Lohn- und Gehaltsabrechnung", ln=True, align="C")
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {employee_obj.surname} {employee_obj.name}", ln=True)
    pdf.cell(0, 8, f"Geburtsdatum: {employee_obj.birthdate}", ln=True)
    pdf.cell(0, 8, f"Eintrittsdatum: {getattr(employee_obj, 'entrydate', '-')}", ln=True)
    pdf.cell(0, 8, f"Adresse: {employee_obj.street} {employee_obj.housenr}, {employee_obj.zip} {employee_obj.place}", ln=True)
    pdf.cell(0, 8, f"Abrechnungsmonat: {datetime.date.today().strftime('%m/%Y')}", ln=True)
    pdf.ln(4)

    # Bruttobezüge
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Bruttobezüge", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(80, 8, "Gehalt", border=1)
    pdf.cell(40, 8, f"{brutto:.2f} EUR", border=1, ln=True)
    # Weitere Bezüge aus abrechnung_data
    if abrechnung_data:
        for k in ["mehrstunden0", "mehrstunden25", "mehrstunden50", "überstunden50", "überstunden100", "sonderzahlungen", "sachbezug", "diäten", "reisekosten"]:
            val = abrechnung_data.get(k, 0)
            if val:
                pdf.cell(80, 8, k, border=1)
                pdf.cell(40, 8, f"{val:.2f} EUR", border=1, ln=True)
    pdf.ln(2)

    # Abzüge
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Abzüge", ln=True)
    pdf.set_font("Arial", size=11)
    if abrechnung_data:
        for k in ["SV", "Lohnsteuer", "Gewerkschaft", "Freibetragsbescheid", "Pendlerpauschale"]:
            val = abrechnung_data.get(k, 0)
            if val:
                pdf.cell(80, 8, k, border=1)
                pdf.cell(40, 8, f"{val:.2f} EUR", border=1, ln=True)
    pdf.ln(2)

    # Netto
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 8, "Nettolohn", border=1)
    pdf.cell(40, 8, f"{netto:.2f} EUR", border=1, ln=True)
    pdf.ln(2)

    # Lohnnebenkosten
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Lohnnebenkosten", ln=True)
    pdf.set_font("Arial", size=11)
    if abrechnung_data:
        for k in ["Kommunalsteuer", "U-Bahnsteuer", "Dienstgeberbeitrag", "Zuschlag DB", "BV"]:
            val = abrechnung_data.get(k, 0)
            if val:
                pdf.cell(80, 8, k, border=1)
                pdf.cell(40, 8, f"{val:.2f} EUR", border=1, ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Erstellt am: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')

def generate_monthly_summary_pdf(new_employees, total_payroll):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Monatsbericht: {datetime.date.today().strftime('%B %Y')}", ln=True)
    pdf.cell(0, 10, f"Neu eingestellte Mitarbeiter: {len(new_employees)}", ln=True)
    for emp in new_employees:
        pdf.cell(0, 10, f"- {emp}", ln=True)
    pdf.cell(0, 10, f"Monatliche Auszahlung: {total_payroll} EUR", ln=True)
    return pdf.output(dest='S').encode('latin1')

def generate_payroll_pdf(employee_name, amount):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Lohn-/Gehaltszettel für {employee_name}", ln=True)
    pdf.cell(0, 10, f"Betrag: {amount} EUR", ln=True)
    pdf.cell(0, 10, f"Datum: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')

new_employees = ["Kilian Klein ", "Luis Schultes"]
total_payroll = 5000
employee_name = "Emmanuel Amamsiugwudi"
amount = 2500

st.subheader("Automatisierte PDF-Reports")

if st.button("Monatsbericht herunterladen"):
    pdf_bytes = generate_monthly_summary_pdf(new_employees, total_payroll)
    st.download_button("Monatsbericht als PDF", pdf_bytes, file_name="Monatsbericht.pdf")

if st.button("Lohn-/Gehaltszettel herunterladen"):
    pdf_bytes = generate_payroll_pdf(employee_name, amount)
    st.download_button("Lohn-/Gehaltszettel als PDF", pdf_bytes, file_name="Gehaltszettel.pdf")
