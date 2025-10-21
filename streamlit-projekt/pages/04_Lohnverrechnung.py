"""
Lohnverrechnung – Moderne Streamlit-Umsetzung mit korrektem DB-Schema
Vollständige Gehaltsabrechnung mit historischen Daten und steuerlichen Vorteilen
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt
import sqlite3
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
        total_brutto = sum([p.get('lv_dn_brutto', 0) or 0 for p in monthly_payrolls])
        st.metric("💵 Gesamt Brutto (aktueller Monat)", f"{total_brutto:,.2f} €")
    
    # Recent payrolls table
    if monthly_payrolls:
        st.subheader(f"📋 Abrechnungen für {current_month}")
        df_data = []
        for p in monthly_payrolls:
            df_data.append({
                'Vorname': p.get('FIRSTNAME', ''),
                'Nachname': p.get('SURNAME', ''),
                'Brutto': p.get('lv_dn_brutto', 0),
                'Monat': p.get('lv_dn_monat', ''),
                'Wochenstunden': p.get('lv_dn_wochenstunden', 0),
                'Überstunden 50%': p.get('lv_dn_ueberstunden50', 0)
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info(f"Noch keine Abrechnungen für {current_month} vorhanden.")

with tab2:
    st.header("💸 Neue Gehaltsabrechnung erstellen")
    
    employees = payroll_manager.get_all_employees_for_payroll()
    
    if not employees:
        st.warning("Keine Mitarbeiter vorhanden. Bitte erstellen Sie zuerst Mitarbeiter in der Mitarbeiterverwaltung.")
    else:
        employee_options = [f"{emp['FULL_NAME']} (MA-ID: {emp['EMPL_ID']})" for emp in employees]
        
        with st.form("new_payroll_form"):
            st.subheader("👤 Mitarbeiter & Zeitraum")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_employee = st.selectbox("Mitarbeiter auswählen", employee_options)
                if selected_employee:
                    empl_id = int(selected_employee.split("MA-ID: ")[1].split(")")[0])
                    selected_emp = next((emp for emp in employees if emp['EMPL_ID'] == empl_id), None)
                    if selected_emp:
                        st.info(f"Grundgehalt: {selected_emp['SALARY']:,.2f} €")
                        
                        # Load existing tax benefits
                        tax_benefits = payroll_manager.get_tax_benefits(empl_id)

            with col2:
                abrechnungsmonat = st.date_input("Abrechnungsmonat", dt.datetime.now())
                monat_str = abrechnungsmonat.strftime("%Y-%m")
            
            st.subheader("💰 Gehaltskomponenten")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                brutto = st.number_input("Grundgehalt (Brutto)", value=selected_emp['SALARY'] if 'selected_emp' in locals() else 2500.0, min_value=0.0, step=50.0)
                wochenstunden = st.number_input("Wochenstunden", value=38.5, min_value=0.0, step=0.5)
                stundensatz = st.number_input("Stundensatz", value=20.0, min_value=0.0, step=0.5)
            
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
                jahressechstel = st.number_input("Jahressechstel", value=0.0, min_value=0.0, step=100.0)

            st.subheader("📋 Steuerliche Vorteile")
            st.info("💡 Diese Daten werden separat in der Tabelle 'steuerliche_vorteile' gespeichert")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                freibetrag = st.number_input("Freibetragsbescheid", value=float(tax_benefits.get('freibetrag', 0)) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)
                pendlerpauschale = st.number_input("Pendlerpauschale", value=float(tax_benefits.get('pendlerpauschale', 0)) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)
            
            with col2:
                anzahl_kinder = st.number_input("Anzahl Kinder (AVAB)", value=int(tax_benefits.get('anzahl_kinder_avab', 0)) if 'tax_benefits' in locals() else 0, min_value=0, step=1)
                anspruch_fabo = st.number_input("Familienbonus+", value=float(tax_benefits.get('anspruch_fabo', 0)) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)
            
            with col3:
                gewerkschaftsmitglied = st.checkbox("Gewerkschaftsmitglied", value=bool(tax_benefits.get('gewerkschaft', 0)) if 'tax_benefits' in locals() else False)
                pendlereuro = st.number_input("Pendlereuro", value=float(tax_benefits.get('pendlereuro', 0)) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)

            submitted = st.form_submit_button("📝 Abrechnung erstellen", type="primary")

            if submitted and selected_employee:
                # Save tax benefits first
                tax_benefits_data = {
                    'freibetrag': freibetrag,
                    'pendlerpauschale': pendlerpauschale,
                    'pendlereuro': pendlereuro,
                    'anzahl_kinder_avab': anzahl_kinder,
                    'anspruch_fabo': anspruch_fabo,
                    'gewerkschaft': 1 if gewerkschaftsmitglied else 0
                }
                payroll_manager.save_tax_benefits(empl_id, tax_benefits_data)

                # Create payroll record
                payroll_data = {
                    'lv_dn_empl_id': empl_id,
                    'lv_dn_monat': monat_str,
                    'lv_dn_stundensatz': stundensatz,
                    'lv_dn_wochenstunden': wochenstunden,
                    'lv_dn_brutto': brutto,
                    'lv_dn_mehrstunden0': mehrstunden0,
                    'lv_dn_mehrstunden25': mehrstunden25,
                    'lv_dn_mehrstunden50': mehrstunden50,
                    'lv_dn_ueberstunden50': überstunden50,
                    'lv_dn_ueberstunden100': überstunden100,
                    'lv_dn_sonderzahlungen': sonderzahlungen,
                    'lv_dn_sachbezug': sachbezug,
                    'lv_dn_diäten': diäten,
                    'lv_dn_reisekosten': reisekosten,
                    'lv_dn_jahressechstel': jahressechstel
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
        employee_options = [f"{emp['FULL_NAME']} (MA-ID: {emp['EMPL_ID']})" for emp in employees]
        selected_employee = st.selectbox("Mitarbeiter für Berechnung auswählen", employee_options, key="calc_employee")
        
        if selected_employee:
            empl_id = int(selected_employee.split("MA-ID: ")[1].split(")")[0])
            
            # Get payroll history for this employee
            payroll_history = payroll_manager.get_employee_payroll_history(empl_id)
            
            if payroll_history:
                st.subheader("📋 Verfügbare Abrechnungen")
                
                # Create month selector
                available_months = [record['lv_dn_monat'] for record in payroll_history]
                selected_month = st.selectbox("Monat auswählen", available_months)

                if selected_month:
                    # Find the selected record
                    selected_record = next((record for record in payroll_history if record['lv_dn_monat'] == selected_month), None)
                    
                    if selected_record:
                        st.subheader(f"💰 Berechnung für {selected_record['FIRSTNAME']} {selected_record['SURNAME']} - {selected_month}")
                        
                        # Get tax benefits
                        tax_benefits = payroll_manager.get_tax_benefits(empl_id)

                        try:
                            # Use the Abrechnung module to calculate
                            jahr = int(selected_month.split('-')[0])
                            monat = int(selected_month.split('-')[1])

                            result = Abrechnung.calc_brutto2netto(
                                monat=monat,
                                jahr=jahr,
                                stundensatz=float(selected_record.get('lv_dn_stundensatz', 20.0) or 20.0),
                                brutto=float(selected_record.get('lv_dn_brutto', 0) or 0),
                                mehrstunden0=float(selected_record.get('lv_dn_mehrstunden0', 0) or 0),
                                mehrstunden25=float(selected_record.get('lv_dn_mehrstunden25', 0) or 0),
                                mehrstunden50=float(selected_record.get('lv_dn_mehrstunden50', 0) or 0),
                                überstunden50=float(selected_record.get('lv_dn_ueberstunden50', 0) or 0),
                                überstunden100=float(selected_record.get('lv_dn_ueberstunden100', 0) or 0),
                                sonderzahlungen=float(selected_record.get('lv_dn_sonderzahlungen', 0) or 0),
                                sachbezug=float(selected_record.get('lv_dn_sachbezug', 0) or 0),
                                diäten=float(selected_record.get('lv_dn_diäten', 0) or 0),
                                reisekosten=float(selected_record.get('lv_dn_reisekosten', 0) or 0),
                                freibetragsbescheid=float(tax_benefits.get('freibetrag', 0)),
                                pendlerpauschale=float(tax_benefits.get('pendlerpauschale', 0)),
                                pendlereuro=float(tax_benefits.get('pendlereuro', 0)),
                                anzahl_Kinder_AVAB=int(tax_benefits.get('anzahl_kinder_avab', 0)),
                                anspruch_fabo=bool(tax_benefits.get('anspruch_fabo', 0)),
                                gewerkschaftmitglied=bool(tax_benefits.get('gewerkschaft', 0)),
                                jahressechstel=float(selected_record.get('lv_dn_jahressechstel', 0) or 0)
                            )

                            # Display result in a nice format
                            st.code(result, language="text")

                            # Additional info
                            with st.expander("📊 Eingabedaten anzeigen"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown("**Gehaltskomponenten:**")
                                    input_data = {
                                        'Grundgehalt': f"{selected_record.get('lv_dn_brutto', 0):,.2f} €",
                                        'Wochenstunden': selected_record.get('lv_dn_wochenstunden', 0),
                                        'Mehrstunden (0%)': selected_record.get('lv_dn_mehrstunden0', 0),
                                        'Mehrstunden (25%)': selected_record.get('lv_dn_mehrstunden25', 0),
                                        'Mehrstunden (50%)': selected_record.get('lv_dn_mehrstunden50', 0),
                                        'Überstunden (50%)': selected_record.get('lv_dn_ueberstunden50', 0),
                                        'Überstunden (100%)': selected_record.get('lv_dn_ueberstunden100', 0),
                                    }
                                    st.table(pd.DataFrame.from_dict(input_data, orient='index', columns=['Wert']))

                                with col2:
                                    st.markdown("**Steuerliche Vorteile:**")
                                    tax_data = {
                                        'Freibetragsbescheid': f"{tax_benefits.get('freibetrag', 0):,.2f} €",
                                        'Pendlerpauschale': f"{tax_benefits.get('pendlerpauschale', 0):,.2f} €",
                                        'Pendlereuro': f"{tax_benefits.get('pendlereuro', 0):,.2f} €",
                                        'Anzahl Kinder': tax_benefits.get('anzahl_kinder_avab', 0),
                                        'Familienbonus+': f"{tax_benefits.get('anspruch_fabo', 0):,.2f} €",
                                        'Gewerkschaft': 'Ja' if tax_benefits.get('gewerkschaft', 0) else 'Nein'
                                    }
                                    st.table(pd.DataFrame.from_dict(tax_data, orient='index', columns=['Wert']))

                        except Exception as e:
                            st.error(f"Fehler bei der Berechnung: {e}")
                            st.write("Debug Info:")
                            st.write(selected_record)
                            st.write("Tax Benefits:")
                            st.write(tax_benefits)
            else:
                st.info("Für diesen Mitarbeiter sind noch keine Abrechnungen vorhanden.")
    else:
        st.warning("Keine Mitarbeiter vorhanden.")

with tab4:
    st.header("📋 Abrechnungshistorie")
    
    employees = payroll_manager.get_all_employees_for_payroll()
    if employees:
        employee_options = ["Alle Mitarbeiter"] + [f"{emp['FULL_NAME']} (MA-ID: {emp['EMPL_ID']})" for emp in employees]
        selected_filter = st.selectbox("Filter", employee_options, key="history_filter")

        if selected_filter == "Alle Mitarbeiter":
            # Show all payroll records using correct schema
            conn = sqlite3.connect(str(DB_PATH))
            query = '''
                SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME
                FROM lohnverrechnung_dn l
                JOIN MITARBEITER m ON l.lv_dn_empl_id = m.EMPL_ID
                JOIN PERSON p ON m.PERS_ID = p.PERS_ID
                ORDER BY l.lv_dn_monat DESC, p.PERS_SURNAME
            '''
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                # Format the display
                df['Mitarbeiter'] = df['PERS_FIRSTNAME'] + ' ' + df['PERS_SURNAME']
                display_data = {
                    'Mitarbeiter': df['Mitarbeiter'],
                    'Monat': df['lv_dn_monat'],
                    'Brutto': df['lv_dn_brutto'],
                    'Wochenstunden': df['lv_dn_wochenstunden'],
                    'Überstunden 50%': df['lv_dn_ueberstunden50']
                }
                display_df = pd.DataFrame(display_data)
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("Noch keine Abrechnungshistorie vorhanden.")
        else:
            # Show specific employee history
            empl_id = int(selected_filter.split("MA-ID: ")[1].split(")")[0])
            payroll_history = payroll_manager.get_employee_payroll_history(empl_id)
            
            if payroll_history:
                df_data = []
                for record in payroll_history:
                    df_data.append({
                        'Mitarbeiter': f"{record['FIRSTNAME']} {record['SURNAME']}",
                        'Monat': record['lv_dn_monat'],
                        'Brutto': record['lv_dn_brutto'],
                        'Wochenstunden': record['lv_dn_wochenstunden'],
                        'Überstunden 50%': record['lv_dn_ueberstunden50'],
                        'Sonderzahlungen': record['lv_dn_sonderzahlungen']
                    })
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
                
                # Statistics
                st.subheader("📊 Statistiken")
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_brutto = df['Brutto'].mean()
                    st.metric("⌀ Durchschnittsgehalt", f"{avg_brutto:,.2f} €")
                with col2:
                    total_overtime = df['Überstunden 50%'].sum()
                    st.metric("Σ Überstunden (50%)", f"{total_overtime:.1f} h")
                with col3:
                    total_months = len(df)
                    st.metric("📅 Abrechnungsmonate", total_months)
            else:
                st.info("Keine Abrechnungshistorie für diesen Mitarbeiter vorhanden.")
    else:
        st.warning("Keine Mitarbeiter vorhanden.")