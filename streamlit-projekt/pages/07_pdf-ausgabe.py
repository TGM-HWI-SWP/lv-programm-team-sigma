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

# Professionelles Stammdatenblatt - VOLLSTÄNDIGE A4-NUTZUNG
def generate_stammdatenblatt_pdf(person_obj):
    """
    Generiert ein vollständiges, professionelles Stammdatenblatt im BMD-Stil.
    Nutzt die gesamte A4-Seite mit allen relevanten Mitarbeiterinformationen.
    
    Args:
        person_obj: Person-Objekt mit Attributen: surname, name, birthdate, street, housenr, zip, place, obj_id
    
    Returns:
        bytes: PDF als bytes (latin1-encoded)
    """
    pdf = FPDF()
    pdf.add_page()
    
    # === FARBEN (BMD-STIL) ===
    COLOR_HEADER = (41, 128, 185)     # Blau wie Lohnzettel
    COLOR_SECTION = (52, 152, 219)    # Hellblau für Sektionen
    COLOR_LIGHT_BG = (236, 240, 241)  # Hellgrau
    COLOR_TEXT = (44, 62, 80)         # Dunkelgrau
    COLOR_BORDER = (189, 195, 199)    # Hellgrau für Rahmen
    
    # === KOPFZEILE MIT FIRMENINFO ===
    pdf.set_fill_color(*COLOR_HEADER)
    pdf.rect(0, 0, 210, 40, 'F')
    
    # Logo-Bereich (Platzhalter)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, 8, 25, 25, 'D')  # Weißes Quadrat für Logo
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(*COLOR_HEADER)
    pdf.set_xy(15, 18)
    pdf.cell(25, 5, "LOGO", align='C')
    
    # Firmenname und Titel
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_xy(45, 10)
    pdf.cell(0, 10, "STAMMDATENBLATT", ln=True)
    
    pdf.set_font("Arial", '', 9)
    pdf.set_xy(45, 22)
    pdf.cell(0, 5, "Team Sigma GmbH | Musterstraße 1 | 1010 Wien", ln=True)
    pdf.set_xy(45, 28)
    pdf.cell(0, 5, f"Erstellt am: {datetime.date.today().strftime('%d.%m.%Y')}", ln=True)
    
    # === MITARBEITER-ÜBERSCHRIFT ===
    y_pos = 50
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 10, f"{person_obj.surname} {person_obj.name}", border=1, fill=True, align='C')
    y_pos += 12
    
    # === SEKTION 1: PERSONENDATEN ===
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "PERSONENDATEN", border=1, fill=True, align='L')
    y_pos += 8
    
    # Tabelle mit 2 Spalten
    pdf.set_font("Arial", '', 10)
    pdf.set_draw_color(*COLOR_BORDER)
    
    person_data = [
        ("Personen-ID:", str(person_obj.obj_id), "Geschlecht:", "-"),
        ("Geburtsdatum:", str(person_obj.birthdate), "Staatsangehörigkeit:", "Österreich"),
        ("Geburtsort:", "-", "Familienstand:", "-"),
        ("SV-Nummer:", "-", "Telefon:", "-"),
    ]
    
    for i, (label1, value1, label2, value2) in enumerate(person_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # === SEKTION 2: ADRESSDATEN ===
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "ADRESSDATEN", border=1, fill=True, align='L')
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Arial", '', 10)
    
    address_data = [
        ("Straße / Hausnr.:", f"{person_obj.street} {person_obj.housenr}", "E-Mail:", "-"),
        ("PLZ / Ort:", f"{person_obj.zip} {person_obj.place}", "Mobil:", "-"),
        ("Land:", "Österreich", "Fax:", "-"),
    ]
    
    for i, (label1, value1, label2, value2) in enumerate(address_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # === SEKTION 3: BESCHÄFTIGUNGSDATEN ===
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "BESCHÄFTIGUNGSDATEN", border=1, fill=True, align='L')
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    
    employment_data = [
        ("Eintrittsdatum:", getattr(person_obj, 'entrydate', '-'), "Personalnummer:", str(person_obj.obj_id)),
        ("Position:", "-", "Abteilung:", "-"),
        ("Beschäftigungsart:", "Vollzeit", "Wochenarbeitszeit:", "40,0 Std."),
        ("Lohnart:", "Monatslohn", "Kollektivvertrag:", "-"),
    ]
    
    for i, (label1, value1, label2, value2) in enumerate(employment_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # === SEKTION 4: BANKDATEN ===
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "BANKDATEN", border=1, fill=True, align='L')
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    
    bank_data = [
        ("Bankname:", "-", "Kontoinhaber:", f"{person_obj.surname} {person_obj.name}"),
        ("IBAN:", "AT__ ____ ____ ____ ____", "BIC:", "-"),
    ]
    
    for i, (label1, value1, label2, value2) in enumerate(bank_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value2, border=1, fill=fill)
        y_pos += 7
    
    y_pos += 3
    
    # === SEKTION 5: STEUERDATEN ===
    pdf.set_fill_color(*COLOR_SECTION)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_xy(10, y_pos)
    pdf.cell(190, 8, "STEUERDATEN", border=1, fill=True, align='L')
    y_pos += 8
    
    pdf.set_text_color(*COLOR_TEXT)
    
    tax_data = [
        ("Steuernummer:", "-", "Freibetrag:", "0,00 EUR"),
        ("Pendlerpauschale:", "Nein", "Alleinverdiener:", "Nein"),
        ("Kinderfreibetrag:", "0", "Kirchenbeitrag:", "Nein"),
    ]
    
    for i, (label1, value1, label2, value2) in enumerate(tax_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(*COLOR_LIGHT_BG) if fill else pdf.set_fill_color(255, 255, 255)
        
        pdf.set_xy(10, y_pos)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label1, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value1, border=1, fill=fill)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(45, 7, label2, border=1, fill=fill)
        pdf.set_font("Arial", '', 9)
        pdf.cell(50, 7, value2, border=1, fill=fill)
        y_pos += 7
    
    # === SIGNATURFELD (falls Platz) ===
    if y_pos < 260:
        y_pos += 5
        pdf.set_draw_color(*COLOR_BORDER)
        pdf.rect(10, y_pos, 90, 20)
        pdf.rect(110, y_pos, 90, 20)
        
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(150, 150, 150)
        pdf.set_xy(10, y_pos + 15)
        pdf.cell(90, 5, "Unterschrift Mitarbeiter", align='C')
        pdf.set_xy(110, y_pos + 15)
        pdf.cell(90, 5, "Unterschrift Geschäftsführung", align='C')
    
    # === FUßZEILE ===
    pdf.set_y(285)
    pdf.set_font("Arial", '', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 3, "Team Sigma GmbH | UID: ATU12345678", align='L')
    pdf.cell(95, 3, f"Seite 1 | {datetime.date.today().strftime('%d.%m.%Y')}", align='R')
    
    return pdf.output(dest='S').encode('latin1')


