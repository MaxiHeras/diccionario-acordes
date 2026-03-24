import streamlit as st
import pandas as pd

# 1. ESTADO DE LA BARRA LATERAL
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(
    page_title="Acordes", 
    layout="wide", 
    initial_sidebar_state=st.session_state.sb_state
)

# --- DATOS Y QR ---
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

if df is not None:
    # 2. CONFIGURACIÓN EN BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        r_sel = st.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
        df_r = df[df['Raiz'] == r_sel]
        n_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        st.write("---")
        st.image(QR, caption="Compartir App", width=120)
        
        # Espaciador para llevar el botón al final
        for _ in range(10): st.write("") 
        
        # BOTÓN QUE OCULTA LA BARRA
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if n_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun() # Esto cierra la barra lateral inmediatamente
            else:
                st.warning("Elegí un acorde")

    # 3. RESULTADOS EN PANTALLA PRINCIPAL
    if n_sel:
        # Botón para reabrir la barra si está oculta
        if st.session_state.sb_state == "collapsed":
            if st.button("⬅️ Cambiar Selección"):
                st.session_state.sb_state = "expanded"
                st.rerun()

        for _, row in df_r[df_r['Naturaleza'].isin(n_sel)].iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Notas con separador " - "
                col_n = ['N1','N2','N3','N4']
                ns = [str(row[c]).strip() for c in col_n if c in row and pd.notna(row[c]) and str(row[c]).lower()!='nan']
                st.write(f"**Notas:** {' - '.join(ns)}")

                # Intervalos
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                # Diagramas compactos para móvil
                imgs = []
                for i in range(1, 10):
                    c = f'Diagrama{i}'
                    if c in row and pd.notna(row[c]) and str(row[c]) not in ["0","nan",""]:
                        f = str(row[c]).split('/')[-1]
                        imgs.append(f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{f}")

                if imgs:
                    cols = st.columns(len(imgs))
                    for idx, url in enumerate(imgs):
                        with cols[idx]:
                            st.image(url, width=100)
                            st.caption(f"P{idx+1}")
    else:
        st.info("Configurá tu acorde en el menú lateral.")
else:
    st.error("Error de conexión con la base de datos.")
