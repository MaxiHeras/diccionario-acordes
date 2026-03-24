import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS para evitar imágenes rotas y galería horizontal
st.markdown("""
<style>
@media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
.scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
.chord-item { flex: 0 0 auto; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS (URLs en una sola línea para evitar el SyntaxError)
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df = load_data()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        notas_disp = [n for n in orden if n in df['Raiz'].unique()]
        
        raiz_sel = st.selectbox("Nota Raíz:", notas_disp)
        df_r = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.write("---")
        st.image(QR, caption="Compartir App", width=200)
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()

    # 4. RESULTADOS
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_f = df_r[df_r['Naturaleza'].isin(nat_sel)]
        
        for index, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Notas
                ns = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(ns)}")
                
                # Info
                if 'Int_IVAN' in row and pd.notna(row['Int_IVAN']): st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                
                st.write("---")
                st.subheader("Posiciones")

                # GALERÍA HORIZONTAL (Con filtro estricto para no mostrar imágenes rotas)
                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', '0')).strip().lower()
                    
                    # Solo procesamos si la celda termina en .png (esto ignora las celdas borradas)
                    if val.endswith('.png'):
                        nombre_archivo = val.split('/')[-1]
                        url_img = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{nombre_archivo}"
                        
                        # El 'onerror' es el seguro final: si falla, desaparece todo el cuadrito
                        id_div = f"wrap_{index}_{i}"
                        h_items += f'<div class="chord-item" id="{id_div}"><img src="{url_img}" class="chord-img" width="115" onerror="document.getElementById(\'{id_div}\').style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas disponibles.")
    else:
        st.info("Elegí un acorde en el menú de la izquierda.")
else:
    st.error("No se pudo cargar el Excel.")