# Professioneller BMD-Style Lohnzettel - OPTIMIERT
def generate_real_payroll_pdf(employee_obj, brutto, netto, abrechnung_data=None):
    """
    Generiert einen vollständigen, professionellen Lohn- und Gehaltszettel im BMD-Stil.
    Optimiert für maximale Raumnutzung und professionelle Optik.
    
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
    
    # === FARBEN (BMD-STIL) ===
    COLOR_HEADER_BG = (41, 128, 185)      # Blau für Kopfzeile
    COLOR_TABLE_HEADER = (52, 152, 219)   # Hellblau für Tabellenheader
    COLOR_GRAY_LIGHT = (236, 240, 241)    # Hellgrau für alternierende Zeilen
    COLOR_TEXT_DARK = (44, 62, 80)        # Dunkelgrau für Text
    COLOR_ACCENT = (46, 204, 113)         # Grün für Netto
    COLOR_BORDER = (189, 195, 199)        # Hellgrau für Rahmen
    
    # === KOPFZEILE MIT FIRMENINFO ===
    pdf.set_fill_color(*COLOR_HEADER_BG)
    pdf.rect(0, 0, 210, 45, 'F')
    
    # Logo-Bereich
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(15, 8, 25, 25, 'D')
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(*COLOR_HEADER_BG)
    pdf.set_xy(15, 18)
    pdf.cell(25, 5, "LOGO", align='C')
    
    # Firmentitel
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 18)
    pdf.set_xy(45, 8)
    pdf.cell(0, 8, "Lohn- und Gehaltsabrechnung", ln=True)
    
    pdf.set_font("Arial", '', 9)
    pdf.set_xy(45, 18)
    pdf.cell(0, 4, "Team Sigma GmbH", ln=True)
    pdf.set_xy(45, 23)
    pdf.cell(0, 4, "Musterstraße 1 | 1010 Wien", ln=True)
    pdf.set_xy(45, 28)
    pdf.cell(0, 4, "UID: ATU12345678", ln=True)
    
    # Abrechnungsmonat
    pdf.set_font("Arial", 'B', 10)
    pdf.set_xy(45, 35)
    month_year = datetime.date.today().strftime('%B %Y')
    pdf.cell(0, 5, f"Abrechnungsmonat: {month_year}", ln=True)
    
    # === MITARBEITER-INFORMATIONSBOX (KOMPAKT) ===
    y_start = 52
    pdf.set_text_color(*COLOR_TEXT_DARK)
    pdf.set_draw_color(*COLOR_BORDER)
    pdf.set_line_width(0.3)
    
    # Box-Header
    pdf.set_fill_color(*COLOR_TABLE_HEADER)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_xy(10, y_start)
    pdf.cell(190, 7, "MITARBEITER-DATEN", border=1, fill=True, align='L')
    y_start += 7
    
    # Mitarbeiterdaten in 2 Spalten
    pdf.set_text_color(*COLOR_TEXT_DARK)
    pdf.set_font("Arial", '', 8)
    
    name = f"{employee_obj.surname} {employee_obj.name}"
    addr = f"{employee_obj.street} {employee_obj.housenr}".strip()
    place = f"{employee_obj.zip} {employee_obj.place}".strip()
    
    # Linke Spalte
    pdf.set_xy(10, y_start)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(30, 5, "Name:", border=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(65, 5, name, border=1)
    
    # Rechte Spalte
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(30, 5, "Pers.-Nr.:", border=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(65, 5, str(getattr(employee_obj, 'obj_id', '-')), border=1)
    y_start += 5
    
    pdf.set_xy(10, y_start)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(30, 5, "Geburtsdatum:", border=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(65, 5, str(employee_obj.birthdate), border=1)
    
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(30, 5, "Eintritt:", border=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(65, 5, str(getattr(employee_obj, 'entrydate', '-')), border=1)
    y_start += 5
    
    pdf.set_xy(10, y_start)
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(30, 5, "Adresse:", border=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(65, 5, f"{addr}, {place}", border=1)
    
    pdf.set_font("Arial", 'B', 8)
    pdf.cell(30, 5, "SV-Nr.:", border=1)
    pdf.set_font("Arial", '', 8)
    pdf.cell(65, 5, "-", border=1)
    y_start += 8
    
    # === GEHALTSTABELLE (ERWEITERT) ===
    y_table = y_start
    
    # Tabellen-Header
    pdf.set_fill_color(*COLOR_TABLE_HEADER)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 9)
    
    col_widths = [80, 30, 30, 50]  # Bezeichnung | Menge | Satz | Betrag
    headers = ["Bezeichnung", "Menge", "Satz", "Betrag (EUR)"]
    
    x_pos = 10
    for i, header in enumerate(headers):
        pdf.set_xy(x_pos, y_table)
        pdf.cell(col_widths[i], 7, header, border=1, fill=True, align='C')
        x_pos += col_widths[i]
    
    y_table += 7
    
    # === BRUTTOBEZÜGE ===
    pdf.set_text_color(*COLOR_TEXT_DARK)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(*COLOR_GRAY_LIGHT)
    pdf.set_xy(10, y_table)
    pdf.cell(190, 6, "BRUTTOBEZÜGE", border=1, fill=True)
    y_table += 6
    
    pdf.set_font("Arial", '', 8)
    
    # Grundgehalt
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 6, "  Grundgehalt / Monatslohn", border=1)
    pdf.cell(col_widths[1], 6, "1,000", border=1, align='C')
    pdf.cell(col_widths[2], 6, "", border=1)
    pdf.cell(col_widths[3], 6, f"{brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 6
    
    # Weitere Bezüge (falls vorhanden)
    if abrechnung_data:
        extra_items = [
            ("sonderzahlungen", "  Sonderzahlungen"),
            ("mehrstunden25", "  Mehrstunden 25%"),
            ("überstunden50", "  Überstunden 50%"),
            ("zulagen", "  Zulagen"),
        ]
        
        for key, label in extra_items:
            betrag = abrechnung_data.get(key, 0)
            if betrag > 0:
                pdf.set_xy(10, y_table)
                pdf.cell(col_widths[0], 6, label, border=1)
                pdf.cell(col_widths[1], 6, "", border=1)
                pdf.cell(col_widths[2], 6, "", border=1)
                pdf.cell(col_widths[3], 6, f"{betrag:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
                y_table += 6
    
    # Zwischensumme Brutto
    brutto_gesamt = brutto
    if abrechnung_data:
        for key in ["sonderzahlungen", "mehrstunden25", "überstunden50", "zulagen"]:
            brutto_gesamt += abrechnung_data.get(key, 0)
    
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(*COLOR_GRAY_LIGHT)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 6, "Zwischensumme Brutto", border=1, fill=True, align='R')
    pdf.cell(col_widths[3], 6, f"{brutto_gesamt:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    y_table += 8
    
    # === ABZÜGE ===
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(*COLOR_GRAY_LIGHT)
    pdf.set_xy(10, y_table)
    pdf.cell(190, 6, "ABZÜGE", border=1, fill=True)
    y_table += 6
    
    pdf.set_font("Arial", '', 8)
    
    # SV-Abzug
    sv = abrechnung_data.get("SV", 0) if abrechnung_data else 0
    satz_sv = (sv / brutto * 100) if brutto > 0 else 0
    
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 6, "  Sozialversicherung lfd.", border=1)
    pdf.cell(col_widths[1], 6, "", border=1)
    pdf.cell(col_widths[2], 6, f"{satz_sv:.2f}%", border=1, align='C')
    pdf.cell(col_widths[3], 6, f"-{sv:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 6
    
    # Lohnsteuer
    tax = abrechnung_data.get("Lohnsteuer", 0) if abrechnung_data else 0
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0], 6, "  Lohnsteuer", border=1)
    pdf.cell(col_widths[1], 6, "", border=1)
    pdf.cell(col_widths[2], 6, "", border=1)
    pdf.cell(col_widths[3], 6, f"-{tax:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
    y_table += 6
    
    # Weitere Abzüge
    if abrechnung_data and abrechnung_data.get("Gewerkschaft", 0) > 0:
        gew = abrechnung_data["Gewerkschaft"]
        pdf.set_xy(10, y_table)
        pdf.cell(col_widths[0], 6, "  Gewerkschaftsbeitrag", border=1)
        pdf.cell(col_widths[1], 6, "", border=1)
        pdf.cell(col_widths[2], 6, "", border=1)
        pdf.cell(col_widths[3], 6, f"-{gew:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R')
        y_table += 6
    
    # Summe Abzüge
    summe_abzuege = sv + tax + (abrechnung_data.get("Gewerkschaft", 0) if abrechnung_data else 0)
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(*COLOR_GRAY_LIGHT)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 6, "Summe Abzüge", border=1, fill=True, align='R')
    pdf.cell(col_widths[3], 6, f"-{summe_abzuege:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    y_table += 8
    
    # === NETTO (HERVORGEHOBEN) ===
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(*COLOR_ACCENT)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(10, y_table)
    pdf.cell(col_widths[0] + col_widths[1] + col_widths[2], 10, "AUSZAHLUNGSBETRAG (NETTO)", border=1, fill=True, align='R')
    pdf.cell(col_widths[3], 10, f"{netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), border=1, align='R', fill=True)
    y_table += 12
    
    # === ZUSATZINFORMATIONEN ===
    if y_table < 250:
        y_table += 5
        pdf.set_text_color(*COLOR_TEXT_DARK)
        pdf.set_font("Arial", 'B', 9)
        pdf.set_xy(10, y_table)
        pdf.cell(0, 5, "ZUSATZINFORMATIONEN", ln=True)
        y_table += 6
        
        pdf.set_font("Arial", '', 8)
        pdf.set_xy(10, y_table)
        pdf.multi_cell(190, 4, 
            "Der Auszahlungsbetrag wird auf das hinterlegte Bankkonto überwiesen.\n"
            "Bitte bewahren Sie diese Abrechnung für Ihre Unterlagen auf.\n"
            "Bei Fragen wenden Sie sich bitte an die Personalabteilung."
        )
    
    # === FUßZEILE ===
    pdf.set_y(285)
    pdf.set_font("Arial", '', 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(63, 3, "Team Sigma GmbH", align='L')
    pdf.cell(64, 3, "Vertraulich", align='C')
    pdf.cell(63, 3, f"Seite 1 | {datetime.date.today().strftime('%d.%m.%Y')}", align='R')
    
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

