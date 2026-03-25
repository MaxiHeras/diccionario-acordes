import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: AJUSTE DE DISEÑO Y FORZADO DE 3 COLUMNAS EN SIDEBAR
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-img-web { width: 150px; height: auto; display: block; margin: 0 auto; }
    
    /* SUBE EL CONTENIDO DE LA BARRA LATERAL */
    [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; }

    /* FORZAR 3 COLUMNAS EN EL SIDEBAR (GRILLA) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 5px !important;
    }
    [data-testid="stSidebar"] [data-testid="column"] {
        width: 32% !important;
        flex: 1 1 32% !important;
        min-width: 32% !important;
    }

    /* ESTILO DE BOTONES */
    .stButton > button {
        width: 100% !important;
        padding: 5px 2px !important;
        font-size: 13px !important;
        min-height: 42px !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
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

# Inicialización de estados
if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "notas_inversas" not in st.session_state: st.session_state.notas_inversas = set()
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None
if "descargado" not in st.session_state: st.session_state.descargado = False

def seleccionar_todo(opciones): st.session_state.seleccionados = opciones
def limpiar_todo(): 
    st.session_state.seleccionados = []
    st.session_state.pdf_data = None
    st.session_state.descargado = False

def toggle_nota(nota):
    if nota in st.session_state.notas_inversas: st.session_state.notas_inversas.remove(nota)
    else: st.session_state.notas_inversas.add(nota)

def confirmar_descarga(): st.session_state.descargado = True

# 3. MOTOR PDF
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
        # Lógica de diagramas...
        X_START, GAP_X, COLS, DIAG_W, DIAG_H = 15, 5, 4, 38, 45
        y_curr, count = pdf.get_y(), 0
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                url_img = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{val.split('/')[-1]}"
                try:
                    img_data = requests.get(url_img, timeout=5).content
                    col, fila = count % COLS, count // COLS
                    pos_x, pos_y = X_START + (col * (DIAG_W + GAP_X)), y_curr + (fila * (DIAG_H + 10))
                    pdf.image(BytesIO(img_data), x=pos_x, y=pos_y, w=DIAG_W, h=DIAG_H)
                    count += 1
                except: continue
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
            
            # Autoseleccionar todo al cambiar raíz
            if "u_raiz" not in st.session_state or st.session_state.u_raiz != raiz_sel:
                st.session_state.u_raiz = raiz_sel
                st.session_state.seleccionados = opciones
                st.session_state.pdf_data = None
                st.session_state.descargado = False

            st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            c1.button("Todo", on_click=seleccionar_todo, args=(opciones,), use_container_width=True)
            c2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
            
            st.write("")
            placeholder = st.empty()
            if st.session_state.descargado: placeholder.success("✅ ¡Listo, guardado!")
            elif st.session_state.pdf_data: placeholder.info("✅ ¡Listo para guardar!")

            if st.button("📥 Generar PDF de Selección", use_container_width=True):
                df_para_pdf = df_raiz[df_raiz['Naturaleza'].isin(st.session_state.seleccionados)]
                if not df_para_pdf.empty:
                    placeholder.markdown("⏳ *Preparando PDF...*")
                    st.session_state.pdf_data = generar_pdf(df_para_pdf)
                    st.session_state.descargado = False
                    st.rerun()
                else: st.warning("Seleccioná acordes primero.")

            if st.session_state.pdf_data:
                st.download_button(label="💾 GUARDAR ARCHIVO", data=bytes(st.session_state.pdf_data), file_name=f"Acordes_{raiz_sel}.pdf", mime="application/pdf", use_container_width=True, type="primary", on_click=confirmar_descarga)

        else:
            # GRILLA DE 3 BOTONES EN SIDEBAR (CORREGIDO)
            st.write("### Identificador")
            for i in range(0, len(notas_musicales), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < len(notas_musicales):
                        n = notas_musicales[idx]
                        active = n in st.session_state.notas_inversas
                        with cols[j]:
                            if st.button(n, key=f"side_{n}", type="primary" if active else "secondary"):
                                toggle_nota(n); st.rerun()
            
            st.write("")
            if st.button("🗑️ Borrar Notas", use_container_width=True):
                st.session_state.notas_inversas = set(); st.rerun()

        # SECCIÓN COMPARTIR (BOTÓN DEBAJO DEL QR)
        st.write("---")
        st.write("📲 **Compartir App**")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="Escaneá para abrir")
        if st.button("🔗 Copiar enlace"):
            st.code(APP_URL, language=None)
            st.toast("¡Enlace listo para copiar!", icon="🔗")

    # 4. CUERPO PRINCIPAL
    if modo == "Identificador 🔍":
        st.header("Acorde Resultante:")
        notas_actuales = st.session_state.notas_inversas
        res = df[df.apply(lambda r: set([str(r[n]) for n in ['N1','N2','N3','N4'] if pd.notna(r[n])]) == notas_actuales, axis=1)]
        if notas_actuales:
            if not res.empty: st.success(f"### {res.iloc[0]['Raiz']} {res.iloc[0]['Naturaleza']}")
            else: st.warning("Acorde no identificado")
        else: st.info("Seleccioná notas en la barra lateral.")
    else:
        st.header("📖 Diccionario")
        if st.session_state.seleccionados:
            tabs = st.tabs([t for t in orden_tipos if t in st.session_state.seleccionados])
            # ... (Resto de tu lógica de visualización de pestañas igual que antes)
