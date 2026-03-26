import streamlit as st
import pandas as pd
import requests
from fpdf import FPDF
from io import BytesIO
import urllib.parse

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# CSS: POSICIONAMIENTO, COLORES Y ESTILOS
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
    div[data-testid="stRadio"] > div { gap: 20px; margin-top: 10px; }
    @media (prefers-color-scheme: dark) { .chord-img-web { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex !important; overflow-x: auto !important; gap: 15px !important; padding: 10px 0 !important; flex-wrap: nowrap !important; }
    .chord-diag-item { flex: 0 0 auto !important; width: 150px !important; text-align: center; }
    .chord-img-web { width: 100% !important; height: auto !important; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 5px !important; }
    [data-testid="stSidebar"] [data-testid="column"] { width: 32% !important; flex: 1 1 32% !important; min-width: 32% !important; }
    .stButton > button { width: 100% !important; padding: 5px 2px !important; font-size: 13px !important; min-height: 42px !important; border-radius: 6px !important; }
    
    /* URL con fuente monoespaciada para facilitar copia manual */
    .stTextInput input:disabled {
        -webkit-text-fill-color: #31333F !important;
        opacity: 1 !important;
        cursor: text !important;
        background-color: #f0f2f6 !important;
        font-family: monospace !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
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

# Estados de sesión
if "seleccionados" not in st.session_state: st.session_state.seleccionados = []
if "notas_inversas" not in st.session_state: st.session_state.notas_inversas = set()
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None
if "descargado" not in st.session_state: st.session_state.descargado = False
if "filtro_alteracion" not in st.session_state: st.session_state.filtro_alteracion = "Nat."

def seleccionar_todo(opciones): st.session_state.seleccionados = opciones
def limpiar_todo(): 
    st.session_state.seleccionados = []
    st.session_state.pdf_data = None
    st.session_state.descargado = False

def toggle_nota(nota):
    if nota in st.session_state.notas_inversas: st.session_state.notas_inversas.remove(nota)
    else: st.session_state.notas_inversas.add(nota)

def mostrar_detalle_acorde(row):
    st.markdown(f"### {row['Raiz']} {row['Naturaleza']}")
    lista_n = [str(row.get(n,'')).strip() for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))]
    st.write(f"**Notas:** {' - '.join(lista_n)}")
    c1, c2 = st.columns(2)
    with c1: st.success(f"**Int_IVAN:** {row.get('Int_IVAN','N/A')}") 
    with c2: st.info(f"**Int_TRAD:** {row.get('Int_TRAD','N/A')}")
    st.write("---")
    st.write("**Diagramas:**")
    h_items = ""
    for j in range(1, 10):
        v = str(row.get(f'Diagrama{j}', 'nan')).strip()
        if v.lower().endswith('.png'):
            nat_cod = urllib.parse.quote(str(row['Naturaleza']))
            img_name = v.split('/')[-1].replace('#', 'SOS')
            url = f"{GITHUB_BASE}/{nat_cod}/{img_name}"
            h_items += f'<div class="chord-diag-item"><img src="{url}" class="chord-img-web"><p style="font-size:12px;color:gray;">P{j}</p></div>'
    if h_items: st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)

class PDF_Final(FPDF):
    def footer(self):
        # MODIFICACIÓN: Nuevo Footer ALINEADO A LA DERECHA con QR y texto
        self.set_y(-30) # Subimos un poco el footer para que entre el QR
        
        # 1. Insertar el QR (descargándolo de la URL)
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(APP_URL)}"
        try:
            # Posicionamos el QR alineado a la derecha
            # Ancho A4 es 210mm. QR de 20mm de ancho. Margen derecho de 15mm.
            # 210 - 20 - 15 = 175
            self.image(qr_url, x=175, y=self.get_y(), w=20, h=20)
        except:
            # Si falla la descarga, no mostramos nada para no romper el PDF
            pass
            
        # 2. Insertar el texto debajo del QR
        self.set_y(self.get_y() + 22) # Bajamos 22mm para el texto (20 del QR + 2 de margen)
        self.set_font("helvetica", "", 10) # Fuente normal, tamaño 10 como en el caption
        self.set_text_color(128, 128, 128) # Gris medio
        # Alineamos el texto a la derecha
        self.cell(0, 5, "by Maxi Heras - Tucumán", align='R', ln=True)

