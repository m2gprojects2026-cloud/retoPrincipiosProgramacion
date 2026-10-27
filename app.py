
import streamlit as st
import pandas as pd

from sqlalchemy import text
from db import engine, crear_tablas
from ia import recomendar

crear_tablas()

st.set_page_config(
    page_title="AutoCare AI",
    page_icon="🚗"
)

st.title("🚗 AutoCare AI")

tab1, tab2, tab3 = st.tabs(
    [
        "Vehículos",
        "Mantenimientos",
        "IA"
    ]
)

with tab1:

    st.subheader("Registrar Vehículo")

    marca = st.text_input("Marca")
    modelo = st.text_input("Modelo")
    anio = st.number_input(
        "Año",
        1980,
        2050
    )

    kilometraje = st.number_input(
        "Kilometraje",
        0
    )

    if st.button("Guardar Vehículo"):

        with engine.begin() as conn:

            conn.execute(
                text("""
                INSERT INTO vehiculos
                (marca, modelo, anio, kilometraje)
                VALUES
                (:marca,:modelo,:anio,:km)
                """),
                {
                    "marca": marca,
                    "modelo": modelo,
                    "anio": anio,
                    "km": kilometraje
                }
            )

        st.success("Vehículo registrado")

with tab2:

    st.subheader("Registrar mantenimiento")

    with engine.begin() as conn:

        vehiculos = conn.execute(
            text("""
            SELECT id,
                   marca,
                   modelo
            FROM vehiculos
            """)
        ).fetchall()

    opciones = {
        f"{v[1]} {v[2]}": v[0]
        for v in vehiculos
    }

    seleccionado = st.selectbox(
        "Vehículo",
        opciones.keys()
    )

    servicio = st.text_input(
        "Servicio realizado"
    )

    costo = st.number_input(
        "Costo",
        0.0
    )

    km = st.number_input(
        "Kilometraje actual",
        0
    )

    if st.button("Guardar mantenimiento"):

        with engine.begin() as conn:

            conn.execute(
                text("""
                INSERT INTO mantenimientos
                (
                    vehiculo_id,
                    fecha,
                    servicio,
                    kilometraje,
                    costo
                )
                VALUES
                (
                    :vehiculo,
                    CURRENT_DATE,
                    :servicio,
                    :km,
                    :costo
                )
                """),
                {
                    "vehiculo": opciones[seleccionado],
                    "servicio": servicio,
                    "km": km,
                    "costo": costo
                }
            )

        st.success("Mantenimiento guardado")

with tab3:

    st.subheader("Asistente IA")

    historial = st.text_area(
        "Describe el historial"
    )

    if st.button("Analizar"):

        recomendacion = recomendar(historial)

        st.success(
            f"Próximo mantenimiento recomendado: {recomendacion}"
        )

