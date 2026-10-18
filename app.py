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
modeloAuto = st.text_input("¿Cuál es tu consulta?", placeholder="selecciona tu modelo de auto..")
if modeloAuto:
    st.balloons()
    st.write(f"✨ ¡Modelo auto ingresado:, {modeloAuto}! a continuacion sus datos")
