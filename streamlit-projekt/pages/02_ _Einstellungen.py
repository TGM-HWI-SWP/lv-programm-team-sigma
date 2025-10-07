"""
Einstellungen – Systemkonfiguration und Benutzerverwaltung
"""
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import yaml
import pandas as pd

from modules import auth

# Authentication check
auth.init_session_state()
if not st.session_state.get('authenticated', False):
    st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")
    st.stop()

st.set_page_config(page_title="Einstellungen", page_icon="⚙️", layout="wide")
st.title("⚙️ Systemeinstellungen")

# Sidebar for user info
with st.sidebar:
    user_data = st.session_state.get('user_data', {})
    st.success(f"Angemeldet: **{user_data.get('username', '')}**")
    if user_data.get('is_admin', False):
        st.info("🔑 Administrator-Rechte")
    if st.button("Abmelden", type="secondary"):
        auth.logout()

# Database path
DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"
auth_manager = auth.AuthManager(str(DB_PATH))

# Check if user is admin
is_admin = st.session_state.get('user_data', {}).get('is_admin', False)

# Tab structure
if is_admin:
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Benutzerverwaltung", "⚙️ Systemkonfiguration", "🔑 Sicherheit", "📊 System-Info"])
else:
    tab1, tab2, tab3 = st.tabs(["⚙️ Systemkonfiguration", "🔑 Passwort ändern", "📊 System-Info"])

# Admin-only: User Management
if is_admin:
    with tab1:
        st.header("👥 Benutzerverwaltung")
        st.caption("🔑 Nur für Administratoren verfügbar")
        
        # Current users
        st.subheader("📋 Aktuelle Benutzer")
        users = auth_manager.get_all_users()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    'ID': user[0],
                    'Benutzername': user[1],
                    'Admin': '✅ Ja' if user[2] else '❌ Nein',
                    'Erstellt am': user[3][:10] if user[3] else 'Unbekannt'  # Show only date part
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Keine Benutzer gefunden.")
        
        # Add new user
        st.subheader("➕ Neuen Benutzer hinzufügen")
        
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Benutzername", help="Eindeutiger Benutzername")
                new_password = st.text_input("Passwort", type="password", help="Mindestens 6 Zeichen empfohlen")
            with col2:
                is_new_admin = st.checkbox("Administrator-Rechte vergeben")
                st.markdown("**Hinweis:** Administratoren können alle Funktionen nutzen und andere Benutzer verwalten.")
            
            submitted = st.form_submit_button("👤 Benutzer erstellen", type="primary")
            
            if submitted:
                if not new_username or not new_password:
                    st.error("❌ Benutzername und Passwort sind erforderlich!")
                elif len(new_password) < 6:
                    st.error("❌ Passwort sollte mindestens 6 Zeichen lang sein!")
                else:
                    if auth_manager.create_user(new_username, new_password, is_new_admin):
                        st.success(f"✅ Benutzer '{new_username}' wurde erfolgreich erstellt!")
                        st.rerun()
                    else:
                        st.error(f"❌ Benutzer '{new_username}' existiert bereits!")

