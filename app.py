import streamlit as st
import pandas as pd

# 1. ESTADO Y CONFIGURACIÓN
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# --- CSS PARA MODO OSCURO (Invierte colores de diagramas) ---
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) {
        .chord-img { filter: invert(1) hue-rotate(180deg); }
    }
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
    # 2. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        r_sel = st.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
        df_r = df[df['Raiz'] == r_sel]
        n_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.image(QR, caption="Compartir App", width=210)
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
                # NOTAS
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower()!='nan' and str(row[c])!='']
                st.write(f"**Notas:** {' - '.join(ns)}")

                # INTERVALOS
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")

                # GALERÍA HORIZONTAL OPTIMIZADA
                imgs = []
                for i in range(1, 10):
                    c = f'Diagrama{i}'
                    val = str(row.get(c, '0')).strip().lower()
                    # FILTRO ESTRICTO: Solo agrega si hay un nombre de archivo real
                    if pd.notna(row.get(c)) and val not in ["0", "nan", "", "none"]:
                        f = str(row[c]).split('/')[-1]
                        url = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{f}"
                        imgs.append(url)

                if imgs:
                    h_items = "".join([f'<div class="chord-item"><img src="{u}" class="chord-img" width="115"><p style="font-size:12px;color:gray;">P{i+1}</p></div>' for i, u in enumerate(imgs)])
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("Error al conectar con el Excel.")
