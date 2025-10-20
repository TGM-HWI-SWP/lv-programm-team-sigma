# 🎨 PDF-Design Vorschau - Quick Reference

## STAMMDATENBLATT LAYOUT

```
┌─────────────────────────────────────────────────────────────┐
│ ████████████████████████████████████████████████████████████│ ← DUNKELBLAU
│ ███ Stammdatenblatt (Weiß, 18pt Bold) ████████████████████ │
│ ████████████████████████████████████████████████████████████│
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│          ███ Mauermann Willrich (Weiß) ███                  │ ← HELLBLAU (zentriert)
└─────────────────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────────────────┐
│ Geburtsdatum:          │ 08.06.1999                         │ ← HELLGRAU
├────────────────────────┼────────────────────────────────────┤
│ Straße / Hausnr.:      │ Forellenstraße 82                  │ ← WEISS
├────────────────────────┼────────────────────────────────────┤
│ PLZ / Ort:             │ 55624 Weitersbach                  │ ← HELLGRAU
├────────────────────────┼────────────────────────────────────┤
│ Personen-ID:           │ 23                                 │ ← WEISS
└────────────────────────┴────────────────────────────────────┘

                  Erstellt am 20.10.2025 | Team Sigma (Grau, klein)
```

---

## LOHNZETTEL LAYOUT (BMD-STIL)

```
┌───────────────────────────────────────────────────────────────────┐
│ ██████████████████████████████████████████████████████████████████│ ← BLAU
│ ███ Lohn- und Gehaltsabrechnung (Weiß, 16pt Bold) ███████████████│
│ ███ Team Sigma GmbH | Musterstraße 1 | 1010 Wien ████████████████│
│ ███ Abrechnungsmonat: Oktober 2025 ███████████████████████████████│
└───────────────────────────────────────────────────────────────────┘

┌─ MITARBEITER ─────────────────────────────────────────────────────┐
│ Name: Mauermann Willrich | Adresse: Forellenstraße 82, 55624 ... │
└───────────────────────────────────────────────────────────────────┘

┌──────────────────────────┬─────────────┬──────────────────────────┐
│ ██ Bezüge / Abzüge ██████│ ██ Satz ████│ ██ Betrag (EUR) █████████│ ← HELLBLAU (Header)
├──────────────────────────┼─────────────┼──────────────────────────┤
│   Grundgehalt (Brutto)   │             │               2.891,31   │
├──────────────────────────┼─────────────┼──────────────────────────┤
│ ░ Zwischensumme Brutto ░ │ ░░░░░░░░░░░ │ ░░░░░░░░░░░    2.891,31 ░│ ← HELLGRAU
├──────────────────────────┼─────────────┼──────────────────────────┤
│   Sozialversicherung     │   18,1%     │                -522,46   │
├──────────────────────────┼─────────────┼──────────────────────────┤
│   Lohnsteuer             │             │                -473,77   │
├──────────────────────────┼─────────────┼──────────────────────────┤
│ ███ AUSZAHLUNGSBETRAG ██ │ ███████████ │ ███████████    1.895,08 █│ ← GRÜN (Netto)
│ ███ (NETTO) ████████████ │ ███████████ │ ████████████████████████ │   (Weiße Schrift)
└──────────────────────────┴─────────────┴──────────────────────────┘

                Erstellt am 20.10.2025 | Seite 1 von 1 (Grau, klein)
```

---

## FARB-LEGENDE

