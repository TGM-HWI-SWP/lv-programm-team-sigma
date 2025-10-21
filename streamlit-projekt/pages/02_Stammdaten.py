"""
Stammdatenverwaltung – Moderne Streamlit-Umsetzung
Vollständige CRUD-Funktionen für Personen mit historischen Daten
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

from modules import dbms, person, auth

# Authentication check
auth.init_session_state()
if not st.session_state.get('authenticated', False):
    st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")
    st.stop()

# --- DB initialisieren ---
DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

st.set_page_config(page_title="Stammdaten", page_icon="👤", layout="wide")
st.title("👤 Stammdatenverwaltung")

# Sidebar for user info
with st.sidebar:
    user_data = st.session_state.get('user_data', {})
    st.success(f"Angemeldet: **{user_data.get('username', '')}**")
    if st.button("Abmelden", type="secondary"):
        auth.logout()

# --- Daten laden ---
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_personen():
    return person.person.select_all(db_ms=db)

# Tab structure for better organization
tab1, tab2, tab3 = st.tabs(["📋 Übersicht", "➕ Person hinzufügen", "✏️ Person bearbeiten"])

with tab1:
    st.header("📋 Personenübersicht")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Aktualisieren"):
            st.cache_data.clear()
    
    personen = load_personen()
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👥 Gesamt Personen", len(personen))
    with col2:
        # Count employed persons (those who are also employees)
        import sqlite3
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT PERS_ID) FROM MITARBEITER")
        employed_count = cursor.fetchone()[0]
        conn.close()
        st.metric("🧑‍💼 Angestellte", employed_count)
    with col3:
        non_employed = len(personen) - employed_count
        st.metric("👤 Nicht angestellt", non_employed)
    
    # Search and filter
    st.subheader("🔍 Suchen & Filtern")
    search_term = st.text_input("Suche nach Name", placeholder="Vorname oder Nachname eingeben...")
    # Neue Filter-Widgets
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        straße_filter = st.text_input("Straße filtern", value="")
    with col2:
        hausnr_filter = st.text_input("Hausnummer filtern", value="")
    with col3:
        plz_filter = st.text_input("PLZ filtern", value="")
    with col4:
        ort_filter = st.text_input("Ort filtern", value="")

    # Display table
    if personen:
        data = [p.value() for p in personen]
        columns = [row[2] for row in person.person.table_row_names]
        df = pd.DataFrame(data, columns=columns)
        # Apply search filter
        if search_term:
            mask = (df['Vorname'].str.contains(search_term, case=False, na=False) | 
                   df['Nachname'].str.contains(search_term, case=False, na=False))
            df = df[mask]
        # Apply advanced filters
        if straße_filter:
            df = df[df['Straße'].str.contains(straße_filter, case=False, na=False)]
        if hausnr_filter:
            df = df[df['Hausnummer'].astype(str).str.contains(hausnr_filter, case=False, na=False)]
        if plz_filter:
            df = df[df['PLZ'].astype(str).str.contains(plz_filter, case=False, na=False)]
        if ort_filter:
            df = df[df['Ort'].str.contains(ort_filter, case=False, na=False)]
        # Enhanced table display
        if not df.empty:
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Vorname": st.column_config.TextColumn("Vorname", width="medium"),
                    "Nachname": st.column_config.TextColumn("Nachname", width="medium"),
                    "Geburtsdatum": st.column_config.TextColumn("Geburtsdatum", width="medium"),
                    "PLZ": st.column_config.NumberColumn("PLZ", width="small"),
                }
            )
        else:
            st.info("Keine Personen gefunden, die den Suchkriterien entsprechen.")
    else:
        st.info("Noch keine Personen in der Datenbank vorhanden.")

with tab2:
    st.header("➕ Neue Person hinzufügen")
    
    with st.form("create_person_form", clear_on_submit=True):
        st.subheader("📝 Persönliche Daten")
        col1, col2 = st.columns(2)
        
        with col1:
            vorname = st.text_input("Vorname *", help="Pflichtfeld")
            nachname = st.text_input("Nachname *", help="Pflichtfeld") 
            geburtsdatum = st.date_input("Geburtsdatum *", 
                                       min_value=datetime(1920, 1, 1),
                                       max_value=datetime.now(),
                                       help="Format: TT.MM.JJJJ")
        
        with col2:
            # Convert date to German format string
            geb_str = geburtsdatum.strftime("%d.%m.%Y") if geburtsdatum else ""
            st.write(f"**Geburtsdatum als Text:** {geb_str}")
        
        st.subheader("🏠 Adressdaten")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            straße = st.text_input("Straße")
            hausnr = st.text_input("Hausnummer")
            
        with col2:
            stiege = st.text_input("Stiege/Top/Wohnung")
            plz = st.number_input("Postleitzahl", min_value=1000, max_value=99999, step=1, value=None)
            
        with col3:
            ort = st.text_input("Ort")
        
        st.markdown("**Hinweis:** Felder mit * sind Pflichtfelder")
        
        submitted = st.form_submit_button("✅ Person anlegen", type="primary")
        
        if submitted:
            # Validation
            errors = []
            if not vorname.strip():
                errors.append("Vorname ist erforderlich")
            if not nachname.strip():
                errors.append("Nachname ist erforderlich")
            if not geburtsdatum:
                errors.append("Geburtsdatum ist erforderlich")
                
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Convert hausnr to int if provided and is digit
                    hausnr_int = None
                    if hausnr and hausnr.isdigit():
                        hausnr_int = int(hausnr)
                    
                    new_p = person.person(
                        id=None,  # Auto-generate ID
                        nachname=nachname.strip(),
                        vorname=vorname.strip(),
                        geburtsdatum=geb_str,
                        straße=straße.strip() if straße else None,
                        hausnr=hausnr_int,
                        stiege_top_etc=stiege.strip() if stiege else None,
                        plz=int(plz) if plz else None,
                        ort=ort.strip() if ort else None
                    )
                    new_p.insert(db)
                    st.success(f"✅ Person {vorname} {nachname} wurde erfolgreich angelegt!")
                    st.cache_data.clear()  # Clear cache to refresh data
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Anlegen: {e}")

with tab3:
    st.header("✏️ Person bearbeiten oder löschen")
    
    personen = load_personen()
    
    if personen:
        # Person selector
        person_options = [f"{p.name} {p.surname} (ID: {p.obj_id})" for p in personen]
        selected_person_str = st.selectbox("Person auswählen", person_options)
        
        if selected_person_str:
            # Extract ID from selection
            selected_id = int(selected_person_str.split("ID: ")[1].split(")")[0])
            selected_person = next((p for p in personen if p.obj_id == selected_id), None)
            
            if selected_person:
                # Check if person is an employee
                import sqlite3
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM MITARBEITER WHERE PERS_ID = ?", (selected_id,))
                is_employee = cursor.fetchone()[0] > 0
                conn.close()
                
                if is_employee:
                    st.warning("⚠️ Diese Person ist als Mitarbeiter registriert. Löschung kann Probleme verursachen.")
                
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    st.subheader("🗑️ Gefährliche Aktionen")
                    if st.button("🗑️ Person löschen", type="secondary"):
                        if is_employee:
                            st.error("❌ Diese Person kann nicht gelöscht werden, da sie als Mitarbeiter registriert ist. Entfernen Sie zuerst den Mitarbeiter-Eintrag.")
                        else:
                            try:
                                selected_person.delete(db)
                                st.success("✅ Person wurde gelöscht.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Fehler beim Löschen: {e}")
                
                with col1:
                    st.subheader("📝 Daten bearbeiten")
                    
                    with st.form("edit_person_form"):
                        st.markdown("**Persönliche Daten**")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_vorname = st.text_input("Vorname", value=selected_person.name)
                            edit_nachname = st.text_input("Nachname", value=selected_person.surname)
                            
                        with col2:
                            # Convert current birthdate string to date object
                            try:
                                current_date = datetime.strptime(selected_person.birthdate, "%d.%m.%Y").date()
                            except:
                                current_date = datetime.now().date()
                            
                            edit_geburtsdatum = st.date_input("Geburtsdatum", 
                                                            value=current_date,
                                                            min_value=datetime(1920, 1, 1),
                                                            max_value=datetime.now())
                        
                        st.markdown("**Adressdaten**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            edit_straße = st.text_input("Straße", value=selected_person.street or "")
                            edit_hausnr = st.text_input("Hausnummer", value=str(selected_person.housenr) if selected_person.housenr else "")
                            
                        with col2:
                            edit_stiege = st.text_input("Stiege/Top/Wohnung", value=selected_person.floor or "")
                            edit_plz = st.number_input("PLZ", value=selected_person.zip if selected_person.zip else None, min_value=1000, max_value=99999)
                            
                        with col3:
                            edit_ort = st.text_input("Ort", value=selected_person.place or "")
                        
                        update_submitted = st.form_submit_button("💾 Änderungen speichern", type="primary")
                        
                        if update_submitted:
                            # Validation
                            errors = []
                            if not edit_vorname.strip():
                                errors.append("Vorname ist erforderlich")
                            if not edit_nachname.strip():
                                errors.append("Nachname ist erforderlich")
                                
                            if errors:
                                for error in errors:
                                    st.error(f"❌ {error}")
                            else:
                                try:
                                    # Convert hausnr to int if provided
                                    edit_hausnr_int = None
                                    if edit_hausnr and edit_hausnr.isdigit():
                                        edit_hausnr_int = int(edit_hausnr)
                                    
                                    geb_str = edit_geburtsdatum.strftime("%d.%m.%Y")
                                    
                                    values = [
                                        selected_person.obj_id,
                                        edit_nachname.strip(),
                                        edit_vorname.strip(),
                                        geb_str,
                                        edit_straße.strip() if edit_straße else None,
                                        edit_hausnr_int,
                                        edit_stiege.strip() if edit_stiege else None,
                                        int(edit_plz) if edit_plz else None,
                                        edit_ort.strip() if edit_ort else None
                                    ]
                                    
                                    selected_person.update(db, values)
                                    st.success("✅ Person wurde erfolgreich aktualisiert!")
                                    st.cache_data.clear()
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Fehler beim Aktualisieren: {e}")
    else:
        st.info("Noch keine Personen vorhanden. Bitte erstellen Sie zuerst eine Person über den Tab 'Person hinzufügen'.")
