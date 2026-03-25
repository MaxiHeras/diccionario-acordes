import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS ---
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

# --- FUNCIÓN PARA GENERAR PDF ---
def generar_pdf(dataframe_seleccionado):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        # Título del Acorde
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 10, f"{row['Raiz']} {row['Naturaleza']}", ln=True, align='C')
        
        # Notas
        pdf.set_font("Helvetica", "", 12)
        notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c])]
        pdf.cell(0, 10, f"Notas: {' - '.join(notas)}", ln=True)
        
        # Intervalos
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 5, f"IVAN: {row.get('Int_IVAN', 'N/A')}", ln=True)
        pdf.cell(0, 5, f"TRAD: {row.get('Int_TRAD', 'N/A')}", ln=True)
        pdf.ln(10)

        # Diagramas (Imágenes)
        x_start = 10
        y_start = pdf.get_y()
        count = 0
        
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                nombre_archivo = val.split('/')[-1]
                nat_url = str(row['Naturaleza']).replace(' ', '%20')
                url_img = f"{GITHUB_BASE}/{nat_url}/{nombre_archivo}"
                
                try:
                    # Descargar imagen temporalmente para el PDF
                    img_data = requests.get(url_img).content
                    img_buffer = BytesIO(img_data)
                    
                    # Acomodar 3 imágenes por fila
                    col = count % 3
                    row_idx = count // 3
                    pdf.image(img_buffer, x=x_start + (col * 65), y=y_start + (row_idx * 55), w=55)
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

        # --- BOTÓN DE EXPORTAR PDF ---
        st.write("---")
        if nat_sel:
            df_export = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
            pdf_bytes = generar_pdf(df_export)
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_bytes,
                file_name=f"acordes_{raiz_sel}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.write("---")
        st.image(URL_QR, caption="Escanear para compartir", width=180)

    # 4. RESULTADOS (Visualización en App)
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
