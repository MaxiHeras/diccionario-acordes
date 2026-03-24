import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", page_icon="🎸", layout="wide")

# 1. CONEXIÓN CON TU GOOGLE SHEET
SHEET_ID = "1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    # Cargamos el CSV y nos aseguramos de que los nombres de columnas coincidan
    return pd.read_csv(URL)

try:
    df = cargar_datos()

    # INTERFAZ DE USUARIO
    st.title("🎸 Diccionario de Acordes para Estudiantes")
    st.markdown("---")

    # BARRA LATERAL PARA FILTROS
    st.sidebar.header("Filtros de búsqueda")
    
    # Filtro 1: Nota Raíz (C, D, E, F, G, A, B)
    lista_raices = sorted(df['Raiz'].unique())
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices)

    # Filtro 2: Naturaleza (Mayor, Menor, Dominante, etc.)
    lista_naturaleza = sorted(df['Naturaleza'].unique())
    nat_sel = st.sidebar.multiselect("Tipo de Acorde:", lista_naturaleza, default=lista_naturaleza[0])

    # FILTRADO DE DATOS
    df_filtrado = df[(df['Raiz'] == raiz_sel) & (df['Naturaleza'].isin(nat_sel))]

    # MOSTRAR RESULTADOS
    if not df_filtrado.empty:
        for index, row in df_filtrado.iterrows():
            with st.expander(f"📖 Acorde: {row['Raiz']} - {row['Naturaleza']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Estado:** {row['Estado']}")
                    st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) else ''}")
                    st.write(f"**Intervalos:** {row['Intervalos']}")
                
                with col2:
                    st.info(f"**Estructura (Intervalos):** {row['Int_IVAN']}")
                
                # Aquí podrías mostrar los diagramas si estuvieran en una URL pública
                # st.image(f"URL_DE_TU_SERVIDOR/{row['Diagrama1']}") 

    else:
        st.warning("No se encontraron acordes con esos filtros.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
