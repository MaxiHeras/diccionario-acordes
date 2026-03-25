import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS mejorados para los botones de notas
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    div.stDownloadButton > button { width: 100% !important; border: 1px solid #ff4b4b; }
    .copy-btn {
        width: 100%; cursor: pointer; background-color: #f0f2f6;
        border: 1px solid #dcdfe3; padding: 8px; border-radius: 5px;
        font-size: 14px; transition: 0.3s;
    }
    .copy-btn:hover { background-color: #e0e2e6; }
    .chord-img-web { width: 150px; height: auto; display: block; margin: 0 auto; }
    
    /* Estilo para los botones de notas tipo toggle */
    .stButton > button { margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqacv.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={APP_URL}"
GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

# Callbacks
def seleccionar_todo(opciones): st.session_state.seleccionados = opciones
def limpiar_todo(): st.session_state.seleccionados = []

def toggle_nota(nota):
    if "notas_inversas" not in st.session_state:
        st.session_state.notas_inversas = set()
    if nota in st.session_state.notas_inversas:
        st.session_state.notas_inversas.remove(nota)
    else:
        st.session_state.notas_inversas.add(nota)

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
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(60, 60, 60)
        notas_str = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
        pdf.write(5, f"Notas: {' - '.join(notas_str)}\n")
        pdf.write(5, f"Intervalos IVAN: {str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.write(5, f"Intervalos TRAD: {str(row.get('Int_TRAD', 'N/A'))}\n")
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
                    pdf.set_xy(pos_x, pos_y + DIAG_H + 1)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(DIAG_W, 5, f"P{i}", align='C')
                    count += 1
                except: continue
    return pdf.output()

df = load()
if df is not None:
    orden_notas_musicales = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    
    with st.sidebar:
        modo = st.radio("Modo de uso:", ["Diccionario 📖", "Identificador 🔍"])
        st.write("---")

        if modo == "Diccionario 📖":
            r_list = [n for n in orden_notas_musicales if n in df['Raiz'].unique()]
            raiz_sel = st.selectbox("Nota Raíz:", r_list)
            df_raiz = df[df['Raiz'] == raiz_sel]
            opciones = [t for t in df_raiz['Naturaleza'].unique()]
            
            if "ultima_raiz" not in st.session_state or st.session_state.ultima_raiz != raiz_sel:
                st.session_state.ultima_raiz = raiz_sel
                st.session_state.seleccionados = opciones

            nat_sel = st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            c1.button("Todo", on_click=seleccionar_todo, args=(opciones,), use_container_width=True)
            c2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
        
        else:
            st.header("🔍 Identificar Acorde")
            st.info("Toca las notas que estás presionando:")
            
            if "notas_inversas" not in st.session_state:
                st.session_state.notas_inversas = set()

            # Botonera de notas (3 filas de 4 o 4 de 3 para celular)
            cols_notas = st.columns(4)
            for idx, n in enumerate(orden_notas_musicales):
                with cols_notas[idx % 4]:
                    is_active = n in st.session_state.notas_inversas
                    style = "primary" if is_active else "secondary"
                    if st.button(n, key=f"btn_{n}", type=style, use_container_width=True):
                        toggle_nota(n)
                        st.rerun()
            
            if st.button("Resetear notas", use_container_width=True):
                st.session_state.notas_inversas = set()
                st.rerun()

        st.write("---")
        st.image(URL_QR, caption="App Online", width=120)
        copy_html = f"""<button class="copy-btn" onclick="navigator.clipboard.writeText('{APP_URL}')">📋 Copiar enlace</button>"""
        st.components.v1.html(copy_html, height=45)

    # --- VISUALIZACIÓN ---
    if modo == "Diccionario 📖":
        if nat_sel:
            tabs = st.tabs(nat_sel)
            for i, tab in enumerate(tabs):
                with tab:
                    tipo_actual = nat_sel[i]
                    row = df_raiz[df_raiz['Naturaleza'] == tipo_actual].iloc[0]
                    st.markdown(f"### {row['Raiz']} {row['Naturaleza']}")
                    lista_n = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
                    st.write(f"**Notas:** {' - '.join(lista_n)}")
                    col1, col2 = st.columns(2)
                    col1.success(f"**IVAN:** {row.get('Int_IVAN','')}")
                    col2.info(f"**TRAD:** {row.get('Int_TRAD','')}")
                    h_items = ""
                    for j in range(1, 10):
                        v = str(row.get(f'Diagrama{j}', 'nan'))
                        if v.lower().endswith('.png'):
                            url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                            h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
            
            if st.button("📥 Generar PDF"):
                pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(nat_sel)])
                st.download_button("Descargar PDF", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf")

    else: # MODO IDENTIFICADOR
        seleccion = st.session_state.notas_inversas
        if seleccion:
            st.write(f"**Notas seleccionadas:** {' - '.join(sorted(list(seleccion)))}")
            
            def coincide(row):
                notas_row = {str(row[n]) for n in ['N1', 'N2', 'N3', 'N4'] if pd.notna(row[n])}
                return seleccion == notas_row
            
            res = df[df.apply(coincide, axis=1)]
            
            if not res.empty:
                st.success(f"Se encontraron {len(res)} coincidencias:")
                for _, row in res.iterrows():
                    with st.expander(f"✅ {row['Raiz']} {row['Naturaleza']}", expanded=True):
                        col1, col2 = st.columns(2)
                        col1.success(f"**IVAN:** {row.get('Int_IVAN','')}")
                        col2.info(f"**TRAD:** {row.get('Int_TRAD','')}")
                        h_items = ""
                        for j in range(1, 10):
                            v = str(row.get(f'Diagrama{j}', 'nan'))
                            if v.lower().endswith('.png'):
                                url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                                h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
                        st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
            else:
                st.warning("No hay acordes con ese grupo exacto de notas en tu base de datos.")
        else:
            st.write("Selecciona notas en el panel izquierdo para empezar.")
