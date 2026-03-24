import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Diccionario de Acordes",
    page_icon="🎸",
    layout="wide"
)

# --- DATOS DE TU CUENTA (Asegúrate de que sean exactos) ---
USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
URL_APP = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"

# 2. CONEXIÓN CON GOOGLE SHEET
SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv(URL_SHEET)
        return df
    except Exception as e:
        return None

df = cargar_datos()

if df is not None:
    # LIMPIEZA DE DATOS BÁSICA
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()

    # TÍTULO PRINCIPAL
    st.title("🎸 Diccionario de Acordes")
    st.markdown("Herramienta interactiva para alumnos de guitarra.")
    st.divider()

    # 3. BARRA LATERAL (FILTROS Y QR)
    st.sidebar.header("🔍 Buscar Acorde")
    
    # Filtro de Nota Raíz
    lista_raices = sorted(df['Raiz'].unique())
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices)
    
    # Filtrar naturalezas disponibles para esa nota
    df_raiz = df[df['Raiz'] == raiz_sel]
    lista_naturalezas = sorted(df_raiz['Naturaleza'].unique())
    
    nat_sel = st.sidebar.multiselect(
        "Tipo de Acorde:", 
        options=lista_naturalezas, 
        default=lista_naturalezas
    )

    # --- CÓDIGO QR SEGURO (Sin librerías extra) ---
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}"
    st.sidebar.image(qr_url, caption="Escanea para entrar")

    # 4. MOSTRAR RESULTADOS
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]

    if not df_filtrado.empty:
        for _, row in df_filtrado.iterrows():
            # Título del acorde desplegable
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Info técnica
                col_n, col_i = st.columns([2, 1])
                with col_n:
                    st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) and str(row['N4']) != 'nan' else ''}")
                with col_i:
                    st.info(f"**Intervalos:** {row['Int_IVAN']}")
                
                st.write("---")
                st.subheader("Posiciones en el diapasón")
                
                # SECCIÓN DE DIAGRAMAS (Corregida e Inteligente)
                
                # 1. Recolectar SOLO las imágenes que existen realmente
                lista_imagenes_validas = []
                for i in range(1, 10): # Busca hasta Diagrama9 por si acaso
                    col_name = f'Diagrama{i}'
                    # Verifica si la columna existe en el Excel y si tiene un valor válido
                    if col_name in row and pd.notna(row[col_name]) and str(row[col_name]).strip() != "" and str(row[col_name]) != 'nan':
                        # Limpiamos el nombre (por si acaso el Excel tiene la ruta completa)
                        nombre_archivo = str(row[col_name]).split('/')[-1].strip()
                        carpeta = str(row['Naturaleza']).strip()
                        
                        # Construir la URL completa de GitHub
                        url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{nombre_archivo}"
                        lista_imagenes_validas.append(url_img)

                # 2. Mostrar imágenes en un diseño controlado
                if lista_imagenes_validas:
                    # Creamos columnas exactamente para la cantidad de imágenes encontradas
                    cantidad_fotos = len(lista_imagenes_validas)
                    
                    # Usamos st.columns para distribuir las fotos
                    # st.columns automáticamente centrará si hay menos de 5 fotos en pantalla completa
                    cols_imgs = st.columns(cantidad_fotos)
                    
                    for idx, img_url in enumerate(lista_imagenes_validas):
                        with cols_imgs[idx]:
                            # width=220 hace que la imagen sea más chica y controlada
                            st.image(img_url, width=220) 
                            st.caption(f"Posición {idx+1}")
                else:
                    st.warning("No hay diagramas disponibles para este acorde.")
    else:
        st.info("Selecciona un tipo de acorde.")

else:
    st.error("Error al conectar con la base de datos.")

st.divider()
st.caption(f"Diccionario - {USUARIO_GITHUB}")
