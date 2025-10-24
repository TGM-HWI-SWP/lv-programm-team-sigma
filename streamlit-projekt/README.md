# Team Sigma - Streamlit Personalverwaltung

Moderne Webanwendung zur Verwaltung von Stammdaten, Mitarbeitern und Lohnverrechnung, gebaut mit Streamlit.

## 🚀 Features

- **Stammdatenverwaltung**: CRUD-Operationen für Personen
- **Mitarbeiterverwaltung**: Verwaltung von Mitarbeiterdaten mit Verknüpfung zu Personen
- **Lohnverrechnung**: Brutto-Netto-Rechner für österreichisches Lohnsteuerrecht (2025)
- **Datenanalyse**: Upload und Analyse von CSV/XLSX-Dateien
- **Extras**: PDF-Download, Datenbank-Reset, Konfiguration

## 📦 Installation

Kurzfassung (falls Umgebung bereits steht):
```powershell
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
streamlit run Startseite.py
```
Die App öffnet sich unter `http://localhost:8501`.

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
├── Startseite.py                # App-Einstieg
├── requirements.txt             # Abhängigkeiten
├── stammdatenverwaltung.db      # SQLite-Datenbank
├── .streamlit/
│   └── config.toml              # Streamlit-Konfiguration
├── modules/
│   ├── __init__.py
│   ├── Abrechnung.py            # Lohnverrechnung / B2N-Logik
│   ├── auth.py                  # Login/Session
│   ├── dbms.py                  # DB-Access-Layer
│   ├── employee.py              # Mitarbeiter-Modell
│   ├── hashing.py               # Passwort-Hashing
│   ├── payroll.py               # Payroll-Orchestrierung
│   └── person.py                # Personen-Modell
├── pages/
│   ├── 01_Analyse.py
│   ├── 02_Stammdaten.py
│   ├── 03_Mitarbeiter.py
│   ├── 04_Lohnverrechnung.py
│   ├── 05_Extras.py
│   ├── 06_Pdf-Ausgabe.py
│   └── 07_Einstellungen.py
└── data/
    └── .gitkeep
```

## 🔧 Technologie-Stack

- **Streamlit**: Web-Framework
- **SQLite**: Datenbank
- **Pandas**: Datenverarbeitung
- **Plotly**: Interaktive Visualisierungen
- **Python 3.11+**: Programmiersprache

## 📝 Datenbank-Schema (Kurz)

### Tabelle: PERSON (Auszug)
- PERS_ID (PK), PERS_SURNAME, PERS_FIRSTNAME, PERS_BIRTHDATE, Adresse…
- PERS_VALID_FROM, PERS_VALID_TO (für Historisierung)

### Tabelle: MITARBEITER (Auszug)
- EMPL_ID (PK), PERS_ID (FK → PERSON), EMPL_ENTRYDATE, EMPL_BRUTTOGEHALT, EMPL_EXITDATE
- EMPL_VALID_FROM, EMPL_VALID_TO (für Historisierung)


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