def generar_pdf(dataframe_seleccionado):
    pdf = PDF_Final(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=35) # Aumentamos el margen inferior para el nuevo footer
    for _, row in dataframe_seleccionado.iterrows():
        pdf.add_page()
        pdf.set_font("helvetica", "B", 24)
        pdf.cell(0, 20, f"{row['Raiz']} {row['Naturaleza']}", border=1, ln=True, align='C')
        pdf.ln(8) 
        pdf.set_font("helvetica", "B", 11); pdf.write(6, "Notas: "); pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{' - '.join([str(row.get(n,'')).strip() for n in ['N1','N2','N3','N4'] if pd.notna(row.get(n))])}\n")
        pdf.set_font("helvetica", "B", 11); pdf.write(6, "Int_IVAN: "); pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{str(row.get('Int_IVAN', 'N/A'))}\n")
        pdf.set_font("helvetica", "B", 11); pdf.write(6, "Int_TRAD: "); pdf.set_font("helvetica", "", 11)
        pdf.write(6, f"{str(row.get('Int_TRAD', 'N/A'))}\n")
        pdf.ln(14) 
        X_START, GAP_X, GAP_Y, COLS, DIAG_W, DIAG_H = 15, 8, 12, 4, 38, 45
        y_grid_top = pdf.get_y()
        count = 0
        for i in range(1, 10):
            val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if val.lower().endswith('.png'):
                nat_pdf = urllib.parse.quote(str(row['Naturaleza']))
                img_name_pdf = val.split('/')[-1].replace('#', 'SOS')
                url_img = f"{GITHUB_BASE}/{nat_pdf}/{img_name_pdf}"
                try:
                    resp = requests.get(url_img, timeout=5)
                    if resp.status_code == 200:
                        img_data = resp.content
                        col, fila = count % COLS, count // COLS
                        pos_x = X_START + (col * (DIAG_W + GAP_X))
                        pos_y = y_grid_top + (fila * (DIAG_H + GAP_Y))
                        pdf.image(BytesIO(img_data), x=pos_x, y=pos_y, w=DIAG_W, h=DIAG_H)
                        count += 1
                except: continue
    return pdf.output()

