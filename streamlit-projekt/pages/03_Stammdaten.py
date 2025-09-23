"""
Stammdatenverwaltung – Streamlit-Umsetzung
Alle CRUD-Funktionen für Personen (Personalstammblatt)
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# --- Importiere die bestehenden Module ---
MODULE_PATH = Path(__file__).parent.parent / "Stammdaten-Projekt" / "modules"
sys.path.append(str(MODULE_PATH))

import dbms
import person

# --- DB initialisieren ---
DB_PATH = Path(__file__).parent.parent / "Stammdaten-Projekt" / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

st.set_page_config(page_title="Stammdaten", page_icon="👤", layout="wide")
st.title("👤 Stammdatenverwaltung")

# --- Daten laden ---
def load_personen():
    return person.person.select_all(db_ms=db)

personen = load_personen()

# --- Tabelle anzeigen ---
data = [p.value() for p in personen]
columns = [row[2] for row in person.person.table_row_names]
df = pd.DataFrame(data, columns=columns)
st.dataframe(df, use_container_width=True)

# --- CRUD: Neue Person anlegen ---
st.subheader("Neue Person anlegen")
with st.form("create_person_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        id_ = st.text_input("ID", key="id")
        nachname = st.text_input("Nachname", key="nachname")
        vorname = st.text_input("Vorname", key="vorname")
    with col2:
        geburtsdatum = st.text_input("Geburtsdatum", key="geburtsdatum")
        straße = st.text_input("Straße", key="straße")
        hausnr = st.text_input("Hausnummer", key="hausnr")
    with col3:
        stiege = st.text_input("Stiege/Top/etc.", key="stiege")
        plz = st.text_input("PLZ", key="plz")
        ort = st.text_input("Ort", key="ort")
    submitted = st.form_submit_button("Anlegen")
    if submitted:
        try:
            new_p = person.person(id=id_, nachname=nachname, vorname=vorname, geburtsdatum=geburtsdatum, straße=straße, hausnr=hausnr, stiege_top_etc=stiege, plz=plz, ort=ort)
            new_p.insert(db)
            st.success(f"Person {vorname} {nachname} wurde angelegt.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Fehler beim Anlegen: {e}")

# --- CRUD: Person bearbeiten/löschen ---
st.subheader("Person bearbeiten oder löschen")
if not df.empty:
    selected = st.selectbox("Person auswählen", df["ID"])
    p = next((x for x in personen if str(x.obj_id) == str(selected)), None)
    if p:
        with st.form("edit_person_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                nachname = st.text_input("Nachname", value=p.surname, key="edit_nachname")
                vorname = st.text_input("Vorname", value=p.name, key="edit_vorname")
            with col2:
                geburtsdatum = st.text_input("Geburtsdatum", value=p.birthdate, key="edit_geburtsdatum")
                straße = st.text_input("Straße", value=p.street, key="edit_straße")
                hausnr = st.text_input("Hausnummer", value=p.housenr, key="edit_hausnr")
            with col3:
                stiege = st.text_input("Stiege/Top/etc.", value=p.floor, key="edit_stiege")
                plz = st.text_input("PLZ", value=p.zip, key="edit_plz")
                ort = st.text_input("Ort", value=p.place, key="edit_ort")
            update = st.form_submit_button("Aktualisieren")
            delete = st.form_submit_button("Löschen")
            if update:
                try:
                    values = [p.obj_id, nachname, vorname, geburtsdatum, straße, hausnr, stiege, plz, ort]
                    p.update(db, values)
                    st.success("Person aktualisiert.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fehler beim Aktualisieren: {e}")
            if delete:
                try:
                    p.delete(db)
                    st.success("Person gelöscht.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Fehler beim Löschen: {e}")
else:
    st.info("Noch keine Personen vorhanden.")
