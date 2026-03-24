import streamlit as st
import pandas as pd

# 1. ESTADO Y CONFIGURACIÓN
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# --- CSS PARA MODO OSCURO E INTERFAZ (Scroll Horizontal) ---
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) {
        .chord-img { filter: invert(1) hue-rotate(180deg); }
    }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS Y QR ---
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

if df is not None:
    # 2. BARRA LATERAL (Sidebar)
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        # ORDEN MUSICAL PERSONALIZADO (C, D, E, F, G, A, B)
        orden_musical = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        notas_en_df = df['Raiz'].unique()
        r_list = [n for n in orden_musical if n in notas_en_df]
        
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        # Filtro inmediato por raíz para el multiselect
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())
        
        st.write("---")
        st.image(QR, caption="Compartir App", width=180)
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()

    # 3. RESULTADOS (Pantalla Principal)
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Limpieza de notas (evita mostrar 'nan' o '0')
                notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(notas)}")
                
                st.write("---")
                
                # --- GALERÍA HORIZONTAL CON FILTRO ESTRICTO ---
                h_items = ""
                # Definimos la base de GitHub (asegúrate de que no termine en /)
                GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                
                for i in range(1, 10):
                    c = f'Diagrama{i}'
                    # Obtenemos el valor como texto limpio
                    val = str(row.get(c, '0')).strip()
                    
                    # FILTRO CRÍTICO: Solo procesar si termina en extensión de imagen (png, jpg)
                    # Esto ignorará las celdas vacías o que digan "0".
                    if val.lower().endswith(('.png', '.jpg', '.jpeg')):
                        # CORRECCIÓN DE URL: Unimos la base directamente con la ruta del Excel
                        # val ya es "Diagramas/Mayores/C-MAY-1.png", por lo que no hace falta split
                        url_img = f"{GITHUB_BASE}/{val}"
                        
                        # Generamos el HTML. Usamos ID único por posición y acorde.
                        div_id = f"pos_{idx}_{i}"
                        
                        h_items += f'''
                        <div class="chord-item" id="{div_id}">
                            <img src="{url_img}" class="chord-img" width="115" onerror="document.getElementById(\'{div_id}\').style.display=\'none\';">
                            <p style="font-size:12px;color:gray;">P{i}</p>
                        </div>
                        '''
                
                if h_items:
                    # Inyectamos el HTML de la galería horizontal
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas disponibles para este acorde en tu repositorio de GitHub.")
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("Error al conectar con el Excel. Revisa la URL.")