df = load()
if df is not None:
    notas_musicales = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
    orden_tipos = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    with st.sidebar:
        st.subheader("Seleccionar Modo")
        modo_previo = st.session_state.get("modo_actual", "Diccionario 📖")
        modo = st.radio(" ", ["Diccionario 📖", "Identificador 🔍"], label_visibility="collapsed")
        st.session_state.modo_actual = modo
        
        if modo != modo_previo:
            if "u_raiz" in st.session_state: del st.session_state.u_raiz

        st.write("---")

        if modo == "Diccionario 📖":
            st.write("Filtrar Alteración:")
            f_cols = st.columns(3)
            
            nat = f_cols[0].checkbox("Nat.", value=(st.session_state.filtro_alteracion == "Nat."))
            sost = f_cols[1].checkbox("Sost.", value=(st.session_state.filtro_alteracion == "Sost."))
            bem = f_cols[2].checkbox("Bem.", value=(st.session_state.filtro_alteracion == "Bem."))
            
            if nat and st.session_state.filtro_alteracion != "Nat.":
                st.session_state.filtro_alteracion = "Nat."
                if "u_raiz" in st.session_state: del st.session_state.u_raiz
                st.rerun()
            elif sost and st.session_state.filtro_alteracion != "Sost.":
                st.session_state.filtro_alteracion = "Sost."
                if "u_raiz" in st.session_state: del st.session_state.u_raiz
                st.rerun()
            elif bem and st.session_state.filtro_alteracion != "Bem.":
                st.session_state.filtro_alteracion = "Bem."
                if "u_raiz" in st.session_state: del st.session_state.u_raiz
                st.rerun()
            elif not nat and not sost and not bem:
                st.session_state.filtro_alteracion = "Nat."
                if "u_raiz" in st.session_state: del st.session_state.u_raiz
                st.rerun()

            if st.session_state.filtro_alteracion == "Nat.":
                notas_filtradas = [n for n in notas_musicales if len(n) == 1]
            elif st.session_state.filtro_alteracion == "Sost.":
                notas_filtradas = [n for n in notas_musicales if "#" in n]
            else:
                notas_filtradas = [n for n in notas_musicales if "b" in n]

            raiz_sel = st.selectbox("Nota Raíz:", [n for n in notas_filtradas if n in df['Raiz'].unique()])
            
            df_raiz = df[df['Raiz'] == raiz_sel]
            opciones = [t for t in orden_tipos if t in df_raiz['Naturaleza'].unique()]
            
            if "u_raiz" not in st.session_state or st.session_state.u_raiz != raiz_sel:
                st.session_state.u_raiz = raiz_sel
                st.session_state.seleccionados = opciones
                st.session_state.pdf_data = None
                st.session_state.descargado = False
            
            st.multiselect("Tipo:", opciones, key="seleccionados")
            c1, c2 = st.columns(2)
            c1.button("Todo", on_click=seleccionar_todo, args=(opciones,), use_container_width=True)
            c2.button("Limpiar", on_click=limpiar_todo, use_container_width=True)
            st.write("")
            placeholder = st.empty()
            if st.session_state.descargado: placeholder.success("✅ ¡Listo, guardado!")
            elif st.session_state.pdf_data: placeholder.info("✅ ¡Listo para guardar!")
            if st.button("📥 Generar PDF de Selección", use_container_width=True):
                df_para_pdf = df_raiz[df_raiz['Naturaleza'].isin(st.session_state.seleccionados)]
                if not df_para_pdf.empty:
                    placeholder.markdown("⏳ *Preparando PDF...*")
                    st.session_state.pdf_data = generar_pdf(df_para_pdf)
                    st.session_state.descargado = False
                    st.rerun()
            if st.session_state.pdf_data:
                st.download_button("💾 GUARDAR ARCHIVO", bytes(st.session_state.pdf_data), f"Acordes_{raiz_sel}.pdf", "application/pdf", use_container_width=True, type="primary", on_click=lambda: st.session_state.update({"descargado": True}))
        else:
            st.write("### Identificador")
            for i in range(0, len(notas_musicales), 3):
                cols = st.columns(3)
                for j in range(3):
                    idx = i + j
                    if idx < len(notas_musicales):
                        n = notas_musicales[idx]
                        active = n in st.session_state.notas_inversas
                        with cols[j]:
                            if st.button(n, key=f"id_{n}", type="primary" if active else "secondary"):
                                toggle_nota(n); st.rerun()
            if st.button("🗑️ Borrar Notas", use_container_width=True):
                st.session_state.notas_inversas = set(); st.rerun()

        st.write("---")
        st.write("📲 **Compartir App**")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={urllib.parse.quote(APP_URL)}"
        st.image(qr_url, caption="Escaneá para abrir", width=180)
        st.text_input("Enlace de la app:", value=APP_URL, disabled=True, help="Haz clic y arrastra para copiar")
        st.caption("by Maxi Heras - Tucumán")

    # CUERPO PRINCIPAL
    if modo == "Diccionario 📖":
        st.header(f"📖 Diccionario: {raiz_sel}")
        tipos_visibles = [t for t in orden_tipos if t in st.session_state.seleccionados]
        if tipos_visibles:
            tabs = st.tabs(tipos_visibles)
            for i, tab in enumerate(tabs):
                with tab:
                    row = df_raiz[df_raiz['Naturaleza'] == tipos_visibles[i]].iloc[0]
                    mostrar_detalle_acorde(row)
        else: st.info("Seleccioná tipos en el sidebar.")
    else:
        st.header("🔍 Identificador de Acordes")
        notas_act = {n.strip() for n in st.session_state.notas_inversas}
        res = df[df.apply(lambda r: set([str(r[n]).strip() for n in ['N1','N2','N3','N4'] if pd.notna(r[n])]) == notas_act, axis=1)]
        if notas_act:
            if not res.empty: mostrar_detalle_acorde(res.iloc[0])
            else: st.warning("Acorde no identificado.")
        else: st.info("Seleccioná notas en la barra lateral.")
