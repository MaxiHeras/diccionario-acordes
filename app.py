import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_SHEET = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(URL_SHEET)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df = cargar_datos()

if df is not None:
    st.title("🎸 Diccionario de Acordes")
    
    # 2. SELECTORES
    orden_notas = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
    raices = [n for n in orden_notas if n in df['Raiz'].unique()]
    
    raiz_sel = st.sidebar.selectbox("Nota Raíz:", raices)
    df_raiz = df[df['Raiz'] == raiz_sel]
    
    nat_sel = st.sidebar.multiselect("Tipo de Acorde:", options=df_raiz['Naturaleza'].unique())

    # 3. RESULTADOS
    if nat_sel:
        for _, row in df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                
                # NOTAS CON SEPARADOR " - "
                notas = [str(row[c]) for c in ['N1', 'N2', 'N3', 'N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() != 'nan']
                st.write(f"**Notas:** {' - '.join(notas)}")

                # INTERVALOS
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                
                # Forzamos Int_TRAD ahora que lo corregiste en el Excel
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")
                
                # IMÁGENES (DISEÑO PARA CELULAR)
                imgs = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]) and str(row[col]) not in ["0", "nan", ""]:
                        file = str(row[col]).split('/')[-1]
                        imgs.append(f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{file}")

                if imgs:
                    # Creamos solo las columnas necesarias para evitar iconos rotos
                    cols = st.columns(len(imgs))
                    for idx, url in enumerate(imgs):
                        with cols[idx]:
                            st.image(url, width=110) # Tamaño reducido para móvil
                            st.caption(f"P{idx+1}")
    else:
        st.info("Selecciona un tipo de acorde.")
