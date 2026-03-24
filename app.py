import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Diccionario de Acordes",
    page_icon="🎸",
    layout="wide"
)

# --- DATOS DE TU CUENTA (Asegúrate de que sean exactos) ---
USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_APP = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

# 2. CONEXIÓN CON GOOGLE SHEET
SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    # Cargamos el CSV y limpiamos los nombres de las columnas por si acaso
    df = pd.read_csv(URL_SHEET)
    return df

try:
    df = cargar_datos()
    
    # LIMPIEZA DE DATOS (Para evitar errores de espacios o números)
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()
    if 'Diagrama1' in df.columns:
        df['Diagrama1'] = df['Diagrama1'].astype(str).str.strip()

    # TÍTULO PRINCIPAL
    st.title("🎸 Diccionario de Acordes")
    st.markdown("Herramienta interactiva para alumnos de guitarra.")
    st.divider()

    # 3. BARRA LATERAL (FILTROS Y QR)
    st.sidebar.header("🔍 Buscar Acorde")
    
    # Filtro de Nota Raíz
    lista_raices = sorted(df['Raiz'].unique())
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices)
    
    # Filtrar naturalezas disponibles para esa nota
    df_raiz = df[df['Raiz'] == raiz_sel]
    lista_naturalezas = sorted(df_raiz['Naturaleza'].unique())
    
    nat_sel = st.sidebar.multiselect(
        "Tipo de Acorde:", 
        options=lista_naturalezas, 
        default=lista_naturalezas
    )

    # --- CÓDIGO QR SEGURO (Sin librerías extra) ---
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    qr_url = f"
