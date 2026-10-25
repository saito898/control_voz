import time
import json
import streamlit as st
import paho.mqtt.client as paho

from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from streamlit_bokeh_events import streamlit_bokeh_events


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Control por voz",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BROKER = "broker.mqttdashboard.com"
PORT = 1883
TOPIC = "voice_ctrl"


# =====================================================
# DISEÑO CSS
# Aquí solo hay estilos, no contenido HTML.
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(119,94,255,.17), transparent 30%),
        radial-gradient(circle at 95% 30%, rgba(44,207,230,.10), transparent 28%),
        #0b1020;
    color: #f3f4ff;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: #f3f4ff !important;
}

p, label, .stMarkdown {
    color: #c2cbe0;
}

.hero-title {
    text-align: center;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(38px, 6vw, 62px);
    font-weight: 800;
    letter-spacing: -2px;
    color: #f6f5ff;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(21,31,53,.78);
    border: 1px solid rgba(164,177,255,.16);
    border-radius: 18px;
}

div[data-testid="stMetric"] {
    background: rgba(21,31,53,.8);
    border: 1px solid rgba(164,177,255,.14);
    border-radius: 15px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #9facc9;
}

div[data-testid="stMetricValue"] {
    color: #f0f1ff;
}

.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    border: 1px solid rgba(182,171,255,.5);
    background: linear-gradient(105deg,#8978fa,#6856dc);
    color: white;
    font-size: 15px;
    font-weight: 700;
    transition: .2s ease;
}

