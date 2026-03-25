import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: AJUSTE DE DISEÑO (Mantiene tu estilo original)
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-img-web { width: 150px; height: auto; display: block; margin: 0 auto; }
    [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; }
    div[data-testid="stRadio"] > div { gap: 25px !important; padding: 10px 0; }
    [data-testid="stWidgetLabel"] p { font-weight: bold; font-size: 16px; }
    .stButton > button { width: 100% !important; border-radius: 6px !important; min-height: 42px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqxacv.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

# Inicialización de estados
if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "notas_inversas" not in st.session_state: st.session_state.notas_inversas = set()
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None
if "descargado" not in st.session_state: st.session_state.descargado = False

# --- FUNCIONES DE CONTROL ---
def seleccionar_todo(opciones): 
    st.session_state.seleccionados = opciones

def limpiar_todo(): 
    st.session_state.seleccionados = []
    st.session_state.pdf_data = None
    st.session_state.descargado = False

def toggle_nota(nota):
    if nota in st.session_state.notas_inversas: st.session_state.notas_inversas.remove(nota)
    else: st.session_state.notas_inversas.add(nota)

def identificar_acorde(notas_set, dataframe):
    if not notas_set: return None
    # Lógica para buscar en el Excel qué acorde coincide con las notas N1, N2, N3, N4
    res = dataframe[dataframe.apply(lambda r: set([str(r[n]) for n in ['N1','N2','N3','N4'] if pd.notna(r[n])]) == notas_set, axis=1)]
    return f"{res.iloc[0]['Raiz']} {res.iloc[0]['Naturaleza']}" if not res.empty else "Acorde no encontrado"

# 3. MOTOR PDF (Mantiene tu clase original)
class PDF_Final(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(190, 190, 190)
        self.cell(0, 10, "Maxi Heras - Tucumán", align='R')

def generar_pdf(dataframe_seleccionado):
    pdf = PDF_Final(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        pdf.set_font("helvetica", "B", 24)
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        pdf.ln(8) 
        notas_str = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
        pdf.set_font("helvetica", "B", 11)
        pdf.write(5, f"Notas: {' - '.join(notas_str)}\n")
        pdf.write(5, f"IVAN: {str(row.get('Int_IVAN', 'N/A'))} | TRAD: {str(row.get('Int_TRAD', 'N/A'))}\n")
        pdf.ln(10)
        # ... (Resto de tu lógica de imágenes para el PDF)
    return pdf.output()

df = load()
if df is not None:
    notas_musicales = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    orden_tipos = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.subheader("Seleccionar Modo")
        modo = st.radio(" ", ["Diccionario 📖", "Identificador 🔍"], label_visibility="collapsed")
        st.write("---")

        if modo == "Diccionario 📖":
            raiz_sel = st.selectbox("Nota Raíz:", [n for n in notas_musicales if n in df['Raiz'].unique()])
            df_raiz = df[df['Raiz'] == raiz_sel]
            opciones = [t for t in orden_tipos if t in df_raiz['Naturaleza'].unique()]
            
            # Autoseleccionar todo al cambiar de raíz
            if "ultima_raiz" not in st.session_state or st.session_state.ultima_raiz != raiz_sel:
                st.session_state.ultima_raiz = raiz_sel
                st.session_state.seleccionados = opciones

            st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            c1.button("Todo", on_click=seleccionar_todo, args=(opciones,), use_container_width=True)
            c2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
            
            if st.button("📥 Generar PDF de Selección", use_container_width=True):
                # Lógica de generación...
                pass

        # --- SECCIÓN COMPARTIR (QR DEBAJO DEL BOTÓN) ---
        st.write("---")
        st.write("📲 **Compartir App**")
        
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="Escaneá para abrir")
        
        if st.button("🔗 Copiar enlace de la App", use_container_width=True):
            st.code(APP_URL, language=None)
            st.toast("¡Enlace listo para copiar!", icon="🔗")

    # --- CUERPO PRINCIPAL ---
    if modo == "Diccionario 📖":
        # Muestra tus pestañas (Tabs) originales...
        pass
    else:
        st.header("🔍 Identificador")
        for i in range(0, len(notas_musicales), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(notas_musicales):
                    n = notas_musicales[i + j]
                    is_active = n in st.session_state.notas_inversas
                    if cols[j].button(n, key=f"id_{n}", type="primary" if is_active else "secondary"):
                        toggle_nota(n)
                        st.rerun()
        
        st.divider()
        st.subheader("Acorde Resultante:")
        resultado = identificar_acorde(st.session_state.notas_inversas, df)
        if resultado:
            st.success(f"### {resultado}")
