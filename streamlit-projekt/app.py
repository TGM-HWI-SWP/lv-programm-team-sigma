import sys
import sqlite3
from pathlib import Path
import datetime

import streamlit as st
from fpdf import FPDF

# Hilfsfunktion für sichere Float-Konvertierung
def str_to_float(value, default=0.0):
    """Konvertiert String (auch mit Komma) zu Float"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(',', '.'))
    except (ValueError, AttributeError):
        return default

# Optional project modules
try:
    from modules import dbms, person, employee, auth
except Exception:
    dbms = None
    person = None
    employee = None
    auth = None

st.set_page_config(
    page_title="Personalverwaltung - Team Sigma",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Datenbank initialisieren ---
DB_PATH = Path(__file__).parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

# Tabellen erstellen, falls nicht vorhanden
person.person.initialize_db_table(db)
employee.mitarbeiter.initialize_db_table(db)

# --- Authentication Setup ---
auth_manager = auth.AuthManager(str(DB_PATH))
auth.init_session_state()

# Check if user is authenticated
if not st.session_state.get('authenticated', False):
    auth.show_login_form(auth_manager)
    st.stop()

# --- User Interface nach Login ---
st.title("💼 Personalverwaltungssystem - Team Sigma")

# Sidebar with user info and logout
with st.sidebar:
    user_data = st.session_state.get('user_data', {})
    st.success(f"Angemeldet als: **{user_data.get('username', '')}**")
    if user_data.get('is_admin', False):
        st.info("🔑 Administrator-Rechte")
    
    if st.button("Abmelden", type="secondary"):
        auth.logout()
    
    st.divider()
    
    st.header("📊 Daten laden")
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
    st.caption("Version 2.0.0 • Personalverwaltung")

# --- Dashboard Übersicht ---
col1, col2, col3, col4 = st.columns(4)

# Statistiken laden
personen = person.person.select_all(db_ms=db)
mitarbeiter = employee.mitarbeiter.select_all(dbms_obj=db)

with col1:
    st.metric("👥 Personen", len(personen))

with col2:
    st.metric("🧑‍💼 Mitarbeiter", len(mitarbeiter))

with col3:
    # Anzahl Lohnabrechnungen diesen Monat
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    current_month = pd.Timestamp.now().strftime("%Y-%m")
    cursor.execute("SELECT COUNT(*) FROM lohnverrechnung_dn WHERE lv_dn_monat LIKE ?", (f"{current_month}%",))
    payroll_count = cursor.fetchone()[0]
    conn.close()
    st.metric("💰 Abrechnungen (aktueller Monat)", payroll_count)

with col4:
    st.metric("📁 Datensätze geladen", len(st.session_state.get('df', [])) if st.session_state.get('df') is not None else 0)

st.subheader("🚀 Navigation")
st.markdown(
    """
    **📋 Verfügbare Funktionen:**
    
    **� Stammdaten** – Personen verwalten (Anlegen, Bearbeiten, Löschen)
    - Vollständige Adressdaten
    - Historische Datenhaltung
    
    **🧑‍💼 Mitarbeiter** – Mitarbeiterverwaltung mit Dienstverträgen
    - Zuordnung zu Personen
    - Gehaltsinformationen
    - Einstellungs-/Austrittsdaten
    
    **� Lohnverrechnung** – Moderne Gehaltsabrechnung
    - Automatische Brutto-Netto-Berechnung
    - Überstunden- und Zulagenabrechnung
    - Historische Abrechnungsverläufe
    
    **� Analyse** – Datenanalyse und Berichte
    - CSV/XLSX Import
    - Statistische Auswertungen
    
    **⚙️ Einstellungen** – Systemkonfiguration
    - Benutzerverwaltung (für Administratoren)
    - Systemparameter
    
    **✨ Extras** – Zusätzliche Tools
    - PDF-Generierung (Lohnzettel, Stammdatenblätter)
    - Datenbank-Management
    - System-Informationen
    """
)

# --- Session State Defaults ---
if "dataset" not in st.session_state:
    st.session_state.dataset = None
if "df" not in st.session_state:
    st.session_state.df = None

# Datenvorschau wenn vorhanden
if st.session_state.df is not None:
    with st.expander("📊 Vorschau auf die geladenen Daten"):
        st.dataframe(st.session_state.df.head(50), use_container_width=True)

# Letzte Aktivitäten
st.subheader("📈 Systemaktivität")
col1, col2 = st.columns(2)

with col1:
    st.metric("👥 Personen", len(persons))
with col2:
    st.metric("🧑‍💼 Mitarbeiter", len(employees))
with col3:
    st.metric("💰 Abrechnungen (aktueller Monat)", count_payroll_current_month())
with col4:
    st.metric("📄 PDF-Tools", 2)

st.subheader("📄 PDF-Ausgabe")

emp_display = [f"{e['PERS_SURNAME']}, {e['PERS_FIRSTNAME']} (EMPL_ID {e['EMPL_ID']})" for e in employees]
selected_idx = st.selectbox("Mitarbeiter auswählen", list(range(len(emp_display))), format_func=lambda i: emp_display[i] if emp_display else "-") if employees else None

colA, colB = st.columns(2)

with colA:
    st.markdown("**Stammdatenblatt**")
    if employees and selected_idx is not None:
        if st.button("📄 Stammdatenblatt als PDF"):
            person_like = employees[selected_idx]
            pdf_bytes = pdf_stammdatenblatt(person_like)
            st.download_button(
                "Download Stammdatenblatt.pdf",
                data=pdf_bytes,
                file_name=f"Stammdatenblatt_{employees[selected_idx]['PERS_SURNAME']}_{employees[selected_idx]['PERS_FIRSTNAME']}.pdf",
                mime="application/pdf",
            )
    else:
        st.info("Keine Mitarbeiter in der Datenbank.")

with colB:
    st.markdown("**Lohn- und Gehaltszettel**")
    if employees and selected_idx is not None:
        empl = employees[selected_idx]
        payroll_data, _raw = find_latest_payroll_for_employee(int(empl["EMPL_ID"]))
        if payroll_data is None:
            st.warning("Keine Abrechnungsdaten gefunden. Es werden angenäherte Werte aus dem Mitarbeiterstamm verwendet.")
            payroll_data = {}
        if st.button("📄 Lohnzettel als PDF"):
            pdf_bytes = pdf_lohnzettel(empl, payroll_data)
            month_tag = (payroll_data.get("month") or datetime.date.today().strftime("%Y-%m")).replace("/", "-")
            st.download_button(
                "Download Lohnzettel.pdf",
                data=pdf_bytes,
                file_name=f"Lohnzettel_{empl['PERS_SURNAME']}_{empl['PERS_FIRSTNAME']}_{month_tag}.pdf",
                mime="application/pdf",
            )
    else:
        st.info("Keine Mitarbeiter in der Datenbank.")

st.divider()
st.caption(f"Datenbankdatei: {DB_PATH}")
st.caption("💡 Tipp: Verwende die Seitenleiste (links), um zu anderen Funktionen zu navigieren")