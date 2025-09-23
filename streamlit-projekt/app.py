import streamlit as st
from pathlib import Path
import pandas as pd

st.set_page_config(page_title="Team Sigma – Demo", page_icon=" ", layout="wide")

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
     - Lade oben in der Sidebar eine Datei hoch.
     - Wechsle zur Seite ** Analyse** für erste Auswertungen.
     - In ** Einstellungen** kannst du Parameter anpassen.
     """
)

if st.session_state.df is not None:
    with st.expander(" Vorschau auf die Daten"):
        st.dataframe(st.session_state.df.head(50), use_container_width=True)
else:
    st.info("Noch keine Daten geladen.")
