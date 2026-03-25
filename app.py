import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: VELOCIDAD Y DISEÑO MÓVIL
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-img-web { width: 150px; height: auto; display: block; margin: 0 auto; }
    
    [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: wrap !important; gap: 4px !important; }
    [data-testid="column"] { width: 31% !important; flex: 1 1 31% !important; min-width: 31% !important; }

    .stButton > button {
        width: 100% !important;
        padding: 5px 2px !important;
        font-size: 13px !important;
        min-height: 42px !important;
        border-radius: 6px !important;
        transition: none !important; 
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

if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "notas_inversas" not in st.session_state: st.session_state.notas_inversas = set()
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None

def seleccionar_todo(opciones): st.session_state.seleccionados = opciones
def limpiar_todo(): st.session_state.seleccionados = []
def toggle_nota(nota):
    if nota in st.session_state.notas_inversas: st.session_state.notas_inversas.remove(nota)
    else: st.session_state.notas_inversas.add(nota)

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
        modo = st.radio("Modo:", ["Diccionario 📖", "Identificador 🔍"])
        st.write("---")

        if modo == "Diccionario 📖":
            raiz_sel = st.selectbox("Nota Raíz:", [n for n in notas_musicales if n in df['Raiz'].unique()])
            df_raiz = df[df['Raiz'] == raiz_sel]
            opciones = [t for t in orden_tipos if t in df_raiz['Naturaleza'].unique()]
            
            if "ultima_raiz_control" not in st.session_state or st.session_state.ultima_raiz_control != raiz_sel:
                st.session_state.ultima_raiz_control = raiz_sel
                st.session_state.seleccionados = opciones
                st.session_state.pdf_data = None # Resetear PDF al cambiar de nota

            st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            c1.button("Todo", on_click=seleccionar_todo, args=(opciones,), use_container_width=True)
            c2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
            
            st.write("")
            # PROCESO DE PDF SIN RECUADROS
            placeholder = st.empty()
            if st.button("📥 Generar PDF de Selección", use_container_width=True):
                df_para_pdf = df_raiz[df_raiz['Naturaleza'].isin(st.session_state.seleccionados)]
                if not df_para_pdf.empty:
                    placeholder.markdown("⏳ *Preparando PDF...*")
                    st.session_state.pdf_data = generar_pdf(df_para_pdf)
                    placeholder.markdown("✅ *¡Listo!*")
                else:
                    st.warning("Seleccioná acordes primero.")

            # BOTÓN DE DESCARGA (Fuera del proceso para que sea persistente)
            if st.session_state.pdf_data:
                st.download_button(
                    label="💾 Guardar Archivo",
                    data=bytes(st.session_state.pdf_data),
                    file_name=f"Acordes_{raiz_sel}.pdf",
                    use_container_width=True,
                    type="primary"
                )

            st.write("---")
            st.write("📲 **Compartir App**")
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
            st.image(qr_url)
            st.code(APP_URL, language=None)
        
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
            st.write("")
            if st.button("🗑️ Borrar Notas", use_container_width=True):
                st.session_state.notas_inversas = set()
                st.rerun()

    # --- RENDERIZADO PRINCIPAL ---
    if modo == "Diccionario 📖":
        if st.session_state.seleccionados:
            tabs_ordenados = [t for t in orden_tipos if t in st.session_state.seleccionados]
            tabs = st.tabs(tabs_ordenados)
            for i, tab in enumerate(tabs):
                with tab:
                    tipo_actual = tabs_ordenados[i]
                    row = df_raiz[df_raiz['Naturaleza'] == tipo_actual].iloc[0]
                    st.markdown(f"### {row['Raiz']} {row['Naturaleza']}")
                    lista_n = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
                    st.write(f"**Notas:** {' - '.join(lista_n)}")
                    st.info(f"**IVAN:** {row.get('Int_IVAN','')} | **TRAD:** {row.get('Int_TRAD','')}")
                    h_items = ""
                    for j in range(1, 10):
                        v = str(row.get(f'Diagrama{j}', 'nan'))
                        if v.lower().endswith('.png'):
                            url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                            h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)

    else: # MODO IDENTIFICADOR
        seleccion = st.session_state.notas_inversas
        if seleccion:
            res = df[df.apply(lambda r: seleccion == {str(r[n]) for n in ['N1','N2','N3','N4'] if pd.notna(r[n])}, axis=1)]
            if not res.empty:
                for _, row in res.iterrows():
                    with st.expander(f"✅ {row['Raiz']} {row['Naturaleza']}", expanded=True):
                        st.info(f"**IVAN:** {row.get('Int_IVAN','')} | **TRAD:** {row.get('Int_TRAD','')}")
                        h_items = ""
                        for j in range(1, 10):
                            v = str(row.get(f'Diagrama{j}', 'nan'))
                            if v.lower().endswith('.png'):
                                url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                                h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
                        st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
