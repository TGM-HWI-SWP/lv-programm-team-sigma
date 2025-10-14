""""""

Lohnverrechnung – Moderne Streamlit-Umsetzung mit neuem DB-SchemaLohnverrechnung – Moderne Streamlit-Umsetzung

Vollständige Gehaltsabrechnung mit historischen Daten und steuerlichen VorteilenVollständige Gehaltsabrechnung mit historischen Daten

""""""

import streamlit as stimport streamlit as st

import pandas as pdimport pandas as pd

from pathlib import Pathfrom pathlib import Path

import datetime as dtimport datetime as dt

from decimal import Decimal

from modules import dbms, employee, Abrechnung, payroll, auth

from modules import dbms, employee, Abrechnung, payroll, auth

# Authentication check

auth.init_session_state()# Authentication check

if not st.session_state.get('authenticated', False):auth.init_session_state()

    st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")if not st.session_state.get('authenticated', False):

    st.stop()    st.error("Sie müssen sich anmelden, um diese Seite zu sehen.")

    st.stop()

DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"

db = dbms.dbms(str(DB_PATH))DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"

payroll_manager = payroll.PayrollManager(str(DB_PATH))db = dbms.dbms(str(DB_PATH))

payroll_manager = payroll.PayrollManager(str(DB_PATH))

st.set_page_config(page_title="Lohnverrechnung", page_icon="💰", layout="wide")

st.title("💰 Lohnverrechnung & Gehaltsabrechnung")st.set_page_config(page_title="Lohnverrechnung", page_icon="💰", layout="wide")

st.title("💰 Lohnverrechnung & Gehaltsabrechnung")

# Sidebar for user info

with st.sidebar:# Sidebar for user info

    user_data = st.session_state.get('user_data', {})with st.sidebar:

    st.success(f"Angemeldet: **{user_data.get('username', '')}**")    user_data = st.session_state.get('user_data', {})

    if st.button("Abmelden", type="secondary"):    st.success(f"Angemeldet: **{user_data.get('username', '')}**")

        auth.logout()    if st.button("Abmelden", type="secondary"):

        auth.logout()

# Tab structure

tab1, tab2, tab3, tab4 = st.tabs(["📊 Übersicht", "💸 Neue Abrechnung", "📈 Abrechnung anzeigen", "📋 Historie"])# Tab structure

tab1, tab2, tab3, tab4 = st.tabs(["📊 Übersicht", "💸 Neue Abrechnung", "📈 Abrechnung anzeigen", "📋 Historie"])

