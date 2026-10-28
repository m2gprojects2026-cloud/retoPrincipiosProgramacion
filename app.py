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
MODELO = "gemini-3.5-flash-lite"#"gemini-3.8-flash"

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )

    st.success("✅ Gemini configured successfully")

except Exception as e:

    st.error(
        f"❌ Error configuring Gemini: {str(e)}"
    )

    client = None

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
            min_value=0.0,
            format="%.2f"
        )

        km = st.number_input(
            "Kilometraje",
            min_value=0
        )

        if st.button(
            "Guardar mantenimiento"
        ):

            if not servicio:

                st.warning(
                    "Ingrese el servicio realizado."
                )

            else:

                st.session_state.mantenimientos.append(
                    {
                        "vehiculo_id":
                            opciones[vehiculo],
                        "vehiculo":
                            vehiculo,
                        "servicio":
                            servicio,
                        "costo":
                            costo,
                        "kilometraje":
                            km
                    }
                )

                st.success(
                    "✅ Mantenimiento guardado"
                )

# =====================================
# TAB 3 - Historial
# =====================================

with tab3:

    st.subheader("🚘 Vehículos")

    if st.session_state.vehiculos:

        st.dataframe(
            pd.DataFrame(
                st.session_state.vehiculos
            ),
            use_container_width=True
        )

    else:

        st.info(
            "No hay vehículos registrados."
        )

    st.subheader(
        "🛠️ Mantenimientos"
    )

    if st.session_state.mantenimientos:

        st.dataframe(
            pd.DataFrame(
                st.session_state.mantenimientos
            ),
            use_container_width=True
        )

    else:

        st.info(
            "No hay mantenimientos registrados."
        )

# =====================================
# TAB 4 - IA
# =====================================

with tab4:

    st.subheader(
        "Asistente de Mantenimiento"
    )

    consulta = st.text_area(
        "Describe el problema o consulta sobre el vehículo"
    )

    if st.button(
        "Analizar con IA"
    ):

        if client is None:

            st.warning(
                "Configure GEMINI_API_KEY en Secrets."
            )

        elif not consulta.strip():

            st.warning(
                "Ingrese una consulta."
            )

        else:

            historial_vehiculos = str(
                st.session_state.vehiculos
            )

            historial_mantenimientos = str(
                st.session_state.mantenimientos
            )

            prompt = f"""
            Actúa como un mecánico automotriz experto.

            Vehículos registrados:
            {historial_vehiculos}

            Historial de mantenimiento:
            {historial_mantenimientos}

            Consulta del usuario:
            {consulta}

            Responde en español.

            Incluye:

            1. Riesgos detectados.
            2. Recomendaciones de mantenimiento.
            3. Prioridad (Baja, Media o Alta).
            4. Explicación sencilla.
            """

            try:

                with st.spinner(
                    "Analizando..."
                ):

                    respuesta = client.models.generate_content(
                        model=MODELO,
                        contents=prompt
                    )

                st.markdown(
                    respuesta.text
                )

            except Exception as e:

                st.error(
                    f"Error Gemini: {e}"
                )

# =====================================
# Información
# =====================================

st.sidebar.info(
    """
    AutoCareAI MVP

    ⚠️ Los datos se almacenan temporalmente
    mientras la aplicación permanezca activa.

    Si la aplicación se reinicia,
    los datos se perderán.
    """
)
