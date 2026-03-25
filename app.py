import streamlit as st
import pandas as pd

# Configuración básica
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# Carga de datos
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error cargando Excel: {e}")
        return None

df = load()

if df is not None:
    # Sidebar de filtros
    with st.sidebar:
        st.header("🔍 Filtros")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())

    # Mostrar resultados
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Notas e Intervalos
                n_str = ' - '.join([str(row[c]) for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]) not in ['0','nan','']])
                st.write(f"**Notas:** {n_str}")
                
                col1, col2 = st.columns(2)
                with col1:
                    ivan = str(row.get('Int_IVAN', '')).strip()
                    if ivan and ivan.lower() not in ['nan', '0', '']: st.info(f"**Int_IVAN:** {ivan}")
                with col2:
                    trad = str(row.get('Int_TRAD', '')).strip()
                    if trad and trad.lower() not in ['nan', '0', '']: st.success(f"**Int_TRAD:** {trad}")
                
                # Galería de imágenes (Web)
                h_html = ""
                BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                for i in range(1, 10):
                    v = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if v.lower().endswith('.png'):
                        url = f"{BASE}/{row['Naturaleza']}/{v.split('/')[-1]}"
                        h_html += f'<div class="chord-item"><img src="{url}" class="chord-img" width="110"><p>P{i}</p></div>'
                
                if h_html:
                    st.markdown(f'<div class="scroll-container">{h_html}</div>', unsafe_allow_html=True)
    else:
        st.info("Selecciona un acorde en el menú lateral.")
