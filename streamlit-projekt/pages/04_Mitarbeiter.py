"""
Mitarbeiterverwaltung – Streamlit-Umsetzung
Alle CRUD-Funktionen für Mitarbeiter
"""
import streamlit as st
import pandas as pd
from pathlib import Path

from modules import dbms, employee, person

DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

st.set_page_config(page_title="Mitarbeiter", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 Mitarbeiterverwaltung")

def load_mitarbeiter():
    return employee.mitarbeiter.select_all(dbms_obj=db)

mitarbeiter = load_mitarbeiter()
data = [m.value() for m in mitarbeiter]
columns = [row[2] for row in employee.mitarbeiter.table_row_names[:-1]]
df = pd.DataFrame(data, columns=columns)
st.dataframe(df, use_container_width=True)

st.subheader("Neuen Mitarbeiter anlegen")
personen = person.person.select_all(db_ms=db)
personen_ids = [str(p.obj_id) for p in personen]
with st.form("create_ma_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        ma_id = st.text_input("Mitarbeiter-ID", key="ma_id")
        persid = st.selectbox("Personen-ID", options=personen_ids, key="persid")
    with col2:
        eintritt = st.text_input("Eintrittsdatum", key="eintritt")
        gehalt = st.text_input("Gehalt", key="gehalt")
    with col3:
        abteilung = st.text_input("Abteilung", key="abteilung")
    submitted = st.form_submit_button("Anlegen")
    if submitted:
        try:
            p = next((x for x in personen if str(x.obj_id) == str(persid)), None)
            new_ma = employee.mitarbeiter(vorname=p.name, nachname=p.surname, geburtsdatum=p.birthdate, eintrittsdatum=eintritt, gehalt=gehalt, persid=persid, straße=p.street, hausnr=p.housenr, stiege_top_etc=p.floor, plz=p.zip, ort=p.place, ma_id=ma_id, abteilung=abteilung)
            new_ma.insert(db)
            st.success(f"Mitarbeiter {p.name} {p.surname} wurde angelegt.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Fehler beim Anlegen: {e}")

st.subheader("Mitarbeiter bearbeiten oder löschen")
if not df.empty:
    selected = st.selectbox("Mitarbeiter auswählen", df["Mitarbeiter-ID"])
    m = next((x for x in mitarbeiter if str(x.empolyee_ID) == str(selected)), None)
    if m:
        with st.form("edit_ma_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                eintritt = st.text_input("Eintrittsdatum", value=m.entrydate, key="edit_eintritt")
                gehalt = st.text_input("Gehalt", value=m.salary, key="edit_gehalt")
            with col2:
                abteilung = st.text_input("Abteilung", value=getattr(m, "abteilung", ""), key="edit_abteilung")
            update = st.form_submit_button("Aktualisieren")
            delete = st.form_submit_button("Löschen")
            if update:
                try:
                    values = [m.empolyee_ID, m.persid, eintritt, gehalt, abteilung]
                    m.update(db, values)
                    st.success("Mitarbeiter aktualisiert.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fehler beim Aktualisieren: {e}")
            if delete:
                try:
                    m.delete(db)
                    st.success("Mitarbeiter gelöscht.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fehler beim Löschen: {e}")
else:
    st.info("Noch keine Mitarbeiter vorhanden.")
