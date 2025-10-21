import sqlite3

conn = sqlite3.connect('streamlit-projekt/stammdatenverwaltung.db')
cursor = conn.cursor()

# Drop the broken trigger
try:
    cursor.execute("DROP TRIGGER IF EXISTS trg_update_person")
    conn.commit()
    print("✅ Trigger 'trg_update_person' wurde erfolgreich gelöscht!")
except Exception as e:
    print(f"❌ Fehler beim Löschen des Triggers: {e}")

conn.close()
