import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILO
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS Y URLS
APP_URL = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={APP_URL}"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())
        
        st.write("---")
        st.image(URL_QR, caption="Escanear para compartir", width=180)
        st.caption(f"**Enlace de la App:**")
        st.code(APP_URL, language=None)
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()

    # 4. RESULTADOS
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        # Determinar si las pestañas deben estar contraídas (si hay más de un tipo seleccionado)
        esta_expandido = False if len(nat_sel) > 1 else True
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=esta_expandido):
                # Sección de Notas
                notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(notas)}")
                
                # Sección de Intervalos (Restaurada)
                intervalos = [str(row[c]).strip() for c in ['I1','I2','I3','I4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']]
                if intervalos:
                    st.write(f"**Intervalos:** {' - '.join(intervalos)}")
                
                st.write("---")
                
                # GALERÍA HORIZONTAL
                h_items = ""
                GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if val.lower().endswith('.png'):
                        nombre_archivo = val.split('/')[-1]
                        url_img = f"{GITHUB_BASE}/{row['Naturaleza']}/{nombre_archivo}"
                        div_id = f"pos_{idx}_{i}"
                        h_items += f'<div class="chord-item" id="{div_id}"><img src="{url_img}" class="chord-img" width="110" onerror="document.getElementById(\'{div_id}\').style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas disponibles.")
    else:
        st.info("Elegí un acorde en el menú lateral.")
else:
    st.error("Error al cargar el Excel.")
