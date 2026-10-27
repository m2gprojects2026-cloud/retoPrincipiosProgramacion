import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

# ==========================
# Configuración de Página
# ==========================
st.set_page_config(
    page_title="AutoCare AI",
    page_icon="🚗",
    layout="wide"
)

# ==========================
# Conexión a Base de Datos (PostgreSQL)
# ==========================
# Inicializamos la conexión utilizando el conector SQL nativo de Streamlit
try:
    conn = st.connection("postgresql", type="sql")
    db_ok = True
except Exception as e:
    db_ok = False
    st.error(f"❌ Error al conectar con PostgreSQL Guadamuz: {e}")

# Función para inicializar las tablas en PostgreSQL si no existen
def inicializar_db():
    if db_ok:
        with conn.session as session:
            # Tabla de vehículos
            session.execute("""
                CREATE TABLE IF NOT EXISTS vehiculos (
                    id SERIAL PRIMARY KEY,
                    marca VARCHAR(100),
                    modelo VARCHAR(100),
                    anio INT,
                    kilometraje INT
                );
            """)
            # Tabla de mantenimientos
            session.execute("""
                CREATE TABLE IF NOT EXISTS mantenimientos (
                    id SERIAL PRIMARY KEY,
                    vehiculo_id INT REFERENCES vehiculos(id) ON DELETE CASCADE,
                    servicio TEXT,
                    costo NUMERIC(10, 2),
                    kilometraje INT
                );
            """)
            session.commit()

inicializar_db()

# ==========================
# IA Gemini (SDK google-genai)
# ==========================
client = None
MODELO = "gemini-2.5-flash"

try:
    clave = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=clave)
except Exception:
    pass

# ==========================
# Interfaz - Título y Pestañas
# ==========================
st.title("🚗 AutoCare AI (Database Powered)")

tab1, tab2, tab3, tab4 = st.tabs([
    "Vehículos",
    "Mantenimientos",
    "Historial",
    "IA"
])

# ==========================
# Pestaña 1: Vehículos
# ==========================
with tab1:
    st.subheader("Registrar vehículo en base de datos")
    with st.form("vehiculo_form"):
        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        anio = st.number_input("Año", min_value=1980, max_value=2050, value=2024)
        kilometraje = st.number_input("Kilometraje", min_value=0, value=0)
        guardar = st.form_submit_button("Guardar vehículo")

    if guardar:
        if not db_ok:
            st.error("Base de datos no disponible.")
        elif not marca or not modelo:
            st.warning("Por favor, completa la marca y modelo del vehículo.")
        else:CustomSQL = """
            INSERT INTO vehiculos (marca, modelo, anio, kilometraje)
            VALUES (:marca, :modelo, :anio, :kilometraje);
        """
        with conn.session as session:
            session.execute(CustomSQL, {"marca": marca, "modelo": modelo, "anio": anio, "kilometraje": kilometraje})
            session.commit()
        st.success(f"✅ {marca} {modelo} registrado correctamente en PostgreSQL.")

# ==========================
# Pestaña 2: Mantenimientos
# ==========================
with tab2:
    if db_ok:
        # Obtenemos los vehículos registrados directamente de la DB
        df_vehiculos = conn.query("SELECT id, marca, modelo FROM vehiculos;", ttl="0")
        
        if df_vehiculos.empty:
            st.warning("Primero registra un vehículo en la pestaña anterior.")
        else:
            # Creamos diccionario de opciones para el selector
            opciones = {
                f"{row['marca']} {row['modelo']} (ID: {row['id']})": row['id']
                for _, row in df_vehiculos.iterrows()
            }
            
            vehiculo_seleccionado = st.selectbox("Vehículo", list(opciones.keys()))
            servicio = st.text_input("Servicio realizado")
            costo = st.number_input("Costo (€)", min_value=0.0, format="%.2f")
            km_actual = st.number_input("Kilometraje del servicio", min_value=0)
            
            if st.button("Guardar mantenimiento"):
                if not servicio:
                    st.warning("Describe el servicio realizado.")
                else:
                    id_vehiculo = opciones[vehiculo_seleccionado]
                    insert_mantenimiento = """
                        INSERT INTO mantenimientos (vehiculo_id, servicio, costo, kilometraje)
                        VALUES (:vehiculo_id, :servicio, :costo, :kilometraje);
                    """
                    with conn.session as session:
                        session.execute(insert_mantenimiento, {
                            "vehiculo_id": id_vehiculo,
                            "servicio": servicio,
                            "costo": costo,
                            "kilometraje": km_actual
                        })
                        session.commit()
                    st.success("✅ Mantenimiento guardado en PostgreSQL.")

# ==========================
# Pestaña 3: Historial
# ==========================
with tab3:
    st.subheader("Historial en Tiempo Real (PostgreSQL)")
    if db_ok:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚘 Vehículos")
            df_v = conn.query("SELECT * FROM vehiculos ORDER BY id DESC;", ttl="0")
            if not df_v.empty:
                st.dataframe(df_v, use_container_width=True)
            else:
                st.info("No hay vehículos registrados.")
                
        with col2:
            st.markdown("### 🛠️ Servicios de Mantenimiento")
            # Hacemos una consulta con JOIN para mostrar la marca y modelo del vehículo asociado
            query_m = """
                SELECT m.id, v.marca, v.modelo, m.servicio, m.costo, m.kilometraje 
                FROM mantenimientos m 
                JOIN vehiculos v ON m.vehiculo_id = v.id
                ORDER BY m.id DESC;
            """
            df_m = conn.query(query_m, ttl="0")
            if not df_m.empty:
                st.dataframe(df_m, use_container_width=True)
            else:
                st.info("No hay servicios registrados.")

# ==========================
# Pestaña 4: IA
# ==========================
with tab4:
    st.subheader("Asistente de Mantenimiento Predictivo")
    
    if client is None:
        st.info("Configura GEMINI_API_KEY en tus Secretos de Streamlit para habilitar la IA.")
    
    consulta = st.text_area(
        "Describe los síntomas del vehículo o solicita un plan de mantenimiento basado en el historial:"
    )
    
    if st.button("Analizar con IA"):
        if client is not None:
            with st.spinner("Analizando con Gemini..."):
                try:
                    prompt = f"""
                    Actúas como un mecánico automotriz experto.
                    
                    Analiza la siguiente consulta del usuario:
                    {consulta}
                    
                    Por favor, proporciona estructuradamente:
                    1. Riesgos o averías potenciales detectadas.
                    2. Lista de mantenimientos recomendados a corto y mediano plazo.
                    3. Nivel de prioridad general (Baja, Media, Alta).
                    4. Explicación sencilla, comprensible para un conductor promedio.
                    """
                    
                    # Usamos la sintaxis oficial actualizada de google-genai
                    respuesta = client.models.generate_content(
                        model=MODELO,
                        contents=prompt
                    )
                    st.markdown(respuesta.text)
                except Exception as e:
                    st.error(f"Error al consultar a Gemini: {e}")
        else:
            st.warning("La API de Gemini no está configurada.")
