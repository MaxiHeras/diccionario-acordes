import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN INICIAL
# Usamos session_state para manejar si la barra debe estar colapsada o no
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

st.set_page_config(
    page_title="Diccionario de Acordes", 
    layout="wide", 
    initial_sidebar_state=st.session_state.sidebar_state
)

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
    
    # 2. BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden_notas = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
        raices_existentes = df['Raiz'].unique()
        raices = [n for n in orden_notas if n in raices_existentes]
        
        raiz_sel = st.selectbox("Nota Raíz:", raices)
        df_raiz = df[df['Raiz'] == raiz_sel]
        
        nat_sel = st.multiselect("Tipo de Acorde:", options=df_raiz['Naturaleza'].unique())
        
        st.write("---") # Separador visual
        # BOTÓN AL FINAL DE LA BARRA
        if st.button("Mostrar acordes", use_container_width=True):
            if nat_sel:
                st.session_state.sidebar_state = "collapsed"
                st.rerun() # Recarga para aplicar el cierre de la barra
            else:
                st.warning("Selecciona al menos un tipo.")

    # 3. RESULTADOS
    if nat_sel:
        # Botón para volver a mostrar la barra si el usuario lo desea
        if st.session_state.sidebar_state == "collapsed":
            if st.button("⬅️ Cambiar selección"):
                st.session_state.sidebar_state = "expanded"
                st.rerun()

        for _, row in df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                
                # NOTAS CON SEPARADOR " - "
                columnas_notas = ['N1', 'N2', 'N3', 'N4']
                notas = [str(row[c]).strip() for c in columnas_notas if c in row and pd.notna(row[c]) and str(row[c]).lower() != 'nan']
                st.write(f"**Notas:** {' - '.join(notas)}") #

                # INTERVALOS
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                
                # Int_TRAD ahora que la columna está corregida en el Excel
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}") #
                
                st.write("---")
                st.subheader("Posiciones")
                
                # IMÁGENES
                imgs = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]) and str(row[col]) not in ["0", "nan", ""]:
                        file = str(row[col]).split('/')[-1]
                        imgs.append(f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{file}")

                if imgs:
                    cols = st.columns(len(imgs))
                    for idx, url in enumerate(imgs):
                        with cols[idx]:
                            st.image(url, width=110) #
                            st.caption(f"P{idx+1}")
    else:
        st.info("Configura tu acorde en el menú de la izquierda y presiona 'Mostrar acordes'.")

else:
    st.error("No se pudo cargar la base de datos.")
