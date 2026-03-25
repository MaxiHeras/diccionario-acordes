import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS original para mantener el diseño de botones y cuadrícula
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-img-web { width: 150px; height: auto; display: block; margin: 0 auto; }
    [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; }
    
    /* Diseño de la cuadrícula de botones en el sidebar */
    [data-testid="column"] { width: 31% !important; flex: 1 1 31% !important; min-width: 31% !important; }
    .stButton > button { width: 100% !important; padding: 5px 2px !important; font-size: 13px !important; border-radius: 6px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS Y ESTADOS
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqacv.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "notas_inversas" not in st.session_state: st.session_state.notas_inversas = set()

def toggle_nota(nota):
    if nota in st.session_state.notas_inversas: st.session_state.notas_inversas.remove(nota)
    else: st.session_state.notas_inversas.add(nota)

df = load()
if df is not None:
    notas_musicales = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    orden_tipos = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.subheader("Seleccionar Modo")
        modo = st.radio(" ", ["Diccionario 📖", "Identificador 🔍"], label_visibility="collapsed")
        st.write("---")

        if modo == "Diccionario 📖":
            raiz_sel = st.selectbox("Nota Raíz:", [n for n in notas_musicales if n in df['Raiz'].unique()])
            df_raiz = df[df['Raiz'] == raiz_sel]
            opciones = [t for t in orden_tipos if t in df_raiz['Naturaleza'].unique()]
            
            # Autoselección de tipos al cambiar nota
            if "u_raiz" not in st.session_state or st.session_state.u_raiz != raiz_sel:
                st.session_state.u_raiz = raiz_sel
                st.session_state.seleccionados = opciones

            st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            if c1.button("Todo"): st.session_state.seleccionados = opciones; st.rerun()
            if c2.button("Limpiar"): st.session_state.seleccionados = []; st.rerun()

        else:
            # GRILLA DE 3 BOTONES POR LÍNEA EN EL SIDEBAR
            st.write("### Identificador")
            for i in range(0, len(notas_musicales), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(notas_musicales):
                        n = notas_musicales[i + j]
                        is_active = n in st.session_state.notas_inversas
                        if cols[j].button(n, key=f"side_{n}", type="primary" if is_active else "secondary"):
                            toggle_nota(n)
                            st.rerun()
            
            if st.button("🗑️ Borrar Notas"):
                st.session_state.notas_inversas = set()
                st.rerun()

        # COMPARTIR APP (Al final del sidebar)
        st.write("---")
        st.write("📲 **Compartir App**")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="Escaneá para abrir")
        if st.button("🔗 Copiar enlace"):
            st.code(APP_URL, language=None)
            st.toast("¡Enlace listo para copiar!")

    # --- CUERPO PRINCIPAL ---
    if modo == "Identificador 🔍":
        st.header("Acorde Resultante:")
        # Lógica para identificar el acorde comparando el set de notas
        notas_actuales = st.session_state.notas_inversas
        res = df[df.apply(lambda r: set([str(r[n]) for n in ['N1','N2','N3','N4'] if pd.notna(r[n])]) == notas_actuales, axis=1)]
        
        if notas_actuales:
            if not res.empty:
                st.success(f"### {res.iloc[0]['Raiz']} {res.iloc[0]['Naturaleza']}")
            else:
                st.warning("Acorde no identificado")
        else:
            st.info("Selecciona notas en la barra lateral para identificar el acorde.")
    else:
        # Aquí va tu lógica original de Tabs para el Diccionario
        st.header("📖 Diccionario")
        # ... (resto de tu código de pestañas)
