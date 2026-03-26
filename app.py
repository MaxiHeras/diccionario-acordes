import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse
import time

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: ESTILOS Y ESPACIADO FINO
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex !important; overflow-x: auto !important; gap: 15px !important; padding: 10px 0 !important; flex-wrap: nowrap !important; }
    .chord-diag-item { flex: 0 0 auto !important; width: 150px !important; text-align: center; }
    .chord-img-web { width: 100% !important; height: auto !important; }
    .stButton > button { width: 100% !important; border-radius: 6px !important; }
    
    /* Espaciado reducido entre modos de navegación */
    div[data-testid="stRadio"] > div { gap: 4px !important; }
    [data-testid="stWidgetLabel"] + div div[data-testid="stMarkdownContainer"] { margin-bottom: 2px !important; }

    .stTextInput input:disabled {
        -webkit-text-fill-color: #31333F !important;
        opacity: 1 !important;
        background-color: #f0f2f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. FUNCIONES DE CARGA Y PDF (MÉTODO ALTERNATIVO ANTIFALLOS)
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

def generar_pdf_con_qr(df_seleccion, raiz_nombre):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # QR dentro del PDF
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(APP_URL)}"
    try: pdf.image(qr_url, x=170, y=10, w=25)
    except: pass
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(160, 10, txt=f"Acordes de {raiz_nombre}", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(160, 10, txt="Escanea el QR para volver a la App", ln=True)
    pdf.ln(10)
    
    for _, row in df_seleccion.iterrows():
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(240, 242, 246)
        pdf.cell(0, 10, txt=f"{row['Raiz']} {row['Naturaleza']}", ln=True, fill=True)
        pdf.set_font("Arial", '', 12)
        notas = [str(row[n]) for n in ['N1','N2','N3','N4'] if pd.notna(row[n])]
        pdf.cell(0, 8, txt=f"Notas: {' - '.join(notas)}", ln=True)
        pdf.set_text_color(46, 125, 50)
        pdf.cell(0, 8, txt=f"Int_IVAN: {row.get('Int_IVAN','')}", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
    
    # MÉTODO INVISIBLE DE SALIDA (Para evitar AttributeError)
    return pdf.output(dest='S').encode('latin-1')

# 3. LÓGICA DE LA APP
if "alteracion" not in st.session_state: st.session_state.alteracion = "Nat."
if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "ultima_nota_completa" not in st.session_state: st.session_state.ultima_nota_completa = ""
if "ultimo_modo" not in st.session_state: st.session_state.ultimo_modo = "Diccionario 📖"
if "notas_id" not in st.session_state: st.session_state.notas_id = set()

def seleccionar_todo(opciones): st.session_state.seleccionados = opciones
def limpiar_todo(): st.session_state.seleccionados = []

def mostrar_detalle_acorde(row):
    st.markdown(f"### {row['Raiz']} {row['Naturaleza']}")
    lista_n = [str(row.get(n,'')) for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
    st.write(f"**Notas:** {' - '.join(lista_n)}")
    c1, c2 = st.columns(2)
    with c1: st.success(f"**Int_IVAN:** {row.get('Int_IVAN','N/A')}") 
    with c2: st.info(f"**Int_TRAD:** {row.get('Int_TRAD','N/A')}")
    st.write("---")
    
    h_items = ""
    nat_url = urllib.parse.quote(str(row['Naturaleza']).replace("#", "SOS"))
    for j in range(1, 10):
        v = str(row.get(f'Diagrama{j}', 'nan')).strip()
        if v.lower().endswith('.png'):
            nombre_archivo = v.split('/')[-1].replace("#", "SOS")
            url = f"{GITHUB_BASE}/{nat_url}/{nombre_archivo}"
            h_items += f'<div class="chord-diag-item"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
    if h_items: 
        st.write("**Diagramas:**")
        st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)

df = load()
if df is not None:
    notas_base = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    orden_tipos = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.subheader("Seleccionar Modo")
        modo = st.radio(" ", ["Diccionario 📖", "Identificador 🔍"], label_visibility="collapsed")
        
        if modo != st.session_state.ultimo_modo:
            st.session_state.ultimo_modo = modo
            st.session_state.ultima_nota_completa = "" 
        st.write("---")

        if modo == "Diccionario 📖":
            raiz_base = st.selectbox("Nota Raíz:", notas_base)
            st.write("Alteración:")
            c_nat, c_sos, c_bem = st.columns(3)
            
            # Etiquetas completas Sost. y Bem.
            with c_nat: 
                if st.checkbox("Nat.", value=(st.session_state.alteracion == "Nat."), key="chk_nat"):
                    if st.session_state.alteracion != "Nat.":
                        st.session_state.alteracion = "Nat."; st.rerun()
            with c_sos: 
                if st.checkbox("Sost.", value=(st.session_state.alteracion == "Sost."), key="chk_sos"):
                    if st.session_state.alteracion != "Sost.":
                        st.session_state.alteracion = "Sost."; st.rerun()
            with c_bem: 
                if st.checkbox("Bem.", value=(st.session_state.alteracion == "Bem."), key="chk_bem"):
                    if st.session_state.alteracion != "Bem.":
                        st.session_state.alteracion = "Bem."; st.rerun()
            
            raiz_final = raiz_base
            if st.session_state.alteracion == "Sost.": raiz_final = f"{raiz_base}#"
            elif st.session_state.alteracion == "Bem.": raiz_final = f"{raiz_base}b"
            
            df_raiz = df[df['Raiz'] == raiz_final]
            if not df_raiz.empty:
                opciones_disponibles = [t for t in orden_tipos if t in df_raiz['Naturaleza'].unique()]
                if raiz_final != st.session_state.ultima_nota_completa:
                    st.session_state.ultima_nota_completa = raiz_final
                    st.session_state.seleccionados = opciones_disponibles
                
                st.multiselect("Tipo:", opciones_disponibles, key="seleccionados")
                col1, col2 = st.columns(2)
                col1.button("Todo", on_click=seleccionar_todo, args=(opciones_disponibles,), use_container_width=True)
                col2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
                
                st.write("---")
                if st.session_state.seleccionados:
                    if st.button("📄 Generar PDF de Selección", use_container_width=True):
                        with st.status("Preparando PDF con QR...", expanded=True) as status:
                            df_sel = df_raiz[df_raiz['Naturaleza'].isin(st.session_state.seleccionados)]
                            pdf_data = generar_pdf_con_qr(df_sel, raiz_final)
                            time.sleep(1)
                            status.update(label="✅ PDF generado con éxito", state="complete", expanded=False)
                        st.download_button("⬇️ Descargar PDF", data=pdf_data, file_name=f"Acordes_{raiz_final}.pdf", mime="application/pdf", use_container_width=True)
            else:
                st.warning(f"La nota {raiz_final} no está en la base de datos.")

        elif modo == "Identificador 🔍":
            st.write("**Selecciona Notas:**")
            notas_id_list = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
            for i in range(0, len(notas_id_list), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(notas_id_list):
                        n = notas_id_list[i + j]
                        es_activa = n in st.session_state.notas_id
                        if cols[j].button(n, key=f"id_side_{n}", type="primary" if es_activa else "secondary"):
                            if es_activa: st.session_state.notas_id.remove(n)
                            else: st.session_state.notas_id.add(n)
                            st.rerun()
            if st.button("Limpiar Notas", use_container_width=True):
                st.session_state.notas_id = set(); st.rerun()

        st.write("---")
        st.write("📲 **Compartir App**")
        qr_side_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_side_url, caption="Escaneá para abrir", width=180)
        st.text_input("Enlace:", value=APP_URL, disabled=True)

    # CUERPO PRINCIPAL
    if modo == "Diccionario 📖":
        if not df_raiz.empty:
            st.header(f"📖 Diccionario: {raiz_final}")
            tipos_para_mostrar = [t for t in orden_tipos if t in st.session_state.seleccionados]
            if tipos_para_mostrar:
                tabs = st.tabs(tipos_para_mostrar)
                for i, tab in enumerate(tabs):
                    with tab:
                        row = df_raiz[df_raiz['Naturaleza'] == tipos_para_mostrar[i]].iloc[0]
                        mostrar_detalle_acorde(row)
            else: st.info("Seleccioná tipos en el sidebar.")

    elif modo == "Identificador 🔍":
        st.header("🔍 Identificador de Acordes")
        if st.session_state.notas_id:
            res = df[df.apply(lambda r: set([str(r[x]) for x in ['N1','N2','N3','N4'] if pd.notna(r[x])]) == st.session_state.notas_id, axis=1)]
            if not res.empty:
                st.success("✅ Acorde Identificado:")
                mostrar_detalle_acorde(res.iloc[0])
            else: st.warning("No se encontró el acorde en la base.")
        else: st.info("Selecciona las notas en la barra lateral.")
