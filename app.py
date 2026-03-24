import streamlit as st
import pandas as pd

# 1. ESTADO Y CONFIGURACIÓN
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(
    page_title="Diccionario de Acordes", 
    layout="wide", 
    initial_sidebar_state=st.session_state.sb_state
)

# --- CSS PARA MODO OSCURO E INTERFAZ (Scroll Horizontal) ---
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) {
        .chord-img { filter: invert(1) hue-rotate(180deg); }
    }
    .scroll-container { 
        display: flex; 
        overflow-x: auto; 
        gap: 15px; 
        padding: 10px 0; 
        -webkit-overflow-scrolling: touch; /* Scroll suave en iOS */
    }
    .chord-item { 
        flex: 0 0 auto; 
        text-align: center; 
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS Y QR ---
URL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

# Definimos el orden musical deseado
ORDEN_MUSICAL = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']

@st.cache_data
def load_and_clean_data():
    try:
        df = pd.read_csv(URL)
        # Limpieza inicial de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- LIMPIEZA PROFUNDA DE DATOS ---
        # 1. Convertimos las columnas de diagramas a texto
        columnas_diagramas = [f'Diagrama{i}' for i in range(1, 10)]
        for col in columnas_diagramas:
            if col in df.columns:
                # Convertimos a string, eliminamos espacios al inicio/final y pasamos a minúsculas
                df[col] = df[col].astype(str).str.strip().str.lower()
                
                # Reemplazamos valores que Pandas lee como vacíos por '0'
                df[col] = df[col].replace({'nan': '0', 'none': '0', '': '0'})

        return df
    except:
        return None

df = load_and_clean_data()

if df is not None:
    # 2. BARRA LATERAL (Sidebar)
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        # Filtramos el orden musical para que solo aparezcan las notas que existen en el Excel
        notas_existentes = df['Raiz'].unique()
        r_list = [n for n in ORDEN_MUSICAL if n in notas_existentes]
        
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        df_r = df[df['Raiz'] == raiz_sel]
        
        # Selector de Naturaleza (Tipo de acorde)
        nat_sel = st.multiselect("Tipo:", options=df_r['Naturaleza'].unique())
        
        # QR Grande al fondo
        st.write("---")
        st.image(QR_URL, caption="Compartir App", width=220) # Aumentado a 220
        
        # Espaciador para empujar el botón al fondo
        for _ in range(6): st.write("") 
        
        # Botón "Mostrar acordes"
        if st.button("✅ Mostrar acordes", use_container_width=True, type="primary"):
            if nat_sel:
                st.session_state.sb_state = "collapsed"
                st.rerun() # Esto cierra la barra lateral inmediatamente
            else:
                st.warning("Elegí al menos un tipo de acorde.")

    # 3. RESULTADOS (Pantalla Principal)
    if nat_sel:
        # Aseguramos que la barra lateral permanezca colapsada si hay una selección activa
        st.session_state.sb_state = "collapsed"
        
        # Filtramos los datos finales
        df_filtrado = df_r[df_r['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # NOTAS CON SEPARADOR " - "
                col_n = ['N1','N2','N3','N4']
                # Limpieza de notas (quitamos espacios y 'nan')
                notas_list = []
                for c in col_n:
                    val = str(row.get(c, '')).strip()
                    if pd.notna(row.get(c)) and val.lower() != 'nan' and val != '':
                        notas_list.append(val)
                st.write(f"**Notas:** {' - '.join(notas_list)}")

                # INTERVALOS
                st.info(f"**Int_IVAN:** {row.get('Int_IVAN', '')}")
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                    # Solo mostramos Int_TRAD si no es nulo
                    val_trad = str(row['Int_TRAD']).strip()
                    if val_trad.lower() != 'nan' and val_trad != '':
                        st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")

                # --- GALERÍA HORIZONTAL (Blindada contra iconos rotos) ---
                imgs = []
                # Ahora que los datos están limpios ('load_and_clean_data'), 
                # sabemos que un '0' significa "no hay imagen".
                for i in range(1, 10):
                    col_name = f'Diagrama{i}'
                    # Obtenemos el valor ya limpio
                    img_filename = row.get(col_name, '0')
                    
                    if img_filename != '0':
                        # Construimos la URL
                        # Nota: .split('/')[-1] por si el Excel traía la ruta completa
                        url = f"https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main/{row['Naturaleza']}/{img_filename.split('/')[-1]}"
                        imgs.append(url)

                # Mostramos la galería solo si hay imágenes que cargar
                if imgs:
                    # Usamos 'enumerate' para tener el índice P1, P2...
                    h_items = "".join([f'<div class="chord-item"><img src="{u}" class="chord-img" width="120"><p style="font-size:13px;color:gray;margin-top:5px;">P{i+1}</p></div>' for i, u in enumerate(imgs)])
                    
                    # Markdown con unsafe_allow_html para inyectar la galería horizontal
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
