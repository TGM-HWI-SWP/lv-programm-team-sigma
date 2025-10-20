from fpdf import FPDF
import datetime
import streamlit as st

# Hilfsfunktion: Konvertiere String mit Komma zu Float
def str_to_float(value, default=0.0):
    """Konvertiert String (auch mit Komma) zu Float"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Ersetze Komma durch Punkt und konvertiere
        return float(str(value).replace(',', '.'))
    except (ValueError, AttributeError):
        return default

# Professionelles Stammdatenblatt
def generate_stammdatenblatt_pdf(person_obj):
    """
    Generiert ein professionelles Stammdatenblatt-PDF für eine Person.
    
    Args:
        person_obj: Person-Objekt mit Attributen: surname, name, birthdate, street, housenr, zip, place, obj_id
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    
    # === FARBEN ===
    COLOR_HEADER = (52, 73, 94)      # Dunkelblau
    COLOR_ACCENT = (41, 128, 185)    # Hellblau
    COLOR_LIGHT_BG = (236, 240, 241) # Hellgrau
    COLOR_TEXT = (44, 62, 80)        # Dunkelgrau
    
    # === KOPFZEILE ===
    pdf.set_fill_color(*COLOR_HEADER)
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_xy(10, 10)
    pdf.cell(0, 10, "Stammdatenblatt", ln=True)
    
    # === PERSONENDATEN BOX ===
    pdf.set_text_color(*COLOR_TEXT)
    y_pos = 45
    
    # Name - Hervorgehoben
    pdf.set_fill_color(*COLOR_ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 10, f"{person_obj.surname} {person_obj.name}", border=1, fill=True, align='C')
    y_pos += 15
    
    # Datenfelder mit alternierender Hintergrundfarbe
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Arial", '', 11)
    
    fields = [
        ("Personen-ID:", str(person_obj.obj_id)),
        ("Geburtsdatum:", str(person_obj.birthdate)),
        ("Straße / Hausnummer:", f"{person_obj.street} {person_obj.housenr}"),
        ("PLZ / Ort:", f"{person_obj.zip} {person_obj.place}")
    ]
    
    for i, (label, value) in enumerate(fields):
        # Alternierende Hintergrundfarbe
        if i % 2 == 0:
            pdf.set_fill_color(*COLOR_LIGHT_BG)
            fill = True
        else:
            fill = False
        
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(70, 9, label, border=1, fill=fill)
        pdf.set_font("Arial", '', 11)
        pdf.cell(120, 9, value, border=1, fill=fill)
        y_pos += 9
    
    # === DEKORATIVE LINIE ===
    pdf.set_draw_color(*COLOR_ACCENT)
    pdf.set_line_width(0.5)
    pdf.line(10, y_pos + 10, 200, y_pos + 10)
    
    # === FUßZEILE ===
    pdf.set_y(270)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')} | Team Sigma Personalverwaltung", align='C')
    
    return pdf.output(dest='S').encode('latin1')


