import streamlit as st
import pandas as pd
from fpdf import FPDF
import urllib.parse

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# CSS Reducido para evitar conflictos
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] { padding-top: 0.5rem !important; }
    .stButton > button { width: 100% !important; border-radius: 6px !important; }
    div[data-testid="stRadio"] > div { gap: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

# 3. CLASE PDF SIMPLIFICADA (Sin imágenes ni QR para evitar errores)
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Diccionario de Acordes', 0, 1, 'C')

def generar_pdf(df_sel, nota):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Acordes de {nota}", ln=True)
    pdf.ln(5)
    
    for _, row in df_sel.iterrows():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{row['Raiz']} {row['Naturaleza']}", ln=True, fill=False)
        pdf.set_font("Arial", '', 10)
        notas = [str(row[n]) for n in ['N1','N2','N3','N4'] if pd.notna(row[n])]
        pdf.cell(0, 8, f"Notas: {' - '.join(notas)} | IVAN: {row.get('Int_IVAN','')}", ln=True)
        pdf.ln(2)
    
    return pdf.output(dest='S').encode('latin-1')

# 4. LÓGICA PRINCIPAL
df = load_data()

if df is not None:
    # Inicializar estados si no existen
    if "alteracion" not in st.session_state: st.session_state.alteracion = "Nat."
    
    with st.sidebar:
        st.title("Ajustes")
        raiz = st.selectbox("Nota:", ['C', 'D', 'E', 'F', 'G', 'A', 'B'])
        
        # Selectores de alteración
        c1, c2, c3 = st.columns(3)
        if c1.button("Nat."): st.session_state.alteracion = "Nat."
        if c2.button("Sost."): st.session_state.alteracion = "Sost."
        if c3.button("Bem."): st.session_state.alteracion = "Bem."
        
        st.write(f"Seleccionado: **{st.session_state.alteracion}**")
        
        # Construcción de la nota final
        alt_map = {"Sost.": "#", "Bem.": "b", "Nat.": ""}
        nota_final = raiz + alt_map[st.session_state.alteracion]
        
        df_filtrado = df[df['Raiz'] == nota_final]
        
        if not df_filtrado.empty:
            tipos = st.multiselect("Tipos:", df_filtrado['Naturaleza'].unique())
            
            if tipos:
                df_para_pdf = df_filtrado[df_filtrado['Naturaleza'].isin(tipos)]
                if st.button("Generar PDF"):
                    pdf_bytes = generar_pdf(df_para_pdf, nota_final)
                    st.download_button("Descargar Archivo", data=pdf_bytes, file_name=f"{nota_final}.pdf")

    # Visualización en pantalla
    st.header(f"Acordes de {nota_final}")
    if not df_filtrado.empty:
        st.dataframe(df_filtrado[['Raiz', 'Naturaleza', 'N1', 'N2', 'N3', 'N4', 'Int_IVAN']], hide_index=True)
    else:
        st.warning("No se encontraron datos para esta nota.")

# 5. REQUISITO CRÍTICO
# Asegúrate de tener un archivo llamado 'requirements.txt' con:
# streamlit
# pandas
# fpdf
