import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Diccionario de Acordes", page_icon="🎸", layout="wide")

USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_APP = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def cargar_datos():
    try:
        return pd.read_csv(URL_SHEET)
    except:
        return None

df = cargar_datos()

if df is not None:
    # Limpieza de datos
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()
    
    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # Barra lateral
    st.sidebar.header("🔍 Buscar Acorde")
    raiz_sel = st.sidebar.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
    df_raiz = df[df['Raiz'] == raiz_sel]
    nat_sel = st.sidebar.multiselect("Tipo:", options=sorted(df_raiz['Naturaleza'].unique()), default=sorted(df_raiz['Naturaleza'].unique()))

    # QR
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    st.sidebar.image(f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}")

    # Resultados
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]

    for _, row in df_filtrado.iterrows():
        with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
            col_info, col_img = st.columns([1, 1])
            with col_info:
                st.subheader("Información")
                st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}")
                st.info(f"**Intervalos:** {row['Int_IVAN']}")
            
            with col_img:
                if pd.notna(row['Diagrama1']):
                    # LIMPIEZA CLAVE: Sacamos solo el nombre del archivo si hay carpetas en el Excel
                    nombre_archivo = str(row['Diagrama1']).split('/')[-1].strip()
                    carpeta = str(row['Naturaleza']).strip()
                    
                    url_final = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{nombre_archivo}"
                    
                    st.image(url_final, use_container_width=True)
                    # Línea para verificar
                    st.caption(f"Buscando en: GitHub -> {carpeta} -> {nombre_archivo}")

else:
    st.error("Error al conectar con Google Sheets.")
