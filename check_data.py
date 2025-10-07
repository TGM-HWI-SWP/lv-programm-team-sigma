import sqlite3

# Check data in streamlit database
conn = sqlite3.connect('streamlit-projekt/stammdatenverwaltung.db')
cursor = conn.cursor()

print("=== PERSON table sample ===")
cursor.execute('SELECT * FROM PERSON LIMIT 5')
for row in cursor.fetchall():
    print(row)

print("\n=== MITARBEITER table sample ===")
cursor.execute('SELECT * FROM MITARBEITER LIMIT 5')
for row in cursor.fetchall():
    print(row)

print("\n=== LOHNABRECHNUNG table sample ===")
cursor.execute('SELECT * FROM LOHNABRECHNUNG LIMIT 5')
for row in cursor.fetchall():
    print(row)

print("\n=== Benutzer table sample ===")
cursor.execute('SELECT * FROM Benutzer LIMIT 5')
for row in cursor.fetchall():
    print(row)

conn.close()