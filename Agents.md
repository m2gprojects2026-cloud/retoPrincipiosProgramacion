Proyecto
AutoCare AI es una aplicación desarrollada con Streamlit, PostgreSQL y Gemini que ayuda a los usuarios a identificar posibles problemas mecánicos y recibir recomendaciones de mantenimiento para sus vehículos.

Tecnologías
Python
Streamlit
PostgreSQL (Supabase)
Google Gemini 3.5 Flash
Estructura
app.py: Interfaz principal y flujo de la aplicación.
ia.py: Integración con Gemini y generación de respuestas.
db.py: Conexión y operaciones de base de datos.
Reglas para el Agente
Utilizar siempre variables de entorno o st.secrets para credenciales.
Generar código limpio y reutilizable.
Manejar excepciones de IA y base de datos.
No almacenar claves API en el código.
Mantener respuestas orientadas a usuarios sin conocimientos mecánicos.
Prompt Base
Actúa como un asesor automotriz. Analiza la descripción del usuario y proporciona:

Posibles causas.
Nivel de urgencia.
Recomendaciones de mantenimiento.
Cuándo acudir a un mecánico.
Utiliza lenguaje sencillo y nunca presentes un diagnóstico como definitivo.

Restricciones
No reemplaza la evaluación de un mecánico profesional.
No garantiza diagnósticos exactos.
Priorizar siempre la seguridad del usuario.
