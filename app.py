import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN E INTERFAZ
# Estado inicial de la barra lateral
if 'sb_state' not in st.session_state:
    st.session_state.sb_state = "expanded"

st.set_page_config(
    page_title="Diccionario de Acordes", 
    layout="wide", 
    initial_sidebar_state=st.session_state.sb_state
)

# CSS para Modo Oscuro y Galería Horizontal
st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) { .chord-img { filter: invert(1) hue-rotate(180deg); } }
    .scroll-container { display: flex; overflow-x: auto; gap: 15px; padding: 10px 0; -webkit-overflow-scrolling: touch; }
    .chord-item { flex: 0 0 auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS Y QR ---
URL = "
