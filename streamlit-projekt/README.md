# Team Sigma - Streamlit Personalverwaltung

Moderne Webanwendung zur Verwaltung von Stammdaten, Mitarbeitern und Lohnverrechnung, gebaut mit Streamlit.

## 🚀 Features

- **Stammdatenverwaltung**: CRUD-Operationen für Personen
- **Mitarbeiterverwaltung**: Verwaltung von Mitarbeiterdaten mit Verknüpfung zu Personen
- **Lohnverrechnung**: Brutto-Netto-Rechner für österreichisches Lohnsteuerrecht (2025)
- **Datenanalyse**: Upload und Analyse von CSV/XLSX-Dateien
- **Extras**: PDF-Download, Datenbank-Reset, Konfiguration

## 📦 Installation

### 1. Repository klonen
```bash
git clone <repository-url>
cd streamlit-projekt
```

### 2. Virtuelle Umgebung erstellen (empfohlen)
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Abhängigkeiten installieren
```powershell
pip install -r requirements.txt
```

## 🎯 Verwendung

### Anwendung starten
```powershell
streamlit run app.py
```

Die Anwendung öffnet sich automatisch im Browser unter `http://localhost:8501`

### Seitenübersicht

#### 📊 01 Analyse
- CSV/XLSX-Dateien hochladen
- Deskriptive Statistik anzeigen
- Interaktive Plots erstellen (Scatter, Bar, Line)

#### ⚙️ 02 Einstellungen
- Konfigurationsdateien verwalten
- API-Keys (Demo) im Session State speichern

#### 👤 03 Stammdaten
- Personen anlegen, bearbeiten, löschen
- Übersicht aller Personen in Tabellenform
- Vollständige Adressverwaltung

#### 🧑‍💼 04 Mitarbeiter
- Mitarbeiter anlegen (verknüpft mit Personen)
- Gehalt und Eintrittsdatum verwalten
- CRUD-Operationen

#### 💶 05 Lohnverrechnung
- Mitarbeiter auswählen (Mehrfachauswahl möglich)
- Brutto-Netto-Berechnung nach österreichischem Recht
- Detaillierte Abrechnungsansicht

#### ✨ 06 Extras
- Projektbeschreibung (PDF) herunterladen
- Datenbank zurücksetzen
- Hilfe und Informationen

## 🗂️ Projektstruktur

```
streamlit-projekt/
├── app.py                      # Hauptanwendung
├── requirements.txt            # Python-Abhängigkeiten
├── stammdatenverwaltung.db    # SQLite-Datenbank
├── .streamlit/
│   └── config.toml            # Streamlit-Konfiguration
├── modules/
│   ├── __init__.py
│   ├── dbms.py                # Datenbankmanagement
│   ├── person.py              # Personen-Model
│   ├── employee.py            # Mitarbeiter-Model
│   └── Abrechnung.py          # Lohnverrechnung
├── pages/
│   ├── 01_ _Analyse.py
│   ├── 02_ _Einstellungen.py
│   ├── 03_Stammdaten.py
│   ├── 04_Mitarbeiter.py
│   ├── 05_Lohnverrechnung.py
│   └── 06_Extras.py
└── data/
    └── .gitkeep
```

## 🔧 Technologie-Stack

- **Streamlit**: Web-Framework
- **SQLite**: Datenbank
- **Pandas**: Datenverarbeitung
- **Plotly**: Interaktive Visualisierungen
- **Python 3.11+**: Programmiersprache

## 📝 Datenbank-Schema

### Tabelle: PERSON
- PERS_ID (Primary Key)
- PERS_SURNAME, PERS_FIRSTNAME
- PERS_BIRTHDATE
- PERS_STREET, PERS_HOUSENR, PERS_FLOOR
- PERS_ZIP, PERS_PLACE

### Tabelle: MITARBEITER
- EMPL_ID (Primary Key)
- PERS_ID (Foreign Key → PERSON)
- EMPL_ENTRYDATE
- EMPL_BRUTTOGEHALT

## 🛠️ Entwicklung

### Code-Stil
- PEP 8 konform
- Type Hints
- Docstrings für alle Funktionen

### Git
```bash
# .gitignore ist bereits konfiguriert für:
.venv/
__pycache__/
*.pyc
*.db (optional)
```

## 📄 Lizenz

Projektarbeit für TGM-HWI-SWP

## 👥 Team Sigma

Version 1.0.0 - Oktober 2025
