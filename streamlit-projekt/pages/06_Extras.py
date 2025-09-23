"""
Extras & Tools – Streamlit-Umsetzung
Datenbank-Reset, Info, PDF-Download
"""
import streamlit as st
from pathlib import Path
import shutil

st.set_page_config(page_title="Extras", page_icon="✨", layout="wide")
st.title("✨ Extras & Tools")

st.subheader("Projektbeschreibung (PDF)")
pdf_path = Path(__file__).parent.parent / "LV-Projektbeschreibung.pdf"
if pdf_path.exists():
    with open(pdf_path, "rb") as f:
        st.download_button("Projektbeschreibung herunterladen", f, file_name="LV-Projektbeschreibung.pdf")
else:
    st.info("PDF nicht gefunden.")

st.subheader("Datenbank zurücksetzen")
db_path = Path(__file__).parent.parent / "Stammdaten-Projekt" / "stammdatenverwaltung.db"
db_backup = db_path.with_suffix(".bak")
if db_path.exists():
    if st.button("Backup erstellen & Datenbank zurücksetzen"):
        shutil.copy(db_path, db_backup)
        db_path.unlink()
        st.success("Backup erstellt und Datenbank gelöscht. Starte die App neu, um eine frische DB zu erhalten.")
else:
    st.info("Datenbank nicht gefunden.")

st.subheader("Info & Hilfe")
st.markdown("""
- **Alle Funktionen**: Stammdaten, Mitarbeiter, Lohnverrechnung, Einstellungen
- **Extras**: PDF-Download, DB-Reset, Info
- **Support**: Bei Problemen bitte an das Team wenden.
""")
