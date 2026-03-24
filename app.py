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
    
    # --- ORDEN MUSICAL (C, D, E, F, G, A, B) ---
    # Definimos el orden lógico para que no empiece por la 'A'
    orden_notas_musical = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
    raices_presentes = df['Raiz'].unique()
    
    # Creamos la lista final siguiendo el orden musical definido arriba
    lista_raices_final = [n for n in orden_notas_musical if n in raices_presentes]
    # Si hay alguna nota en el Excel que no pusimos en la lista, la agregamos al final
    extras_notas = sorted([n for n in raices_presentes if n not in orden_notas_musical])
    lista_raices_final += extras_notas

    raiz_sel = st.sidebar.selectbox("Selecciona la Nota Raíz:", lista_raices_final)
    
    # Filtrar naturalezas disponibles para esa nota
    df_raiz = df[df['Raiz'] == raiz_sel]
    
    # ORDEN DE NATURALEZA (MAYOR primero, etc.)
    orden_deseado = ["MAYOR", "MENOR", "DOMINANTE", "AUMENTADO", "DISMINUIDO", "SEMIDISMINUIDO", "MAJ7", "MENOR7"]
    opciones_reales = df_raiz['Naturaleza'].unique()
    lista_ordenada = [n for n in orden_deseado if n in opciones_reales]
    extras_nat = [n for n in opciones_reales if n not in orden_deseado]
    lista_final_opciones = lista_ordenada + sorted(extras_nat)

    nat_sel = st.
