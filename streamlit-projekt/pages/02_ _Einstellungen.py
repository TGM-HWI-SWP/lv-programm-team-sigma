import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import yaml

st.set_page_config(page_title="Einstellungen", page_icon=" ", layout="wide")
st.title(" Einstellungen")

# Beispiel: Konfiguration laden
config_path = Path("config.yaml")
if config_path.exists():
    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    st.json(cfg)
else:
    st.info("Keine config.yaml gefunden. Lege optional eine an.")

# Beispiel: Umgebungsvariablen
load_dotenv()
secret = st.text_input("API Key (Demo)", type="password")
if secret:
    st.session_state["api_key"] = secret
    st.success("API Key im Session State gespeichert (nur Laufzeit)")
