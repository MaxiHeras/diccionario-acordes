import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS - CORREGIDO PARA MODO OSCURO Y TAMAÑO WEB
st.markdown("""
    <style>
    /* Inversión de colores para modo oscuro aplicada a la nueva clase */
    @media (prefers-color-scheme: dark) { 
        .chord-img-web { filter: invert(1) hue-rotate(180deg); } 
    }
    
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    
    div.stDownloadButton > button {
        width: 100% !important;
        border: 1px solid #ff4b4b;
    }
    
    .copy-btn {
        width: 100%;
        cursor: pointer;
        background-color: #f0f2f6;
        border: 1px solid #dcdfe3;
        padding: 8px;
        border-radius: 5px;
        font-size: 14px;
        transition: 0.3s;
    }
    .copy-btn:hover { background-color: #e0e2e6; }
    
    .chord-img-web {
        width: 150px; 
        height: auto;
        display: block;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqxacv.streamlit.app/"
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

def seleccionar_todo(opciones):
    st.session_state.seleccionados = opciones

def limpiar_todo():
    st.session_state.seleccionados = []

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
        notas = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
        pdf.write(5, f"Notas: {' - '.join(notas)}\n")
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
                    if pos_y + DIAG_H > 265:
                        pdf.add_page()
                        y_curr, pos_y, count = 20, 20, 0
                    pdf.image(BytesIO(img_data), x=pos_x, y=pos_y, w=DIAG_W, h=DIAG_H)
                    pdf.set_xy(pos_x, pos_y + DIAG_H + 1)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(DIAG_W, 5, f"P{i}", align='C')
                    count += 1
                except: continue
    return pdf.output()

df = load()
if df is not None:
    orden_notas = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    orden_tipos = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        r_list = [n for n in orden_notas if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_raiz = df[df['Raiz'] == raiz_sel]
        opciones = [t for t in orden_tipos if t in df_raiz['Naturaleza'].unique()]
        
        if "ultima_raiz" not in st.session_state or st.session_state.ultima_raiz != raiz_sel:
            st.session_state.ultima_raiz = raiz_sel
            st.session_state.seleccionados = opciones

        nat_sel = st.multiselect("Tipo:", opciones, key="seleccionados")

        c1, c2 = st.columns(2)
        c1.button("Todo", use_container_width=True, on_click=seleccionar_todo, args=(opciones,))
        c2.button("Limpiar", use_container_width=True, on_click=limpiar_todo)
        
        st.write("---")
        if st.button("📥 Generar PDF", use_container_width=True):
            if not nat_sel:
                st.warning("Selecciona al menos un tipo.")
            else:
                with st.spinner("Generando..."):
                    pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(nat_sel)])
                    st.download_button("🔥 Descargar", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf", mime="application/pdf", use_container_width=True)

        st.write("---")
        st.image(URL_QR, caption="App Online", width=150)
        copy_html = f"""<button class="copy-btn" onclick="navigator.clipboard.writeText('{APP_URL}')">📋 Copiar enlace</button>"""
        st.components.v1.html(copy_html, height=50)

    if nat_sel:
        for _, row in df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=False):
                col1, col2 = st.columns(2)
                col1.success(f"**IVAN:** {row.get('Int_IVAN','')}")
                col2.info(f"**TRAD:** {row.get('Int_TRAD','')}")
                
                h_items = ""
                for i in range(1, 10):
                    v = str(row.get(f'Diagrama{i}', 'nan'))
                    if v.lower().endswith('.png'):
                        url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                        h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
