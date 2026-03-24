import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA Y ESTADO
# Usamos el estado de la sesión para manejar si la barra lateral está expandida o colapsada
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(
    page_title="Diccionario de Acordes",
    layout="wide",
    initial_sidebar_state=st.session_state.sb_state
)

# --- CSS PERSONALIZADO (Galería Horizontal Blindada y Modo Oscuro) ---
st.markdown("""
<style>
/* Filtro para invertir colores de diagramas en modo oscuro (opcional pero recomendado) */
@media (prefers-color-scheme: dark) {
    .chord-img {
        filter: invert(1) hue-rotate(180deg);
    }
}

/* Contenedor principal de la galería horizontal con scroll */
.scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 15px;
    padding: 10px 0;
    /* Para scroll suave en dispositivos móviles */
    -webkit-overflow-scrolling: touch;
}

/* Estilo para cada ítem de la galería (imagen + texto Px) */
.chord-item {
    flex: 0 0 auto;
    text-align: center;
}

/* Estilo para la imagen del acorde */
.chord-img {
    object-fit: contain; /* Asegura que la imagen no se deforme */
}
</style>
""", unsafe_allow_html=True)


# 2. CARGA Y LIMPIEZA DE DATOS
# URLs completas en una sola línea para evitar SyntaxError al copiar/pegar
URL_DATA = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv(URL_DATA)
        # Limpieza inicial: quitar espacios en los nombres de las columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- LIMPIEZA PROFUNDA DE DATOS (Solución a imágenes rotas) ---
        # Convertimos las columnas de diagramas a texto limpio
        columnas_diagramas = [f'Diagrama{i}' for i in range(1, 10)]
        for col in columnas_diagramas:
            if col in df.columns:
                # Convertimos a string, quitamos espacios al inicio y final, y pasamos a minúsculas
                df[col] = df[col].astype(str).str.strip().str.lower()
                # Reemplazamos valores que Pandas lee como vacíos por '0'
                df[col] = df[col].replace({'nan': '0', 'none': '0', '': '0'})

        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

df = load_and_clean_data()


# 3. INTERFAZ DE USUARIO
if df is not None:
    # --- BARRA LATERAL (Sidebar) ---
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        # Definimos el orden musical deseado
        orden_musical = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        
        # Filtramos el orden musical para mostrar solo las notas que existen en el Excel
        notas_existentes = df['Raiz'].unique()
        r_list = [n for n in orden_musical if n in notas_existentes]
        
        # Selector de Nota Raíz
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        
        # Selector de Naturaleza (Tipo de acorde)
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        # Código QR Grande
        st.write("---")
        st.image(URL_QR, caption="Compartir App", width=220)
        
        # Espaciador para empujar el botón al fondo
        for _ in range(6): st.write("") 
        
        # Botón para mostrar acordes
        if st.button("Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                # Si hay selección, colapsamos la barra lateral y recargamos
                st.session_state.sb_state = "collapsed"
                st.rerun()
            else:
                st.warning("Elegí al menos un tipo de acorde.")

    # --- PANTALLA PRINCIPAL DE RESULTADOS ---
    if nat_sel:
        # Aseguramos que la barra lateral permanezca colapsada si hay una selección activa
        st.session_state.sb_state = "collapsed"
        
        # Filtramos los datos finales
        df_filtrado = df_r[df_r['Naturaleza'].isin(nat_sel)]
        
        for index, row in df_filtrado.iterrows():
            # Creamos un desplegable (expander) para cada acorde
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # NOTAS CON SEPARADOR " - "
                cols_notas = ['N1','N2','N3','N4']
                notas_list = []
                for c in cols_notas:
                    val_nota = str(row.get(c, '')).strip()
                    # Filtramos nulos o vacíos
                    if pd.notna(row.get(c)) and val_nota.lower() != 'nan' and val_nota != '':
                        notas_list.append(val_nota)
                st.write(f"**Notas:** {' - '.join(notas_list)}")

                # INTERVALOS
                if pd.notna(row.get('Int_IVAN')):
                    st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                
                # Intervalo Tradicional (opcional)
                if 'Int_TRAD
