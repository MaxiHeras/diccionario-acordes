import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

def generate_pdf(df_filtered):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 800, "Hoja de Estudio de Acordes")
    y = 750
    c.setFont("Helvetica", 12)
    for _, row in df_filtered.iterrows():
        if y < 100:
            c.showPage()
            y = 800
        c.drawString(100, y, f"Acorde: {row['Raiz']} {row['Naturaleza']}")
        c.drawString(100, y-20, f"Notas: {row.get('N1','')} - {row.get('N2','')} - {row.get('N3','')}")
        y -= 60
    c.save()
    return buffer.getvalue()

if df is not None:
    raiz = st.sidebar.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
    tipo = st.sidebar.multiselect("Tipo:", options=df[df['Raiz']==raiz]['Naturaleza'].unique())
    if tipo:
        df_f = df[(df['Raiz']==raiz) & (df['Naturaleza'].isin(tipo))]
        st.download_button("📄 Descargar PDF", generate_pdf(df_f), "estudio.pdf", "application/pdf")
        st.write(df_f)
else:
    st.error("Error al conectar con los datos.")
