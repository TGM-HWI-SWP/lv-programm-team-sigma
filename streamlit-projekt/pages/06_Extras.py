import streamlit as st
import shutil
from pathlib import Path
import sqlite3

st.title("Extras & Werkzeuge")

# --- Projektbeschreibung ---
st.subheader("Projektbeschreibung (PDF)")
pdf_path = Path(__file__).parent.parent / "LV-Projektbeschreibung.pdf"  # liegt im Projektroot
if pdf_path.exists():
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📄 Projektbeschreibung herunterladen",
            data=pdf_file,
            file_name="LV-Projektbeschreibung.pdf",
            mime="application/pdf",
        )
else:
    st.warning("Projektbeschreibung nicht gefunden.")

# --- Datenbank zurücksetzen ---
st.subheader("Datenbank zurücksetzen")

# immer dieselbe DB wie die App verwenden (Projektroot)
db_path = Path(__file__).parent.parent / "stammdatenverwaltung.db"
db_backup = db_path.with_suffix(".bak")

if db_path.exists():
    if st.button("Backup erstellen & Datenbank zurücksetzen"):
        shutil.copy(db_path, db_backup)
        db_path.unlink()
        st.success(
            "✅ Backup erstellt und Datenbank gelöscht.\n"
            "Starte die App neu, um eine frische Datenbank zu erhalten."
        )
else:
    st.info("ℹ️ Datenbank nicht gefunden.")

# --- Debug-Info: aktueller Pfad & Größe ---
st.subheader("Debug: aktuell verwendete Datenbank")
st.code(
    f"DB-Pfad: {db_path.resolve()}\n"
    f"Existiert: {db_path.exists()}\n"
    f"Größe: {db_path.stat().st_size if db_path.exists() else 0} Bytes"
)

# --- Tabellenübersicht (optional zum Prüfen) ---
if db_path.exists() and st.checkbox("Tabellen anzeigen"):
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = [r[0] for r in cur.fetchall()]
        st.write("Gefundene Tabellen:", tables)
    except Exception as e:
        st.error(f"Fehler beim Lesen der Tabellen: {e}")
    finally:
        con.close()
