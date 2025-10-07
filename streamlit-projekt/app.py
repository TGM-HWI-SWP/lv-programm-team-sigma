import streamlit as st
from pathlib import Path
import pandas as pd

from modules import dbms, person, employee

st.set_page_config(page_title="Team Sigma – Demo", page_icon=" ", layout="wide")

# --- Datenbank initialisieren ---
DB_PATH = Path(__file__).parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

# Tabellen erstellen, falls nicht vorhanden
person.person.initialize_db_table(db)
employee.mitarbeiter.initialize_db_table(db)

# --- Session State Defaults ---
if "dataset" not in st.session_state:
    st.session_state.dataset = None
if "df" not in st.session_state:
    st.session_state.df = None

st.title(" Team Sigma – Streamlit Starter")
st.write("Willkommen! Nutze die Seitenleiste zur Navigation.")

with st.sidebar:
    st.header(" Daten laden")
    uploaded = st.file_uploader("CSV/XLSX hochladen", type=["csv", "xlsx"])
    if uploaded is not None:
        st.session_state.dataset = uploaded.name
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.session_state.df = df
            st.success(f"{uploaded.name} geladen – {df.shape[0]} Zeilen × {df.shape[1]} Spalten")
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")
    st.divider()
    st.caption("Version 0.1.0 • Streamlit Starter")

st.subheader("Schnellstart")
st.markdown(
    """
    📋 **Navigation:**
    - **01 📊 Analyse** – Lade CSV/XLSX-Dateien hoch und analysiere Daten
    - **02 ⚙️ Einstellungen** – Konfiguriere die Anwendung
    - **03 👤 Stammdaten** – Verwalte Personen (Anlegen, Bearbeiten, Löschen)
    - **04 🧑‍💼 Mitarbeiter** – Verwalte Mitarbeiter (CRUD-Operationen)
    - **05 💶 Lohnverrechnung** – Führe Lohnabrechnungen durch
    - **06 ✨ Extras** – PDF-Download, Datenbank-Reset, Hilfe
    
    💡 **Tipp:** Beginne mit **Stammdaten**, um Personen anzulegen, dann **Mitarbeiter** für die Zuordnung.
    """
)

if st.session_state.df is not None:
    with st.expander(" Vorschau auf die Daten"):
        st.dataframe(st.session_state.df.head(50), use_container_width=True)
else:
    st.info("Noch keine Daten geladen.")
