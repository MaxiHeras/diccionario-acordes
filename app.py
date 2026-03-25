import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

# Estilos visuales para el scroll de diagramas e inversión de colores en modo oscuro
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURACIÓN DE DATOS Y COMPARTIR
APP_URL = "https://diccionario-acordes-kmwrk2p5uzfumx5tac3ff4.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={APP_URL}"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

df = load()

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        
        # Ordenamos las notas para el selector
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        # Filtramos las naturalezas según la nota raíz elegida
        df_raiz = df[df['Raiz'] == raiz_sel]
        opciones_tipo = sorted(df_raiz['Naturaleza'].unique())
        
        # Multiselect con todos los tipos seleccionados por defecto
        nat_sel = st.multiselect(
            "Tipo:", 
            options=opciones_tipo, 
            default=opciones_tipo
        )
        
        st.write("---")
        st.image(URL_QR, caption="Escanear para compartir", width=180)
        st.caption("**Enlace de la App:**")
        st.code(APP_URL, language=None)

    # 4. RESULTADOS
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        # LÓGICA DE EXPANSIÓN: Si hay más de 1 tipo seleccionado, aparece contraído (False)
        # Si hay solo 1, aparece expandido (True)
        expandir_por_defecto = True if len(nat_sel) == 1 else False
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=expandir_por_defecto):
                
                # NOTAS (N1 a N4)
                notas = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] 
                         if c in row and pd.notna(row[c]) and str(row[c]).lower() not in ['nan','','0']]
                st.write(f"**Notas:** {' - '.join(notas)}")
                
                # INTERVALOS
                col1, col2 = st.columns(2)
                ivan = str(row.get('Int_IVAN', '')).strip()
                trad = str(row.get('Int_TRAD', '')).strip()
                
                if ivan and ivan.lower() not in ['nan', '0', '']:
                    col1.info(f"**Int_IVAN:**\n\n{ivan}")
                if trad and trad.lower() not in ['nan', '0', '']:
                    col2.success(f"**Int_TRAD:**\n\n{trad}")
                
                st.write("---")
                
                # GALERÍA DE DIAGRAMAS (Carga desde GitHub)
                h_items = ""
                GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                
                for i in range(1, 10):
                    col_diag = f'Diagrama{i}'
                    val = str(row.get(col_diag, 'nan')).strip()
                    if val.lower().endswith('.png'):
                        nombre_archivo = val.split('/')[-1]
                        # Reemplazamos espacios por %20 para URLs válidas
                        naturaleza_url = str(row['Naturaleza']).replace(' ', '%20')
                        url_img = f"{GITHUB_BASE}/{naturaleza_url}/{nombre_archivo}"
                        
                        h_items += f'''
                            <div class="chord-item">
                                <img src="{url_img}" class="chord-img" width="110">
                                <p style="font-size:12px;color:gray;">P{i}</p>
                            </div>
                        '''
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
                else:
                    st.warning("No hay diagramas disponibles para este acorde.")
    else:
        st.info("Selecciona al menos un tipo de acorde en el menú lateral.")
else:
    st.error("No se pudo cargar la base de datos. Verifica la conexión con el Excel.")
