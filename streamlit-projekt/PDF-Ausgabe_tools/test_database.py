import sqlite3
from pathlib import Path

# Prüfe die richtige Datenbank
db_path = Path("Stammdaten-Projekt/stammdatenverwaltung.db")
print(f"Datenbank-Pfad: {db_path.absolute()}")
print(f"Existiert: {db_path.exists()}\n")

if not db_path.exists():
    print("FEHLER: Datenbank nicht gefunden!")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Zeige alle Tabellen
print("=== ALLE TABELLEN ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f"  - {table}")

print("\n=== PERSON Tabelle ===")
cursor.execute('SELECT COUNT(*) FROM PERSON')
count = cursor.fetchone()[0]
print(f"Anzahl Personen: {count}")
if count > 0:
    cursor.execute('SELECT PERS_ID, PERS_SURNAME, PERS_FIRSTNAME, PERS_BIRTHDATE FROM PERSON LIMIT 5')
    for row in cursor.fetchall():
        print(f"  {row}")

print("\n=== MITARBEITER Tabelle ===")
cursor.execute('SELECT COUNT(*) FROM MITARBEITER')
count = cursor.fetchone()[0]
print(f"Anzahl Mitarbeiter: {count}")
if count > 0:
    cursor.execute('SELECT EMPL_ID, PERS_ID, EMPL_ENTRYDATE, EMPL_BRUTTOGEHALT FROM MITARBEITER LIMIT 5')
    for row in cursor.fetchall():
        print(f"  {row}")
else:
    print("  ⚠️ KEINE MITARBEITER IN DER DATENBANK!")

print("\n=== lohnverrechnung_dn Tabelle ===")
if "lohnverrechnung_dn" in tables:
    cursor.execute('SELECT COUNT(*) FROM lohnverrechnung_dn')
    count = cursor.fetchone()[0]
    print(f"Anzahl Abrechnungen: {count}")
    if count > 0:
        cursor.execute('SELECT * FROM lohnverrechnung_dn LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row}")
else:
    print("  Tabelle nicht vorhanden")

print("\n=== Benutzer Tabelle ===")
if "Benutzer" in tables:
    cursor.execute('SELECT COUNT(*) FROM Benutzer')
    count = cursor.fetchone()[0]
    print(f"Anzahl Benutzer: {count}")
    if count > 0:
        cursor.execute('SELECT * FROM Benutzer LIMIT 3')
        for row in cursor.fetchall():
            print(f"  {row}")
else:
    print("  Tabelle nicht vorhanden")

conn.close()

print("\n" + "="*50)
print("ZUSAMMENFASSUNG:")
print("="*50)
print("✅ Datenbank gefunden")
cursor = sqlite3.connect(str(db_path)).cursor()
person_count = cursor.execute('SELECT COUNT(*) FROM PERSON').fetchone()[0]
mitarbeiter_count = cursor.execute('SELECT COUNT(*) FROM MITARBEITER').fetchone()[0]

print(f"📊 {person_count} Person(en)")
print(f"👥 {mitarbeiter_count} Mitarbeiter")

if mitarbeiter_count == 0:
    print("\n⚠️  PROBLEM: Keine Mitarbeiter vorhanden!")
    print("   → Die PDF-Ausgabe kann nicht getestet werden")
    print("   → Lösung: Erstelle Mitarbeiter über die Streamlit-App")
