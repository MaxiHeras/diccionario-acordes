import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTADO
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(
    page_title="Diccionario de Acordes", 
    layout="wide", 
    initial_sidebar_state=st.session_state.sb_state
)

# --- DATOS Y QR ---
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypTp45pMAOjyno/gviz/tq?tqx=out:csv"
QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

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
    # 2. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        r_list = sorted(df['Raiz'].unique())
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())
        
        # QR MÁS GRANDE
        st.write("---")
        st.image(QR_URL, caption="Compartir App", width=200)
        
        for _ in range(5): st.write("") 
        
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun()
            else:
                st.warning("Selecciona un tipo")

    # 3. RESULTADOS
    if nat_sel:
        st.session_state.sb_state = "collapsed"
        df_filtro = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtro.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # NOTAS CON GUIONES
                cols_n = ['N1','N2','N3','N4']
                ns = [str(row[c]).strip() for c in cols_n if c in row and pd.notna(row[c]) and str(row[c]).lower()!='nan']
                st.write(f"**Notas:** {' - '.join(ns)}")

                # INTERVALOS
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")

                # --- GALERÍA HORIZONTAL (CELULAR Y PC) ---
                imgs = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]) and str(row[col]) not in ["0","nan",""]:
                        img_name = str(row[col]).split('/')[-1]
                        url = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{img_name}"
                        imgs.append(url)

                if imgs:
                    # Construcción del HTML de forma más robusta
                    html_items = ""
                    for idx, url in enumerate(imgs):
                        html_items += f'<div style="flex:0 0 auto; text-align:center;"><img src="{url}" width="110"><p style="font-size:12px;color:gray;">P{idx+1}</p></div>'
                    
                    galeria = f'<div style="display:flex; overflow-x:auto; gap:15px; padding:10px 0;">{html_items}</div>'
                    st.markdown(galeria, unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas")
    else:
        st.info("Configura tu acorde a la izquierda.")
else:
    st.error("Error al conectar con el Excel.")
