import streamlit as st
from pathlib import Path
import pandas as pd

from modules import dbms, person, employee, auth

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
    cursor.execute("SELECT COUNT(*) FROM LOHNABRECHNUNG WHERE MONAT LIKE ?", (f"{current_month}%",))
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
    st.markdown("**Letzte Personalaktionen:**")
    # Hier könnten wir ein Log implementieren
    st.info("🔧 Feature in Entwicklung - Aktivitätsprotokoll wird implementiert")

with col2:
    st.markdown("**Systemstatus:**")
    st.success("✅ Datenbank verbunden")
    st.success("✅ Authentifizierung aktiv") 
    st.success("✅ Alle Module geladen")
