import streamlit as st

st.set_page_config(page_title="Prueba de diseño")

st.markdown("""
<style>
body {
    background-color: #0b1020;
}

.titulo {
    color: #a89aff;
    font-size: 40px;
    font-weight: bold;
    text-align: center;
}

.descripcion {
    color: #ffffff;
    font-size: 18px;
    text-align: center;
}
</style>

<div class="titulo">Control por voz</div>
<div class="descripcion">La interfaz está funcionando correctamente.</div>
""", unsafe_allow_html=True)
