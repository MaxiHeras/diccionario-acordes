import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Diccionario de Acordes", page_icon="🎸", layout="wide")

# --- DATOS DE CUENTA ---
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
    except:
        return None

df = cargar_datos()

if df is not None:
    # Limpieza de datos
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()

    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    
    # Filtro Nota Raíz
    lista_raices = sorted(df['Raiz'].unique())
    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices)
    
    # Filtrar naturalezas disponibles para esa nota
    df_raiz = df[df['Raiz'] == raiz_sel]
    
    # ORDEN PERSONALIZADO SOLICITADO
    orden_deseado = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    
    # Obtenemos las naturalezas reales del CSV y las ordenamos según tu lista
    opciones_reales = df_raiz['Naturaleza'].unique()
    lista_ordenada = [n for n in orden_deseado if n in opciones_reales]
    # Si hay alguna que no esté en tu lista, la agregamos al final
    extras = [n for n in opciones_reales if n not in orden_deseado]
    lista_final_opciones = lista_ordenada + sorted(extras)

    # FILTRO SIN SELECCIÓN PREVIA (default=[])
    nat_sel = st.sidebar.multiselect(
        "Tipo de Acorde:", 
        options=lista_final_opciones, 
        default=[], 
        placeholder="Elegí un tipo..."
    )

    # QR
    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    st.sidebar.image(f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}")

    # 4. MOSTRAR RESULTADOS
    if nat_sel:
        df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                st.write(f"**Notas:** {row['N1']}, {row['N2']}, {row['N3']}, {row['N4'] if pd.notna(row['N4']) and str(row['N4']) != 'nan' else ''}")
                st.info(f"**Intervalos:** {row['Int_IVAN']}")
                
                st.write("---")
                st.subheader("Posiciones")
                
                # Recolectar imágenes existentes
                lista_imagenes = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]) and str(row[col]).strip() != "" and str(row[col]) != 'nan':
                        archivo = str(row[col]).split('/')[-1].strip()
                        url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{archivo}"
                        lista_imagenes.append(url_img)

                if lista_imagenes:
                    # Usamos columnas para que se acomoden bien en el celular
                    cols = st.columns(len(lista_imagenes))
                    for idx, url in enumerate(lista_imagenes):
                        with cols[idx]:
                            # Tamaño más chico (150px) para comodidad en móvil
                            st.image(url, width=150)
                            st.caption(f"Pos. {idx+1}")
                else:
                    st.warning("No hay diagramas disponibles.")
    else:
        st.info("👋 ¡Hola! Selecciona un **Tipo de Acorde** en el menú de la izquierda para empezar.")

else:
    st.error("Error al conectar con la base de datos.")
