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
        st.error(f"Error al cargar datos: {e}")
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
                # Sección de Información (arriba, a lo ancho)
                st.subheader("Información")
                col_n, col_i = st.columns([2, 1])
                with col_n:
                    st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) and str(row['N4']) != 'nan' else ''}")
                with col_i:
                    st.info(f"**Intervalos:** {row['Int_IVAN']}")
                
                st.write("---")
                
                # SECCIÓN DE DIAGRAMAS (AQUÍ ESTÁ EL CAMBIO CLAVE)
                st.subheader("Posiciones en el diapasón")
                
                # 1. Recolectar todas las imágenes válidas del Excel (Diagrama1 a Diagrama4)
                lista_imagenes = []
                for i in range(1, 5): # Busca Diagrama1, Diagrama2, Diagrama3, Diagrama4
                    col_name = f'Diagrama{i}'
                    if col_name in df.columns and pd.notna(row[col_name]) and str(row[col_name]) != 'nan':
                        # Limpiamos el nombre por si acaso (sacamos la ruta si la tiene)
                        nombre_archivo = str(row[col_name]).split('/')[-1].strip()
                        carpeta = str(row['Naturaleza']).strip()
                        
                        # Construir la URL completa de GitHub
                        url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{nombre_archivo}"
                        lista_imagenes.append(url_img)

                # 2. Mostrar imágenes según la cantidad que haya
                if lista_imagenes:
                    cantidad = len(lista_imagenes)
                    
                    if cantidad == 1:
                        # Si hay solo una, la centramos y le damos tamaño mediano
                        c1, c2, c3 = st.columns([1, 1, 1]) # 3 columnas iguales
                        with c2: # Usamos la del medio
                            st.image(lista_imagenes[0], use_container_width=True)
                            st.caption("Posición principal")
                    else:
                        # Si hay varias (2, 3 o 4), creamos columnas automáticas
                        cols_imgs = st.columns(cantidad)
                        for idx, img_url in enumerate(lista_imagenes):
                            with cols_imgs[idx]:
                                st.image(img_url, use_container_width=True)
                                st.caption(f"Posición {idx+1}")
                else:
                    st.warning("No hay diagramas disponibles para este acorde en el Excel.")
    else:
        st.info("Selecciona un tipo de acorde en la barra lateral.")

else:
    st.error("No se pudieron cargar los datos del Google Sheet.")

st.divider()
st.caption(f"Diccionario de Acordes - Versión Final - {USUARIO_GITHUB}")
