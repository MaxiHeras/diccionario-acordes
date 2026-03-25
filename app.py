import streamlit as st
import pandas as pd

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
APP_URL = "https://diccionario-acordes-xz99pzx875gw2ytzpqxacv.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={APP_URL}"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        
        # ORDEN PERSONALIZADO
        orden_deseado = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
        tipos_reales = df_raiz['Naturaleza'].unique()
        opciones_finales = [t for t in orden_deseado if t in tipos_reales] + sorted([t for t in tipos_reales if t not in orden_deseado])

        # --- LÓGICA DE CONTROL DE SELECCIÓN ---
        if 'selector_key' not in st.session_state:
            st.session_state.selector_key = 0
        if 'valores_actuales' not in st.session_state:
            st.session_state.valores_actuales = opciones_finales

        # El multiselect usa una 'key' que cambia para forzar el refresco
        nat_sel = st.multiselect(
            "Tipo:", 
            options=opciones_finales, 
            default=st.session_state.valores_actuales,
            key=f"ms_{st.session_state.selector_key}"
        )

        col_btn1, col_btn2 = st.columns(2)
        
        if col_btn1.button("Todo", use_container_width=True):
            st.session_state.valores_actuales = opciones_finales
            st.session_state.selector_key += 1 # Cambiamos la key para resetear el widget
            st.rerun()

        if col_btn2.button("Limpiar", use_container_width=True):
            st.session_state.valores_actuales = []
            st.session_state.selector_key += 1 # Cambiamos la key para resetear el widget
            st.rerun()
        
        st.write("---")
        st.image(URL_QR, caption="Escanear para compartir", width=180)
        st.caption("**Enlace de la App:**")
        st.code(APP_URL, language=None)

    # 4. RESULTADOS
    if nat_sel:
        # Re-ordenar el DataFrame para los resultados
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)].copy()
        df_f['Naturaleza'] = pd.Categorical(df_f['Naturaleza'], categories=opciones_finales, ordered=True)
        df_f = df_f.sort_values('Naturaleza')
        
        # Si hay más de 1 tipo, aparece contraído
        esta_expandido = True if len(nat_sel) == 1 else False
        
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
                GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
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