# System Configuration
config_tab = tab2 if is_admin else tab1
with config_tab:
    st.header("⚙️ Systemkonfiguration")
    
    # Configuration file management
    st.subheader("📄 Konfigurationsdatei")
    config_path = Path(__file__).parent.parent / "config.yaml"
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            st.success("✅ Konfigurationsdatei gefunden")
            
            with st.expander("📋 Aktuelle Konfiguration anzeigen"):
                st.json(cfg)
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Konfiguration: {e}")
            cfg = {}
    else:
        st.info("ℹ️ Keine config.yaml gefunden. Eine Standardkonfiguration kann erstellt werden.")
        cfg = {}
    
    # System settings
    st.subheader("🔧 Systemeinstellungen")
    
    with st.form("system_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Anwendungseinstellungen**")
            app_name = st.text_input("Anwendungsname", value=cfg.get('app_name', 'Personalverwaltung'))
            company_name = st.text_input("Firmenname", value=cfg.get('company_name', 'Muster GmbH'))
            
        with col2:
            st.markdown("**Datenbank-Einstellungen**")
            backup_enabled = st.checkbox("Automatische Backups", value=cfg.get('backup_enabled', True))
            log_level = st.selectbox("Log-Level", 
                                   options=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                                   index=['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(cfg.get('log_level', 'INFO')))
        
        save_config = st.form_submit_button("💾 Konfiguration speichern", type="primary")
        
        if save_config:
            new_config = {
                'app_name': app_name,
                'company_name': company_name,
                'backup_enabled': backup_enabled,
                'log_level': log_level,
                'updated_at': str(pd.Timestamp.now())
            }
            
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
                st.success("✅ Konfiguration wurde gespeichert!")
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {e}")

# Security settings (Password change for regular users, additional settings for admins)
security_tab = tab3 if is_admin else tab2
with security_tab:
    if is_admin:
        st.header("🔑 Sicherheitseinstellungen")
        
        st.subheader("🔐 Passwort-Richtlinien")
        st.info("""
        **Aktuelle Sicherheitsmaßnahmen:**
        - ✅ Passwort-Hashing mit PBKDF2
        - ✅ Salz-basierte Verschlüsselung
        - ✅ Session-basierte Authentifizierung
        
        **Empfohlene Sicherheitspraktiken:**
        - Passwörter mindestens 8 Zeichen lang
        - Verwendung von Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen
        - Regelmäßige Passwort-Änderungen
        """)
        
        st.subheader("🚨 Sicherheitsereignisse")
        st.info("🔧 Feature in Entwicklung - Protokollierung von Anmeldeversuchen")
        
    else:
        st.header("🔑 Passwort ändern")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Aktuelles Passwort", type="password")
            new_password = st.text_input("Neues Passwort", type="password")
            confirm_password = st.text_input("Neues Passwort bestätigen", type="password")
            
            change_submitted = st.form_submit_button("🔄 Passwort ändern", type="primary")
            
            if change_submitted:
                if not all([current_password, new_password, confirm_password]):
                    st.error("❌ Alle Felder sind erforderlich!")
                elif new_password != confirm_password:
                    st.error("❌ Die neuen Passwörter stimmen nicht überein!")
                elif len(new_password) < 6:
                    st.error("❌ Das neue Passwort sollte mindestens 6 Zeichen lang sein!")
                else:
                    # Verify current password
                    username = st.session_state.get('user_data', {}).get('username', '')
                    success, _ = auth_manager.verify_login(username, current_password)
                    if success:
                        # Here you would implement password change functionality
                        st.info("🔧 Passwort-Änderung wird in einer zukünftigen Version implementiert")
                    else:
                        st.error("❌ Aktuelles Passwort ist falsch!")

# System Information
info_tab = tab4 if is_admin else tab3
with info_tab:
    st.header("📊 System-Informationen")
    
    # Database statistics
    st.subheader("🗄️ Datenbankstatistiken")
    
    import sqlite3
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get table sizes
        tables_info = []
        for table_name in ['PERSON', 'MITARBEITER', 'LOHNABRECHNUNG', 'Benutzer']:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            tables_info.append({'Tabelle': table_name, 'Anzahl Datensätze': count})
        
        conn.close()
        
        df_stats = pd.DataFrame(tables_info)
        st.dataframe(df_stats, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Datenbankstatistiken: {e}")
    
    # System info
    st.subheader("💻 Systemumgebung")
    
    import sys
    import platform
    
    system_info = {
        'Python Version': sys.version.split()[0],
        'Betriebssystem': platform.system(),
        'Plattform': platform.platform(),
        'Streamlit Version': st.__version__,
        'Datenbankdatei': str(DB_PATH),
        'Konfigurationsdatei': str(config_path) if config_path.exists() else 'Nicht vorhanden'
    }
    
    for key, value in system_info.items():
        st.text(f"{key}: {value}")
    
    # Version info
    st.subheader("📦 Anwendungsversion")
    st.info("**Version:** 2.0.0 - Moderne Personalverwaltung mit Authentifizierung")
    
    # Quick actions
    if is_admin:
        st.subheader("⚡ Schnellaktionen")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Cache leeren"):
                st.cache_data.clear()
                st.success("✅ Cache wurde geleert!")
        
        with col2:
            if st.button("📊 Statistiken aktualisieren"):
                st.rerun()
        
        with col3:
            st.info("🔧 Weitere Admin-Tools in Entwicklung")
