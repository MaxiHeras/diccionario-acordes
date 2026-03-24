import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN E INTERFAZ
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS para Modo Oscuro y Galería
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS Y QR ---
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

if df is not None:
    # 2. MENÚ LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        notas_df = df['Raiz'].unique()
        r_list = [n for n in orden if n in notas_df]
        
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        n_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.write("---")
        st.image(QR, caption="Compartir App", width=220)
        for _ in range(5): st.write("") 
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if n_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()
            else: st.warning("Elegí un acorde")

    # 3. RESULTADOS
    if n_sel:
        st.session_state.sb_state = "collapsed"
        for _, row in df_r[df_r['Naturaleza'].isin(n_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Notas e Intervalos
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower()!='nan' and str(row[c])!='']
                st.write(f"**Notas:** {' - '.join(ns)}")
                
                if pd.notna(row.get('Int_IVAN')): st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                if pd.notna(row.get('Int_TRAD')): st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")

                # Galería que solo muestra imágenes que cargan
                h_items = ""
                for i in range(1, 10):
                    c = f'Diagrama{i}'
                    val = str(row.get(c, '0')).strip()
                    if val not in ["0", "nan", ""]:
                        fname = val.split('/')[-1]
                        # URL corregida basada en tu estructura de GitHub
                        url = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{fname}"
                        h_items += f'<div class="chord-item"><img src="{url}" class="chord-img" width="115" onerror="this.parentElement.style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No se encontraron imágenes para este acorde.")
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("Error al conectar con el Excel.")
