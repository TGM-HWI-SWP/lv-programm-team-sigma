"""
Lohnverrechnung – Streamlit-Umsetzung
Mitarbeiter auswählen, Abrechnung anzeigen
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import datetime as dt

from modules import dbms, employee, Abrechnung

DB_PATH = Path(__file__).parent.parent / "stammdatenverwaltung.db"
db = dbms.dbms(str(DB_PATH))

st.set_page_config(page_title="Lohnverrechnung", page_icon="💶", layout="wide")
st.title("💶 Lohnverrechnung")

mitarbeiter = employee.mitarbeiter.select_all(dbms_obj=db)
data = [m.value() for m in mitarbeiter]
columns = [row[2] for row in employee.mitarbeiter.table_row_names[:-1]]
df = pd.DataFrame(data, columns=columns)
st.dataframe(df, use_container_width=True)

st.subheader("Lohnverrechnung durchführen")
if not df.empty:
    selected = st.multiselect("Mitarbeiter auswählen", df["Mitarbeiter-ID"])
    if selected:
        for sel in selected:
            m = next((x for x in mitarbeiter if str(x.empolyee_ID) == str(sel)), None)
            if m:
                st.markdown(f"### Abrechnung für {m.vorname} {m.nachname}")
                try:
                    monat = dt.datetime.now().month
                    jahr = dt.datetime.now().year
                    # Beispiel: Stundensatz 38.5, Brutto = Gehalt
                    result = Abrechnung.calc_brutto2netto(monat=monat, jahr=jahr, stundensatz=38.5, brutto=float(m.salary))
                    st.code(result)
                except Exception as e:
                    st.error(f"Fehler bei der Abrechnung: {e}")
    else:
        st.info("Bitte mindestens einen Mitarbeiter auswählen.")
else:
    st.info("Noch keine Mitarbeiter vorhanden.")
