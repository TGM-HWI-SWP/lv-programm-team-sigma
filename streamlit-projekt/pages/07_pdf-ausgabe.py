from fpdf import FPDF
import datetime
import streamlit as st

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