with tab1:

    st.header("📊 Gehaltsabrechnungs-Übersicht")with tab1:

        st.header("📊 Gehaltsabrechnungs-Übersicht")

    # Current month statistics    

    current_month = dt.datetime.now().strftime("%Y-%m")    # Current month statistics

    monthly_payrolls = payroll_manager.get_monthly_payroll_summary(current_month)    current_month = dt.datetime.now().strftime("%Y-%m")

        monthly_payrolls = payroll_manager.get_monthly_payroll_summary(current_month)

    col1, col2, col3 = st.columns(3)    

    with col1:    col1, col2, col3 = st.columns(3)

        st.metric("🧑‍💼 Mitarbeiter", len(payroll_manager.get_all_employees_for_payroll()))    with col1:

    with col2:        st.metric("🧑‍💼 Mitarbeiter", len(payroll_manager.get_all_employees_for_payroll()))

        st.metric("💰 Abrechnungen (aktueller Monat)", len(monthly_payrolls))    with col2:

    with col3:        st.metric("💰 Abrechnungen (aktueller Monat)", len(monthly_payrolls))

        total_brutto = sum([p.get('lv_dn_brutto', 0) or 0 for p in monthly_payrolls])    with col3:

        st.metric("💵 Gesamt Brutto (aktueller Monat)", f"{total_brutto:,.2f} €")        total_brutto = sum([p.get('BRUTTO', 0) for p in monthly_payrolls])

            st.metric("💵 Gesamt Brutto (aktueller Monat)", f"{total_brutto:,.2f} €")

    # Recent payrolls table    

    if monthly_payrolls:    # Recent payrolls table

        st.subheader(f"📋 Abrechnungen für {current_month}")    if monthly_payrolls:

        df_data = []        st.subheader(f"📋 Abrechnungen für {current_month}")

        for p in monthly_payrolls:        df = pd.DataFrame(monthly_payrolls)

            df_data.append({        display_columns = ['FIRSTNAME', 'SURNAME', 'BRUTTO', 'MONAT', 'WOCHENSTUNDEN', 'ÜBERSTUNDEN50']

                'Vorname': p.get('FIRSTNAME', ''),        st.dataframe(df[display_columns], use_container_width=True)

                'Nachname': p.get('SURNAME', ''),    else:

                'Brutto': p.get('lv_dn_brutto', 0),        st.info(f"Noch keine Abrechnungen für {current_month} vorhanden.")

                'Monat': p.get('lv_dn_monat', ''),

                'Wochenstunden': p.get('lv_dn_wochenstunden', 0),with tab2:

                'Überstunden 50%': p.get('lv_dn_ueberstunden50', 0)    st.header("💸 Neue Gehaltsabrechnung erstellen")

            })    

        df = pd.DataFrame(df_data)    employees = payroll_manager.get_all_employees_for_payroll()

        st.dataframe(df, use_container_width=True)    

    else:    if not employees:

        st.info(f"Noch keine Abrechnungen für {current_month} vorhanden.")        st.warning("Keine Mitarbeiter vorhanden. Bitte erstellen Sie zuerst Mitarbeiter in der Mitarbeiterverwaltung.")

    else:

