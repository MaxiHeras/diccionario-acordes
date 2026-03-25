import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

# Configuración de página
st.set_page_config(page_title="Diccionario de Acordes", layout="wide")

# --- LÓGICA DE DATOS ---
NOTAS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
TIPOS_ACORDE = ["Mayor", "Menor", "7ma", "Sustentado", "Diminuido"]

DICCIONARIO_ACORDES = {
    frozenset(['C', 'E', 'G']): "Do Mayor (C)",
    frozenset(['D', 'F#', 'A']): "Re Mayor (D)",
    # Agrega aquí más acordes según necesites
}

# --- ESTADO DE LA SESIÓN ---
if 'notas_seleccionadas' not in st.session_state:
    st.session_state.notas_seleccionadas = set()

def reset_seleccion_tipos():
    st.session_state.tipo_seleccionado = TIPOS_ACORDE

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("Seleccionar Modo")
    modo = st.radio("Elige una opción:", ["Diccionario 📖", "Identificador 🔍"], on_change=reset_seleccion_tipos)
    
    st.divider()
    
    # --- SECCIÓN COMPARTIR (DENTRO DEL SIDEBAR) ---
    st.subheader("📲 Compartir App")
    url_app = "https://diccionario-acordes-xz99pzx875gw2ytzpqacv.streamlit.app/"

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url_app)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img_qr.save(buf, format="PNG")
        
        # 1. QR en la barra lateral
        st.image(buf, caption="Escaneá para abrir", use_container_width=True)
        
        # 2. Botón de copia DEBAJO del QR en la barra lateral
        if st.button("Copiar enlace"):
            st.code(url_app, language=None)
            st.toast("¡Enlace listo para copiar!")

    except Exception as e:
        st.error("Error con el QR. Revisa requirements.txt")

# --- CUERPO PRINCIPAL ---
if modo == "Diccionario 📖":
    st.header("📖 Diccionario de Acordes")
    col1, col2 = st.columns(2)
    with col1:
        nota_raiz = st.selectbox("Nota Raíz:", NOTAS, on_change=reset_seleccion_tipos)
    with col2:
        tipo = st.multiselect(
            "Tipo:", 
            options=TIPOS_ACORDE, 
            default=st.session_state.get('tipo_seleccionado', TIPOS_ACORDE)
        )
    st.divider()
    st.button("Generar PDF de Selección")

else:
    st.header("🔍 Identificador")
    st.write("Selecciona las notas para formar el acorde:")

    # Cuadrícula de notas
    cols = st.columns(3)
    for i, nota in enumerate(NOTAS):
        with cols[i % 3]:
            if nota in st.session_state.notas_seleccionadas:
                if st.button(nota, key=f"btn_{nota}", type="primary", use_container_width=True):
                    st.session_state.notas_seleccionadas.remove(nota)
                    st.rerun()
            else:
                if st.button(nota, key=f"btn_{nota}", type="secondary", use_container_width=True):
                    st.session_state.notas_seleccionadas.add(nota)
                    st.rerun()

    if st.button("🗑️ Borrar Notas", use_container_width=True):
        st.session_state.notas_seleccionadas = set()
        st.rerun()

    st.divider()
    st.subheader("Acorde Resultante:")
    notas_actuales = frozenset(st.session_state.notas_seleccionadas)
    resultado = DICCIONARIO_ACORDES.get(notas_actuales, "Acorde no identificado")
    
    if st.session_state.notas_seleccionadas:
        st.success(f"**{resultado}**")
    else:
        st.info("Selecciona notas arriba para identificar el acorde.")