### Stammdatenblatt:
- 🟦 **DUNKELBLAU** (#34495e / RGB 52,73,94) - Kopfzeile
- 🔵 **HELLBLAU** (#2980b9 / RGB 41,128,185) - Name-Box
- ⬜ **HELLGRAU** (#ecf0f1 / RGB 236,240,241) - Alternierende Zeilen
- ⬛ **DUNKELGRAU** (#2c3e50 / RGB 44,62,80) - Text

### Lohnzettel:
- 🔵 **BLAU** (#2980b9 / RGB 41,128,185) - Header Background
- 🟦 **HELLBLAU** (#3498db / RGB 52,152,219) - Tabellen-Header
- ⬜ **HELLGRAU** (#ecf0f1 / RGB 236,240,241) - Zwischensummen
- 🟢 **GRÜN** (#2ecc71 / RGB 46,204,113) - Netto-Betrag
- ⬛ **DUNKELGRAU** (#2c3e50 / RGB 44,62,80) - Text
- ⚪ **HELLGRAU TEXT** (RGB 150,150,150) - Fußzeile

---

## MASS-ANGABEN

### Stammdatenblatt:
```
Seite: 210mm x 297mm (A4)
Kopfzeile: 0-30mm
Name-Box: 10mm x 45mm, Breite: 190mm, Höhe: 10mm
Datenfelder: Start bei y=60mm
  - Label-Spalte: 70mm breit
  - Wert-Spalte: 120mm breit
  - Zeilenhöhe: 9mm
Fußzeile: y=270mm
```

### Lohnzettel:
```
Seite: 210mm x 297mm (A4)
Kopfzeile: 0-35mm
Mitarbeiter-Box: 10mm x 45mm, Breite: 190mm, Höhe: 30mm
Tabelle: Start bei y≈85mm
  - Spalte 1 (Bezeichnung): 100mm
  - Spalte 2 (Satz): 40mm
  - Spalte 3 (Betrag): 50mm
  - Zeilenhöhe: 7-8mm (normal), 9mm (Netto)
Fußzeile: y=280mm
```

---

## SCHRIFTARTEN & GRÖSSEN

### Stammdatenblatt:
- **Titel (Kopfzeile):** Arial Bold, 18pt, Weiß
- **Name:** Arial Bold, 14pt, Weiß
- **Labels:** Arial Bold, 11pt, Dunkelgrau
- **Werte:** Arial Regular, 11pt, Dunkelgrau
- **Fußzeile:** Arial Italic, 9pt, Hellgrau

### Lohnzettel:
- **Titel (Kopfzeile):** Arial Bold, 16pt, Weiß
- **Firma-Info:** Arial Regular, 10pt, Weiß
- **Box-Überschrift:** Arial Bold, 11pt, Dunkelgrau
- **Tabellen-Header:** Arial Bold, 10pt, Weiß
- **Tabellen-Inhalt:** Arial Regular, 10pt, Dunkelgrau
- **Zwischensumme:** Arial Bold, 10pt, Dunkelgrau
- **Netto:** Arial Bold, 11pt, Weiß
- **Fußzeile:** Arial Regular, 8pt, Hellgrau

---

## ZAHLENFORMATIERUNG

### Deutsch (Österreich/Deutschland):
```python
# Vorher:  1234.56
# Nachher: 1.234,56

# Code:
betrag_str = f"{betrag:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
# Ergebnis: "2.891,31 EUR"
```

### Prozent-Anzeige:
```python
# Berechnung SV-Satz
satz_sv = (sv / brutto * 100) if brutto > 0 else 0
# Ausgabe: "18,1%"
```

---

## DESIGN-PRINZIPIEN

### ✅ Befolgt:
1. **Visuelle Hierarchie** - Wichtiges steht hervor (Netto grün, Name blau)
2. **Weißraum** - Genug Abstand zwischen Elementen
3. **Konsistenz** - Gleiche Abstände, Schriften, Farben
4. **Lesbarkeit** - Kontrastreiche Farben (Weiß auf Blau/Grün)
5. **Struktur** - Klare Boxen und Tabellen
6. **Professionalität** - Firmen-CI ähnlich BMD

### 🎯 Ziel erreicht:
- ✅ Von "schlicht" zu "professionell"
- ✅ Von "unstrukturiert" zu "klar gegliedert"
- ✅ Von "schwarz/weiß" zu "farbcodiert"
- ✅ Von "Textliste" zu "Tabelle mit Hierarchie"

---

## QUICK-START: Farben anpassen

Alle Farben sind am Anfang der Funktionen definiert:

```python
# In generate_stammdatenblatt_pdf():
COLOR_HEADER = (52, 73, 94)      # Kopfzeile ändern → z.B. (0, 100, 0) für Grün
COLOR_ACCENT = (41, 128, 185)    # Name-Box ändern
COLOR_LIGHT_BG = (236, 240, 241) # Alternierende Zeilen
COLOR_TEXT = (44, 62, 80)        # Textfarbe

# In generate_real_payroll_pdf():
COLOR_HEADER_BG = (41, 128, 185)    # Kopfzeile
COLOR_TABLE_HEADER = (52, 152, 219) # Tabellen-Header
COLOR_ACCENT = (46, 204, 113)       # NETTO-Box → z.B. (255, 165, 0) für Orange
```

---

**Tipp:** Nutze https://www.color-hex.com/ um RGB-Werte zu finden!
