import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# CARGA DE DATOS
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

# FUNCIÓN PDF SIMPLIFICADA (A prueba de errores)
def generate_simple_pdf(df_filtered):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 800, "Hoja de Estudio de Acordes")
    
    y = 750
    c.setFont("Helvetica", 12)
    for _, row in df_filtered.iterrows():
        if y < 100: # Nueva página si se acaba el espacio
            c.showPage()
            y = 800
        
        acorde = f"{row['Raiz']} {row['Naturaleza']}"
        notas = f"Notas: {row.get('N1','')} - {row.get('N2','')} - {row.get('N3','')} - {row.get('N4','')}"
        
        c.drawString(100, y, f"Acorde: {acorde}")
        c.drawString(100, y-20, notas)
        y -= 60
        
    c.save()
    return buffer.getvalue()

if df is not None:
    st.sidebar.header("Filtros")
    raiz_sel = st.sidebar.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
    df_raiz = df[df['Raiz'] == raiz_sel]
    nat_sel = st.sidebar.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())

    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        # Botón PDF
        pdf_data = generate_simple_pdf(df_f)
        st.download_button("📄 Descargar PDF (Texto)", pdf_data, "estudio.pdf", "application/pdf")

        # Mostrar en pantalla con imágenes
        for _, row in df_f.iterrows():
            with st.expander(f"{row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.write(f"**Notas:** {row.get('N1','')} - {row.get('N2','')} - {row.get('N3','')} - {row.get('N4','')}")
                # Aquí puedes mantener tu lógica de mostrar imágenes en la web como antes
    else:
        st.info("Selecciona un tipo de acorde.")
else:
    st.error("No se pudo conectar con el Excel.")
