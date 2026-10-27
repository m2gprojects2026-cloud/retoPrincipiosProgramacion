import streamlit as st
import pandas as pd

from sqlalchemy import text

from google import genai


# =====================================
# Configuración de página
# =====================================

st.set_page_config(
    page_title="AutoCare AI",
    page_icon="🚗",
    layout="wide"
)


# =====================================
# Conexión PostgreSQL
# =====================================

try:

    conn = st.connection(
        "postgresql",
        type="sql"
    )

    db_ok = True

except Exception as e:

    db_ok = False

    st.error(
        f"❌ Error al conectar con PostgreSQL: {e}"
    )


# =====================================
# Crear tablas
# =====================================

def inicializar_db():

    if not db_ok:
        return

    with conn.session as session:

        session.execute(text("""
            CREATE TABLE IF NOT EXISTS vehiculos (
                id SERIAL PRIMARY KEY,
                marca VARCHAR(100),
                modelo VARCHAR(100),
                anio INTEGER,
                kilometraje INTEGER
            );
        """))

        session.execute(text("""
            CREATE TABLE IF NOT EXISTS mantenimientos (
                id SERIAL PRIMARY KEY,
                vehiculo_id INTEGER
                    REFERENCES vehiculos(id)
                    ON DELETE CASCADE,
                servicio TEXT,
                costo NUMERIC(10,2),
                kilometraje INTEGER
            );
        """))

        session.commit()


inicializar_db()


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
# UI
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
# TAB 1
# =====================================

with tab1:

    st.subheader(
        "Registrar vehículo"
    )

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

        if not db_ok:

            st.error(
                "Base de datos no disponible."
            )

        elif not marca or not modelo:

            st.warning(
                "Debe indicar marca y modelo."
            )

        else:

            sql = text("""
                INSERT INTO vehiculos
                (
                    marca,
                    modelo,
                    anio,
                    kilometraje
                )
                VALUES
                (
                    :marca,
                    :modelo,
                    :anio,
                    :kilometraje
                )
            """)

            with conn.session as session:

                session.execute(
                    sql,
                    {
                        "marca": marca,
                        "modelo": modelo,
                        "anio": int(anio),
                        "kilometraje": int(kilometraje)
                    }
                )

                session.commit()

            st.success(
                "✅ Vehículo guardado"
            )


# =====================================
# TAB 2
# =====================================

with tab2:

    st.subheader(
        "Registrar mantenimiento"
    )

    if db_ok:

        df_vehiculos = conn.query(
            """
            SELECT
                id,
                marca,
                modelo
            FROM vehiculos
            ORDER BY id DESC
            """,
            ttl=0
        )

        if df_vehiculos.empty:

            st.info(
                "No hay vehículos registrados."
            )

        else:

            opciones = {
                f"{row['marca']} {row['modelo']}": row["id"]
                for _, row
                in df_vehiculos.iterrows()
            }

            vehiculo = st.selectbox(
                "Vehículo",
                list(opciones.keys())
            )

   
