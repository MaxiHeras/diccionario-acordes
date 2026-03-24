import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS para Modo Oscuro y Galería
st.markdown("""
<style>
@media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
.scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
.chord-item { flex: 0 0 auto; text-align: center; }
</style>
""", unsafe_allow_html=True)

URL_DATA = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load_and_clean():
    try:
        df = pd.read_csv(URL_DATA)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_and_clean()

if df is not None:
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden_m = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in orden_m if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.write("---")
        st.image(URL_QR, caption="Compartir App", width=210)
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()
            else: st.warning("Elegí un acorde")

    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_f = df_r[df_r['Naturaleza'].isin(nat_sel)]
        abierto = len(nat_sel) == 1
        
        for _, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=abierto):
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(ns)}")
                
                st.write("---")
                st.subheader("Posiciones")

                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', '')).strip().lower()
                    # FILTRO CRÍTICO: Solo si termina en extensión de imagen y no es basura
                    if val.endswith(('.png', '.jpg', '.jpeg')) and val not in ['nan', '0', 'none']:
                        f = val.split('/')[-1]
                        url_img = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{f}"
                        # El 'onerror' es el último recurso: si la imagen falla, oculta el contenedor
                        h_items += f'<div class="chord-item" id="p{i}_{row.name}"><img src="{url_img}" class="chord-img" width="115" onerror="document.getElementById(\'p{i}_{row.name}\').style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas disponibles")
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("Error al conectar con el Excel.")
