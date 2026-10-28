import streamlit as st

st.title("PostgreSQL Test")

try:

    conn = st.connection(
        "postgresql",
        type="sql"
    )

    result = conn.query(
        "SELECT NOW() AS fecha",
        ttl=0
    )

    st.success("✅ Connected!")

    st.dataframe(result)

except Exception as e:

    st.error(f"Connection error: {e}")
