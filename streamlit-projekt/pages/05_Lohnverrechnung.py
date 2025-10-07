"""
Lohnverrechnung – Moderne Streamlit-Umsetzung
Vollständige Gehaltsabrechnung mit historischen Daten
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt
from decimal import Decimal

from modules import dbms, employee, Abrechnung, payroll, auth

# Authentication check
auth.init_session_state()
if not st.session_state.get('authenticated', False):
    st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")
    st.stop()

DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))
payroll_manager = payroll.PayrollManager(str(DB_PATH))

st.set_page_config(page_title="Lohnverrechnung", page_icon="💰", layout="wide")
st.title("💰 Lohnverrechnung & Gehaltsabrechnung")

# Sidebar for user info
with st.sidebar:
    user_data = st.session_state.get('user_data', {})
    st.success(f"Angemeldet: **{user_data.get('username', '')}**")
    if st.button("Abmelden", type="secondary"):
        auth.logout()

# Tab structure
tab1, tab2, tab3, tab4 = st.tabs(["📊 Übersicht", "💸 Neue Abrechnung", "📈 Abrechnung anzeigen", "📋 Historie"])

with tab1:
    st.header("📊 Gehaltsabrechnungs-Übersicht")
    
    # Current month statistics
    current_month = dt.datetime.now().strftime("%Y-%m")
    monthly_payrolls = payroll_manager.get_monthly_payroll_summary(current_month)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🧑‍💼 Mitarbeiter", len(payroll_manager.get_all_employees_for_payroll()))
    with col2:
        st.metric("💰 Abrechnungen (aktueller Monat)", len(monthly_payrolls))
    with col3:
        total_brutto = sum([p.get('BRUTTO', 0) for p in monthly_payrolls])
        st.metric("💵 Gesamt Brutto (aktueller Monat)", f"{total_brutto:,.2f} €")
    
    # Recent payrolls table
    if monthly_payrolls:
        st.subheader(f"📋 Abrechnungen für {current_month}")
        df = pd.DataFrame(monthly_payrolls)
        display_columns = ['FIRSTNAME', 'SURNAME', 'BRUTTO', 'MONAT', 'WOCHENSTUNDEN', 'ÜBERSTUNDEN50']
        st.dataframe(df[display_columns], use_container_width=True)
    else:
        st.info(f"Noch keine Abrechnungen für {current_month} vorhanden.")

with tab2:
    st.header("💸 Neue Gehaltsabrechnung erstellen")
    
    employees = payroll_manager.get_all_employees_for_payroll()
    
    if not employees:
        st.warning("Keine Mitarbeiter vorhanden. Bitte erstellen Sie zuerst Mitarbeiter in der Mitarbeiterverwaltung.")
    else:
        employee_options = [f"{emp['FULL_NAME']} (ID: {emp['PERS_ID']})" for emp in employees]
        
        with st.form("new_payroll_form"):
            st.subheader("👤 Mitarbeiter & Zeitraum")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_employee = st.selectbox("Mitarbeiter auswählen", employee_options)
                if selected_employee:
                    emp_id = int(selected_employee.split("ID: ")[1].split(")")[0])
                    selected_emp = next((emp for emp in employees if emp['PERS_ID'] == emp_id), None)
                    if selected_emp:
                        st.info(f"Grundgehalt: {selected_emp['SALARY']:,.2f} €")
            
            with col2:
                abrechnungsmonat = st.date_input("Abrechnungsmonat", dt.datetime.now())
                monat_str = abrechnungsmonat.strftime("%Y-%m")
            
            st.subheader("💰 Gehaltskomponenten")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                brutto = st.number_input("Grundgehalt (Brutto)", value=selected_emp['SALARY'] if 'selected_emp' in locals() else 2500.0, min_value=0.0, step=50.0)
                wochenstunden = st.number_input("Wochenstunden", value=38.5, min_value=0.0, step=0.5)
                stundensatz = st.number_input("Stundensatz", value=38.5, min_value=0.0, step=0.5)
            
            with col2:
                mehrstunden0 = st.number_input("Mehrstunden (0%)", value=0.0, min_value=0.0, step=0.5)
                mehrstunden25 = st.number_input("Mehrstunden (25%)", value=0.0, min_value=0.0, step=0.5)
                mehrstunden50 = st.number_input("Mehrstunden (50%)", value=0.0, min_value=0.0, step=0.5)
                
            with col3:
                überstunden50 = st.number_input("Überstunden (50%)", value=0.0, min_value=0.0, step=0.5)
                überstunden100 = st.number_input("Überstunden (100%)", value=0.0, min_value=0.0, step=0.5)
            
            st.subheader("🎁 Zusätze & Abzüge")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sonderzahlungen = st.number_input("Sonderzahlungen", value=0.0, min_value=0.0, step=50.0)
                sachbezug = st.number_input("Sachbezug", value=0.0, min_value=0.0, step=10.0)
                
            with col2:
                diäten = st.number_input("Diäten", value=0.0, min_value=0.0, step=10.0)
                reisekosten = st.number_input("Reisekosten", value=0.0, min_value=0.0, step=10.0)
                
            with col3:
                freibetragsbescheid = st.number_input("Freibetragsbescheid", value=0.0, min_value=0.0, step=10.0)
                pendlerpauschale = st.number_input("Pendlerpauschale", value=0.0, min_value=0.0, step=10.0)
            
            st.subheader("👨‍👩‍👧‍👦 Familie & Weitere Angaben")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                anzahl_kinder = st.number_input("Anzahl Kinder (AVAB)", value=0, min_value=0, step=1)
                anspruch_fabo = st.checkbox("Anspruch auf Familienbonus+")
                
            with col2:
                gewerkschaftsmitglied = st.checkbox("Gewerkschaftsmitglied")
                pendlereuro = st.number_input("Pendlereuro", value=0.0, min_value=0.0, step=10.0)
                
            with col3:
                jahressechstel = st.number_input("Jahressechstel", value=0.0, min_value=0.0, step=100.0)
            
            submitted = st.form_submit_button("📝 Abrechnung erstellen", type="primary")
            
            if submitted and selected_employee:
                # Create payroll record
                payroll_data = {
                    'PERS_ID': emp_id,
                    'MONAT': monat_str,
                    'STUNDENSATZ': stundensatz,
                    'WOCHENSTUNDEN': wochenstunden,
                    'BRUTTO': brutto,
                    'MEHRSTUNDEN0': mehrstunden0,
                    'MEHRSTUNDEN25': mehrstunden25,
                    'MEHRSTUNDEN50': mehrstunden50,
                    'ÜBERSTUNDEN50': überstunden50,
                    'ÜBERSTUNDEN100': überstunden100,
                    'SONDERZAHLUNGEN': sonderzahlungen,
                    'SACHBEZUG': sachbezug,
                    'DIÄTEN': diäten,
                    'REISEKOSTEN': reisekosten,
                    'FREIBETRAGSBESCHEID': freibetragsbescheid,
                    'PENDLERPAUSCHALE': pendlerpauschale,
                    'PENDLEREURO': pendlereuro,
                    'ANZAHL_KINDER_AVAB': anzahl_kinder,
                    'ANSPRUCH_FABO': 1 if anspruch_fabo else 0,
                    'GEWERKSCHAFTSMITGLIED': 1 if gewerkschaftsmitglied else 0,
                    'JAHRESSECHSTEL': jahressechstel
                }
                
                if payroll_manager.create_payroll_record(payroll_data):
                    st.success(f"✅ Abrechnung für {selected_emp['FULL_NAME']} wurde erfolgreich erstellt!")
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Erstellen der Abrechnung. Möglicherweise existiert bereits eine Abrechnung für diesen Monat.")

with tab3:
    st.header("📈 Gehaltsabrechnung berechnen & anzeigen")
    
    employees = payroll_manager.get_all_employees_for_payroll()
    if employees:
        employee_options = [f"{emp['FULL_NAME']} (ID: {emp['PERS_ID']})" for emp in employees]
        selected_employee = st.selectbox("Mitarbeiter für Berechnung auswählen", employee_options, key="calc_employee")
        
        if selected_employee:
            emp_id = int(selected_employee.split("ID: ")[1].split(")")[0])
            
            # Get payroll history for this employee
            payroll_history = payroll_manager.get_employee_payroll_history(emp_id)
            
            if payroll_history:
                st.subheader("📋 Verfügbare Abrechnungen")
                
                # Create month selector
                available_months = [record['MONAT'] for record in payroll_history]
                selected_month = st.selectbox("Monat auswählen", available_months)
                
                if selected_month:
                    # Find the selected record
                    selected_record = next((record for record in payroll_history if record['MONAT'] == selected_month), None)
                    
                    if selected_record:
                        st.subheader(f"💰 Berechnung für {selected_record['FIRSTNAME']} {selected_record['SURNAME']} - {selected_month}")
                        
                        try:
                            # Use the Abrechnung module to calculate
                            jahr = int(selected_month.split('-')[0])
                            monat = int(selected_month.split('-')[1])
                            
                            result = Abrechnung.calc_brutto2netto(
                                monat=monat,
                                jahr=jahr,
                                stundensatz=float(selected_record.get('STUNDENSATZ', 38.5)),
                                brutto=float(selected_record.get('BRUTTO', 0)),
                                mehrstunden0=float(selected_record.get('MEHRSTUNDEN0', 0)),
                                mehrstunden25=float(selected_record.get('MEHRSTUNDEN25', 0)),
                                mehrstunden50=float(selected_record.get('MEHRSTUNDEN50', 0)),
                                überstunden50=float(selected_record.get('ÜBERSTUNDEN50', 0)),
                                überstunden100=float(selected_record.get('ÜBERSTUNDEN100', 0)),
                                sonderzahlungen=float(selected_record.get('SONDERZAHLUNGEN', 0)),
                                sachbezug=float(selected_record.get('SACHBEZUG', 0)),
                                diäten=float(selected_record.get('DIÄTEN', 0)),
                                reisekosten=float(selected_record.get('REISEKOSTEN', 0)),
                                freibetragsbescheid=float(selected_record.get('FREIBETRAGSBESCHEID', 0)),
                                pendlerpauschale=float(selected_record.get('PENDLERPAUSCHALE', 0)),
                                pendlereuro=float(selected_record.get('PENDLEREURO', 0)),
                                anzahl_Kinder_AVAB=int(selected_record.get('ANZAHL_KINDER_AVAB', 0)),
                                anspruch_fabo=bool(selected_record.get('ANSPRUCH_FABO', 0)),
                                gewerkschaftmitglied=bool(selected_record.get('GEWERKSCHAFTSMITGLIED', 0)),
                                jahressechstel=float(selected_record.get('JAHRESSECHSTEL', 0))
                            )
                            
                            # Display result in a nice format
                            st.code(result, language="text")
                            
                            # Additional info
                            with st.expander("📊 Eingabedaten anzeigen"):
                                input_data = {
                                    'Grundgehalt': f"{selected_record.get('BRUTTO', 0):,.2f} €",
                                    'Wochenstunden': selected_record.get('WOCHENSTUNDEN', 0),
                                    'Mehrstunden (0%)': selected_record.get('MEHRSTUNDEN0', 0),
                                    'Mehrstunden (25%)': selected_record.get('MEHRSTUNDEN25', 0),
                                    'Mehrstunden (50%)': selected_record.get('MEHRSTUNDEN50', 0),
                                    'Überstunden (50%)': selected_record.get('ÜBERSTUNDEN50', 0),
                                    'Überstunden (100%)': selected_record.get('ÜBERSTUNDEN100', 0),
                                    'Sonderzahlungen': f"{selected_record.get('SONDERZAHLUNGEN', 0):,.2f} €",
                                    'Sachbezug': f"{selected_record.get('SACHBEZUG', 0):,.2f} €",
                                }
                                st.table(pd.DataFrame.from_dict(input_data, orient='index', columns=['Wert']))
                                
                        except Exception as e:
                            st.error(f"Fehler bei der Berechnung: {e}")
                            st.write("Debug Info:")
                            st.write(selected_record)
            else:
                st.info("Für diesen Mitarbeiter sind noch keine Abrechnungen vorhanden.")
    else:
        st.warning("Keine Mitarbeiter vorhanden.")

with tab4:
    st.header("📋 Abrechnungshistorie")
    
    employees = payroll_manager.get_all_employees_for_payroll()
    if employees:
        employee_options = ["Alle Mitarbeiter"] + [f"{emp['FULL_NAME']} (ID: {emp['PERS_ID']})" for emp in employees]
        selected_filter = st.selectbox("Filter", employee_options, key="history_filter")
        
        if selected_filter == "Alle Mitarbeiter":
            # Show all payroll records
            import sqlite3
            conn = sqlite3.connect(str(DB_PATH))
            query = '''
                SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME
                FROM LOHNABRECHNUNG l
                JOIN PERSON p ON l.PERS_ID = p.PERS_ID
                ORDER BY l.MONAT DESC, p.PERS_SURNAME
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                # Format the display
                df['Mitarbeiter'] = df['PERS_FIRSTNAME'] + ' ' + df['PERS_SURNAME']
                display_columns = ['Mitarbeiter', 'MONAT', 'BRUTTO', 'WOCHENSTUNDEN', 'ÜBERSTUNDEN50']
                st.dataframe(df[display_columns], use_container_width=True)
            else:
                st.info("Noch keine Abrechnungshistorie vorhanden.")
        else:
            # Show specific employee history
            emp_id = int(selected_filter.split("ID: ")[1].split(")")[0])
            payroll_history = payroll_manager.get_employee_payroll_history(emp_id)
            
            if payroll_history:
                df = pd.DataFrame(payroll_history)
                df['Mitarbeiter'] = df['FIRSTNAME'] + ' ' + df['SURNAME']
                display_columns = ['Mitarbeiter', 'MONAT', 'BRUTTO', 'WOCHENSTUNDEN', 'ÜBERSTUNDEN50', 'SONDERZAHLUNGEN']
                st.dataframe(df[display_columns], use_container_width=True)
                
                # Statistics
                st.subheader("📊 Statistiken")
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_brutto = df['BRUTTO'].mean()
                    st.metric("⌀ Durchschnittsgehalt", f"{avg_brutto:,.2f} €")
                with col2:
                    total_overtime = df['ÜBERSTUNDEN50'].sum()
                    st.metric("Σ Überstunden (50%)", f"{total_overtime:.1f} h")
                with col3:
                    total_months = len(df)
                    st.metric("📅 Abrechnungsmonate", total_months)
            else:
                st.info("Keine Abrechnungshistorie für diesen Mitarbeiter vorhanden.")
    else:
        st.warning("Keine Mitarbeiter vorhanden.")
