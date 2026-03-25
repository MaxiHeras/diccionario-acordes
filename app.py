import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# URL del Excel
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        # Cargamos solo las columnas necesarias para evitar errores de memoria
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al cargar Excel: {e}")
        return None

df = load_data()

# Función de PDF básica (solo texto para asegurar compatibilidad)
def generate_pdf(df_filtered):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 800, "Hoja de Estudio de Acordes")
    
    y = 770
    c.setFont("Helvetica", 11)
    for _, row in df_filtered.iterrows():
        if y < 100:
            c.showPage()
            y = 800
        
        texto_acorde = f"Acorde: {row['Raiz']} {row['Naturaleza']}"
        notas = f"Notas: {row.get('N1','')} {row.get('N2','')} {row.get('N3','')} {row.get('N4','')}"
        
        c.drawString(100, y, texto_acorde)
        c.drawString(100, y-15, notas)
        y -= 45
        
    c.save()
    return buffer.getvalue()

if df is not None:
    st.title("🎸 Diccionario de Acordes")
    
    # Filtros simples
    raiz = st.sidebar.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
    tipos_disponibles = df[df['Raiz'] == raiz]['Naturaleza'].unique()
    tipo = st.sidebar.multiselect("Tipo de Acorde:", options=tipos_disponibles)
    
    if tipo:
        df_f = df[(df['Raiz'] == raiz) & (df['Naturaleza'].isin(tipo))]
        
        col1, col2 = st.columns([1, 3])
        with col1:
            pdf_data = generate_pdf(df_f)
            st.download_button("📄 Descargar PDF", pdf_data, "acordes.pdf", "application/pdf")
        
        # Mostrar acordes en pantalla
        for _, row in df_f.iterrows():
            with st.expander(f"{row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.write(f"**Notas:** {row.get('N1','')} - {row.get('N2','')} - {row.get('N3','')} - {row.get('N4','')}")
                
                # Mostrar diagramas en la web (esto no requiere Pillow)
                BASE_IMG = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                cols = st.columns(5)
                for i in range(1, 6):
                    img_name = str(row.get(f'Diagrama{i}', ''))
                    if img_name.endswith('.png'):
                        url = f"{BASE_IMG}/{row['Naturaleza']}/{img_name}"
                        cols[i-1].image(url, caption=f"P{i}")
    else:
        st.info("Selecciona al menos un tipo de acorde en el menú lateral.")
