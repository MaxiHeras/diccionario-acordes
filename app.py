import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: POSICIONAMIENTO, COLORES Y ESTILOS
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    div[data-testid="stRadio"] > div { gap: 20px; margin-top: 10px; }
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex !important; overflow-x: auto !important; gap: 15px !important; padding: 10px 0 !important; flex-wrap: nowrap !important; }
    .chord-diag-item { flex: 0 0 auto !important; width: 150px !important; text-align: center; }
    .chord-img-web { width: 100% !important; height: auto !important; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 5px !important; }
    [data-testid="stSidebar"] [data-testid="column"] { width: 32% !important; flex: 1 1 32% !important; min-width: 32% !important; }
    .stButton > button { width: 100% !important; padding: 5px 2px !important; font-size: 13px !important; min-height: 42px !important; border-radius: 6px !important; }
    
    /* Estilo para que el texto de la URL sea legible aunque esté deshabilitado */
    .stTextInput input:disabled {
        -webkit-text-fill-color: #31333F !important;
        opacity: 1 !important;
        cursor: text !important;
        background-color: #f0f2f6 !important;
    }
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

# Estados de sesión
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

def mostrar_detalle_acorde(row):
    st.markdown(f"### {row['Raiz']} {row['Naturaleza']}")
    lista_n = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
    st.write(f"**Notas:** {' - '.join(lista_n)}")
    c1, c2 = st.columns(2)
    with c1: st.success(f"**Int_IVAN:** {row.get('Int_IVAN','N/A')}") 
    with c2: st.info(f"**Int_TRAD:** {row.get('Int_TRAD','N/A')}")
    st.write("---")
    st.write("**Diagramas:**")
    h_items = ""
    for j in range(1, 10):
        v = str(row.get(f'Diagrama{j}', 'nan')).strip()
        if v.lower().endswith('.png'):
            nat_cod = urllib.parse.quote(str(row['Naturaleza']))
            url = f"{GITHUB_BASE}/{nat_cod}/{v.split('/')[-1]}"
            h_items += f'<div class="chord-diag-item"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
    if h_items: st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)

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
        pdf.set_font("helvetica", "B", 11); pdf.write(6, "Notas: "); pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{' - '.join([str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))])}\n")
        pdf.set_font("helvetica", "B", 11); pdf.write(6, "Int_IVAN: "); pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.set_font("helvetica", "B", 11); pdf.write(6, "Int_TRAD: "); pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{str(row.get('Int_TRAD', 'N/A'))}\n")
        pdf.ln(14) 
        X_START, GAP_X, GAP_Y, COLS, DIAG_W, DIAG_H = 15, 8, 12, 4, 38, 45
        y_grid_top = pdf.get_y()
        count = 0
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                nat_pdf = urllib.parse.quote(str(row['Naturaleza']))
                url_img = f"{GITHUB_BASE}/{nat_pdf}/{val.split('/')[-1]}"
                try:
                    img_data = requests.get(url_img, timeout=5).content
                    col, fila = count % COLS, count // COLS
                    pos_x = X_START + (col * (DIAG_W + GAP_X))
                    pos_y = y_grid_top + (fila * (DIAG_H + GAP_Y))
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
            if st.session_state.pdf_data:
                st.download_button("💾 GUARDAR ARCHIVO", bytes(st.session_state.pdf_data), f"Acordes_{raiz_sel}.pdf", "application/pdf", use_container_width=True, type="primary", on_click=lambda: st.session_state.update({"descargado": True}))
        else:
            st.write("### Identificador")
            for i in range(0, len(notas_musicales), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < len(notas_musicales):
                        n = notas_musicales[idx]
                        active = n in st.session_state.notas_inversas
                        with cols[j]:
                            if st.button(n, key=f"id_{n}", type="primary" if active else "secondary"):
                                toggle_nota(n); st.rerun()
            if st.button("🗑️ Borrar Notas", use_container_width=True):
                st.session_state.notas_inversas = set(); st.rerun()

        st.write("---")
        st.write("📲 **Compartir App**")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="Escaneá para abrir", width=180)
        
        # URL DE SOLO LECTURA (Sin iconos confusos, segura y fácil de seleccionar)
        st.text_input("Enlace de la app:", value=APP_URL, disabled=True)
        st.caption("Seleccioná la URL de arriba para copiarla.")

    # CUERPO PRINCIPAL
    if modo == "Diccionario 📖":
        st.header(f"📖 Diccionario: {raiz_sel}")
        tipos_visibles = [t for t in orden_tipos if t in st.session_state.seleccionados]
        if tipos_visibles:
            tabs = st.tabs(tipos_visibles)
            for i, tab in enumerate(tabs):
                with tab:
                    row = df_raiz[df_raiz['Naturaleza'] == tipos_visibles[i]].iloc[0]
                    mostrar_detalle_acorde(row)
        else: st.info("Seleccioná tipos en el sidebar.")
    else:
        st.header("🔍 Identificador de Acordes")
        notas_act = st.session_state.notas_inversas
        res = df[df.apply(lambda r: set([str(r[n]) for n in ['N1','N2','N3','N4'] if pd.notna(r[n])]) == notas_act, axis=1)]
        if notas_act:
            if not res.empty: mostrar_detalle_acorde(res.iloc[0])
            else: st.warning("Acorde no identificado.")
        else: st.info("Seleccioná notas en la barra lateral.")
