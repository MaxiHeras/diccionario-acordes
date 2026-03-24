import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTADO
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = "expanded"

st.set_page_config(
    page_title="Diccionario de Acordes", 
    layout="wide", 
    initial_sidebar_state=st.session_state.sidebar_state
)

# --- DATOS ---
USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_SHEET = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(URL_SHEET)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df = cargar_datos()

if df is not None:
    st.title("🎸 Diccionario de Acordes")
    
    # 2. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        # Selectores
        raices = sorted(df['Raiz'].unique())
        raiz_sel = st.selectbox("Nota Raíz:", raices)
        df_raiz = df[df['Raiz'] == raiz_sel]
        
        nat_sel = st.multiselect("Tipo de Acorde:", options=df_raiz['Naturaleza'].unique())
        
        # Espacio para empujar el botón al fondo (Cerca del borde inferior)
        for _ in range(12):
            st.write("") 

        # BOTÓN FINAL
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sidebar_state = "collapsed"
                st.rerun()
            else:
                st.warning("Elegí un acorde.")

    # 3. MOSTRAR RESULTADOS
    if nat_sel:
        # Botón auxiliar por si se oculta la barra y quieres volver
        if st.session_state.sidebar_state == "collapsed":
            if st.button("⬅️ Cambiar Selección"):
                st.session_state.sidebar_state = "expanded"
                st.rerun()

        df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                
                # Notas con separador " - "
                columnas_n = ['N1', 'N2', 'N3', 'N4']
                notas_list = []
                for c in columnas_n:
                    val = str(row.get(c, 'nan')).strip()
                    if val.lower() != 'nan' and val != "":
                        notas_list.append(val)
                
                st.write(f"**Notas:** {' - '.join(notas_list)}")

                # Intervalos
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")
                
                # Imágenes compactas para celular
                imgs = []
                for i in range(1, 10):
                    col_name = f'Diagrama{i}'
                    if col_name in row and pd.notna(row[col_name]):
                        img_val = str(row[col_name]).strip()
                        if img_val not in ["0", "nan", ""]:
                            filename = img_val.split('/')[-1]
                            url = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{filename}"
                            imgs.append(url)

                if imgs:
                    # Crea solo las columnas que tienen fotos para evitar errores visuales
                    cols = st.columns(len(imgs))
                    for idx, url in enumerate(imgs):
                        with cols[idx]:
                            st.image(url, width=105)
                            st.caption(f"P{idx+1}")
                else:
                    st.warning("Sin diagramas.")
    else:
        st.info("Configurá tu acorde a la izquierda.")
else:
    st.error("Error
