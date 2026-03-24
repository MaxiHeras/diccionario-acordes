import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTADO
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS: Inversión para modo oscuro y contenedor de scroll horizontal
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

if df is not None:
    # 2. BARRA LATERAL CON ORDEN MUSICAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden_m = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        notas_df = df['Raiz'].unique()
        r_list = [n for n in orden_m if n in notas_df]
        
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.write("---")
        st.image(QR_URL, caption="Compartir App", width=220)
        for _ in range(5): st.write("") 
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()
            else: st.warning("Elegí un acorde")

    # 3. RESULTADOS
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        for _, row in df_r[df_r['Naturaleza'].isin(nat_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan', '']]
                st.write(f"**Notas:** {' - '.join(ns)}")
                
                if pd.notna(row.get('Int_IVAN')): st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                if pd.notna(row.get('Int_TRAD')): st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")

                h_items = ""
                for i in range(1, 10):
                    c = f'Diagrama{i}'
                    val = str(row.get(c, '0')).strip()
                    # Filtro estricto para evitar iconos rotos
                    if val not in ["0", "nan", "", "None"]:
                        fname = val.split('/')[-1]
                        url = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{fname}"
                        # 'onerror' elimina el elemento si la imagen falla al cargar
                        h_items += f'<div class="chord-item" onerror="this.style.display=\'none\';"><img src="{url}" class="chord-img" width="115" onerror="this.parentElement.style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas disponibles.")
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("Error al conectar con el Excel.")
