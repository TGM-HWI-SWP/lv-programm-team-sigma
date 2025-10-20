"""
PDF-Ausgabe Tester
Generiert Test-PDFs direkt ohne Streamlit UI
"""
import sqlite3
from pathlib import Path
import sys
import datetime

# Füge streamlit-projekt zu sys.path hinzu
sys.path.insert(0, str(Path(__file__).parent / "streamlit-projekt"))

from fpdf import FPDF

# Import der PDF-Funktionen aus der pages Datei
# Da wir nicht importieren können, definieren wir sie hier neu

def generate_stammdatenblatt_test(person_data):
    """Generiert Stammdatenblatt mit dict-Daten"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Stammdatenblatt", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {person_data['surname']} {person_data['name']}", ln=True)
    pdf.cell(0, 8, f"Geburtsdatum: {person_data['birthdate']}", ln=True)
    pdf.cell(0, 8, f"Adresse: {person_data['street']} {person_data['housenr']}", ln=True)
    pdf.cell(0, 8, f"Ort: {person_data['zip']} {person_data['place']}", ln=True)
    pdf.cell(0, 8, f"Personen-ID: {person_data['pers_id']}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    return pdf.output(dest='S').encode('latin1')

def generate_lohnzettel_test(employee_data, brutto, netto, abrechnung):
    """Generiert Lohnzettel mit dict-Daten"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Lohn- und Gehaltsabrechnung", align="C", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Name: {employee_data['surname']} {employee_data['name']}", ln=True)
    pdf.cell(0, 8, f"Geburtsdatum: {employee_data['birthdate']}", ln=True)
    pdf.cell(0, 8, f"Eintrittsdatum: {employee_data.get('entrydate', '-')}", ln=True)
    pdf.cell(0, 8, f"Adresse: {employee_data['street']} {employee_data['housenr']}, {employee_data['zip']} {employee_data['place']}", ln=True)
    pdf.cell(0, 8, f"Abrechnungsmonat: {datetime.date.today().strftime('%m/%Y')}", ln=True)

    # Bruttobezüge
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Bruttobezüge:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(80, 8, "Grundgehalt", border=1)
    pdf.cell(40, 8, f"{brutto:.2f} EUR", border=1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Abzüge:", ln=True)
    pdf.set_font("Arial", size=11)

    for key in ["SV", "Lohnsteuer"]:
        betrag = abrechnung.get(key, 0)
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

# Hauptprogramm
if __name__ == "__main__":
    print("="*60)
    print("PDF-AUSGABE TESTER")
    print("="*60)
    
    # Datenbank laden
    DB_PATH = Path("Stammdaten-Projekt/stammdatenverwaltung.db")
    
    if not DB_PATH.exists():
        print(f"❌ Fehler: Datenbank nicht gefunden: {DB_PATH.absolute()}")
        exit(1)
    
    print(f"✅ Datenbank gefunden: {DB_PATH.absolute()}\n")
    
    # Mitarbeiter laden
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    employees = conn.execute("""
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
        LIMIT 3
    """).fetchall()
    
    conn.close()
    
    if not employees:
        print("❌ Keine Mitarbeiter gefunden!")
        exit(1)
    
    print(f"📊 {len(employees)} Mitarbeiter werden getestet\n")
    
    # Erstelle Ausgabe-Ordner
    output_dir = Path("test_pdfs")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Ausgabe-Ordner: {output_dir.absolute()}\n")
    
    # Generiere PDFs
    for idx, emp in enumerate(employees, 1):
        print(f"\n[{idx}/{len(employees)}] {emp['PERS_SURNAME']} {emp['PERS_FIRSTNAME']}")
        
        # Daten vorbereiten
        person_data = {
            'surname': emp['PERS_SURNAME'],
            'name': emp['PERS_FIRSTNAME'],
            'birthdate': emp['PERS_BIRTHDATE'],
            'street': emp['PERS_STREET'],
            'housenr': emp['PERS_HOUSENR'],
            'zip': emp['PERS_ZIP'],
            'place': emp['PERS_PLACE'],
            'pers_id': emp['PERS_ID']
        }
        
        employee_data = person_data.copy()
        employee_data['entrydate'] = emp['EMPL_ENTRYDATE']
        
        # Stammdatenblatt
        try:
            pdf_bytes = generate_stammdatenblatt_test(person_data)
            filename = output_dir / f"Stammdatenblatt_{emp['PERS_SURNAME']}_{emp['PERS_FIRSTNAME']}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            print(f"  ✅ Stammdatenblatt erstellt: {filename.name}")
        except Exception as e:
            print(f"  ❌ Stammdatenblatt Fehler: {e}")
        
        # Lohnzettel
        try:
            brutto = float(emp['EMPL_BRUTTOGEHALT'])
            sv = round(brutto * 0.1807, 2)
            tax = round(max(brutto - sv, 0) * 0.2, 2)
            netto = round(brutto - sv - tax, 2)
            
            abrechnung = {
                "SV": sv,
                "Lohnsteuer": tax
            }
            
            pdf_bytes = generate_lohnzettel_test(employee_data, brutto, netto, abrechnung)
            filename = output_dir / f"Lohnzettel_{emp['PERS_SURNAME']}_{emp['PERS_FIRSTNAME']}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            print(f"  ✅ Lohnzettel erstellt: {filename.name}")
            print(f"     Brutto: {brutto:.2f} EUR | Netto: {netto:.2f} EUR")
        except Exception as e:
            print(f"  ❌ Lohnzettel Fehler: {e}")
    
    print("\n" + "="*60)
    print("✅ FERTIG! Alle PDFs wurden erstellt.")
    print(f"📂 Speicherort: {output_dir.absolute()}")
    print("="*60)
