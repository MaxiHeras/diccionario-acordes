import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

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
        notas = [str(row[c]) for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]) not in ['0','nan','']]
        pdf.cell(0, 7, f"Notas: {' - '.join(notas)}", ln=True)
        ivan = str(row.get('Int_IVAN', '')).strip()
        if ivan and ivan.lower() not in ['nan', '0', '']:
            pdf.cell(0, 7, f"Int_IVAN: {ivan}", ln=True)
        trad = str(row.get('Int_TRAD', '')).strip()
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
        t_wa = f"Mirá este diccionario de acordes: {APP_URL}"
        l_wa = f"https://wa.me/?text={t_wa.replace(' ', '%20')}"
        st.link_button("📲 Compartir por WhatsApp", l_wa, use_container_width=True)
        st.image(URL_QR, width=180)

    # 4. RESULTADOS
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        try:
            p_data = create_pdf(df_f)
            st.download_button("📄 Descargar PDF", p_data, f"Acordes_{raiz_sel}.pdf", "application/pdf")
        except:
            st.warning("Instalando componentes de PDF...")

        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Notas
                n_raw = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c))]
                n_clean = [n for n in n_raw if n.lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(n_clean)}")
                
                # Intervalos
                c1, c2 = st.columns(2)
                v_ivan = str(row.get('Int_IVAN', '')).strip()
                v_trad = str(row.get('Int_TRAD', '')).strip()
                
                if v_ivan and v_ivan.lower() not in ['nan', '0', '']:
                    c1.info(f"**Int_IVAN:**\n\n{v_ivan}")
                if v_trad and v_trad.lower() not in ['nan', '0', '']:
                    c2.success(f"**Int_TRAD:**\n\n{v_trad}")
                
                st.write("---")
                
                # Galería
                h_html = ""
                BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                for i in range(1, 10):
                    img_name = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if img_name.lower().endswith('.png'):
                        archivo = img_name.split('/')[-1]
                        url = f"{BASE}/{row['Naturaleza']}/{archivo}"
                        h_html += f'<div class="chord-item"><img src="{url}" class="chord-img" width="110"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_html:
                    st.markdown(f'<div class="scroll-container">{h_html}</div>', unsafe_allow_html=True)
    else:
        st.info("Elegí un acorde en el menú lateral.")
else:
    st.error("Error crítico: No se pudo conectar con la base de datos de Google Sheets.")
