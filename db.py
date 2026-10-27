from sqlalchemy import create_engine, text
import streamlit as st

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def crear_tablas():

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
            vehiculo_id INTEGER REFERENCES vehiculos(id),
            fecha DATE,
            servicio VARCHAR(200),
            kilometraje INTEGER,
            costo NUMERIC(10,2)
        )
        """))
