import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# Estilos para que las imágenes no salgan en negativo en modo oscuro y galería horizontal
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={APP_URL}"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df = load()

# FUNCIÓN PARA EL PDF (Ignora errores de caracteres raros)
def create_pdf(df_filtered):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Hoja de Estudio de Acordes", ln=True, align="C")
    pdf.ln(10)
    for _, row in df_filtered.iterrows():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Acorde: {row['Raiz']} {row['Naturaleza']}", ln=True)
        pdf.set_font("Arial", "", 10)
        notas = [str(row[c]) for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]) not in ['0','nan']]
        pdf.cell(0, 7, f"Notas: {' - '.join(notas)}", ln=True)
        
        # Intervalos en el PDF
        ivan = str(row.get('Int_IVAN', ''))
        if ivan and ivan.lower() not in ['nan', '0', '']:
            pdf.cell(0, 7, f"Int_IVAN: {ivan}", ln=True)
        trad = str(row.get('Int_TRAD', ''))
        if trad and trad.lower() not in ['nan', '0', '']:
            pdf.cell(0, 7, f"Int_TRAD: {trad}", ln=True)
        
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())
        
        st.write("---")
        # Botón de WhatsApp
        texto_wa = f"Mirá este diccionario de acordes: {APP_URL}"
        link_wa = f"https://wa.me/?text={texto_wa.replace(' ', '%20')}"
        st.link_button("📲 Compartir por WhatsApp", link_wa, use_container_width=True)
        
        st.image(URL_QR, caption="Escanear para compartir", width=180)
        st.code(APP_URL, language=None)

    # 4. RESULTADOS
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        # Botón PDF (Protegido por si no cargó la librería aún)
        try:
            pdf_data = create_pdf(df_f)
            st.download_button("📄 Descargar Hoja de Estudio (PDF)", pdf_data, f"Acordes_{raiz_sel}.pdf", "application/pdf")
        except:
            st.warning("El PDF se activará cuando GitHub termine de instalar la librería 'fpdf'.")

        expandir = False if len(nat_sel) > 1 else True
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=expandir):
                # Notas
                n_list = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(n_list)}")
                
                # Columnas de Intervalos corregidas
                c1, c2 = st.columns(2)
                with c1:
                    ivan = str(row.get('Int_IVAN', '')).strip()
                    if ivan and ivan.lower() not in ['nan', '0', '']:
                        st.info(f"**Int_IVAN:**\n\n{ivan}")
                with c2:
                    trad = str(row.get('Int_TRAD', '')).strip()
                    if trad and trad.lower() not in ['nan', '0', '']:
                        st.success(f"**Int_TRAD:**\n\n{trad}")
                
                st.write("---")
                
                # Galería de imágenes (Filtrada para evitar íconos rotos)
                h_items = ""
                GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if val.lower().endswith('.png'):
                        archivo = val.split('/')[-1]
                        url_img = f"{GITHUB_BASE}/{row['Naturaleza']}/{archivo}"
                        div_id = f"pos_{idx}_{i}"
                        h_items += f'<div class="chord-item" id="{div_id}"><img src="{url_img}" class="chord-img" width="110" onerror="document.getElementById(\'{div_id}\').style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
    else:
        st.info("Elegí un acorde en el menú lateral.")
else:
    st.error("No se pudo cargar el Excel. Revisá la URL de Google Sheets.")
