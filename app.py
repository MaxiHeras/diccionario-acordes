import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS para la Web
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    .notas-web { font-size: 20px; font-weight: bold; color: #31333F; margin-bottom: 10px; }
    /* Ajuste para reducir la altura de los recuadros st.info y st.success */
    div[data-testid="stNotification"] { padding: 0.5rem 1rem; min-height: auto; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-gpblssuywitmaglkwvdqde.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

# --- FUNCIÓN PDF CON MARCA DE AGUA ---
def generar_pdf(dataframe_seleccionado):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        
        # MARCA DE AGUA (Nombre: Maxi Heras)
        pdf.set_font("Helvetica", "B", 40)
        pdf.set_text_color(240, 240, 240) # Gris muy claro
        # Rotación y posición central de la marca de agua
        with pdf.rotation(45, x=105, y=148):
            pdf.text(60, 148, "MAXI HERAS")
        
        # Restablecer color para el contenido
        pdf.set_text_color(0, 0, 0)
        
        # TÍTULO
        pdf.set_font("Helvetica", "B", 24)
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        
        pdf.ln(8) 
        
        # CONTENIDO INFORMATIVO
        pdf.set_text_color(60, 60, 60)
        alt_linea = 5
        
        # Notas
        pdf.set_font("Helvetica", "B", 11)
        pdf.write(alt_linea, "Notas: ")
        pdf.set_font("Helvetica", "", 11)
        notas_list = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c])]
        pdf.write(alt_linea, f"{' - '.join(notas_list)}\n")
        pdf.ln(2)

        # Intervalos IVAN
        pdf.set_font("Helvetica", "B", 11)
        pdf.write(alt_linea, "Intervalos IVAN: ")
        pdf.set_font("Helvetica", "", 11)
        pdf.write(alt_linea, f"{str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.ln(2)

        # Intervalos TRAD
        pdf.set_font("Helvetica", "B", 11)
        pdf.write(alt_linea, "Intervalos TRAD: ")
        pdf.set_font("Helvetica", "", 11)
        pdf.write(alt_linea, f"{str(row.get('Int_TRAD', 'N/A'))}\n")
        
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
                url_img = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{val.split('/')[-1]}"
                try:
                    img_data = requests.get(url_img, timeout=5).content
                    img_buffer = BytesIO(img_data)
                    col = count % COLS
                    fila = count // COLS
                    if col == 0 and fila > 0:
                        y_inicial_bloque += (DIAG_HEIGHT + TEXT_Px_HEIGHT + GAP_SIMETRICO)
                    pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    if y_inicial_bloque + DIAG_HEIGHT + 10 > 282: 
                        pdf.add_page()
                        y_inicial_bloque = 20
                        pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    pdf.image(img_buffer, x=pos_x, y=y_inicial_bloque, w=DIAG_WIDTH, h=DIAG_HEIGHT)
                    pdf.set_xy(pos_x, y_inicial_bloque + DIAG_HEIGHT + 1)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(128, 128, 128)
                    pdf.cell(DIAG_WIDTH, TEXT_Px_HEIGHT, f"P{i}", border=0, ln=False, align='C')
                    count += 1
                except: continue
    return pdf.output()

df = load()

if df is not None:
    orden_deseado = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        
        if "raiz_anterior" not in st.session_state: st.session_state.raiz_anterior = r_list[0]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        tipos_reales = df_raiz['Naturaleza'].unique()
        opciones_finales = [t for t in orden_deseado if t in tipos_reales] + sorted([t for t in tipos_reales if t not in orden_deseado])

        if raiz_sel != st.session_state.raiz_anterior:
            st.session_state.seleccionados = opciones_finales
            st.session_state.raiz_anterior = raiz_sel
            if "ms_key" not in st.session_state: st.session_state.ms_key = 0
            st.session_state.ms_key += 1
            st.rerun()

        if 'ms_key' not in st.session_state: st.session_state.ms_key = 0
        if 'seleccionados' not in st.session_state: st.session_state.seleccionados = opciones_finales

        nat_sel = st.multiselect("Tipo:", options=opciones_finales, default=st.session_state.seleccionados, key=f"ms_{st.session_state.ms_key}")

        col1, col2 = st.columns(2)
        if col1.button("Todo", use_container_width=True):
            st.session_state.seleccionados = opciones_finales
            st.session_state.ms_key += 1
            st.rerun()
        if col2.button("Limpiar", use_container_width=True):
            st.session_state.seleccionados = []
            st.session_state.ms_key += 1
            st.rerun()

        st.write("---")
        if nat_sel:
            if st.button("📥 Generar PDF", use_container_width=True):
                with st.spinner("Generando PDF..."):
                    pdf_bytes = generar_pdf(df_raiz[df_raiz['Naturaleza'].isin(nat_sel)])
                    st.download_button(label="🔥 Descargar PDF", data=bytes(pdf_bytes), file_name=f"Acordes_{raiz_sel}.pdf", mime="application/pdf", use_container_width=True)

    # 4. RESULTADOS (WEB)
    if nat_sel:
        debe_expandir = len(nat_sel) == 1
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].copy()
        df_f['Naturaleza'] = pd.Categorical(df_f['Naturaleza'], categories=opciones_finales, ordered=True)
        df_f = df_f.sort_values('Naturaleza')

        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=debe_expandir):
                notas_web = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c])]
                st.markdown(f'<p class="notas-web">Notas: {" - ".join(notas_web)}</p>', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                ivan, trad = str(row.get('Int_IVAN', '')).strip(), str(row.get('Int_TRAD', '')).strip()
                
                # INVERSIÓN DE COLORES: IVAN (Verde/Success) y TRAD (Azul/Info)
                if ivan and ivan.lower() != 'nan': c1.success(f"**Intervalos IVAN:**\n\n{ivan}")
                if trad and trad.lower() != 'nan': c2.info(f"**Intervalos TRAD:**\n\n{trad}")
                
                st.write("---")
                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if val.lower().endswith('.png'):
                        url_img = f"{GITHUB_BASE}/{str(row['Naturaleza']).replace(' ', '%20')}/{val.split('/')[-1]}"
                        h_items += f'<div class="chord-item"><img src="{url_img}" class="chord-img" width="110"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                if h_items: st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
else:
    st.error("Error al cargar la base de datos.")
