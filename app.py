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
    /* Ajuste de altura para recuadros de intervalos */
    div[data-testid="stNotification"] { padding: 2px 10px; min-height: 0px; }
    div[data-testid="stNotificationContent"] { padding: 0px; }
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

# --- FUNCIÓN PDF CORREGIDA (Sin errores de fuente y con marca de agua correcta) ---
def generar_pdf(dataframe_seleccionado):
    # Usamos fuentes núcleo de PDF para evitar errores de archivos .ttf faltantes
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        
        # TÍTULO (24pt)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_text_color(0, 0, 0) 
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        pdf.ln(8) 
        
        # CONTENIDO (Notas 11pt)
        pdf.set_text_color(60, 60, 60)
        
        pdf.set_font("helvetica", "B", 11)
        pdf.write(5, "Notas: ")
        pdf.set_font("helvetica", "", 11)
        notas_list = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c])]
        pdf.write(5, f"{' - '.join(notas_list)}\n")
        pdf.ln(2)

        pdf.set_font("helvetica", "B", 11)
        pdf.write(5, "Intervalos IVAN: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(5, f"{str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.ln(2)

        pdf.set_font("helvetica", "B", 11)
        pdf.write(5, "Intervalos TRAD: ")
        pdf.set_font("helvetica", "", 11)
        pdf.write(5, f"{str(row.get('Int_TRAD', 'N/A'))}\n")
        
        pdf.ln(10) 

        # CUADRÍCULA DE DIAGRAMAS
        X_START, GAP_X, COLS = 15, 5, 4
        DIAG_WIDTH, DIAG_HEIGHT, TEXT_Px_HEIGHT = 38, 45, 5
        y_inicial = pdf.get_y()
        count = 0
        
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                url_img = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{val.split('/')[-1]}"
                try:
                    img_data = requests.get(url_img, timeout=5).content
                    img_buffer = BytesIO(img_data)
                    col, fila = count % COLS, count // COLS
                    pos_y = y_inicial + (fila * (DIAG_HEIGHT + TEXT_Px_HEIGHT + 5))
                    pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    
                    # Verificamos si la imagen cabe en la página actual
                    if pos_y + DIAG_HEIGHT > 270:
                        pdf.add_page()
                        y_inicial = 20
                        pos_y = y_inicial
                        # Al cambiar de página, reiniciamos el contador de columnas para esta fila
                        count = 0 
                        col, fila = 0, 0
                        pos_x = X_START

                    pdf.image(img_buffer, x=pos_x, y=pos_y, w=DIAG_WIDTH, h=DIAG_HEIGHT)
                    pdf.set_xy(pos_x, pos_y + DIAG_HEIGHT + 1)
                    pdf.set_font("helvetica", "", 9)
                    pdf.set_text_color(128, 128, 128)
                    pdf.cell(DIAG_WIDTH, TEXT_Px_HEIGHT, f"P{i}", align='C')
                    count += 1
                except: continue
        
        # MARCA DE AGUA (Inferior Derecho en cada página de acorde)
        pdf.set_y(-15)
        pdf.set_font("helvetica", "B", 13)
        pdf.set_text_color(180, 180, 180)
        pdf.cell(0, 10, "Maxi Heras - Tucumán", align='R')
        
    return pdf.output()

df = load()

if df is not None:
    # 3. LÓGICA DE FILTROS Y ORDEN MUSICAL
    orden_notas = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    orden_acordes = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        # Restauramos el orden musical (C, D, E...) en el selector
        r_list = [n for n in orden_notas if n in df['Raiz'].unique()]
        
        if "raiz_ant" not in st.session_state: st.session_state.raiz_ant = r_list[0]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        tipos_reales = df_raiz['Naturaleza'].unique()
        opciones = [t for t in orden_acordes if t in tipos_reales] + sorted([t for t in tipos_reales if t not in orden_acordes])

        if raiz_sel != st.session_state.raiz_ant:
            st.session_state.seleccionados = opciones
            st.session_state.raiz_ant = raiz_sel
            st.session_state.ms_key = st.session_state.get('ms_key', 0) + 1
            st.rerun()

        if 'seleccionados' not in st.session_state: st.session_state.seleccionados = opciones
        nat_sel = st.multiselect("Tipo:", opciones, default=st.session_state.seleccionados, key=f"ms_{st.session_state.get('ms_key', 0)}")

        c1, c2 = st.columns(2)
        if c1.button("Todo", use_container_width=True):
            st.session_state.seleccionados = opciones
            st.session_state.ms_key = st.session_state.get('ms_key', 0) + 1
            st.rerun()
        if c2.button("Limpiar", use_container_width=True):
            st.session_state.seleccionados = []
            st.session_state.ms_key = st.session_state.get('ms_key', 0) + 1
            st.rerun()

        st.write("---")
        if nat_sel:
            # Recuperamos la animación de "Generando PDF..."
            if st.button("📥 Generar PDF", use_container_width=True):
                with st.spinner("Generando archivo..."):
                    pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(nat_sel)])
                    st.download_button("🔥 Descargar PDF", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf", mime="application/pdf", use_container_width=True)

        st.write("---")
        st.image(URL_QR, caption="Escanea para abrir en el móvil", width=150)
        st.code(APP_URL, language=None)

    # 4. RESULTADOS WEB
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].copy()
        df_f['Naturaleza'] = pd.Categorical(df_f['Naturaleza'], categories=opciones, ordered=True)
        df_f = df_f.sort_values('Naturaleza')

        for _, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=(len(nat_sel)==1)):
                notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row[c])]
                st.markdown(f'<p class="notas-web">Notas: {" - ".join(notas)}</p>', unsafe_allow_html=True)
                
                col_ivan, col_trad = st.columns(2)
                ivan, trad = str(row.get('Int_IVAN','')), str(row.get('Int_TRAD',''))
                if ivan.lower() != 'nan': col_ivan.success(f"**Intervalos IVAN:**\n\n{ivan}")
                if trad.lower() != 'nan': col_trad.info(f"**Intervalos TRAD:**\n\n{trad}")
                
                st.write("---")
                h_items = ""
                for i in range(1, 10):
                    v = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if v.lower().endswith('.png'):
                        url = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{v.split('/')[-1]}"
                        h_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" width="110"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                if h_items: st.markdown(f'<div class="scroll-container" style="display:flex; overflow-x:auto; gap:15px;">{h_items}</div>', unsafe_allow_html=True)
else:
    st.error("Error: No se pudo conectar con la base de datos.")
