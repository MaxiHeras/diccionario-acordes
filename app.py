import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .notas-web { font-size: 20px; font-weight: bold; color: #31333F; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-gpblssuywitmaglkwvdqde.streamlit.app/"
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

# --- CLASE PDF CORREGIDA (Marca de agua sin hojas extra) ---
class PDF_Final(FPDF):
    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(190, 190, 190)
        # Imprimir marca de agua
        self.cell(0, 10, "Maxi Heras - Tucumán", align='R')

def generar_pdf(dataframe_seleccionado):
    pdf = PDF_Final(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        
        # TÍTULO
        pdf.set_font("helvetica", "B", 24)
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        pdf.ln(8) 
        
        # INFO
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(60, 60, 60)
        pdf.write(5, f"Notas: {str(row.get('N1',''))} - {str(row.get('N2',''))} - {str(row.get('N3',''))} - {str(row.get('N4',''))}\n")
        pdf.write(5, f"Intervalos IVAN: {str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.write(5, f"Intervalos TRAD: {str(row.get('Int_TRAD', 'N/A'))}\n")
        pdf.ln(10)

        # DIAGRAMAS
        X_START, GAP_X, COLS = 15, 5, 4
        DIAG_W, DIAG_H = 38, 45
        y_curr = pdf.get_y()
        count = 0
        
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                url_img = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{val.split('/')[-1]}"
                try:
                    img_data = requests.get(url_img, timeout=5).content
                    col, fila = count % COLS, count // COLS
                    pos_x = X_START + (col * (DIAG_W + GAP_X))
                    pos_y = y_curr + (fila * (DIAG_H + 10))
                    
                    if pos_y + DIAG_H > 265: # Control de salto de página
                        pdf.add_page()
                        y_curr = 20
                        pos_y, pos_x, count = y_curr, X_START, 0

                    pdf.image(BytesIO(img_data), x=pos_x, y=pos_y, w=DIAG_W, h=DIAG_H)
                    pdf.set_xy(pos_x, pos_y + DIAG_H + 1)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(DIAG_W, 5, f"P{i}", align='C')
                    count += 1
                except: continue
    return pdf.output()

df = load()

if df is not None:
    # Orden musical de las notas
    orden_notas = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        r_list = [n for n in orden_notas if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        opciones = sorted(df_raiz['Naturaleza'].unique())
        nat_sel = st.multiselect("Tipo:", opciones, default=opciones)

        if st.button("📥 Generar PDF", use_container_width=True):
            with st.spinner("Preparando documento..."):
                pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(nat_sel)])
                st.download_button("🔥 Descargar Ahora", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf", mime="application/pdf", use_container_width=True)

        st.write("---")
        # QR Y COPIADO (Compatible con todas las versiones)
        st.image(URL_QR, caption="App Online", width=150)
        st.write("Link de la App:")
        
        # Botón de copia mediante HTML/JS
        html_button = f"""
            <button onclick="navigator.clipboard.writeText('{APP_URL}')" 
            style="width:100%; cursor:pointer; background-color:#f0f2f6; border:1px solid #dcdfe3; padding:5px; border-radius:5px;">
            📋 Toca para copiar enlace
            </button>
        """
        st.components.v1.html(html_button, height=45)

    # VISTA WEB
    if nat_sel:
        for _, row in df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.write(f"**Notas:** {row.get('N1','')} - {row.get('N2','')} - {row.get('N3','')} - {row.get('N4','')}")
                col1, col2 = st.columns(2)
                col1.success(f"**IVAN:** {row.get('Int_IVAN','')}")
                col2.info(f"**TRAD:** {row.get('Int_TRAD','')}")
