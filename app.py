import streamlit as st
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
import datetime

# CONFIGURACIÓN APP
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# ESTILOS VISUALES
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# CARGA DE DATOS
APP_URL = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

# FUNCIÓN PDF
def create_pdf(df_filtered):
    GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
    html = f"""
    <html><body>
    <h1 style='text-align:center;'>Hoja de Estudio</h1>
    <p style='text-align:center;'>Fecha: {datetime.date.today()}</p>
    """
    for _, row in df_filtered.iterrows():
        n_list = [str(row[c]) for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]) not in ['0','nan','']]
        html += f"""
        <div style='border-bottom: 1px solid #ccc; margin-bottom: 20px;'>
            <h3>Acorde: {row['Raiz']} {row['Naturaleza']}</h3>
            <p><b>Notas:</b> {' - '.join(n_list)}</p>
        """
        # Agregar diagramas al PDF
        html += "<div style='margin-top:10px;'>"
        for i in range(1, 10):
            img_val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if img_val.lower().endswith('.png'):
                img_file = img_val.split('/')[-1]
                img_url = f"{GITHUB_BASE}/{row['Naturaleza']}/{img_file}"
                html += f'<img src="{img_url}" width="80" style="margin-right:10px;">'
        html += "</div></div>"
    
    html += "</body></html>"
    result = BytesIO()
    pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    return result.getvalue()

if df is not None:
    with st.sidebar:
        st.header("🔍 Filtros")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())

    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        # Botón de PDF
        with st.spinner('Generando PDF...'):
            pdf_bytes = create_pdf(df_f)
            st.download_button("📄 Descargar PDF con Diagramas", pdf_bytes, "Estudio.pdf", "application/pdf")

        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.write(f"**Notas:** {' - '.join([str(row[c]) for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]) not in ['0','nan','']])}")
                
                # Galería Web
                h_items = ""
                BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                for i in range(1, 10):
                    v = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if v.lower().endswith('.png'):
                        url = f"{BASE}/{row['Naturaleza']}/{v.split('/')[-1]}"
                        h_items += f'<div class="chord-item"><img src="{url}" class="chord-img" width="110"><p>P{i}</p></div>'
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
    else:
        st.info("Elegí un acorde.")
else:
    st.error("No se pudo cargar el Excel.")
