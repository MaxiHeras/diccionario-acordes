import streamlit as st
import pandas as pd

st.set_page_config(page_title="Diccionario", layout="wide")

st.title("🎸 Mi Diccionario de Acordes")

URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load()

if df is not None:
    st.success("¡App funcionando y datos cargados!")
    st.write("Usa el menú de la izquierda para filtrar.")
    st.dataframe(df.head())
else:
    st.error("No se pudo cargar el Excel.")
