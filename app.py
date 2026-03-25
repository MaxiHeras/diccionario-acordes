import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    .texto-unificado { font-size: 18px; font-weight: bold; color: #3C3C3C; margin-bottom: 5px; }
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

# --- FUNCIÓN PARA GENERAR PDF (SIMETRÍA AJUSTADA) ---
def generar_pdf(dataframe_seleccionado):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        
        # TÍTULO (Recuadro negro)
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(0, 0, 0) 
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        
        # ESPACIO AL TÍTULO (Más corto para subir el contenido)
        pdf.ln(8) 
        
        # BLOQUE INFORMATIVO (Unificado a 11pt)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(60, 60, 60)
        
        alt_linea = 5 # Altura compacta
        notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','','0']]
        pdf.cell(0, alt_linea, f"Notas: {' - '.join(notas)}", ln=True) 
        
        pdf.cell(0, alt_linea, f"Intervalos IVAN: {str(row.get('Int_IVAN', 'N/A'))}", ln=True) 
        pdf.cell(0, alt_linea, f"Intervalos TRAD: {str(row.get('Int_TRAD', 'N/A'))}", ln=True) 
        
        # --- ESPACIO SIMÉTRICO ---
        # Distancia del texto a los gráficos igual que entre filas de gráficos
        GAP_SIMETRICO = 12 
        pdf.ln(GAP_SIMETRICO) 

        # CUADRÍCULA DE DIAGRAMAS
        X_START, GAP_X, COLS = 15, 5, 4
        DIAG_WIDTH, DIAG_HEIGHT, TEXT_Px_HEIGHT = 38, 45, 5
        
        y_inicial_bloque = pdf.get_y()
        count = 0
        
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                nombre_archivo = val.split('/')[-1]
                nat_url = str(row['Naturaleza']).replace(' ', '%20')
                url_img = f"{GITHUB_BASE}/{nat_url}/{nombre_archivo}"
                
                try:
                    img_data = requests.get(url_img, timeout=5).content
                    img_buffer = BytesIO(img_data)
                    col, fila = count % COLS, count // COLS
                    
                    if col == 0 and fila > 0:
                        # La distancia vertical ahora es simétrica al espacio del texto
                        y_inicial_bloque += (DIAG_HEIGHT + TEXT_Px_HEIGHT + GAP_SIMETRICO)
                    
                    pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    
                    if y_inicial_bloque + DIAG_HEIGHT + 10 > 282: 
                        pdf.add_page()
                        y_inicial_bloque = 20
                        pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    
                    pdf.image(img_buffer, x=pos_x, y=y_inicial_bloque, w=DIAG_WIDTH, h=DIAG_HEIGHT)
                    
                    # Etiquetas P1, P2...
                    pdf.set_xy(pos_x, y_inicial_bloque + DIAG_HEIGHT + 1)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(128, 128, 128)
                    pdf.cell(DIAG_WIDTH, TEXT_Px_HEIGHT, f"P{i}", border=0, ln=False, align='C')
                    count += 1
                except: continue
                    
    return pdf.output()

df = load()

if df is not None:
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        r_list = sorted([n for n in df['Raiz'].unique()])
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_raiz = df[df['Raiz'] == raiz_sel]
        
        tipos = df_raiz['Naturaleza'].unique()
        nat_sel = st.multiselect("Tipo:", options=tipos, default=list(tipos)[:1])

        st.write("---")
        if nat_sel:
            if st.button("📥 Generar PDF", use_container_width=True):
                with st.spinner("Ajustando simetría..."):
                    pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(nat_sel)])
                    st.download_button(label="🔥 Descargar PDF", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf", mime="application/pdf", use_container_width=True)
        
        st.image(URL_QR, caption="App Online", width=150)

    # VISTA WEB
    if nat_sel:
        for idx, row in df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.markdown(f'<p class="texto-unificado">Notas: {row.get("N1","")} - {row.get("N2","")}...</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="texto-unificado">Intervalos TRAD: {row.get("Int_TRAD", "N/A")}</p>', unsafe_allow_html=True)
                st.write("---")
else: st.error("No se pudo conectar con la base de datos.")
