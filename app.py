import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", page_icon="🎸", layout="wide")

# --- DATOS DE TU CUENTA ---
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
    # Limpieza básica de datos
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()

    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    raiz_sel = st.sidebar.selectbox("Nota Raíz:", sorted(df['Raiz'].unique()))
    df_raiz = df[df['Raiz'] == raiz_sel]
    nat_sel = st.sidebar.multiselect("Tipo:", options=sorted(df_raiz['Naturaleza'].unique()), default=sorted(df_raiz['Naturaleza'].unique()))

    # QR
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    st.sidebar.image(f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}")

    # 4. RESULTADOS
    df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]

    for _, row in df_filtrado.iterrows():
        with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
            # Info técnica
            st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) and str(row['N4']) != 'nan' else ''}")
            st.info(f"**Intervalos:** {row['Int_IVAN']}")
            
            st.write("---")
            st.subheader("Posiciones en el diapasón")
            
            # Recolectamos SOLO las imágenes que existen de verdad
            lista_imagenes = []
            for i in range(1, 10): # Buscamos del 1 al 9 por si agregás más
                col = f'Diagrama{i}'
                if col in row and pd.notna(row[col]) and str(row[col]).strip() != "" and str(row[col]) != 'nan':
                    nombre_archivo = str(row[col]).split('/')[-1].strip()
                    carpeta = str(row['Naturaleza']).strip()
                    url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{carpeta}/{nombre_archivo}"
                    lista_imagenes.append(url_img)

            if lista_imagenes:
                # Creamos las columnas según la cantidad de fotos encontradas
                cols = st.columns(len(lista_imagenes))
                for idx, url in enumerate(lista_imagenes):
                    with cols[idx]:
                        # El parámetro width=200 hace que no sean gigantes
                        st.image(url, width=220) 
                        st.caption(f"Posición {idx+1}")
            else:
                st.warning("No hay diagramas disponibles.")

else:
    st.error("Error al conectar con la base de datos.")
