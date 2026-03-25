import streamlit as st
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
import datetime
import base64

# 1. CONFIGURACIÓN Y ESTILO INICIAL (Para la App Web)
st.set_page_config(page_title="Diccionario de Acordes", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Filtro para que las imágenes no salgan en negativo en modo oscuro */
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    
    /* Contenedor de galería horizontal */
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS Y VARIABLES
APP_URL = "https://diccionario-acordes-okhwulgyz9ueachvkdfh26.streamlit.app/"
URL_EXCEL = "https://docs.google.com/spreadsheets/d/1VHwDMfGozCbe4_UKz9TfiQI9TrNr9ypZp45pMAOjyno/gviz/tq?tqx=out:csv"
URL_QR = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={APP_URL}"

@st.cache_data
def load():
    try:
        df = pd.read_csv(URL_EXCEL)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load()

# --- NUEVA FUNCIÓN PARA GENERAR PDF CON IMÁGENES (USANDO XHTML2PDF) ---
def create_pdf_with_images(df_filtered):
    # Base URL de tus diagramas en GitHub (usando raw para acceso directo)
    GITHUB_BASE = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
    
    # 1. Crear el CSS para estilizar el PDF
    css = """
        @page { size: A4; margin: 1cm; }
        body { font-family: Helvetica, Arial, sans-serif; color: #333; }
        h1 { text-align: center; color: #000; font-size: 24pt; margin-bottom: 20px; }
        .date { text-align: center; font-size: 10pt; color: #666; margin-bottom: 30px; }
        .acorde-block { margin-bottom: 30px; page-break-inside: avoid; border-bottom: 1px solid #ccc; padding-bottom: 15px; }
        .acorde-title { font-size: 16pt; font-weight: bold; color: #000; margin-bottom: 5px; }
        .info-row { font-size: 10pt; margin-bottom: 3px; }
        .label { font-weight: bold; }
        .diagramas-row { display: block; width: 100%; margin-top: 10px; text-align: left; }
        .diagrama-box { display: inline-block; width: 100px; text-align: center; margin-right: 15px; vertical-align: top; }
        .diag-img { width: 90px; height: auto; border: 1px solid #ddd; padding: 2px; }
        .diag-label { font-size: 8pt; color: #666; margin-top: 2px; }
    """
    
    # 2. Crear el HTML base
    html_content = f"""
        <html>
        <head><style>{css}</style></head>
        <body>
            <h1>Hoja de Estudio de Acordes</h1>
            <p class="date">Generado el: {datetime.date.today().strftime('%d/%m/%Y')}</p>
    """
    
    # 3. Iterar sobre cada acorde y agregar su contenido
    for idx, row in df_filtered.iterrows():
        # Limpieza de Notas
        notas_list = [str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']]
        notas_str = ' - '.join(notas_list)
        
        # Limpieza de Intervalos
        ivan = str(row.get('Int_IVAN', '')).strip()
        ivan_html = f'<div class="info-row"><span class="label">Int_IVAN:</span> {ivan}</div>' if ivan and ivan.lower() not in ['nan','','0'] else ""
        
        trad = str(row.get('Int_TRAD', '')).strip()
        trad_html = f'<div class="info-row"><span class="label">Int_TRAD:</span> {trad}</div>' if trad and trad.lower() not in ['nan','','0'] else ""
        
        # Iniciar bloque de acorde
        html_content += f"""
            <div class="acorde-block">
                <div class="acorde-title">Acorde: {row['Raiz']} {row['Naturaleza']}</div>
                <div class="info-row"><span class="label">Notas:</span> {notas_str}</div>
                {ivan_html}
                {trad_html}
                <div class="diagramas-row">
        """
        
        # Agregar Diagramas
        tiene_diagramas = False
        for i in range(1, 10): # Buscamos de Diagrama1 a Diagrama9
            img_val = str(row.get(f'Diagrama{i}', 'nan')).strip()
            if img_val.lower().endswith('.png'):
                # Construir la URL completa a GitHub
                img_file = img_val.split('/')[-1]
                img_url = f"{GITHUB_BASE}/{row['Naturaleza']}/{img_file}"
                
                # Crear la caja para el diagrama
                html_content += f"""
                    <div class="diagrama-box">
                        <img src="{img_url}" class="diag-img" />
                        <div class="diag-label">P{i}</div>
                    </div>
                """
                tiene_diagramas = True
                
        if not tiene_diagramas:
            html_content += '<p style="font-size:9pt;color:gray;">(No hay diagramas disponibles)</p>'
            
        # Cerrar bloque de acorde
        html_content += """
                </div> </div> """
        
    # 4. Cerrar el HTML
    html_content += """
        </body>
        </html>
    """
    
    # 5. Convertir HTML a PDF en memoria
    result = BytesIO()
    # pisa.pisaDocument() se encarga de descargar las imágenes desde las URLs
    pisa_status = pisa.pisaDocument(BytesIO(html_content.encode("utf-8")), result)
    
    if pisa_status.err:
        return None
    return result.getvalue()

# --- FIN DE LA NUEVA FUNCIÓN ---

if df is not None:
    # 3. BARRA LATERAL
    with st.sidebar:
        st.header("🔍 Buscar Acorde")
        notas_orden = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
        r_list = [n for n in notas_orden if n in df['Raiz'].unique()]
        raiz_sel = st.selectbox("Nota Raíz:", r_list)
        
        df_raiz = df[df['Raiz'] == raiz_sel]
        nat_sel = st.multiselect("Tipo:", options=df_raiz['Naturaleza'].unique())
        
        st.write("---")
        # Botón de WhatsApp
        t_wa = f"Mirá este diccionario de acordes: {APP_URL}"
        l_wa = f"https://wa.me/?text={t_wa.replace(' ', '%20')}"
        st.link_button("📲 Compartir por WhatsApp", l_wa, use_container_width=True)
        
        st.image(URL_QR, caption="Escanear para compartir", width=180)
        st.code(APP_URL, language=None)

    # 4. RESULTADOS (En la App Web)
    if nat_sel:
        df_f = df_raiz[df_raiz['Naturaleza'].isin(nat_sel)]
        
        # BOTÓN DESCARGA PDF (Actualizado para el nuevo sistema)
        # El proceso de descargar imágenes lleva tiempo, así que usamos un spinner
        with st.spinner('⏳ Generando PDF con diagramas (esto puede tardar unos segundos)...'):
            try:
                pdf_bytes = create_pdf_with_images(df_f)
                if pdf_bytes:
                    st.download_button(
                        label="📄 Descargar Hoja de Estudio (PDF con Diagramas)",
                        data=pdf_bytes,
                        file_name=f"Estudio_{raiz_sel}_{datetime.date.today()}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Error al generar el PDF. Verifica que GitHub sea accesible.")
            except ImportError:
                # Este error saldrá si no actualizaste el requirements.txt
                st.error("Crítico: Debes agregar 'xhtml2pdf' y 'reportlab' a tu archivo 'requirements.txt' en GitHub para que esto funcione.")
            except Exception as e:
                # Otros errores
                st.error(f"Error inesperado: {e}")
        
        st.write("---")
        
        # Mostrar los acordes en la Web (como antes)
        expandir = False if len(nat_sel) > 1 else True
        for idx, row in df_f.iterrows():
            with st.expander(f"📖 {row['Raiz']} {row['Naturaleza']}", expanded=expandir):
                # Notas
                n_str = ' - '.join([str(row[c]).strip() for c in ['N1','N2','N3','N4'] if pd.notna(row.get(c)) and str(row[c]).lower() not in ['nan','','0']])
                st.write(f"**Notas:** {n_str}")
                
                # Intervalos
                c1, c2 = st.columns(2)
                with c1:
                    ivan = str(row.get('Int_IVAN', '')).strip()
                    if ivan and ivan.lower() not in ['nan', '0', '']:
                        st.info(f"**Int_IVAN:**\n\n{ivan}")
                with c2:
                    trad = str(row.get('Int_TRAD', '')).strip()
                    if trad and trad.lower() not in ['nan', '0', '']:
                        st.success(f"**Int_TRAD:**\n\n{trad}")
                
                st.write("---")
                
                # Galería Web
                h_items = ""
                GITHUB_BASE_RAW = "https://raw.githubusercontent.com/MaxiHeras/diccionario-acordes/main"
                for i in range(1, 10):
                    val = str(row.get(f'Diagrama{i}', 'nan')).strip()
                    if val.lower().endswith('.png'):
                        archivo = val.split('/')[-1]
                        # Aseguramos que use la URL raw para la web también
                        url_img = f"{GITHUB_BASE_RAW}/{row['Naturaleza']}/{archivo}"
                        div_id = f"pos_{idx}_{i}"
                        h_items += f'<div class="chord-item" id="{div_id}"><img src="{url_img}" class="chord-img" width="110" onerror="document.getElementById(\'{div_id}\').style.display=\'none\';"><p style="font-size:12px;color:gray;">P{i}</p></div>'
                
                if h_items:
                    st.markdown(f'<div class="scroll-container">{h_items}</div>', unsafe_allow_html=True)
    else:
        st.info("Elegí un acorde en el menú lateral para ver detalles y descargar el PDF.")
else:
    st.error("Error: No se pudo conectar con el Excel de Google Sheets.")
