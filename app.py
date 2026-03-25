import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO

# Configuración básica
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# URL de tu Google Sheets (formato CSV)
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(URL_EXCEL)
        # Limpiamos nombres de columnas por si acaso
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"No se pudo conectar con la base de datos: {e}")
        return None

def generar_pdf(df_filtrado):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Diccionario de Acordes Personalizado")
    
    y = 750
    c.setFont("Helvetica", 12)
    for index, row in df_filtrado.iterrows():
        texto = f"Nota: {row['Raiz']} | Tipo: {row['Naturaleza']} | Notas: {row['Notas']}"
        c.drawString(100, y, texto)
        y -= 25
        if y < 50: # Control de página
            c.showPage()
            y = 800
            
    c.save()
    return buffer.getvalue()

# --- INTERFAZ ---
df = cargar_datos()

if df is not None:
    st.title("🎸 Diccionario de Acordes")
    
    # Filtros en la barra lateral
    st.sidebar.header("Filtros")
    notas_disponibles = sorted(df['Raiz'].unique())
    nota_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", notas_disponibles)
    
    tipos_disponibles = df[df['Raiz'] == nota_sel]['Naturaleza'].unique()
    tipo_sel = st.sidebar.multiselect("Selecciona el Tipo:", tipos_disponibles)
    
    if tipo_sel:
        df_f = df[(df['Raiz'] == nota_sel) & (df['Naturaleza'].isin(tipo_sel))]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(df_f, use_container_width=True)
            
        with col2:
            pdf = generar_pdf(df_f)
            st.download_button(
                label="📥 Descargar Acordes en PDF",
                data=pdf,
                file_name=f"acordes_{nota_sel}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Selecciona al menos un tipo de acorde en el menú lateral para ver los resultados.")
