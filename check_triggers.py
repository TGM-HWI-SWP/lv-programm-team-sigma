import sqlite3

conn = sqlite3.connect('streamlit-projekt/stammdatenverwaltung.db')
cursor = conn.cursor()

# List all triggers on PERSON table
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='PERSON'")
triggers = cursor.fetchall()

print("=== TRIGGERS ON PERSON TABLE ===\n")
for name, sql in triggers:
    print(f"Trigger Name: {name}")
    print(f"SQL:\n{sql}\n")
    print("="*80 + "\n")

# Also check if VALID_TO column exists
cursor.execute("PRAGMA table_info(PERSON)")
columns = cursor.fetchall()
print("\n=== PERSON TABLE COLUMNS ===")
for col in columns:
    print(f"{col[1]} ({col[2]})")

conn.close()
