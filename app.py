import streamlit as st
import pandas as pd
from fpdf import FPDF
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# CSS: ESPACIADO Y ESTILO
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stRadio"] > div { gap: 4px !important; }
    .stButton > button { width: 100% !important; border-radius: 6px !important; }
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-diag-item { flex: 0 0 auto; width: 150px; text-align: center; }
    .chord-img-web { width: 100%; height: auto; }
    </style>
""", unsafe_allow_html=True)

# 2. FUNCIONES CLAVE
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqxacv.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"

@st.cache_data(ttl=600)
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

class PDF_Final(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Maxi Heras - Tucumán", align='R')

def generar_pdf(df_seleccion, raiz_nombre):
    pdf = PDF_Final(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 20)
    pdf.cell(0, 15, txt=f"Acordes de {raiz_nombre}", ln=True, align='C')
    
    for _, row in df_seleccion.iterrows():
        pdf.set_font("helvetica", 'B', 14)
        pdf.set_fill_color(240, 242, 246)
        pdf.cell(0, 10, txt=f"{row['Raiz']} {row['Naturaleza']}", ln=True, fill=True)
        pdf.set_font("helvetica", '', 11)
        notas = [str(row[n]) for n in ['N1','N2','N3','N4'] if pd.notna(row[n])]
        pdf.cell(0, 8, txt=f"Notas: {' - '.join(notas)}", ln=True)
        pdf.cell(0, 8, txt=f"Int_IVAN: {row.get('Int_IVAN','N/A')}", ln=True)
        pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1')

# 3. LÓGICA DE ESTADOS
if "alteracion" not in st.session_state: st.session_state.alteracion = "Nat."
if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None
if "notas_id" not in st.session_state: st.session_state.notas_id = set()

df = load()

if df is not None:
    notas_base = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    orden_tipos = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.subheader("Seleccionar Modo")
        modo = st.radio(" ", ["Diccionario 📖", "Identificador 🔍"], label_visibility="collapsed")
        st.write("---")

        if modo == "Diccionario 📖":
            raiz_base = st.selectbox("Nota Raíz:", notas_base)
            st.write("Alteración:")
            c1, c2, c3 = st.columns(3)
            with c1: 
                if st.checkbox("Nat.", value=(st.session_state.alteracion == "Nat.")):
                    st.session_state.alteracion = "Nat."; st.rerun()
            with c2: 
                if st.checkbox("Sost.", value=(st.session_state.alteracion == "Sost.")):
                    st.session_state.alteracion = "Sost."; st.rerun()
            with c3: 
                if st.checkbox("Bem.", value=(st.session_state.alteracion == "Bem.")):
                    st.session_state.alteracion = "Bem."; st.rerun()
            
            raiz_f = raiz_base + ("#" if st.session_state.alteracion == "Sost." else "b" if st.session_state.alteracion == "Bem." else "")
            df_r = df[df['Raiz'] == raiz_f]
            
            if not df_r.empty:
                opts = [t for t in orden_tipos if t in df_r['Naturaleza'].unique()]
                st.multiselect("Tipo:", opts, key="seleccionados")
                
                if st.session_state.seleccionados:
                    if st.button("📄 Generar PDF"):
                        st.session_state.pdf_data = generar_pdf(df_r[df_r['Naturaleza'].isin(st.session_state.seleccionados)], raiz_f)
                    if st.session_state.pdf_data:
                        st.download_button("⬇️ Descargar", data=st.session_state.pdf_data, file_name=f"{raiz_f}.pdf", mime="application/pdf")
            else:
                st.warning(f"Nota {raiz_f} no encontrada.")

        st.write("---")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="App QR", width=150)

    # CUERPO PRINCIPAL
    if modo == "Diccionario 📖" and not df_r.empty:
        st.header(f"📖 {raiz_f}")
        visibles = [t for t in orden_tipos if t in st.session_state.seleccionados]
        if visibles:
            tabs = st.tabs(visibles)
            for i, tab in enumerate(tabs):
                with tab:
                    row = df_r[df_r['Naturaleza'] == visibles[i]].iloc[0]
                    st.write(f"**Notas:** {' - '.join([str(row[n]) for n in ['N1','N2','N3','N4'] if pd.notna(row[n])])}")
                    st.info(f"IVAN: {row.get('Int_IVAN','N/A')}")
        else: st.info("Selecciona tipos en el sidebar.")
else:
    st.error("Error al cargar la base de datos.")