with tab2:        employee_options = [f"{emp['FULL_NAME']} (ID: {emp['PERS_ID']})" for emp in employees]

    st.header("💸 Neue Gehaltsabrechnung erstellen")        

            with st.form("new_payroll_form"):

    employees = payroll_manager.get_all_employees_for_payroll()            st.subheader("👤 Mitarbeiter & Zeitraum")

                col1, col2 = st.columns(2)

    if not employees:            

        st.warning("Keine Mitarbeiter vorhanden. Bitte erstellen Sie zuerst Mitarbeiter in der Mitarbeiterverwaltung.")            with col1:

    else:                selected_employee = st.selectbox("Mitarbeiter auswählen", employee_options)

        employee_options = [f"{emp['FULL_NAME']} (MA-ID: {emp['EMPL_ID']})" for emp in employees]                if selected_employee:

                            emp_id = int(selected_employee.split("ID: ")[1].split(")")[0])

        with st.form("new_payroll_form"):                    selected_emp = next((emp for emp in employees if emp['PERS_ID'] == emp_id), None)

            st.subheader("👤 Mitarbeiter & Zeitraum")                    if selected_emp:

            col1, col2 = st.columns(2)                        st.info(f"Grundgehalt: {selected_emp['SALARY']:,.2f} €")

                        

            with col1:            with col2:

                selected_employee = st.selectbox("Mitarbeiter auswählen", employee_options)                abrechnungsmonat = st.date_input("Abrechnungsmonat", dt.datetime.now())

                if selected_employee:                monat_str = abrechnungsmonat.strftime("%Y-%m")

                    empl_id = int(selected_employee.split("MA-ID: ")[1].split(")")[0])            

                    selected_emp = next((emp for emp in employees if emp['EMPL_ID'] == empl_id), None)            st.subheader("💰 Gehaltskomponenten")

                    if selected_emp:            col1, col2, col3 = st.columns(3)

                        st.info(f"Grundgehalt: {selected_emp['SALARY']:,.2f} €")            

                                    with col1:

                        # Load existing tax benefits                brutto = st.number_input("Grundgehalt (Brutto)", value=selected_emp['SALARY'] if 'selected_emp' in locals() else 2500.0, min_value=0.0, step=50.0)

                        tax_benefits = payroll_manager.get_tax_benefits(empl_id)                wochenstunden = st.number_input("Wochenstunden", value=38.5, min_value=0.0, step=0.5)

                            stundensatz = st.number_input("Stundensatz", value=38.5, min_value=0.0, step=0.5)

            with col2:            

                abrechnungsmonat = st.date_input("Abrechnungsmonat", dt.datetime.now())            with col2:

                monat_str = abrechnungsmonat.strftime("%Y-%m")                mehrstunden0 = st.number_input("Mehrstunden (0%)", value=0.0, min_value=0.0, step=0.5)

                            mehrstunden25 = st.number_input("Mehrstunden (25%)", value=0.0, min_value=0.0, step=0.5)

            st.subheader("💰 Gehaltskomponenten")                mehrstunden50 = st.number_input("Mehrstunden (50%)", value=0.0, min_value=0.0, step=0.5)

            col1, col2, col3 = st.columns(3)                

                        with col3:

            with col1:                überstunden50 = st.number_input("Überstunden (50%)", value=0.0, min_value=0.0, step=0.5)

                brutto = st.number_input("Grundgehalt (Brutto)", value=selected_emp['SALARY'] if 'selected_emp' in locals() else 2500.0, min_value=0.0, step=50.0)                überstunden100 = st.number_input("Überstunden (100%)", value=0.0, min_value=0.0, step=0.5)

                wochenstunden = st.number_input("Wochenstunden", value=38.5, min_value=0.0, step=0.5)            

                stundensatz = st.number_input("Stundensatz", value=38.5, min_value=0.0, step=0.5)            st.subheader("🎁 Zusätze & Abzüge")

                        col1, col2, col3 = st.columns(3)

            with col2:            

                mehrstunden0 = st.number_input("Mehrstunden (0%)", value=0.0, min_value=0.0, step=0.5)            with col1:

                mehrstunden25 = st.number_input("Mehrstunden (25%)", value=0.0, min_value=0.0, step=0.5)                sonderzahlungen = st.number_input("Sonderzahlungen", value=0.0, min_value=0.0, step=50.0)

                mehrstunden50 = st.number_input("Mehrstunden (50%)", value=0.0, min_value=0.0, step=0.5)                sachbezug = st.number_input("Sachbezug", value=0.0, min_value=0.0, step=10.0)

                                

            with col3:            with col2:

                überstunden50 = st.number_input("Überstunden (50%)", value=0.0, min_value=0.0, step=0.5)                diäten = st.number_input("Diäten", value=0.0, min_value=0.0, step=10.0)

                überstunden100 = st.number_input("Überstunden (100%)", value=0.0, min_value=0.0, step=0.5)                reisekosten = st.number_input("Reisekosten", value=0.0, min_value=0.0, step=10.0)

                            

            st.subheader("🎁 Zusätze & Abzüge")            with col3:

            col1, col2, col3 = st.columns(3)                freibetragsbescheid = st.number_input("Freibetragsbescheid", value=0.0, min_value=0.0, step=10.0)

                            pendlerpauschale = st.number_input("Pendlerpauschale", value=0.0, min_value=0.0, step=10.0)

            with col1:            

                sonderzahlungen = st.number_input("Sonderzahlungen", value=0.0, min_value=0.0, step=50.0)            st.subheader("👨‍👩‍👧‍👦 Familie & Weitere Angaben")

                sachbezug = st.number_input("Sachbezug", value=0.0, min_value=0.0, step=10.0)            col1, col2, col3 = st.columns(3)

                            

            with col2:            with col1:

                diäten = st.number_input("Diäten", value=0.0, min_value=0.0, step=10.0)                anzahl_kinder = st.number_input("Anzahl Kinder (AVAB)", value=0, min_value=0, step=1)

                reisekosten = st.number_input("Reisekosten", value=0.0, min_value=0.0, step=10.0)                anspruch_fabo = st.checkbox("Anspruch auf Familienbonus+")

                                

            with col3:            with col2:

                jahressechstel = st.number_input("Jahressechstel", value=0.0, min_value=0.0, step=100.0)                gewerkschaftsmitglied = st.checkbox("Gewerkschaftsmitglied")

                            pendlereuro = st.number_input("Pendlereuro", value=0.0, min_value=0.0, step=10.0)

            st.subheader("📋 Steuerliche Vorteile")                

            st.info("💡 Diese Daten werden separat in der Tabelle 'steuerliche_vorteile' gespeichert")            with col3:

                            jahressechstel = st.number_input("Jahressechstel", value=0.0, min_value=0.0, step=100.0)

            col1, col2, col3 = st.columns(3)            

                        submitted = st.form_submit_button("📝 Abrechnung erstellen", type="primary")

            with col1:            

                freibetrag = st.number_input("Freibetragsbescheid", value=tax_benefits.get('freibetrag', 0) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)            if submitted and selected_employee:

                pendlerpauschale = st.number_input("Pendlerpauschale", value=tax_benefits.get('pendlerpauschale', 0) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)                # Create payroll record

                                payroll_data = {

            with col2:                    'PERS_ID': emp_id,

                anzahl_kinder = st.number_input("Anzahl Kinder (AVAB)", value=tax_benefits.get('anzahl_kinder_avab', 0) if 'tax_benefits' in locals() else 0, min_value=0, step=1)                    'MONAT': monat_str,

                anspruch_fabo = st.number_input("Familienbonus+", value=tax_benefits.get('anspruch_fabo', 0) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)                    'STUNDENSATZ': stundensatz,

                                    'WOCHENSTUNDEN': wochenstunden,

            with col3:                    'BRUTTO': brutto,

                gewerkschaftsmitglied = st.checkbox("Gewerkschaftsmitglied", value=bool(tax_benefits.get('gewerkschaft', 0)) if 'tax_benefits' in locals() else False)                    'MEHRSTUNDEN0': mehrstunden0,

                pendlereuro = st.number_input("Pendlereuro", value=tax_benefits.get('pendlereuro', 0) if 'tax_benefits' in locals() else 0.0, min_value=0.0, step=10.0)                    'MEHRSTUNDEN25': mehrstunden25,

                                'MEHRSTUNDEN50': mehrstunden50,

            submitted = st.form_submit_button("📝 Abrechnung erstellen", type="primary")                    'ÜBERSTUNDEN50': überstunden50,

                                'ÜBERSTUNDEN100': überstunden100,

            if submitted and selected_employee:                    'SONDERZAHLUNGEN': sonderzahlungen,

                # Save tax benefits first                    'SACHBEZUG': sachbezug,

                tax_benefits_data = {                    'DIÄTEN': diäten,

                    'freibetrag': freibetrag,                    'REISEKOSTEN': reisekosten,

                    'pendlerpauschale': pendlerpauschale,                    'FREIBETRAGSBESCHEID': freibetragsbescheid,

                    'pendlereuro': pendlereuro,                    'PENDLERPAUSCHALE': pendlerpauschale,

                    'anzahl_kinder_avab': anzahl_kinder,                    'PENDLEREURO': pendlereuro,

                    'anspruch_fabo': anspruch_fabo,                    'ANZAHL_KINDER_AVAB': anzahl_kinder,

                    'gewerkschaft': 1 if gewerkschaftsmitglied else 0                    'ANSPRUCH_FABO': 1 if anspruch_fabo else 0,

                }                    'GEWERKSCHAFTSMITGLIED': 1 if gewerkschaftsmitglied else 0,

                payroll_manager.save_tax_benefits(empl_id, tax_benefits_data)                    'JAHRESSECHSTEL': jahressechstel

                                }

                # Create payroll record                

                payroll_data = {                if payroll_manager.create_payroll_record(payroll_data):

                    'lv_dn_empl_id': empl_id,                    st.success(f"✅ Abrechnung für {selected_emp['FULL_NAME']} wurde erfolgreich erstellt!")

                    'lv_dn_monat': monat_str,                    st.rerun()

                    'lv_dn_stundensatz': stundensatz,                else:

                    'lv_dn_wochenstunden': wochenstunden,                    st.error("❌ Fehler beim Erstellen der Abrechnung. Möglicherweise existiert bereits eine Abrechnung für diesen Monat.")

                    'lv_dn_brutto': brutto,

                    'lv_dn_mehrstunden0': mehrstunden0,with tab3:

                    'lv_dn_mehrstunden25': mehrstunden25,    st.header("📈 Gehaltsabrechnung berechnen & anzeigen")

                    'lv_dn_mehrstunden50': mehrstunden50,    

                    'lv_dn_ueberstunden50': überstunden50,    employees = payroll_manager.get_all_employees_for_payroll()

                    'lv_dn_ueberstunden100': überstunden100,    if employees:

                    'lv_dn_sonderzahlungen': sonderzahlungen,        employee_options = [f"{emp['FULL_NAME']} (ID: {emp['PERS_ID']})" for emp in employees]

                    'lv_dn_sachbezug': sachbezug,        selected_employee = st.selectbox("Mitarbeiter für Berechnung auswählen", employee_options, key="calc_employee")

                    'lv_dn_diäten': diäten,        

                    'lv_dn_reisekosten': reisekosten,        if selected_employee:

                    'lv_dn_jahressechstel': jahressechstel            emp_id = int(selected_employee.split("ID: ")[1].split(")")[0])

                }            

                            # Get payroll history for this employee

                if payroll_manager.create_payroll_record(payroll_data):            payroll_history = payroll_manager.get_employee_payroll_history(emp_id)

                    st.success(f"✅ Abrechnung für {selected_emp['FULL_NAME']} wurde erfolgreich erstellt!")            

                    st.rerun()            if payroll_history:

                else:                st.subheader("📋 Verfügbare Abrechnungen")

                    st.error("❌ Fehler beim Erstellen der Abrechnung. Möglicherweise existiert bereits eine Abrechnung für diesen Monat.")                

                # Create month selector

