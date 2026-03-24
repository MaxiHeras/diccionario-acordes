import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Diccionario Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# Filtro visual para modo oscuro (opcional)
st.markdown("<style>@media (prefers-color-scheme: dark) { img { filter: invert(1) hue-rotate(180deg); } }</style>", unsafe_allow_html=True)

URL_DATA = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_DATA)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

if df is not None:
    # 2. MENÚ LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        notas_disp = [n for n in orden if n in df['Raiz'].unique()]
        
        raiz = st.selectbox("Nota Raíz:", notas_disp)
        tipos = st.multiselect("Tipo:", options=df[df['Raiz']==raiz]['Naturaleza'].unique())
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if tipos:
                st.session_state.sb_state = "collapsed"
                st.rerun()

    # 3. PANTALLA PRINCIPAL
    if tipos:
        st.session_state.sb_state = "collapsed"
        df_f = df[(df['Raiz'] == raiz) & (df['Naturaleza'].isin(tipos))]
        
        # Si hay varios, aparecen cerrados por comodidad
        abierto = len(tipos) == 1
        
        for _, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=abierto):
                # Notas
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','0','']]
                st.write(f"**Notas:** {' - '.join(ns)}")
                
                st.write("---")
                st.subheader("Posiciones")

                # USAMOS COLUMNAS NATIVAS (Evita que el código se vea como texto)
                cols = st.columns(5) # Hasta 5 posiciones visibles
                idx_col = 0
                
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', '')).strip()
                    # Solo intentamos cargar si el nombre del archivo es válido
                    if any(ext in val.lower() for ext in ['.png', '.jpg', '.jpeg']):
                        f = val.split('/')[-1]
                        url_img = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{f}"
                        
                        if idx_col < 5:
                            with cols[idx_col]:
                                st.image(url_img, caption=f"P{i}", use_container_width=True)
                                idx_col += 1
                
                if idx_col == 0:
                    st.warning("No se encontraron imágenes válidas. Revisa que en el Excel las celdas terminen en .png")
    else:
        st.info("Elegí un acorde en el menú de la izquierda.")
else:
    st.error("No se pudo conectar con el Excel.")
