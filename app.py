import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS Y CONSTANTES
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

# --- FUNCIÓN PARA GENERAR PDF (CON RECUADRO, ESPACIADO Y ETIQUETAS Px) ---
def generar_pdf(dataframe_seleccionado):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        
        # --- TÍTULO CON RECUADRO ---
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(20, 20, 20)
        # Dibujamos una celda con borde (border=1) y alineación centrada
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        
        # --- MÁS ESPACIO DESPUÉS DEL TÍTULO ---
        pdf.ln(12) # Aumentamos el espacio significativamente
        
        # Notas
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(60, 60, 60)
        notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','','0']]
        pdf.cell(0, 8, f"Notas: {' - '.join(notas)}", ln=True)
        
        # Intervalos
        pdf.set_font("Helvetica", "B", 10)
        ivan = str(row.get('Int_IVAN', 'N/A'))
        trad = str(row.get('Int_TRAD', 'N/A'))
        pdf.cell(0, 6, f"Intervalos IVAN: {ivan}", ln=True)
        pdf.cell(0, 6, f"Intervalos TRAD: {trad}", ln=True)
        
        pdf.ln(10) # Espacio antes de los diagramas

        # --- CUADRÍCULA DE DIAGRAMAS ---
        X_START = 15
        GAP_X = 5
        GAP_Y = 15            # Un poco más de espacio vertical para el texto Px
        COLS = 4
        DIAG_WIDTH = 38
        DIAG_HEIGHT = 45
        
        y_inicial_fila = pdf.get_y()
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
                    
                    col = count % COLS
                    fila = count // COLS
                    
                    if col == 0 and fila > 0:
                        y_inicial_fila += (DIAG_HEIGHT + GAP_Y + 5) # +5 por el texto debajo
                    
                    pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    
                    if y_inicial_fila + DIAG_HEIGHT + 10 > 282: 
                        pdf.add_page()
                        y_inicial_fila = 20
                        pos_x = X_START + (col * (DIAG_WIDTH + GAP_X))
                    
                    # Colocar Imagen
                    pdf.image(img_buffer, x=pos_x, y=y_inicial_fila, w=DIAG_WIDTH, h=DIAG_HEIGHT)
                    
                    # --- ETIQUETA Px DEBAJO DEL DIAGRAMA ---
                    pdf.set_xy(pos_x, y_inicial_fila + DIAG_HEIGHT + 1)
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(128, 128, 128) # Gris como en la app
                    pdf.cell(DIAG_WIDTH, 5, f"P{i}", border=0, ln=False, align='C')
                    
                    count += 1
                except:
                    continue
                    
    return pdf.output()

df = load()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        
        orden_deseado = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
        tipos_reales = df_raiz['Naturaleza'].unique()
        opciones_finales = [t for t in orden_deseado if t in tipos_reales] + sorted([t for t in tipos_reales if t not in orden_deseado])

        if 'selector_key' not in st.session_state:
            st.session_state.selector_key = 0
        if 'valores_actuales' not in st.session_state:
            st.session_state.valores_actuales = opciones_finales

        nat_sel = st.multiselect(
            "Tipo:", 
            options=opciones_finales, 
            default=st.session_state.valores_actuales,
            key=f"ms_{st.session_state.selector_key}"
        )

        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("Todo", use_container_width=True):
            st.session_state.valores_actuales = opciones_finales
            st.session_state.selector_key += 1
            st.rerun()

        if col_btn2.button("Limpiar", use_container_width=True):
            st.session_state.valores_actuales = []
            st.session_state.selector_key += 1
            st.rerun()

        # --- EXPORTACIÓN PDF ---
        st.write("---")
        if nat_sel:
            df_export = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].copy()
            df_export['Naturaleza'] = pd.Categorical(df_export['Naturaleza'], categories=opciones_finales, ordered=True)
            df_export = df_export.sort_values('Naturaleza')

            if st.button("📥 Generar PDF", use_container_width=True):
                with st.spinner("Preparando archivo..."):
                    try:
                        pdf_bytes = generar_pdf(df_export)
                        st.download_button(
                            label="🔥 Descargar archivo PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"Acordes_{raiz_sel}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        st.write("---")
        st.image(URL_QR, caption="Escanear para compartir", width=180)

    # 4. RESULTADOS (WEB)
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].copy()
        df_f['Naturaleza'] = pd.Categorical(df_f['Naturaleza'], categories=opciones_finales, ordered=True)
        df_f = df_f.sort_values('Naturaleza')
        
        esta_expandido = len(nat_sel) == 1
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=esta_expandido):
                notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] 
                         if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(notas)}")
                
                c1, c2 = st.columns(2)
                ivan = str(row.get('Int_IVAN', '')).strip()
                trad = str(row.get('Int_TRAD', '')).strip()
                if ivan and ivan.lower() not in ['nan', '0', '']: c1.info(f"**Int_IVAN:**\n\n{ivan}")
                if trad and trad.lower() not in ['nan', '0', '']: c2.success(f"**Int_TRAD:**\n\n{trad}")
                
                st.write("---")
                
                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if val.lower().endswith('.png'):
                        nombre_archivo = val.split('/')[-1]
                        nat_url = str(row['Naturaleza']).replace(' ', '%20')
                        url_img = f"{GITHUB_BASE}/{nat_url}/{nombre_archivo}"
                        h_items += f'<div class="chord-item"><img src="{url_img}" class="chord-img" width="110"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
    else:
        st.info("Elegí un acorde en el menú lateral.")
else:
    st.error("Error al cargar la base de datos.")