with tab3:                available_months = [record['MONAT'] for record in payroll_history]

    st.header("📈 Gehaltsabrechnung berechnen & anzeigen")                selected_month = st.selectbox("Monat auswählen", available_months)

                    

    employees = payroll_manager.get_all_employees_for_payroll()                if selected_month:

    if employees:                    # Find the selected record

        employee_options = [f"{emp['FULL_NAME']} (MA-ID: {emp['EMPL_ID']})" for emp in employees]                    selected_record = next((record for record in payroll_history if record['MONAT'] == selected_month), None)

        selected_employee = st.selectbox("Mitarbeiter für Berechnung auswählen", employee_options, key="calc_employee")                    

                            if selected_record:

        if selected_employee:                        st.subheader(f"💰 Berechnung für {selected_record['FIRSTNAME']} {selected_record['SURNAME']} - {selected_month}")

            empl_id = int(selected_employee.split("MA-ID: ")[1].split(")")[0])                        

                                    try:

            # Get payroll history for this employee                            # Use the Abrechnung module to calculate

            payroll_history = payroll_manager.get_employee_payroll_history(empl_id)                            jahr = int(selected_month.split('-')[0])

                                        monat = int(selected_month.split('-')[1])

            if payroll_history:                            

                st.subheader("📋 Verfügbare Abrechnungen")                            result = Abrechnung.calc_brutto2netto(

                                                monat=monat,

                # Create month selector                                jahr=jahr,

                available_months = [record['lv_dn_monat'] for record in payroll_history]                                stundensatz=float(selected_record.get('STUNDENSATZ', 38.5)),

                selected_month = st.selectbox("Monat auswählen", available_months)                                brutto=float(selected_record.get('BRUTTO', 0)),

                                                mehrstunden0=float(selected_record.get('MEHRSTUNDEN0', 0)),

                if selected_month:                                mehrstunden25=float(selected_record.get('MEHRSTUNDEN25', 0)),

                    # Find the selected record                                mehrstunden50=float(selected_record.get('MEHRSTUNDEN50', 0)),

                    selected_record = next((record for record in payroll_history if record['lv_dn_monat'] == selected_month), None)                                überstunden50=float(selected_record.get('ÜBERSTUNDEN50', 0)),

                                                    überstunden100=float(selected_record.get('ÜBERSTUNDEN100', 0)),

                    if selected_record:                                sonderzahlungen=float(selected_record.get('SONDERZAHLUNGEN', 0)),

                        st.subheader(f"💰 Berechnung für {selected_record['FIRSTNAME']} {selected_record['SURNAME']} - {selected_month}")                                sachbezug=float(selected_record.get('SACHBEZUG', 0)),

                                                        diäten=float(selected_record.get('DIÄTEN', 0)),

                        # Get tax benefits                                reisekosten=float(selected_record.get('REISEKOSTEN', 0)),

                        tax_benefits = payroll_manager.get_tax_benefits(empl_id)                                freibetragsbescheid=float(selected_record.get('FREIBETRAGSBESCHEID', 0)),

                                                        pendlerpauschale=float(selected_record.get('PENDLERPAUSCHALE', 0)),

                        try:                                pendlereuro=float(selected_record.get('PENDLEREURO', 0)),

                            # Use the Abrechnung module to calculate                                anzahl_Kinder_AVAB=int(selected_record.get('ANZAHL_KINDER_AVAB', 0)),

                            jahr = int(selected_month.split('-')[0])                                anspruch_fabo=bool(selected_record.get('ANSPRUCH_FABO', 0)),

                            monat = int(selected_month.split('-')[1])                                gewerkschaftmitglied=bool(selected_record.get('GEWERKSCHAFTSMITGLIED', 0)),

                                                            jahressechstel=float(selected_record.get('JAHRESSECHSTEL', 0))

                            result = Abrechnung.calc_brutto2netto(                            )

                                monat=monat,                            

                                jahr=jahr,                            # Display result in a nice format

                                stundensatz=float(selected_record.get('lv_dn_stundensatz', 38.5) or 38.5),                            st.code(result, language="text")

                                brutto=float(selected_record.get('lv_dn_brutto', 0) or 0),                            

                                mehrstunden0=float(selected_record.get('lv_dn_mehrstunden0', 0) or 0),                            # Additional info

                                mehrstunden25=float(selected_record.get('lv_dn_mehrstunden25', 0) or 0),                            with st.expander("📊 Eingabedaten anzeigen"):

                                mehrstunden50=float(selected_record.get('lv_dn_mehrstunden50', 0) or 0),                                input_data = {

                                überstunden50=float(selected_record.get('lv_dn_ueberstunden50', 0) or 0),                                    'Grundgehalt': f"{selected_record.get('BRUTTO', 0):,.2f} €",

                                überstunden100=float(selected_record.get('lv_dn_ueberstunden100', 0) or 0),                                    'Wochenstunden': selected_record.get('WOCHENSTUNDEN', 0),

                                sonderzahlungen=float(selected_record.get('lv_dn_sonderzahlungen', 0) or 0),                                    'Mehrstunden (0%)': selected_record.get('MEHRSTUNDEN0', 0),

                                sachbezug=float(selected_record.get('lv_dn_sachbezug', 0) or 0),                                    'Mehrstunden (25%)': selected_record.get('MEHRSTUNDEN25', 0),

                                diäten=float(selected_record.get('lv_dn_diäten', 0) or 0),                                    'Mehrstunden (50%)': selected_record.get('MEHRSTUNDEN50', 0),

                                reisekosten=float(selected_record.get('lv_dn_reisekosten', 0) or 0),                                    'Überstunden (50%)': selected_record.get('ÜBERSTUNDEN50', 0),

                                freibetragsbescheid=float(tax_benefits.get('freibetrag', 0)),                                    'Überstunden (100%)': selected_record.get('ÜBERSTUNDEN100', 0),

                                pendlerpauschale=float(tax_benefits.get('pendlerpauschale', 0)),                                    'Sonderzahlungen': f"{selected_record.get('SONDERZAHLUNGEN', 0):,.2f} €",

                                pendlereuro=float(tax_benefits.get('pendlereuro', 0)),                                    'Sachbezug': f"{selected_record.get('SACHBEZUG', 0):,.2f} €",

                                anzahl_Kinder_AVAB=int(tax_benefits.get('anzahl_kinder_avab', 0)),                                }

                                anspruch_fabo=bool(tax_benefits.get('anspruch_fabo', 0)),                                st.table(pd.DataFrame.from_dict(input_data, orient='index', columns=['Wert']))

                                gewerkschaftmitglied=bool(tax_benefits.get('gewerkschaft', 0)),                                

                                jahressechstel=float(selected_record.get('lv_dn_jahressechstel', 0) or 0)                        except Exception as e:

                            )                            st.error(f"Fehler bei der Berechnung: {e}")

                                                        st.write("Debug Info:")

                            # Display result in a nice format                            st.write(selected_record)

                            st.code(result, language="text")            else:

                                            st.info("Für diesen Mitarbeiter sind noch keine Abrechnungen vorhanden.")

                            # Additional info    else:

                            with st.expander("📊 Eingabedaten anzeigen"):        st.warning("Keine Mitarbeiter vorhanden.")

                                col1, col2 = st.columns(2)

                                with col1:with tab4:

                                    st.markdown("**Gehaltskomponenten:**")    st.header("📋 Abrechnungshistorie")

                                    input_data = {    

                                        'Grundgehalt': f"{selected_record.get('lv_dn_brutto', 0):,.2f} €",    employees = payroll_manager.get_all_employees_for_payroll()

                                        'Wochenstunden': selected_record.get('lv_dn_wochenstunden', 0),    if employees:

                                        'Mehrstunden (0%)': selected_record.get('lv_dn_mehrstunden0', 0),        employee_options = ["Alle Mitarbeiter"] + [f"{emp['FULL_NAME']} (ID: {emp['PERS_ID']})" for emp in employees]

                                        'Mehrstunden (25%)': selected_record.get('lv_dn_mehrstunden25', 0),        selected_filter = st.selectbox("Filter", employee_options, key="history_filter")

                                        'Mehrstunden (50%)': selected_record.get('lv_dn_mehrstunden50', 0),        

                                        'Überstunden (50%)': selected_record.get('lv_dn_ueberstunden50', 0),        if selected_filter == "Alle Mitarbeiter":

                                        'Überstunden (100%)': selected_record.get('lv_dn_ueberstunden100', 0),            # Show all payroll records

                                    }            import sqlite3

                                    st.table(pd.DataFrame.from_dict(input_data, orient='index', columns=['Wert']))            conn = sqlite3.connect(str(DB_PATH))

                                            query = '''

                                with col2:                SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME

                                    st.markdown("**Steuerliche Vorteile:**")                FROM LOHNABRECHNUNG l

                                    tax_data = {                JOIN PERSON p ON l.PERS_ID = p.PERS_ID

                                        'Freibetragsbescheid': f"{tax_benefits.get('freibetrag', 0):,.2f} €",                ORDER BY l.MONAT DESC, p.PERS_SURNAME

                                        'Pendlerpauschale': f"{tax_benefits.get('pendlerpauschale', 0):,.2f} €",            '''

                                        'Pendlereuro': f"{tax_benefits.get('pendlereuro', 0):,.2f} €",            df = pd.read_sql_query(query, conn)

                                        'Anzahl Kinder': tax_benefits.get('anzahl_kinder_avab', 0),            conn.close()

                                        'Familienbonus+': f"{tax_benefits.get('anspruch_fabo', 0):,.2f} €",            

                                        'Gewerkschaft': 'Ja' if tax_benefits.get('gewerkschaft', 0) else 'Nein'            if not df.empty:

                                    }                # Format the display

                                    st.table(pd.DataFrame.from_dict(tax_data, orient='index', columns=['Wert']))                df['Mitarbeiter'] = df['PERS_FIRSTNAME'] + ' ' + df['PERS_SURNAME']

                                                display_columns = ['Mitarbeiter', 'MONAT', 'BRUTTO', 'WOCHENSTUNDEN', 'ÜBERSTUNDEN50']

                        except Exception as e:                st.dataframe(df[display_columns], use_container_width=True)

                            st.error(f"Fehler bei der Berechnung: {e}")            else:

                            st.write("Debug Info:")                st.info("Noch keine Abrechnungshistorie vorhanden.")

                            st.write(selected_record)        else:

                            st.write("Tax Benefits:")            # Show specific employee history

                            st.write(tax_benefits)            emp_id = int(selected_filter.split("ID: ")[1].split(")")[0])

            else:            payroll_history = payroll_manager.get_employee_payroll_history(emp_id)

                st.info("Für diesen Mitarbeiter sind noch keine Abrechnungen vorhanden.")            

    else:            if payroll_history:

        st.warning("Keine Mitarbeiter vorhanden.")                df = pd.DataFrame(payroll_history)

                df['Mitarbeiter'] = df['FIRSTNAME'] + ' ' + df['SURNAME']

