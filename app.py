import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS AGRESIVO PARA FORZAR COLUMNAS EN CELULAR
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    div.stDownloadButton > button { width: 100% !important; border: 1px solid #ff4b4b; }
    .chord-img-web { width: 150px; height: auto; display: block; margin: 0 auto; }
    
    /* ESTE BLOQUE FUERZA LAS 3 COLUMNAS EN EL CELULAR */
    [data-testid="column"] {
        width: 33.33% !important;
        flex: 0 0 33.33% !important;
        min-width: 33.33% !important;
    }
    
    /* Ajuste de botones para que no se encimen */
    .stButton > button {
        margin-bottom: 2px !important;
        padding: 5px 2px !important;
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
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

def seleccionar_todo(opciones): st.session_state.seleccionados = opciones
def limpiar_todo(): st.session_state.seleccionados = []
def toggle_nota(nota):
    if nota in st.session_state.notas_inversas: st.session_state.notas_inversas.remove(nota)
    else: st.session_state.notas_inversas.add(nota)

# Clase PDF (Mantenemos igual para tus descargas)
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
            
            nat_sel = st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            c1.button("Todo", on_click=seleccionar_todo, args=(opciones,), use_container_width=True)
            c2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
        
        else:
            st.header("🔍 Identificador")
            # Forzamos 3 columnas fijas con el CSS de arriba
            for i in range(0, len(notas_musicales), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(notas_musicales):
                        n = notas_musicales[i + j]
                        activo = n in st.session_state.notas_inversas
                        if cols[j].button(n, key=f"inv_{n}", use_container_width=True, type="primary" if activo else "secondary"):
                            toggle_nota(n)
                            st.rerun()
            
            st.write("---")
            if st.button("Resetear notas", use_container_width=True):
                st.session_state.notas_inversas = set()
                st.rerun()

    # --- VISUALIZACIÓN ---
    if modo == "Diccionario 📖":
        if st.session_state.seleccionados:
            tabs_ordenados = [t for t in orden_tipos if t in st.session_state.seleccionados]
            tabs = st.tabs(tabs_ordenados)
            for i, tab in enumerate(tabs):
                with tab:
                    tipo_actual = tabs_ordenados[i]
                    res_filtro = df_raiz[df_raiz['Naturaleza'] == tipo_actual]
                    if not res_filtro.empty:
                        row = res_filtro.iloc[0]
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
            
            if st.button("📥 Descargar PDF"):
                pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(st.session_state.seleccionados)])
                st.download_button("Click aquí para descargar", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf")

    else: # MODO IDENTIFICADOR
        seleccion = st.session_state.notas_inversas
        if seleccion:
            st.write(f"**Notas:** {' - '.join(sorted(list(seleccion)))}")
            def coincide(row):
                notas_row = {str(row[n]) for n in ['N1', 'N2', 'N3', 'N4'] if pd.notna(row[n])}
                return seleccion == notas_row
            res = df[df.apply(coincide, axis=1)]
            if not res.empty:
                for _, row in res.iterrows():
                    with st.expander(f"✅ {row['Raiz']} {row['Naturaleza']}", expanded=True):
                        # Aquí NO usamos columnas para los resultados, para que se vea bien en celular
                        st.success(f"**IVAN:** {row.get('Int_IVAN','')}")
                        st.info(f"**TRAD:** {row.get('Int_TRAD','')}")
                        h_items = ""
                        for j in range(1, 10):
                            v = str(row.get(f'Diagrama{j}', 'nan'))
                            if v.lower().endswith('.png'):
                                url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                                h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
                        st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
            else: st.warning("No se encontró coincidencia exacta.")
