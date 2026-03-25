import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image

# Configuración de página
st.set_page_config(page_title="Diccionario de Acordes", layout="centered")

# --- LÓGICA DE DATOS ---
NOTAS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']
TIPOS_ACORDE = ["Mayor", "Menor", "7ma", "Sustentado", "Diminuido"]

# Diccionario simple de ejemplo para la lógica del identificador
# (Deberás completar esto con tu lógica real de detección)
DICCIONARIO_ACORDES = {
    frozenset(['C', 'E', 'G']): "Do Mayor (C)",
    frozenset(['D', 'F#', 'A']): "Re Mayor (D)",
    # Añade aquí el resto de tus combinaciones
}

# --- ESTADO DE LA SESIÓN ---
if 'notas_seleccionadas' not in st.session_state:
    st.session_state.notas_seleccionadas = set()

# Función para que al cambiar nota o modo, se seleccionen todos los tipos
def reset_seleccion_tipos():
    st.session_state.tipo_seleccionado = TIPOS_ACORDE

# --- INTERFAZ LATERAL (MODOS) ---
with st.sidebar:
    st.title("Seleccionar Modo")
    modo = st.radio("Elige una opción:", ["Diccionario 📖", "Identificador 🔍"], on_change=reset_seleccion_tipos)

# --- MODO 1: DICCIONARIO ---
if modo == "Diccionario 📖":
    st.header("Diccionario de Acordes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Al cambiar la nota raíz, se disparan todas las opciones de 'tipo'
        nota_raiz = st.selectbox("Nota Raíz:", NOTAS, on_change=reset_seleccion_tipos)
    
    with col2:
        tipo = st.multiselect(
            "Tipo:", 
            options=TIPOS_ACORDE, 
            default=st.session_state.get('tipo_seleccionado', TIPOS_ACORDE)
        )
    
    st.divider()
    if st.button("Generar PDF de Selección"):
        st.info("Función de PDF en desarrollo...")

# --- MODO 2: IDENTIFICADOR ---
else:
    st.header("🔍 Identificador")
    st.write("Selecciona las notas para formar el acorde:")

    # Crear la cuadrícula de notas
    cols = st.columns(3)
    for i, nota in enumerate(NOTAS):
        with cols[i % 3]:
            # El botón cambia de color si la nota está en el set
            if nota in st.session_state.notas_seleccionadas:
                if st.button(nota, key=nota, type="primary", use_container_width=True):
                    st.session_state.notas_seleccionadas.remove(nota)
                    st.rerun()
            else:
                if st.button(nota, key=nota, type="secondary", use_container_width=True):
                    st.session_state.notas_seleccionadas.add(nota)
                    st.rerun()

    if st.button("🗑️ Borrar Notas", use_container_width=True):
        st.session_state.notas_seleccionadas = set()
        st.rerun()

    # RESULTADO DEL IDENTIFICADOR
    st.divider()
    st.subheader("Acorde Resultante:")
    notas_actuales = frozenset(st.session_state.notas_seleccionadas)
    resultado = DICCIONARIO_ACORDES.get(notas_actuales, "Acorde no identificado")
    
    if st.session_state.notas_seleccionadas:
        st.success(f"**{resultado}**")
    else:
        st.info("Selecciona notas arriba para identificar el acorde.")

# --- SECCIÓN COMPARTIR (QR Y BOTÓN ABAJO) ---
st.divider()
st.subheader("📲 Compartir App")

url_app = "https://diccionario-acordes-xz99pzx875gw2ytzpqacv.streamlit.app/"

try:
    # Generación del QR (Línea 126 corregida)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url_app)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img_qr.save(buf, format="PNG")
    
    # 1. Mostrar QR
    st.image(buf, caption="Escaneá para abrir", width=200)
    
    # 2. Botón de copia DEBAJO del QR
    if st.button("Copiar enlace"):
        st.code(url_app, language=None)
        st.toast("¡Enlace listo para copiar!")

except Exception as e:
    st.error(f"Error al generar QR: {e}. Asegúrate de instalar 'qrcode' y 'pillow'.")
