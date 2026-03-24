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
    
    lista_raices = sorted(df['Raiz'].unique())
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices)
    
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
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}"
    st.sidebar.image(qr_url, caption="Escanea para entrar")

    # 4. MOSTRAR RESULTADOS
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]

    if not df_filtrado.empty:
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                col_info, col_img = st.columns([1, 1])
                
                with col_info:
                    st.subheader("Información")
                    st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) and str(row['N4']) != 'nan' else ''}")
                    st.info(f"**Intervalos:** {row['Int_IVAN']}")
                
                with col_img:
                    if pd.notna(row['Diagrama1']) and str(row['Diagrama1']) != 'nan':
                        carpeta = str(row['Naturaleza']).strip()
                        archivo = str(row['Diagrama1']).strip()
                        
                        # Generamos la dirección de la imagen en GitHub
                        url_final_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{archivo}"
                        
                        # Intentar mostrar la imagen
                        st.image(url_final_img, use_container_width=True)
                        
                        # LÍNEAS DE INVESTIGACIÓN (
