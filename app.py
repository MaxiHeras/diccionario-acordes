import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Diccionario de Acordes",
    page_icon="🎸",
    layout="wide"
)

# --- CONFIGURACIÓN DE RUTAS (MAXIHERAS) ---
USUARIO_GITHUB = "MaxiHeras"
REPO_GITHUB = "diccionario-acordes"
# -------------------------------------------

# 2. CONEXIÓN CON GOOGLE SHEET
SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL_SHEET = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    # Cargamos los datos desde Google Sheets
    df = pd.read_csv(URL_SHEET)
    return df

try:
    df = cargar_datos()

    # TÍTULO PRINCIPAL
    st.title("🎸 Diccionario de Acordes")
    st.markdown("Herramienta interactiva para estudiantes de música.")
    st.divider()

    # 3. FILTROS EN LA BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    
    # Filtro de Nota Raíz
    lista_raices = sorted(df['Raiz'].unique())
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices)
    
    # Filtro de Naturaleza (Tipo de Acorde)
    df_raiz = df[df['Raiz'] == raiz_sel]
    lista_naturalezas = sorted(df_raiz['Naturaleza'].unique())
    
    nat_sel = st.sidebar.multiselect(
        "Tipo de Acorde:", 
        options=lista_naturalezas, 
        default=lista_naturalezas
    )

    # 4. FILTRADO FINAL DE DATOS
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]

    # 5. MOSTRAR RESULTADOS
    if not df_filtrado.empty:
        for _, row in df_filtrado.iterrows():
            # Título del acorde (ej: C MAYOR)
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                col_info, col_img = st.columns([1, 1])
                
                with col_info:
                    st.subheader("Información Técnica")
                    st.write(f"**Estado:** {row['Estado']}")
                    st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) else ''}")
                    st.info(f"**Estructura (Intervalos):** {row['Int_IVAN']}")
                
                with col_img:
                    # LÓGICA DE IMAGEN MEJORADA
                    if pd.notna(row['Diagrama1']):
                        # Limpiamos el nombre: sacamos solo el archivo (ej: C-MAY-1.png)
                        nombre_archivo = str(row['Diagrama1']).split('/')[-1]
                        
                        # Usamos el nombre de la carpeta (Naturaleza) exactamente como está en el Excel
                        carpeta = str(row['Naturaleza']).strip()
                        
                        # URL de GitHub Raw para tu usuario MaxiHeras
                        url_final_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{nombre_archivo}"
                        
                        # Mostramos la imagen con un control de error por si la ruta no existe
                        st.image(url_final_img, caption=f"Diagrama: {row['Raiz']} {row['Naturaleza']}", use_container_width=True)
                    else:
                        st.warning("No hay diagrama disponible para este acorde.")
    else:
        st.info("Selecciona al menos un tipo de acorde en el menú lateral.")

except Exception as e:
    st.error("No se pudo cargar la base de datos.")
    st.write(f"Detalle del error: {e}")

# PIE DE PÁGINA
st.divider()
st.caption("Actualizado automáticamente desde Google Sheets | Desarrollado por MaxiHeras")
