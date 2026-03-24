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

def cargar_datos():
    try:
        return pd.read_csv(URL_SHEET)
    except:
        return None

df = cargar_datos()

if df is not None:
    # Limpieza básica
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()
    if 'Diagrama1' in df.columns:
        df['Diagrama1'] = df['Diagrama1'].astype(str).str.strip()

    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    raiz_sel = st.sidebar.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
    
    df_raiz = df[df['Raiz'] == raiz_sel]
    nat_sel = st.sidebar.multiselect("Tipo:", options=sorted(df_raiz['Naturaleza'].unique()), default=sorted(df_raiz['Naturaleza'].unique()))

    # QR
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}"
    st.sidebar.image(qr_url)

    # 4. RESULTADOS
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]

    for _, row in df_filtrado.iterrows():
        with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
            col_info, col_img = st.columns([1, 1])
            with col_info:
                st.subheader("Información")
                st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}")
                st.info(f"**Intervalos:** {row['Int_IVAN']}")
            
            with col_img:
                if pd.notna(row['Diagrama1']) and str(row['Diagrama1']) != 'nan':
                    url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{row['Diagrama1']}"
                    st.image(url_img, use_container_width=True)
                    # Línea de ayuda para detectar errores de nombre
                    st.caption(f"Archivo buscado: {row['Naturaleza']}/{row['Diagrama1']}")
else:
    st.error("No se pudo conectar con el Google Sheet. Revisa el ID.")
