import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS para Modo Oscuro y Galería Horizontal
st.markdown("""
<style>
@media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
.scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
.chord-item { flex: 0 0 auto; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS (URLs completas en una sola línea para evitar errores de sintaxis)
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        # Limpieza de celdas vacías en diagramas
        for i in range(1, 10):
            col = f'Diagrama{i}'
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace({'nan': '0', 'None': '0', '': '0'})
        return df
    except: return None

df = load_data()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden_m = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in orden_m if n in df['Raiz'].unique()]
        
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.write("---")
        st.image(QR, caption="Compartir App", width=210)
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()
            else: st.warning("Elegí un acorde")

    # 4. RESULTADOS
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_f = df_r[df_r['Naturaleza'].isin(nat_sel)]
        
        # Pestañas contraídas si hay más de 1 acorde seleccionado
        abierto = len(nat_sel) == 1
        
        for _, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=abierto):
                # Notas
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','']]
                st.write(f"**Notas:** {' - '.join(ns)}")
                
                # Info
                if pd.notna(row.get('Int_IVAN')): st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                if pd.notna(row.get('Int_TRAD')): st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")

                # Galería Horizontal (Sin iconos rotos)
                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', '0'))
                    if val != '0':
                        f = val.split('/')[-1]
                        url_img = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{f}"
                        h_items += f'<div class="chord-item"><img src="{url_img}" class="chord-img" width="115" onerror="this.parentElement.style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else: st.warning("No hay diagramas")
    else: st.info("Configurá tu acorde en el menú.")
else: st.error("Error al conectar con el Excel.")
