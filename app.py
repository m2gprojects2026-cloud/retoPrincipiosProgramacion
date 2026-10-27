import streamlit as st
import pandas as pd
import google.generativeai as genai

# ==========================
# Configuración
# ==========================

st.set_page_config(
    page_title="AutoCare AI",
    page_icon="🚗",
    layout="wide"
)

# ==========================
# Memoria temporal
# ==========================

if "vehiculos" not in st.session_state:
    st.session_state.vehiculos = []

if "mantenimientos" not in st.session_state:
    st.session_state.mantenimientos = []

# ==========================
# IA Gemini (Opcional)
# ==========================

gemini_ok = False

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    gemini_ok = True
except:
    pass

# ==========================
# Título
# ==========================

st.title("🚗 AutoCare AI")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Vehículos",
        "Mantenimientos",
        "Historial",
        "IA"
    ]
)

# ==========================
# Vehículos
# ==========================

with tab1:

    st.subheader("Registrar vehículo")

    with st.form("vehiculo_form"):

        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        anio = st.number_input(
            "Año",
            min_value=1980,
            max_value=2050,
            value=2020
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

        st.session_state.vehiculos.append(
            {
                "id": len(st.session_state.vehiculos) + 1,
                "marca": marca,
                "modelo": modelo,
                "anio": anio,
                "kilometraje": kilometraje,
            }
        )

        st.success("Vehículo registrado")

# ==========================
# Mantenimientos
# ==========================

with tab2:

    if not st.session_state.vehiculos:

        st.warning(
            "Primero registra un vehículo"
        )

    else:

        opciones = {
            f"{v['marca']} {v['modelo']}":
            v["id"]
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
            min_value=0.0
        )

        km = st.number_input(
            "Kilometraje actual",
            min_value=0
        )

        if st.button("Guardar mantenimiento"):

            st.session_state.mantenimientos.append(
                {
                    "vehiculo_id":
                        opciones[vehiculo],
                    "servicio":
                        servicio,
                    "costo":
                        costo,
                    "kilometraje":
                        km
                }
            )

            st.success(
                "Mantenimiento guardado"
            )

# ==========================
# Historial
# ==========================

with tab3:

    st.subheader(
        "Vehículos registrados"
    )

    if st.session_state.vehiculos:

        st.dataframe(
            pd.DataFrame(
                st.session_state.vehiculos
            )
        )

    st.subheader(
        "Mantenimientos"
    )

    if st.session_state.mantenimientos:

        st.dataframe(
            pd.DataFrame(
                st.session_state.mantenimientos
            )
        )

# ==========================
# IA
# ==========================

with tab4:

    st.subheader(
        "Asistente de mantenimiento"
    )

    if not gemini_ok:

        st.info(
            "Configura GEMINI_API_KEY para habilitar IA"
        )

    consulta = st.text_area(
        "Describe el vehículo e historial"
    )

    if st.button(
        "Analizar con IA"
    ):

        if gemini_ok:

            prompt = f"""
        
