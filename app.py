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
    # Limpieza de datos básica
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()

    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    
    # ORDEN MUSICAL (C, D, E, F, G, A, B)
    orden_notas_musical = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
    raices_presentes = df['Raiz'].unique()
    lista_raices_final = [n for n in orden_notas_musical if n in raices_presentes]
    extras_notas = sorted([n for n in raices_presentes if n not in orden_notas_musical])
    lista_raices_final += extras_notas

    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices_final)
    
    df_raiz = df[df['Raiz'] == raiz_sel]
    
    # ORDEN DE NATURALEZA
    orden_deseado = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    opciones_reales = df_raiz['Naturaleza'].unique()
    lista_ordenada = [n for n in orden_deseado if n in opciones_reales]
    extras_nat = [n for n in opciones_reales if n not in orden_deseado]
    lista_final_opciones = lista_ordenada + sorted(extras_nat)

    nat_sel = st.sidebar.multiselect(
        "Tipo de Acorde:", 
        options=lista_final_opciones, 
        default=[], 
        placeholder="Elegí un tipo..."
    )

    st.sidebar.write("---")
    st.sidebar.write("### 📲 Comparte la App")
    st.sidebar.image(f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={URL_APP}")

    # 4. MOSTRAR RESULTADOS
    if nat_sel:
        df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # Notas
                n4_val = str(row['N4']) if 'N4' in row else 'nan'
                notas_str = f"{row['N1']}, {row['N2']}, {row['N3']}"
                if n4_val.lower() != 'nan' and n4_val.strip() != "":
                    notas_str += f", {n4_val}"
                st.write(f"**Notas:** {notas_str}")

                # --- ETIQUETAS DE INTERVALOS CORREGIDAS ---
                st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                
                if 'Int_TRAD' in row and pd.notna(row['Int_TRAD']):
                     st.info(f"**Int_TRAD:** {row['Int_TRAD']}")
                
                st.write("---")
                st.subheader("Posiciones")
                
                # RECOLECCIÓN DE IMÁGENES
                lista_imagenes = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]):
                        val = str(row[col]).strip()
                        if val != "" and val.lower() != 'nan' and val != '0':
                            archivo = val.split('/')[-1]
                            url_img = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{archivo}"
                            lista_imagenes.append(url_img)

                if lista_imagenes:
                    # --- MEJORA PARA MÓVIL: COLUMNAS MÁS PEQUEÑAS ---
                    # Usamos un ancho fijo para que no se estiren demasiado en pantallas grandes
                    # y se vean una al lado de la otra en móviles
                    cols = st.columns(len(lista_imagenes))
                    for idx, url in enumerate(lista_imagenes):
                        with cols[idx]:
                            # width=120 asegura que el diagrama sea legible pero no gigante
                            st.image(url, width=120)
                            st.caption(f"P{idx+1}")
                else:
                    st.warning("No hay diagramas disponibles.")
    else:
        st.info("👋 Selecciona un **Tipo de Acorde** a la izquierda.")

else:
    st.error("Error al conectar con la base de datos.")
