import streamlit as st
import pandas as pd

from google import genai

# =====================================
# Configuración
# =====================================

st.set_page_config(
    page_title="AutoCare AI",
    page_icon="🚗",
    layout="wide"
)

# =====================================
# Memoria temporal
# =====================================

if "vehiculos" not in st.session_state:
    st.session_state.vehiculos = []

if "mantenimientos" not in st.session_state:
    st.session_state.mantenimientos = []

# =====================================
# Gemini
# =====================================

client = None
MODELO = "gemini-2.5-flash"

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception:
    pass

# =====================================
# Título
# =====================================

st.title("🚗 AutoCare AI")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Vehículos",
        "Mantenimientos",
        "Historial",
        "IA"
    ]
)

# =====================================
# TAB 1 - Vehículos
# =====================================

with tab1:

    st.subheader("Registrar vehículo")

    with st.form("vehiculo_form"):

        marca = st.text_input("Marca")

        modelo = st.text_input("Modelo")

        anio = st.number_input(
            "Año",
            min_value=1980,
            max_value=2050,
            value=2024
        )

        kilometraje = st.number_input(
            "Kilometraje",
            min_value=0,
            value=0
        )

        guardar = st.form_submit_button(
            "Guardar vehículo"
        )

    if guardar:

        if not marca or not modelo:

            st.warning(
                "Debe indicar marca y modelo."
            )

        else:

            st.session_state.vehiculos.append(
                {
                    "id": len(st.session_state.vehiculos) + 1,
                    "marca": marca,
                    "modelo": modelo,
                    "anio": int(anio),
                    "kilometraje": int(kilometraje),
                }
            )

            st.success(
                "✅ Vehículo guardado correctamente"
            )

# =====================================
# TAB 2 - Mantenimientos
# =====================================

with tab2:

    st.subheader(
        "Registrar mantenimiento"
    )

    if not st.session_state.vehiculos:

        st.warning(
            "Primero registre un vehículo."
        )

    else:

        opciones = {
            f"{v['marca']} {v['modelo']}": v["id"]
            for v in st.session_state.vehiculos
        }

        vehiculo = st.selectbox(
            "Vehículo",
            list(opciones.keys())
        )

        servicio = st.text_input(
            "Servicio realizado"
        )

        costo = st.number_input(
            "Costo",
            
