"""
Mitarbeiterverwaltung – Moderne Streamlit-Umsetzung
Vollständige CRUD-Funktionen für Mitarbeiter mit erweiterten Features
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date

from modules import dbms, employee, person, auth

# Authentication check
auth.init_session_state()
if not st.session_state.get('authenticated', False):
    st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")
    st.stop()

DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

st.set_page_config(page_title="Mitarbeiter", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 Mitarbeiterverwaltung")

# Sidebar for user info
with st.sidebar:
    user_data = st.session_state.get('user_data', {})
    st.success(f"Angemeldet: **{user_data.get('username', '')}**")
    if st.button("Abmelden", type="secondary"):
        auth.logout()

@st.cache_data(ttl=30)
def load_mitarbeiter():
    return employee.mitarbeiter.select_all(dbms_obj=db)

@st.cache_data(ttl=60)
def load_personen():
    return person.person.select_all(db_ms=db)

# Tab structure for better organization
tab1, tab2, tab3 = st.tabs(["📋 Übersicht", "➕ Mitarbeiter hinzufügen", "✏️ Mitarbeiter bearbeiten"])

with tab1:
    st.header("📋 Mitarbeiterübersicht")
    
    # Refresh button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Aktualisieren"):
            st.cache_data.clear()
    
    mitarbeiter = load_mitarbeiter()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧑‍💼 Gesamt Mitarbeiter", len(mitarbeiter))
    
    with col2:
        # Calculate average salary
        if mitarbeiter:
            salaries = []
            for m in mitarbeiter:
                try:
                    salary = float(str(m.salary).replace(',', '.'))
                    salaries.append(salary)
                except:
                    pass
            avg_salary = sum(salaries) / len(salaries) if salaries else 0
            st.metric("⌀ Durchschnittsgehalt", f"{avg_salary:,.2f} €")
        else:
            st.metric("⌀ Durchschnittsgehalt", "0 €")
    
    with col3:
        # Count employees hired this year
        current_year = datetime.now().year
        this_year_hires = 0
        for m in mitarbeiter:
            try:
                entry_year = datetime.strptime(m.entrydate, "%d.%m.%Y").year
                if entry_year == current_year:
                    this_year_hires += 1
            except:
                pass
        st.metric("📅 Neueinstellungen (Jahr)", this_year_hires)
    
    with col4:
        # Active employees (no exit date or future exit date)
        active_employees = len(mitarbeiter)  # For now, assume all are active
        st.metric("✅ Aktive Mitarbeiter", active_employees)
    
    # Search and filter
    st.subheader("🔍 Suchen & Filtern")
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Suche nach Name", placeholder="Vor- oder Nachname eingeben...")
    with col2:
        salary_filter = st.selectbox("Gehaltsbereich", 
                                   ["Alle", "< 2.000 €", "2.000 - 3.000 €", "3.000 - 4.000 €", "> 4.000 €"])
    
    # Display table
    if mitarbeiter:
        data = []
        for m in mitarbeiter:
            try:
                salary_float = float(str(m.salary).replace(',', '.'))
            except:
                salary_float = 0
            
            data.append([
                m.empolyee_ID,
                m.obj_id,
                m.name,
                m.surname,
                m.entrydate,
                f"{salary_float:,.2f} €",
                m.eval_age()
            ])
        
        columns = ["Mitarbeiter-ID", "Personen-ID", "Vorname", "Nachname", "Eintrittsdatum", "Gehalt", "Alter"]
        df = pd.DataFrame(data, columns=columns)
        
        # Apply search filter
        if search_term:
            mask = (df['Vorname'].str.contains(search_term, case=False, na=False) | 
                   df['Nachname'].str.contains(search_term, case=False, na=False))
            df = df[mask]
        
        # Apply salary filter
        if salary_filter != "Alle":
            # Extract numeric salary for filtering
            df['Salary_Numeric'] = df['Gehalt'].str.replace(' €', '').str.replace(',', '').astype(float)
            
            if salary_filter == "< 2.000 €":
                df = df[df['Salary_Numeric'] < 2000]
            elif salary_filter == "2.000 - 3.000 €":
                df = df[(df['Salary_Numeric'] >= 2000) & (df['Salary_Numeric'] <= 3000)]
            elif salary_filter == "3.000 - 4.000 €":
                df = df[(df['Salary_Numeric'] >= 3000) & (df['Salary_Numeric'] <= 4000)]
            elif salary_filter == "> 4.000 €":
                df = df[df['Salary_Numeric'] > 4000]
            
            df = df.drop('Salary_Numeric', axis=1)
        
        # Enhanced table display
        if not df.empty:
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "Mitarbeiter-ID": st.column_config.NumberColumn("MA-ID", width="small"),
                    "Personen-ID": st.column_config.NumberColumn("Pers-ID", width="small"),
                    "Vorname": st.column_config.TextColumn("Vorname", width="medium"),
                    "Nachname": st.column_config.TextColumn("Nachname", width="medium"),
                    "Eintrittsdatum": st.column_config.TextColumn("Eintritt", width="medium"),
                    "Gehalt": st.column_config.TextColumn("Gehalt", width="medium"),
                    "Alter": st.column_config.NumberColumn("Alter", width="small"),
                }
            )
        else:
            st.info("Keine Mitarbeiter gefunden, die den Suchkriterien entsprechen.")
    else:
        st.info("Noch keine Mitarbeiter in der Datenbank vorhanden.")

with tab2:
    st.header("➕ Neuen Mitarbeiter hinzufügen")
    
    personen = load_personen()
    
    # Check which persons are not yet employees
    mitarbeiter = load_mitarbeiter()
    existing_employee_person_ids = [m.obj_id for m in mitarbeiter]
    available_persons = [p for p in personen if p.obj_id not in existing_employee_person_ids]
    
    if not available_persons:
        st.warning("⚠️ Alle vorhandenen Personen sind bereits als Mitarbeiter registriert.")
        st.info("💡 Erstellen Sie zuerst neue Personen in der Stammdatenverwaltung.")
    else:
        with st.form("create_ma_form", clear_on_submit=True):
            st.subheader("👤 Personenzuordnung")
            person_options = [f"{p.name} {p.surname} (ID: {p.obj_id})" for p in available_persons]
            selected_person_str = st.selectbox("Person auswählen *", person_options, help="Pflichtfeld")
            
            if selected_person_str:
                # Extract person ID and object
                person_id = int(selected_person_str.split("ID: ")[1].split(")")[0])
                selected_person = next((p for p in available_persons if p.obj_id == person_id), None)
                
                if selected_person:
                    # Display person info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**Name:** {selected_person.name} {selected_person.surname}")
                        st.info(f"**Geburtsdatum:** {selected_person.birthdate}")
                    with col2:
                        st.info(f"**Alter:** {selected_person.eval_age()} Jahre")
                        address = f"{selected_person.street or ''} {selected_person.housenr or ''}, {selected_person.zip or ''} {selected_person.place or ''}".strip()
                        st.info(f"**Adresse:** {address if address.replace(',', '').strip() else 'Nicht angegeben'}")
            
            st.subheader("💼 Dienstvertragsdaten")
            col1, col2 = st.columns(2)
            
            with col1:
                eintritt = st.date_input("Eintrittsdatum *", 
                                       value=date.today(),
                                       help="Pflichtfeld")
                
            with col2:
                gehalt = st.number_input("Bruttogehalt (€) *", 
                                       min_value=0.0, 
                                       value=2500.0, 
                                       step=50.0,
                                       help="Monatliches Bruttogehalt")
            
            st.markdown("**Hinweis:** Felder mit * sind Pflichtfelder")
            
            submitted = st.form_submit_button("✅ Mitarbeiter anlegen", type="primary")
            
            if submitted and selected_person_str:
                try:
                    eintritt_str = eintritt.strftime("%d.%m.%Y")
                    
                    new_ma = employee.mitarbeiter(
                        vorname=selected_person.name,
                        nachname=selected_person.surname,
                        geburtsdatum=selected_person.birthdate,
                        eintrittsdatum=eintritt_str,
                        gehalt=gehalt,
                        persid=person_id,
                        ma_id=None,  # Auto-generate
                        straße=selected_person.street,
                        hausnr=selected_person.housenr,
                        stiege_top_etc=selected_person.floor,
                        plz=selected_person.zip,
                        ort=selected_person.place
                    )
                    new_ma.insert(db)
                    st.success(f"✅ Mitarbeiter {selected_person.name} {selected_person.surname} wurde erfolgreich angelegt!")
                    st.cache_data.clear()
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Anlegen: {e}")

with tab3:
    st.header("✏️ Mitarbeiter bearbeiten oder löschen")
    
    mitarbeiter = load_mitarbeiter()
    
    if mitarbeiter:
        # Employee selector
        employee_options = [f"{m.name} {m.surname} (MA-ID: {m.empolyee_ID})" for m in mitarbeiter]
        selected_employee_str = st.selectbox("Mitarbeiter auswählen", employee_options)
        
        if selected_employee_str:
            # Extract employee ID
            ma_id = int(selected_employee_str.split("MA-ID: ")[1].split(")")[0])
            selected_employee = next((m for m in mitarbeiter if m.empolyee_ID == ma_id), None)
            
            if selected_employee:
                col1, col2 = st.columns([3, 1])
                
                with col2:
                    st.subheader("🗑️ Gefährliche Aktionen")
                    
                    # Check for payroll records
                    import sqlite3
                    conn = sqlite3.connect(str(DB_PATH))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM LOHNABRECHNUNG WHERE PERS_ID = ?", (selected_employee.obj_id,))
                    has_payroll = cursor.fetchone()[0] > 0
                    conn.close()
                    
                    if has_payroll:
                        st.warning("⚠️ Mitarbeiter hat Lohnabrechnungen!")
                    
                    if st.button("🗑️ Mitarbeiter löschen", type="secondary"):
                        if has_payroll:
                            st.error("❌ Mitarbeiter kann nicht gelöscht werden, da Lohnabrechnungen vorhanden sind.")
                        else:
                            try:
                                selected_employee.delete(db)
                                st.success("✅ Mitarbeiter wurde gelöscht.")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Fehler beim Löschen: {e}")
                
                with col1:
                    st.subheader("📝 Daten bearbeiten")
                    
                    # Display person info (read-only)
                    with st.expander("👤 Personendaten (nur lesbar)"):
                        col1_info, col2_info = st.columns(2)
                        with col1_info:
                            st.text(f"Name: {selected_employee.name} {selected_employee.surname}")
                            st.text(f"Geburtsdatum: {selected_employee.birthdate}")
                            st.text(f"Alter: {selected_employee.eval_age()} Jahre")
                        with col2_info:
                            address = f"{selected_employee.street or ''} {selected_employee.housenr or ''}, {selected_employee.zip or ''} {selected_employee.place or ''}".strip()
                            st.text(f"Adresse: {address if address.replace(',', '').strip() else 'Nicht angegeben'}")
                    
                    with st.form("edit_ma_form"):
                        st.markdown("**Dienstvertragsdaten bearbeiten**")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Convert current entry date string to date object
                            try:
                                current_entry_date = datetime.strptime(selected_employee.entrydate, "%d.%m.%Y").date()
                            except:
                                current_entry_date = date.today()
                            
                            edit_eintritt = st.date_input("Eintrittsdatum", value=current_entry_date)
                            
                        with col2:
                            # Convert salary to float
                            try:
                                current_salary = float(str(selected_employee.salary).replace(',', '.'))
                            except:
                                current_salary = 0.0
                            
                            edit_gehalt = st.number_input("Bruttogehalt (€)", 
                                                        value=current_salary, 
                                                        min_value=0.0, 
                                                        step=50.0)
                        
                        # Future: Add fields for exit date, department, etc.
                        st.info("💡 Zusätzliche Felder wie Austrittsdatum, Abteilung etc. können in zukünftigen Versionen hinzugefügt werden.")
                        
                        update_submitted = st.form_submit_button("💾 Änderungen speichern", type="primary")
                        
                        if update_submitted:
                            try:
                                eintritt_str = edit_eintritt.strftime("%d.%m.%Y")
                                
                                values = [
                                    selected_employee.empolyee_ID,
                                    selected_employee.obj_id,
                                    eintritt_str,
                                    edit_gehalt
                                ]
                                
                                selected_employee.update(db, values)
                                st.success("✅ Mitarbeiter wurde erfolgreich aktualisiert!")
                                st.cache_data.clear()
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Fehler beim Aktualisieren: {e}")
    else:
        st.info("Noch keine Mitarbeiter vorhanden. Bitte erstellen Sie zuerst einen Mitarbeiter über den Tab 'Mitarbeiter hinzufügen'.")
