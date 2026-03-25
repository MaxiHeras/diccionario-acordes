import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Diccionario", layout="wide")

URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

def make_pdf(df_f):
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 800, "Mis Acordes")
    y = 780
    for _, row in df_f.iterrows():
        c.drawString(100, y, f"{row['Raiz']} {row['Naturaleza']}")
        y -= 20
    c.save()
    return buf.getvalue()

if df is not None:
    st.title("🎸 Mi Diccionario")
    raiz = st.sidebar.selectbox("Nota:", sorted(df['Raiz'].unique()))
    tipo = st.sidebar.multiselect("Tipo:", df[df['Raiz']==raiz]['Naturaleza'].unique())
    
    if tipo:
        df_f = df[(df['Raiz']==raiz) & (df['Naturaleza'].isin(tipo))]
        st.download_button("Descargar PDF", make_pdf(df_f), "acordes.pdf")
        st.write(df_f)
else:
    st.error("Error cargando datos.")
