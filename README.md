# Team Sigma – Lohnverrechnung (Streamlit)

Einfaches Setup, klare Startanleitung. Dieses README ist die maßgebliche Installations- und Abgabe-Anleitung. Das Projekt selbst liegt im Ordner `streamlit-projekt/`.

## 🧭 Quickstart (Windows, PowerShell)

1) Repository klonen
```powershell
git clone <repository-url>
cd lv-programm-team-sigma\streamlit-projekt
```

2) Virtuelle Umgebung erstellen und aktivieren
```powershell
python -m venv .venv
.venv\Scripts\activate
```

3) Abhängigkeiten installieren
```powershell
pip install -r requirements.txt
```

4) Optionale DB-Historisierung initialisieren
- Erstellt/erweitert Spalten VALID_FROM/VALID_TO, History-Tabellen und Trigger
```powershell
python migration_historisierung.py
```

5) Anwendung starten
```powershell
streamlit run Startseite.py
```
Öffnet im Browser: http://localhost:8501

## 🧪 Kurzer Funktionstest
- Stammdaten-Seite: Eine Person anlegen, bearbeiten, löschen
- Mitarbeiter-Seite: Mitarbeiter zuordnen, Gehalt setzen
- Lohnverrechnung: Einen Mitarbeiter auswählen und berechnen
- Historie: Seite „08_Historie“ öffnen und Änderungen sehen (nach Migration)

## 🆘 Troubleshooting
- "streamlit: command not found" → Abhängigkeiten installieren oder `.venv` erneut aktivieren
- "ImportError …" → In `streamlit-projekt/` sein und `pip install -r requirements.txt` ausführen
- Port belegt → `streamlit run Startseite.py --server.port 8502`

## 📁 Struktur (wichtigste Teile)
- `streamlit-projekt/Startseite.py` – Einstieg der App
- `streamlit-projekt/modules/` – Modelle, DB, Abrechnung, Auth
- `streamlit-projekt/pages/` – Einzelseiten (Analyse, Stammdaten, Mitarbeiter, Lohn, PDF, Einstellungen, Historie)
- `streamlit-projekt/migration_historisierung.py` – DB-Historisierung (optional, empfohlen)
- `HISTORISIERUNG.md` – kurze Doku zur Historisierung

## 🔗 Weiterführende Infos
- App-Übersicht und Feature-Beschreibung: `streamlit-projekt/README.md`
- Historisierung (Soft Delete + Audit): `HISTORISIERUNG.md`
- LV-Projektbeschreibung: `LV-Projektbeschreibung.pdf`

## 📦 Abgabehinweis
- Dieses README ist die Referenz für Installation/Start.
- Prüfkriterien: App startet lokal, Stammdaten/Mitarbeiter/Lohnverrechnung funktionieren, PDF/Extras optional, Historie (falls Migration ausgeführt).
- Export als ZIP inkl. Datenbank (`stammdatenverwaltung.db`) oder frischer Start (DB wird angelegt).

Version 1.0.0 – Oktober 2025