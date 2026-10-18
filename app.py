import streamlit as st
import requests
from datetime import datetime
import pytz

st.set_page_config(
    page_title="Sistema de consulta de mantenimientos",
    page_icon="🌤️",
    layout="centered"
)

st.title("Sistema de consulta de mantenimiento para autos")

st.markdown("---")
modeloAuto = st.text_input("¿Cuál es tu consulta?", placeholder="selecciona tu modelo de auto..")
if modeloAuto:
    st.balloons()
    st.write(f"✨ ¡Modelo auto ingresado:, {modeloAuto}! a continuacion sus datos")


