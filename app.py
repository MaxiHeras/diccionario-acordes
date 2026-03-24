import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", page_icon="🎸", layout="wide")

# --- CONFIGURACIÓN ---
USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_APP = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

# 2. CARGA DE DATOS
SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    return pd.read_csv(URL_SHEET)

try:
    df = cargar_datos()
    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", sorted(df['Raiz'].unique()))
    
    df_raiz = df[df['Raiz'] == raiz_sel]
    nat_sel = st.sidebar.multiselect("Tipo:", options=sorted(df_raiz['Naturaleza'].unique()), default=sorted(df_raiz['Naturaleza'].unique()))

    # --- CÓDIGO QR SEGURO ---
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    # Usamos un servicio externo confiable para generar el QR sin instalar nada
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}"
    st.sidebar.image(qr_url, caption="Escanea para entrar")

    # 4. RESULTADOS
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
    for _, row in df_filtrado.iterrows():
        with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) else ''}")
                st.info(f"**Intervalos:** {row['Int_IVAN']}")
            with col2:
                if pd.notna(row['Diagrama1']):
                    nombre_archivo = str(row['Diagrama1']).split('/')[-1]
                    url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{str(row['Naturaleza']).strip()}/{nombre_archivo}"
                    st.image(url_img)

except Exception as e:
    st.error(f"Error al cargar: {e}")
