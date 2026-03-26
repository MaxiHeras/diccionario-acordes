import streamlit as st
import pandas as pd
from fpdf import FPDF
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: ESTILOS DE INTERFAZ Y ESPACIADO
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex !important; overflow-x: auto !important; gap: 15px !important; padding: 10px 0 !important; flex-wrap: nowrap !important; }
    .chord-diag-item { flex: 0 0 auto !important; width: 150px !important; text-align: center; }
    .chord-img-web { width: 100% !important; height: auto !important; }
    .stButton > button { width: 100% !important; border-radius: 6px !important; }
    
    /* Espaciado reducido entre modos */
    div[data-testid="stRadio"] > div { gap: 4px !important; }
    
    .stTextInput input:disabled {
        -webkit-text-fill-color: #31333F !important;
        opacity: 1 !important;
        background-color: #f0f2f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqxacv.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

# 3. GENERACIÓN DE PDF CORREGIDA
def generar_pdf_seguro(df_seleccion, raiz_nombre):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 15, txt=f"Acordes de {raiz_nombre}", ln=True, align='C')
    pdf.ln(5)
    
    for _, row in df_seleccion.iterrows():
        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(240, 242, 246)
        pdf.cell(0, 10, txt=f"{row['Raiz']} {row['Naturaleza']}", ln=True, fill=True)
        
        pdf.set_font("Arial", '', 10)
        notas = [str(row[n]) for n in ['N1','N2','N3','N4'] if pd.notna(row[n])]
        pdf.cell(0, 8, txt=f"Notas: {' - '.join(notas)}", ln=True)
        pdf.cell(0, 8, txt=f"Int_IVAN: {row.get('Int_IVAN','N/A')}", ln=True)
        pdf.ln(4)
    
    # Salida compatible con fpdf2 para evitar el AttributeError
    return pdf.output()

# 4. ESTADOS DE SESIÓN
if "alt" not in st.session_state: st.session_state.alt = "Nat."
if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
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
            raiz_sel = st.selectbox("Nota Raíz:", notas_base)
            st.write("Alteración:")
            c1, c2, c3 = st.columns(3)
            with c1: 
                if st.button("Nat.", type="primary" if st.session_state.alt == "Nat." else "secondary"): 
                    st.session_state.alt = "Nat."; st.rerun()
            with c2: 
                if st.button("Sost.", type="primary" if st.session_state.alt == "Sost." else "secondary"): 
                    st.session_state.alt = "Sost."; st.rerun()
            with c3: 
                if st.button("Bem.", type="primary" if st.session_state.alt == "Bem." else "secondary"): 
                    st.session_state.alt = "Bem."; st.rerun()
            
            nota_f = raiz_sel + ("#" if st.session_state.alt == "Sost." else "b" if st.session_state.alt == "Bem." else "")
            df_r = df[df['Raiz'] == nota_f]
            
            if not df_r.empty:
                opciones = [t for t in orden_tipos if t in df_r['Naturaleza'].unique()]
                st.multiselect("Tipo:", opciones, key="seleccionados")
                
                if st.session_state.seleccionados:
                    if st.button("📄 Generar PDF de Selección", use_container_width=True):
                        pdf_bytes = generar_pdf_seguro(df_r[df_r['Naturaleza'].isin(st.session_state.seleccionados)], nota_f)
                        st.download_button("⬇️ Descargar PDF", data=bytes(pdf_bytes), file_name=f"{nota_f}.pdf", mime="application/pdf")

        st.write("---")
        st.write("📲 **Compartir App**")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="Escaneá para abrir", width=180)
        st.text_input("Enlace:", value=APP_URL, disabled=True)

    # CUERPO PRINCIPAL
    if modo == "Diccionario 📖" and not df_r.empty:
        st.header(f"📖 {nota_f}")
        visibles = [t for t in orden_tipos if t in st.session_state.seleccionados]
        if visibles:
            tabs = st.tabs(visibles)
            for i, tab in enumerate(tabs):
                with tab:
                    row = df_r[df_r['Naturaleza'] == visibles[i]].iloc[0]
                    st.write(f"**Notas:** {' - '.join([str(row[n]) for n in ['N1','N2','N3','N4'] if pd.notna(row[n])])}")
                    st.success(f"IVAN: {row.get('Int_IVAN','N/A')}")
        else: st.info("Seleccioná tipos en el sidebar.")
