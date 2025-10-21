import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Analyse", page_icon=" ", layout="wide")
st.title(" Analyse")

if st.session_state.get("df") is None:
    st.warning("Bitte zuerst auf der Startseite eine Datei laden.")
    st.stop()

df: pd.DataFrame = st.session_state.df

# --- Grundlegende Infos ---
left, right = st.columns([1, 1])
with left:
    st.metric("Zeilen", df.shape[0])
with right:
    st.metric("Spalten", df.shape[1])
st.write("**Spalten**:", ", ".join(map(str, df.columns)))

# --- Numerische Übersicht ---
with st.expander(" Deskriptive Statistik"):
    st.dataframe(df.describe(include=np.number).T, use_container_width=True)

# --- Einfaches Plot-Tool ---
st.subheader("Schneller Plot")
num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
x = st.selectbox("X-Achse", options=df.columns)
y = st.selectbox("Y-Achse (optional)", options=[None] + num_cols, index=0)
color = st.selectbox("Farbe (optional)", options=[None] + cat_cols, index=0)
chart_type = st.radio("Diagrammtyp", ["Scatter", "Bar", "Line"], horizontal=True)

if y is None:
    # 1D-Chart
    if chart_type == "Bar":
        fig = px.bar(df, x=x, color=color)
    else:
        fig = px.histogram(df, x=x, color=color)
else:
    if chart_type == "Scatter":
        fig = px.scatter(df, x=x, y=y, color=color, trendline="ols")
    elif chart_type == "Bar":
        fig = px.bar(df, x=x, y=y, color=color)
    else:
        fig = px.line(df, x=x, y=y, color=color)
st.plotly_chart(fig, use_container_width=True)
