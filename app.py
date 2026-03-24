import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", page_icon="🎸", layout="wide")

# --- DATOS DE TU CUENTA ---
USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_APP = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

# 2. CONEXIÓN CON GOOGLE SHEET
SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    return pd.read_csv(URL_SHEET)

try:
    df = cargar_datos()
    
    # LIMPIEZA AUTOMÁTICA
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()
    if 'Diagrama1' in df.columns:
        df['Diagrama1'] = df['Diagrama1'].astype(str).str.strip()

    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", sorted(df['Raiz'].unique()))
    df_raiz = df[df['Raiz'] == raiz_sel]
    
    lista_naturalezas = sorted(df_raiz['Naturaleza'].unique())
    nat_sel = st.sidebar.multiselect("Tipo de Acorde:", options=lista_naturalezas, default=lista_naturalezas)

    # QR SEGURO
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}"
    st.sidebar.image(qr_url)

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
                        # Esta es la parte clave para la imagen
                        carpeta = row['Naturaleza']
                        archivo = row['Diagrama1']
                        url_final = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{archivo}"
                        st.image(url_final, use_container_width=True)
    else:
        st.info("Selecciona un acorde.")

except Exception as e:
    st.error(f"Error: {e}")
