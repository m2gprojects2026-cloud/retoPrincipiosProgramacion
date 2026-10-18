"""import streamlit as st
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
"""

import streamlit as st
import sqlite3
import google.generativeai as genai
from datetime import datetime

# ----------------------------------
# Configuración
# ----------------------------------
st.set_page_config(
    page_title="AutoCare AI",
    page_icon="🚗",
    layout="wide"
)

# ----------------------------------
# Gemini
# ----------------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    gemini_ok = True
except:
    gemini_ok = False

# ----------------------------------
# Base de datos SQLite
# ----------------------------------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehiculos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT,
    modelo TEXT,
    anio INTEGER,
    kilometraje INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS mantenimientos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_id INTEGER,
    fecha TEXT,
    servicio TEXT,
    kilometraje INTEGER,
    costo REAL
)
""")

conn.commit()

# ----------------------------------
# Título
# ----------------------------------
st.title("🚗 AutoCare AI")
st.write(
    "Gestiona el mantenimiento de tu vehículo y recibe recomendaciones inteligentes."
)

# ----------------------------------
# Registrar vehículo
# ----------------------------------
st.header("Registrar vehículo")

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
        "Kilometraje actual",
        min_value=0,
        value=10000
    )

    guardar = st.form_submit_button("Guardar vehículo")

    if guardar:
        cursor.execute(
            """
            INSERT INTO vehiculos
            (marca, modelo, anio, kilometraje)
            VALUES (?, ?, ?, ?)
            """,
            (marca, modelo, anio, kilometraje)
        )

        conn.commit()
        st.success("Vehículo registrado correctamente")

# ----------------------------------
# Lista de vehículos
# ----------------------------------
st.header("Mis vehículos")

cursor.execute("""
SELECT id, marca, modelo, anio, kilometraje
FROM vehiculos
""")

vehiculos = cursor.fetchall()

if vehiculos:

    nombres = {
        v[0]: f"{v[1]} {v[2]} ({v[3]})"
        for v in vehiculos
    }

    vehiculo_id = st.selectbox(
        "Seleccione un vehículo",
        options=list(nombres.keys()),
        format_func=lambda x: nombres[x]
    )

    # ----------------------------------
    # Registrar mantenimiento
    # ----------------------------------
    st.subheader("Registrar mantenimiento")

    with st.form("mantenimiento_form"):

        servicio = st.selectbox(
            "Tipo de servicio",
            [
                "Cambio de aceite",
                "Filtros",
                "Frenos",
                "Batería",
                "Llantas",
                "Otro"
            ]
        )

        km_servicio = st.number_input(
            "Kilometraje",
            min_value=0
        )

        costo = st.number_input(
            "Costo",
            min_value=0.0
        )

        guardar_servicio = st.form_submit_button(
            "Guardar mantenimiento"
        )

        if guardar_servicio:

            cursor.execute(
                """
                INSERT INTO mantenimientos
                (
                    vehiculo_id,
                    fecha,
                    servicio,
                    kilometraje,
                    costo
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    vehiculo_id,
                    datetime.now().strftime("%Y-%m-%d"),
                    servicio,
                    km_servicio,
                    costo
                )
            )

            conn.commit()

            st.success("Mantenimiento registrado")

    # ----------------------------------
    # Historial
    # ----------------------------------
    st.subheader("Historial")

    cursor.execute(
        """
        SELECT fecha, servicio, kilometraje, costo
        FROM mantenimientos
        WHERE vehiculo_id = ?
        ORDER BY fecha DESC
        """,
        (vehiculo_id,)
    )

    historial = cursor.fetchall()

    if historial:

        import pandas as pd

        df = pd.DataFrame(
            historial,
            columns=[
                "Fecha",
                "Servicio",
                "Kilometraje",
                "Costo"
            ]
        )

        st.dataframe(df, use_container_width=True)

    # ----------------------------------
    # Consejos IA
    # ----------------------------------
    st.subheader("🤖 Recomendación IA")

    if st.button("Generar recomendación"):

        if not gemini_ok:
            st.error(
                "No se encontró la configuración de Gemini."
            )

        else:

            r.execute(
                """
                SELECT fecha, servicio, kilometraje, costo
                FROM mantenimientos
                WHERE vehiculo_id = ?
                """,
                (vehiculo_id,)
            )

            historial_ia = cursor.fetchall()

            prompt = f"""
            Actúa como un asesor básico de mantenimiento automotriz.

            Historial:

            {historial_ia}

            Genera:
            1. Estado general.
            2. Próximo mantenimiento sugerido.
            3. Recomendaciones preventivas.

            Responde en español.
            """

            try:

                respuesta = model.generate_content(prompt)

                st.success("Análisis completado")
                st.write(respuesta.text)

            except Exception:
                st.error(
                    "El servicio de IA no está disponible temporalmente."
                )

else:
    st.info("Aún no existen vehículos registrados.")
