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
    # Limpieza de datos crítica para que aparezcan las columnas
    df.columns = df.columns.str.strip() # Quita espacios en los nombres de columnas
    df['Raiz'] = df['Raiz'].astype(str).str.strip()
    df['Naturaleza'] = df['Naturaleza'].astype(str).str.strip()

    st.title("🎸 Diccionario de Acordes")
    st.divider()

    # 3. BARRA LATERAL
    st.sidebar.header("🔍 Buscar Acorde")
    
    # ORDEN MUSICAL
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

    nat_sel = st.sidebar.multiselect("Tipo de Acorde:", options=lista_final_opciones, default=[], placeholder="Elegí un tipo...")

    # 4. MOSTRAR RESULTADOS
    if nat_sel:
        df_filtrado = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        for _, row in df_filtrado.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=True):
                # NOTAS
                n4 = str(row['N4']) if 'N4' in row else 'nan'
                notas_txt = f"{row['N1']}, {row['N2']}, {row['N3']}"
                if n4.lower() != 'nan' and n4.strip() != "":
                    notas_txt += f", {n4}"
                st.write(f"**Notas:** {notas_txt}")

                # --- INTERVALOS (CORRECCIÓN TOTAL) ---
                st.info(f"**Int_IVAN:** {row['Int_IVAN']}")
                
                # Forzamos la visualización de Int_TRAD si existe valor
                val_trad = str(row.get('Int_TRAD', 'nan')).strip()
                if val_trad.lower() != 'nan' and val_trad != "":
                     st.info(f"**Int_TRAD:** {val_trad}")
                
                st.write("---")
                st.subheader("Posiciones")
                
                # RECOLECCIÓN DE IMÁGENES
                lista_imgs = []
                for i in range(1, 10):
                    col = f'Diagrama{i}'
                    if col in row and pd.notna(row[col]):
                        val = str(row[col]).strip()
                        if val not in ["", "nan", "0"]:
                            archivo = val.split('/')[-1]
                            url = f"https://raw.githubusercontent.com/{USUARIO_GITHUB}/{REPO_GITHUB}/main/{row['Naturaleza']}/{archivo}"
                            lista_imgs.append(url)

                if lista_imgs:
                    # CONFIGURACIÓN PARA CELULAR: Imágenes de 100px para que entren varias por fila
                    cols = st.columns(len(lista_imgs))
                    for idx, url in enumerate(lista_imgs):
                        with cols[idx]:
                            st.image(url, width=100) # Tamaño reducido para comodidad
                            st.caption(f"P{idx+1}")
                else:
                    st.warning("No hay diagramas.")
    else:
        st.info("👋 Selecciona un acorde a la izquierda.")
else:
    st.error("Error al conectar con la base de datos.")