.stButton > button:hover {
    background: linear-gradient(105deg,#a095ff,#7d6df0);
    color: white;
    border-color: #c6beff;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: rgba(164,177,255,.15);
}

.caption {
    color: #8998b8;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# ESTADO DE LA APLICACIÓN
# =====================================================

if "ultimo_texto" not in st.session_state:
    st.session_state.ultimo_texto = ""

if "ultimo_envio" not in st.session_state:
    st.session_state.ultimo_envio = ""


# =====================================================
# ENCABEZADO
# =====================================================

st.markdown(
    "<p style='text-align:center; color:#b9b0ff; "
    "letter-spacing:3px; font-size:12px; font-weight:bold;'>"
    "✦ INTERFACES MULTIMODALES ✦</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align:center; font-size:52px; "
    "font-weight:800; margin-bottom:0;'>"
    "Tu voz, <span style='color:#8d9cff;'>tus comandos.</span>"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; max-width:650px; "
    "margin:15px auto 30px auto; color:#aab6d1; "
    "font-size:16px;'>"
    "Habla con naturalidad, reconoce tus palabras y transmite "
    "instrucciones mediante comunicación MQTT."
    "</p>",
    unsafe_allow_html=True
)


# =====================================================
# INDICADORES
# =====================================================

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("🎙️ ENTRADA", "Reconocimiento de voz")

with m2:
    st.metric("💬 PROCESAMIENTO", "Texto reconocido")

with m3:
    st.metric("📡 COMUNICACIÓN", "Protocolo MQTT")


st.write("")


# =====================================================
# COLUMNAS PRINCIPALES
# =====================================================

col_voz, col_info = st.columns([1.15, 0.85], gap="large")


# =====================================================
# PANEL DE RECONOCIMIENTO DE VOZ
# =====================================================

with col_voz:

    with st.container(border=True):
        st.subheader("01 · Estudio de voz")
        st.write(
            "Pulsa el botón para activar el reconocimiento. "
            "Pronuncia tu comando con claridad."
        )

    st.write("")

    with st.container(border=True):
        st.markdown(
            "<p style='text-align:center; font-size:55px;'>🎙️</p>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<h3 style='text-align:center;'>"
            "Tu voz es el control"
            "</h3>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p style='text-align:center; color:#8998b8;'>"
            "Habla para comenzar la interacción"
            "</p>",
            unsafe_allow_html=True
        )

        # Botón de Bokeh para activar el micrófono
        stt_button = Button(
            label="🎙️ Iniciar reconocimiento de voz",
            width=360,
            height=55,
            button_type="primary"
        )

        stt_button.js_on_event(
            "button_click",
            CustomJS(code="""
                var SpeechRecognition =
                    window.SpeechRecognition ||
                    window.webkitSpeechRecognition;

                if (!SpeechRecognition) {
                    document.dispatchEvent(
                        new CustomEvent("GET_TEXT", {
                            detail: "ERROR_BROWSER_NO_COMPATIBLE"
                        })
                    );
                } else {
                    var recognition = new SpeechRecognition();

                    recognition.lang = "es-CO";
                    recognition.continuous = false;
                    recognition.interimResults = false;

                    recognition.onresult = function(e) {
                        var value = e.results[0][0].transcript;

                        document.dispatchEvent(
                            new CustomEvent("GET_TEXT", {
                                detail: value
                            })
                        );
                    };

                    recognition.onerror = function(e) {
                        document.dispatchEvent(
                            new CustomEvent("GET_TEXT", {
                                detail: "ERROR_VOZ_" + e.error
                            })
                        );
                    };

                    recognition.start();
                }
            """)
        )

        resultado = streamlit_bokeh_events(
            stt_button,
            events="GET_TEXT",
            key="listen",
            refresh_on_update=True,
            override_height=75,
            debounce_time=0
        )

    # Procesar el texto recibido del navegador
    if resultado and "GET_TEXT" in resultado:

        texto = str(resultado.get("GET_TEXT", "")).strip()

        if texto == "ERROR_BROWSER_NO_COMPATIBLE":
            st.error(
                "Tu navegador no admite el reconocimiento de voz. "
                "Prueba con Google Chrome."
            )

        elif texto.startswith("ERROR_VOZ_"):
            st.error(
                "No se pudo reconocer la voz. Detalle: "
                + texto.replace("ERROR_VOZ_", "")
            )

        elif texto:
            st.session_state.ultimo_texto = texto

    st.write("")

    # Mostrar el comando reconocido
    if st.session_state.ultimo_texto:

        with st.container(border=True):
            st.subheader("02 · Comando reconocido")
            st.info(st.session_state.ultimo_texto)

            if st.button(
                "↗ Enviar comando por MQTT",
                key="enviar_mqtt",
                use_container_width=True
            ):

                cliente = None

                try:
                    with st.spinner("Transmitiendo comando..."):

                        client_id = (
                            "control_voz_"
                            + str(int(time.time() * 1000))
                        )

                        # Compatibilidad con Paho MQTT 1.x y 2.x
                        try:
                            cliente = paho.Client(
                                callback_api_version=(
                                    paho.CallbackAPIVersion.VERSION1
                                ),
                                client_id=client_id
                            )
                        except (AttributeError, TypeError):
                            cliente = paho.Client(
                                client_id=client_id
                            )

                        cliente.connect(
                            BROKER,
                            PORT,
                            keepalive=30
                        )

                        cliente.loop_start()

                        mensaje = json.dumps(
                            {
                                "Act1": (
                                    st.session_state.ultimo_texto.strip()
                                )
                            },
                            ensure_ascii=False
                        )

                        info = cliente.publish(
                            TOPIC,
                            mensaje,
                            qos=0
                        )

                        info.wait_for_publish(timeout=10)

                        if info.is_published():
                            st.session_state.ultimo_envio = (
                                st.session_state.ultimo_texto
                            )

                            st.success(
                                "¡Comando enviado correctamente!"
                            )

                            st.write("Mensaje transmitido:")
                            st.json(json.loads(mensaje))

                        else:
                            st.warning(
                                "No se pudo confirmar la publicación."
                            )

                except Exception as error:
                    st.error(
                        "No fue posible enviar el comando por MQTT."
                    )
                    st.caption(f"Detalle técnico: {error}")

                finally:
                    if cliente is not None:
                        try:
                            cliente.loop_stop()
                            cliente.disconnect()
                        except Exception:
                            pass

        if st.session_state.ultimo_envio:
            st.caption(
                "Último comando enviado: "
                + st.session_state.ultimo_envio
            )

    else:
        st.info(
            "Tu transcripción aparecerá aquí después de hablar."
        )


# =====================================================
# PANEL INFORMATIVO
# =====================================================

with col_info:

    with st.container(border=True):
        st.subheader("✦ ¿Cómo funciona?")
        st.write(
            "Tres pasos conectan tu voz con un dispositivo "
            "capaz de interpretar tus instrucciones."
        )

        st.divider()

        st.markdown("### 🎧 01 · Habla")
        st.write(
            "Activa el micrófono y pronuncia la instrucción "
            "que deseas transmitir."
        )

        st.divider()

        st.markdown("### 💬 02 · Reconoce")
        st.write(
            "El navegador convierte tu voz en texto y te permite "
            "revisar el comando antes de enviarlo."
        )

        st.divider()

        st.markdown("### ⚡ 03 · Transmite")
        st.write(
            "El mensaje se publica en el tema MQTT para que "
            "un dispositivo suscrito pueda recibirlo."
        )

    st.write("")

    with st.container(border=True):
        st.subheader("📡 Información de conexión")

        st.caption("BROKER")
        st.code(BROKER, language=None)

        st.caption("PUERTO")
        st.write(PORT)

        st.caption("TEMA MQTT")
        st.code(TOPIC, language=None)

        st.caption("FORMATO DEL MENSAJE")
        st.code('{"Act1": "texto reconocido"}', language="json")


# =====================================================
# PIE DE PÁGINA
# =====================================================

st.divider()

st.markdown(
    "<p style='text-align:center; color:#7281a2; font-size:12px;'>"
    "INTERFACES MULTIMODALES<br>"
    "CONTROL POR VOZ · COMUNICACIÓN MQTT<br>"
    "Conectando la voz con el mundo físico."
    "</p>",
    unsafe_allow_html=True
)
