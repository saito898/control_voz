import html
import time
import json
import streamlit as st
import paho.mqtt.client as paho

from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from streamlit_bokeh_events import streamlit_bokeh_events


# =====================================================
# CONFIGURACIÓN DE LA PÁGINA
# =====================================================

st.set_page_config(
    page_title="Control por voz",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =====================================================
# CONFIGURACIÓN MQTT
# =====================================================

BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC = "voice_ctrl"


# =====================================================
# ESTILOS CSS
# =====================================================

st.markdown(
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 5%,
            rgba(119, 94, 255, 0.17), transparent 30%),
        radial-gradient(circle at 95% 30%,
            rgba(44, 207, 230, 0.10), transparent 28%),
        #0b1020;
    color: #f3f4ff;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu,
footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* ENCABEZADO */

.hero {
    text-align: center;
    padding: 35px 10px 30px;
}

.badge {
    display: inline-block;
    color: #b9b0ff;
    background: rgba(139, 124, 255, 0.10);
    border: 1px solid rgba(139, 124, 255, 0.35);
    border-radius: 30px;
    padding: 8px 17px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 22px;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(38px, 6vw, 62px);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -2px;
    color: #f6f5ff;
    margin: 0 0 18px;
}

.gradient-text {
    background: linear-gradient(100deg, #a89aff, #69e2f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    max-width: 620px;
    margin: 0 auto;
    font-size: 16px;
    line-height: 1.8;
    color: #aab6d1;
}

/* INDICADORES */

.metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 15px 0 35px;
}

.metric {
    background: rgba(21, 31, 53, 0.82);
    border: 1px solid rgba(164, 177, 255, 0.14);
    border-radius: 16px;
    padding: 19px 10px;
    text-align: center;
}

.metric-icon {
    font-size: 23px;
    margin-bottom: 8px;
}

.metric-label {
    color: #8190b3;
    letter-spacing: 1.5px;
    font-size: 10px;
    margin-bottom: 7px;
    text-transform: uppercase;
}

.metric-value {
    color: #f0f1ff;
    font-size: 15px;
    font-weight: 700;
}

/* TARJETAS */

.card {
    background: linear-gradient(
        145deg,
        rgba(25, 37, 62, 0.96),
        rgba(16, 25, 44, 0.96)
    );
    border: 1px solid rgba(164, 177, 255, 0.16);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}

.card-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    color: #f2f2ff;
    font-family: 'Manrope', sans-serif;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 10px;
}

.step {
    display: inline-flex;
    min-width: 34px;
    height: 34px;
    align-items: center;
    justify-content: center;
    border-radius: 11px;
    color: #bcb3ff;
    background: rgba(139, 124, 255, 0.15);
    font-size: 14px;
}

.card-description {
    color: #9facc9;
    font-size: 14px;
    line-height: 1.8;
}

/* BOTONES */

.stButton > button {
    width: 100%;
    min-height: 49px;
    border-radius: 12px;
    border: 1px solid rgba(182, 171, 255, 0.5);
    background: linear-gradient(105deg, #8978fa, #6856dc);
    color: white;
    font-size: 15px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(105deg, #a095ff, #7d6df0);
    color: white;
    border-color: #c6beff;
    transform: translateY(-1px);
}

/* TRANSCRIPCIÓN */

.transcription {
    background: rgba(139, 124, 255, 0.08);
    border: 1px solid rgba(139, 124, 255, 0.30);
    border-radius: 14px;
    padding: 20px;
    color: #f1efff;
    font-size: 18px;
    line-height: 1.7;
    overflow-wrap: anywhere;
}

/* INSTRUCCIONES */

.instruction {
    display: flex;
    gap: 15px;
    align-items: flex-start;
    padding: 17px 0;
    border-bottom: 1px solid rgba(164, 177, 255, 0.10);
}

.instruction:last-child {
    border-bottom: none;
}

.instruction-icon {
    font-size: 23px;
    min-width: 30px;
}

.instruction-title {
    color: #e9eaff;
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 5px;
}

.instruction-text {
    color: #9facc9;
    font-size: 13px;
    line-height: 1.7;
}

/* CONEXIÓN */

.connection {
    background: rgba(100, 227, 242, 0.05);
    border: 1px solid rgba(100, 227, 242, 0.19
