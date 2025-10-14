import streamlit as st
import pandas as pd
from pathlib import Path

from modules import dbms, person, employee, auth

# Dynamically import PDF tools
import importlib.util
import sys
pdf_path = Path(__file__).parent / "pages" / "07_pdf-ausgabe.py"
spec = importlib.util.spec_from_file_location("pdf_tools", str(pdf_path))
pdf_tools = importlib.util.module_from_spec(spec)
sys.modules["pdf_tools"] = pdf_tools
spec.loader.exec_module(pdf_tools)

# App config
st.set_page_config(page_title="Personalverwaltung", page_icon="💼", layout="wide")

# Database setup
DB_PATH = Path(__file__).parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))
person.person.initialize_db_table(db)
employee.mitarbeiter.initialize_db_table(db)

# Auth setup
auth_manager = auth.AuthManager(str(DB_PATH))
auth.init_session_state()
if not st.session_state.get('authenticated', False):
    auth.show_login_form(auth_manager)
    st.stop()

st.title("💼 Personalverwaltungssystem")

# Sidebar: file upload
with st.sidebar:
    st.header("Daten laden")
    uploaded = st.file_uploader("CSV/XLSX hochladen", type=["csv", "xlsx"])
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.session_state.df = df
            st.success(f"{uploaded.name} geladen – {df.shape[0]} Zeilen × {df.shape[1]} Spalten")
        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")

# Dashboard stats
personen = person.person.select_all(db_ms=db)
mitarbeiter = employee.mitarbeiter.select_all(dbms_obj=db)

st.metric("👥 Personen", len(personen))
st.metric("🧑‍💼 Mitarbeiter", len(mitarbeiter))

# PDF-Ausgabe buttons
st.subheader("PDF-Ausgabe")
col1, col2 = st.columns(2)
with col1:
    if st.button("Monatsbericht als PDF herunterladen"):
        pdf_bytes = pdf_tools.generate_monthly_summary_pdf([m[1] for m in mitarbeiter], 5000)
        st.download_button("Monatsbericht als PDF", pdf_bytes, file_name="Monatsbericht.pdf")
with col2:
    if st.button("Lohn-/Gehaltszettel als PDF herunterladen"):
        if mitarbeiter:
            pdf_bytes = pdf_tools.generate_payroll_pdf(mitarbeiter[0][1], 2500)
            st.download_button("Lohn-/Gehaltszettel als PDF", pdf_bytes, file_name="Gehaltszettel.pdf")

# Data preview
if st.session_state.get('df') is not None:
    st.subheader("Datenvorschau")
    st.dataframe(st.session_state.df.head(50), use_container_width=True)
