import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(page_title="Acordes", layout="wide", initial_sidebar_state=st.session_state.sb_state)

# CSS para Galería y Modo Oscuro
st.markdown("""
<style>
@media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
.scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
.chord-item { flex: 0 0 auto; text-align: center; border: 1px solid #ddd; padding: 5px; border-radius: 5px; }
.error-box { color: white; background: #ff4b4b; padding: 5px; font-size: 10px; border-radius: 3px; max-width: 115px; }
</style>
""", unsafe_allow_html=True)

URL_DATA = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_DATA)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

if df is not None:
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        orden_m = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in orden_m if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()

    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_f = df_r[df_r['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.write("---")
                st.subheader("Posiciones (Si ves ROJO, borra esa celda en Excel)")

                h_items = ""
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', '')).strip()
                    
                    if val not in ['nan', '0', '']:
                        f = val.split('/')[-1]
                        url_img = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{f}"
                        
                        # Si la imagen falla, muestra el nombre del archivo en un cuadro rojo
                        h_items += f'''
                        <div class="chord-item">
                            <img src="{url_img}" class="chord-img" width="115" 
                                 onerror="this.style.display='none'; this.nextSibling.style.display='block';">
                            <div class="error-box" style="display:none;">⚠️ ERROR EN EXCEL:<br>"{val}"</div>
                            <p style="font-size:12px;color:gray;">P{i}</p>
                        </div>
                        '''
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay datos en las columnas de diagramas.")
else:
    st.error("Error al conectar con el Excel.")
