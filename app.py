import streamlit as st
import requests
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Mi Portal Inteligente",
    page_icon="🌤️",
    layout="centered"
)

st.title("Portal de Bienvenida Inteligente 🚀")

st.markdown("---")
nombre_usuario = st.text_input("¿Cómo te llamas?", placeholder="Introduce tu nombre aquí...")
if nombre_usuario:
    st.balloons()
    st.write(f"✨ ¡Hola, {nombre_usuario}! Gracias por visitar tu nuevo portal interactivo inteligente.")
