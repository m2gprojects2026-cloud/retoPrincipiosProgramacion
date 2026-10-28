import streamlit as st
import pandas as pd

from sqlalchemy import create_engine, text

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
# PostgreSQL / Supabase
# =====================================

engine = None

try:

    engine = create_engine(
        st.secrets["DATABASE_URL"]
    )

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    st.sidebar.success(
        "✅ PostgreSQL conectado"
    )

except Exception as e:

    st.sidebar.error(
        f"❌ Error PostgreSQL: {e}"
    )

# =====================================
# Crear tablas
# =====================================

def inicializar_db():

    if engine is None:
        return

    with engine.begin() as conn:

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS vehiculos(
            id SERIAL PRIMARY KEY,
            marca VARCHAR(100),
            modelo VARCHAR(100),
            anio INTEGER,
            kilometraje INTEGER
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS mantenimientos(
            id SERIAL PRIMARY KEY,
            vehiculo_id INTEGER
                REFERENCES vehiculos(id)
                ON DELETE CASCADE,
            servicio TEXT,
            costo NUMERIC(10,2),
            kilometraje INTEGER
        )
        """))

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

    st.sidebar.success(
        "✅ Gemini conectado"
    )

except Exception as e:

    st.sidebar.error(
        f"❌ Gemini: {e}"
    )

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

        if not marca or not modelo:

            st.warning(
                "Debe indicar marca y modelo."
            )

        else:

            with engine.begin() as conn:

                conn.execute(
                    text("""
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
                    """),
                    {
                        "marca": marca,
                        "modelo": modelo,
                        "anio": int(anio),
                        "kilometraje": int(kilometraje)
                    }
                )

            st.success(
                "✅ Vehículo registrado"
            )

# =====================================
# TAB 2
# =====================================

with tab2:

    st.subheader(
        "Registrar mantenimiento"
    )

    with engine.connect() as conn:

        df_vehiculos = pd.read_sql(
            text("""
            SELECT *
            FROM vehiculos
            ORDER BY marca
            """),
            conn
        )

    if df_vehiculos.empty:

        st.warning(
            "Primero registre un vehículo."
        )

    else:

        opciones = {
            f"{row['marca']} {row['modelo']}":
                row["id"]
            for _, row
            in df_vehiculos.iterrows()
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

        kilometraje_servicio = st.number_input(
            "Kilometraje del servicio",
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

                with engine.begin() as conn:

                    conn.execute(
                        text("""
                        INSERT INTO mantenimientos
                        (
                            vehiculo_id,
                            servicio,
                            costo,
                            kilometraje
                        )
                        VALUES
                        (
                            :vehiculo_id,
                            :servicio,
                            :costo,
                            :kilometraje
                        )
                        """),
                        {
                            "vehiculo_id":
                                opciones[vehiculo],
                            "servicio":
                                servicio,
                            "costo":
                                costo,
                            "kilometraje":
                                kilometraje_servicio
                        }
                    )

                st.success(
                    "✅ Mantenimiento guardado"
                )

# =====================================
# TAB 3
# =====================================

with tab3:

    st.subheader(
        "🚘 Vehículos"
    )

    with engine.connect() as conn:

        df_v = pd.read_sql(
            text("""
            SELECT *
            FROM vehiculos
            ORDER BY id DESC
            """),
            conn
        )

    st.dataframe(
        df_v,
        use_container_width=True
    )

    st.subheader(
        "🛠️ Mantenimientos"
    )

    with engine.connect() as conn:

        df_m = pd.read_sql(
            text("""
            SELECT
                m.id,
                v.marca,
                v.modelo,
                m.servicio,
                m.costo,
                m.kilometraje
            FROM mantenimientos m
            JOIN vehiculos v
                 ON v.id = m.vehiculo_id
            ORDER BY m.id DESC
            """),
            conn
        )

    st.dataframe(
        df_m,
        use_container_width=True
    )

# =====================================
# TAB 4
# =====================================

with tab4:

    st.subheader(
        "Asistente IA"
    )

    consulta = st.text_area(
        "Describe el problema o consulta"
    )

    if st.button(
        "Analizar con IA"
    ):

        if client is None:

            st.warning(
                "Gemini no configurado."
            )

        elif not consulta.strip():

            st.warning(
                "Ingrese una consulta."
            )

        else:

            with engine.connect() as conn:

                vehiculos = pd.read_sql(
                    text("""
                    SELECT *
                    FROM vehiculos
                    """),
                    conn
                )

                mantenimientos = pd.read_sql(
                    text("""
                    SELECT *
                    FROM mantenimientos
                    """),
                    conn
                )

            prompt = f"""
            Actúa como un mecánico automotriz experto.

            VEHÍCULOS:

            {vehiculos.to_string(index=False)}

            HISTORIAL DE MANTENIMIENTOS:

            {mantenimientos.to_string(index=False)}

            CONSULTA:

            {consulta}

            Genera:

            1. Riesgos detectados.
            2. Próximos mantenimientos.
            3. Prioridad (Baja, Media o Alta).
            4. Explicación sencilla.
            5. Recomendaciones para ahorrar costos.
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
# Sidebar
# =====================================

st.sidebar.info(
    """
    AutoCareAI

    ✅ PostgreSQL (Supabase)
    ✅ Gemini
    ✅ Persistencia permanente
    """
)