with tab4:                display_columns = ['Mitarbeiter', 'MONAT', 'BRUTTO', 'WOCHENSTUNDEN', 'ÜBERSTUNDEN50', 'SONDERZAHLUNGEN']

    st.header("📋 Abrechnungshistorie")                st.dataframe(df[display_columns], use_container_width=True)

                    

    employees = payroll_manager.get_all_employees_for_payroll()                # Statistics

    if employees:                st.subheader("📊 Statistiken")

        employee_options = ["Alle Mitarbeiter"] + [f"{emp['FULL_NAME']} (MA-ID: {emp['EMPL_ID']})" for emp in employees]                col1, col2, col3 = st.columns(3)

        selected_filter = st.selectbox("Filter", employee_options, key="history_filter")                with col1:

                            avg_brutto = df['BRUTTO'].mean()

        if selected_filter == "Alle Mitarbeiter":                    st.metric("⌀ Durchschnittsgehalt", f"{avg_brutto:,.2f} €")

            # Show all payroll records                with col2:

            import sqlite3                    total_overtime = df['ÜBERSTUNDEN50'].sum()

            conn = sqlite3.connect(str(DB_PATH))                    st.metric("Σ Überstunden (50%)", f"{total_overtime:.1f} h")

            query = '''                with col3:

                SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME                    total_months = len(df)

                FROM lohnverrechnung_dn l                    st.metric("📅 Abrechnungsmonate", total_months)

                JOIN MITARBEITER m ON l.lv_dn_empl_id = m.EMPL_ID            else:

                JOIN PERSON p ON m.PERS_ID = p.PERS_ID                st.info("Keine Abrechnungshistorie für diesen Mitarbeiter vorhanden.")

                ORDER BY l.lv_dn_monat DESC, p.PERS_SURNAME    else:

            '''        st.warning("Keine Mitarbeiter vorhanden.")

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
