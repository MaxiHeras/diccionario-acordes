import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN INICIAL
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS para galería y modo oscuro
st.markdown("<style>@media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } } .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; } .chord-item { flex: 0 0 auto; text-align: center; }</style>", unsafe_allow_html=True)

# 2. CARGA DE DATOS (Mantené estas URLs en una sola línea)
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL)
        # Limpieza de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df = load_data()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        
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

    # 4. RESULTADOS
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Limpieza de notas (evita mostrar 'nan' o '0')
                notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(notas)}")
                
                st.write("---")
                
                # GALERÍA HORIZONTAL CON FILTRO ESTRICTO
                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', 'nan')).strip().lower()
                    
                    # FILTRO: Solo si la celda contiene un archivo .png real
                    if val.endswith('.png'):
                        # Extraer solo el nombre del archivo (por si hay rutas largas)
                        archivo = val.split('/')[-1]
                        url_img = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{archivo}"
                        
                        # El ID único permite que el error de una imagen no afecte a las demás
                        div_id = f"cont_{idx}_{i}"
                        h_items += f'<div class="chord-item" id="{div_id}"><img src="{url_img}" class="chord-img" width="115" onerror="document.getElementById(\'{div_id}\').style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No se encontraron diagramas válidos.")
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("No se pudo cargar el Excel. Revisá que la URL sea correcta y esté en una sola línea.")
