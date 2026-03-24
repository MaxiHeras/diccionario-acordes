import streamlit as st
import pandas as pd

# 1. MANEJO DE ESTADO Y CONFIGURACIÓN (Debe ir al principio)
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
        
        # ESPACIADOR PARA EMPUJAR EL BOTÓN AL FONDO
        # En Streamlit esto crea un espacio flexible
        for _ in range(15): 
            st.write("") 

        # BOTÓN AL FINAL DE LA BARRA
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sidebar_state = "collapsed"
                st.rerun()
            else:
                st.warning("Selecciona un tipo.")

    # 3. RESULTADOS
    if nat_sel:
        # Botón pequeño en la parte superior para volver a filtrar sin abrir la sidebar manualmente
        if st.session_state.sidebar_state == "collapsed":
            if st.button("⬅️ Cambiar Acorde"):
                st.session_state.sidebar_state = "expanded"
                st.rerun()

        df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                
                # NOTAS CON SEPARADOR " - "
                columnas_notas = ['N1', 'N2', 'N3', 'N4']
                notas = [str(row[c]).strip() for c in columnas_notas if c in row and pd.notna(row[c]) and str(row[c]).lower() != 'nan']
                st.write(f"**Notas:** {' - '.join(notas)}")

                # INTERVALOS
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")
                
                # IMÁGENES
                imgs = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]) and str(row[col