# Professioneller BMD-Style Lohnzettel
def generate_real_payroll_pdf(employee_obj, brutto, netto, abrechnung_data=None):
    """
    Generiert einen professionellen Lohn- und Gehaltszettel im BMD-Stil.
    
    Args:
        employee_obj: Mitarbeiter-Objekt mit Attributen
        brutto: Bruttogehalt (float)
        netto: Nettogehalt (float)
        abrechnung_data: Dict mit Abrechnungsdaten
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    
    # === FARBEN DEFINIEREN (BMD-Style) ===
    COLOR_HEADER_BG = (41, 128, 185)      # Blau für Kopfzeile
    COLOR_TABLE_HEADER = (52, 152, 219)   # Hellblau für Tabellenheader
    COLOR_GRAY_LIGHT = (236, 240, 241)    # Hellgrau für alternierende Zeilen
    COLOR_TEXT_DARK = (44, 62, 80)        # Dunkelgrau für Text
    COLOR_ACCENT = (46, 204, 113)         # Grün für Netto
    
    # === KOPFZEILE MIT FIRMENINFO ===
    pdf.set_fill_color(*COLOR_HEADER_BG)
    pdf.rect(0, 0, 210, 35, 'F')  # Blaue Box über gesamte Breite
    
    pdf.set_text_color(255, 255, 255)  # Weißer Text
    pdf.set_font("Arial", 'B', 16)
    pdf.set_xy(10, 8)
    pdf.cell(0, 8, "Lohn- und Gehaltsabrechnung", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.set_xy(10, 18)
    pdf.cell(0, 5, "Team Sigma GmbH | Musterstraße 1 | 1010 Wien", ln=True)
    pdf.set_xy(10, 23)
    month_year = datetime.date.today().strftime('%B %Y')
    pdf.cell(0, 5, f"Abrechnungsmonat: {month_year}", ln=True)
    
    # === MITARBEITERDATEN BOX ===
    pdf.set_text_color(*COLOR_TEXT_DARK)
    y_start = 45
    pdf.set_xy(10, y_start)
    
    # Box mit Rahmen
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.rect(10, y_start, 190, 35)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(15, y_start + 3)
    pdf.cell(0, 6, "MITARBEITER", ln=True)
    
    pdf.set_font("Arial", '', 10)
    pdf.set_xy(15, y_start + 11)
    pdf.cell(60, 5, f"Name:", border=0)
    pdf.cell(0, 5, f"{employee_obj.surname} {employee_obj.name}", ln=True)
    
    pdf.set_xy(15, y_start + 17)
    pdf.cell(60, 5, f"Geburtsdatum:", border=0)
    pdf.cell(0, 5, f"{employee_obj.birthdate}", ln=True)
    
    pdf.set_xy(15, y_start + 23)
    pdf.cell(60, 5, f"Adresse:", border=0)
    pdf.cell(0, 5, f"{employee_obj.street} {employee_obj.housenr}, {employee_obj.zip} {employee_obj.place}", ln=True)
    
    # === BEZÜGE TABELLE (BMD-STIL) ===
    y_table = y_start + 45
    pdf.set_xy(10, y_table)
    
    # Tabellen-Header
    pdf.set_fill_color(*COLOR_TABLE_HEADER)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    
    col_widths = [100, 40, 50]  # Spaltenbreiten
    headers = ["Bezüge / Abzüge", "Satz", "Betrag (EUR)"]
    
    x_pos = 10
    for i, header in enumerate(headers):
        pdf.set_xy(x_pos, y_table)
        pdf.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        x_pos += col_widths[i]
    
    y_table += 8
    
    # === BRUTTOBEZÜGE ===
    pdf.set_text_color(*COLOR_TEXT_DARK)
    pdf.set_font("Arial", '', 10)
    
    # Grundgehalt
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Grundgehalt (Brutto)", border=1)
    pdf.cell(col_widths[1], 7, "", border=1)
    pdf.cell(col_widths[2], 7, f"{brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 7
    
    # Weitere Bezüge aus abrechnung_data
    if abrechnung_data:
        bezuege_keys = ["sonderzahlungen", "mehrstunden25", "überstunden50"]
        for key in bezuege_keys:
            betrag = abrechnung_data.get(key, 0)
            if betrag > 0:
                label_map = {
                    "sonderzahlungen": "  Sonderzahlungen",
                    "mehrstunden25": "  Mehrstunden 25%",
                    "überstunden50": "  Überstunden 50%"
                }
                pdf.set_xy(10, y_table)
                pdf.cell(col_widths[0], 7, label_map.get(key, key), border=1)
                pdf.cell(col_widths[1], 7, "", border=1)
                pdf.cell(col_widths[2], 7, f"{betrag:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
                y_table += 7
    
    # === ABZÜGE ===
    # Zwischensumme Brutto
    brutto_gesamt = brutto
    if abrechnung_data:
        for key in ["sonderzahlungen", "mehrstunden25", "überstunden50"]:
            brutto_gesamt += abrechnung_data.get(key, 0)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(*COLOR_GRAY_LIGHT)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Zwischensumme Brutto", border=1, fill=True)
    pdf.cell(col_widths[1], 7, "", border=1, fill=True)
    pdf.cell(col_widths[2], 7, f"{brutto_gesamt:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    y_table += 7
    
    pdf.set_font("Arial", '', 10)
    
    # SV-Abzug
    sv = abrechnung_data.get("SV", 0) if abrechnung_data else 0
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Sozialversicherung", border=1)
    satz_sv = (sv / brutto * 100) if brutto > 0 else 0
    pdf.cell(col_widths[1], 7, f"{satz_sv:.2f}%", border=1, align='C')
    pdf.cell(col_widths[2], 7, f"-{sv:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 7
    
    # Lohnsteuer
    tax = abrechnung_data.get("Lohnsteuer", 0) if abrechnung_data else 0
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 7, "  Lohnsteuer", border=1)
    pdf.cell(col_widths[1], 7, "", border=1)
    pdf.cell(col_widths[2], 7, f"-{tax:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 7
    
    # Weitere Abzüge
    if abrechnung_data:
        if abrechnung_data.get("Gewerkschaft", 0) > 0:
            gew = abrechnung_data["Gewerkschaft"]
            pdf.set_xy(10, y_table)
            pdf.cell(col_widths[0], 7, "  Gewerkschaftsbeitrag", border=1)
            pdf.cell(col_widths[1], 7, "", border=1)
            pdf.cell(col_widths[2], 7, f"-{gew:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
            y_table += 7
    
    # === NETTO (HERVORGEHOBEN) ===
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(*COLOR_ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 9, "  AUSZAHLUNGSBETRAG (NETTO)", border=1, fill=True)
    pdf.cell(col_widths[1], 9, "", border=1, fill=True)
    pdf.cell(col_widths[2], 9, f"{netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    y_table += 9
    
    # === FUßZEILE ===
    pdf.set_text_color(*COLOR_TEXT_DARK)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_xy(10, y_table + 10)
    pdf.cell(0, 5, "Alle Angaben ohne Gewähr. Bei Fragen wenden Sie sich bitte an die Personalabteilung.", ln=True)
    
    # Seitennummer und Datum unten
    pdf.set_y(280)
    pdf.set_font("Arial", '', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Erstellt am {datetime.date.today().strftime('%d.%m.%Y')} | Seite 1 von 1", align='C')
    
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
            
            # WICHTIG: Konvertiere Brutto sicher (kann String mit Komma sein!)
            brutto = str_to_float(selected_employee['EMPL_BRUTTOGEHALT'], 0.0)
            
            # Berechne Abzüge (vereinfacht nach österreichischem System)
            sv = round(brutto * 0.1807, 2)  # Sozialversicherung ~18%
            tax = round(max(brutto - sv, 0) * 0.2, 2)  # Lohnsteuer ~20%
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

