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
# IMPORTANTE: EL CSS ESTÁ DENTRO DE LAS COMILLAS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 5%, rgba(119, 94, 255, 0.17), transparent 30%),
        radial-gradient(circle at 95% 30%, rgba(44, 207, 230, 0.10), transparent 28%),
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
    max-width: 1100px;
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

/* CONEXIÓN MQTT */

.connection {
    background: rgba(100, 227, 242, 0.05);
    border: 1px solid rgba(100, 227, 242, 0.19);
    border-radius: 15px;
    padding: 19px;
    margin-top: 18px;
}

.connection-title {
    color: #70e2f0;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 12px;
}

.connection-line {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    padding: 8px 0;
    font-size: 12px;
    border-bottom: 1px solid rgba(100, 227, 242, 0.09);
}

.connection-line:last-child {
    border-bottom: none;
}

.connection-label {
    color: #8d9bb9;
}

.connection-value {
    color: #dce8ff;
    text-align: right;
    overflow-wrap: anywhere;
}

/* PIE DE PÁGINA */

.footer {
    text-align: center;
    color: #7281a2;
    font-size: 12px;
    line-height: 2;
    padding-top: 25px;
    margin-top: 35px;
    border-top: 1px solid rgba(164, 177, 255, 0.13);
}

@media (max-width: 650px) {
    .metrics {
        grid-template-columns: 1fr;
    }

    .card {
        padding: 19px;
    }

    .hero-title {
        letter-spacing: -1px;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# ENCABEZADO PRINCIPAL
# =====================================================

st.markdown("""
<div class="hero">
    <div class="badge">✦ INTERFACES MULTIMODALES</div>

    <div class="hero-title">
        Tu voz,<br>
        <span class="gradient-text">tus comandos.</span>
    </div>

    <div class="hero-description">
        Una nueva forma de interactuar con la tecnología.
        Habla con naturalidad, reconoce tus palabras y
        transmite instrucciones mediante comunicación MQTT.
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# INDICADORES
# =====================================================

st.markdown("""
<div class="metrics">

    <div class="metric">
        <div class="metric-icon">🎙️</div>
        <div class="metric-label">Entrada</div>
        <div class="metric-value">Reconocimiento de voz</div>
    </div>

    <div class="metric">
        <div class="metric-icon">💬</div>
        <div class="metric-label">Procesamiento</div>
        <div class="metric-value">Texto reconocido</div>
    </div>

    <div class="metric">
        <div class="metric-icon">📡</div>
        <div class="metric-label">Comunicación</div>
        <div class="metric-value">Protocolo MQTT</div>
    </div>

</div>
""", unsafe_allow_html=True)


# =====================================================
# ESTADO DE LA APLICACIÓN
# =====================================================

if "ultimo_texto" not in st.session_state:
    st.session_state.ultimo_texto = ""

if "ultimo_envio" not in st.session_state:
    st.session_state.ultimo_envio = ""


# =====================================================
# DISTRIBUCIÓN EN COLUMNAS
# =====================================================

col_voz, col_info = st.columns([1.15, 0.85], gap="large")


# =====================================================
# PANEL DE VOZ
# =====================================================

with col_voz:

    st.markdown("""
    <div class="card">
        <div class="card-heading">
            <span class="step">01</span>
            Estudio de voz
        </div>

        <div class="card-description">
            Pulsa el botón para activar el reconocimiento.
            Pronuncia tu comando con claridad y espera a que
            aparezca la transcripción.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        text-align:center;
        padding:22px 10px 28px;
    ">
        <div style="
            width:112px;
            height:112px;
            margin:auto;
            display:flex;
            align-items:center;
            justify-content:center;
            border-radius:50%;
            background:linear-gradient(
                145deg,
                rgba(139,124,255,0.23),
                rgba(100,227,242,0.10)
            );
            border:1px solid rgba(166,155,255,0.35);
            box-shadow:0 0 45px rgba(139,124,255,0.12);
            font-size:47px;
        ">🎙️</div>

        <div style="
            color:#e9eaff;
            font-size:18px;
            font-weight:700;
            margin-top:20px;
        ">
            Tu voz es el control
        </div>

        <div style="
            color:#8998b8;
            font-size:13px;
            margin-top:7px;
        ">
            Habla para comenzar la interacción
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón de reconocimiento de voz

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

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=True,
        override_height=75,
        debounce_time=0
    )

    # Procesar resultado del reconocimiento

    if result and "GET_TEXT" in result:

        texto = str(result.get("GET_TEXT", "")).strip()

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

    # Mostrar texto reconocido

    if st.session_state.ultimo_texto:

        st.markdown("""
        <div class="card-heading">
            <span class="step">02</span>
            Comando reconocido
        </div>
        """, unsafe_allow_html=True)

        texto_seguro = html.escape(
            st.session_state.ultimo_texto
        )

        st.markdown(
            f'<div class="transcription">{texto_seguro}</div>',
            unsafe_allow_html=True
        )

        st.write("")

        # Botón para enviar por MQTT

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

                        st.markdown(
                            "**Mensaje transmitido:**"
                        )

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

    st.markdown("""
    <div class="card">

        <div class="card-heading">
            <span class="step">✦</span>
            ¿Cómo funciona?
        </div>

        <div class="card-description">
            Tres pasos conectan tu voz con un dispositivo
            capaz de interpretar tus instrucciones.
        </div>

        <div class="instruction">
            <div class="instruction-icon">🎧</div>
            <div>
                <div class="instruction-title">01 · Habla</div>
                <div class="instruction-text">
                    Activa el micrófono y pronuncia la instrucción
                    que deseas transmitir.
                </div>
            </div>
        </div>

        <div class="instruction">
            <div class="instruction-icon">💬</div>
            <div>
                <div class="instruction-title">02 · Reconoce</div>
                <div class="instruction-text">
                    El navegador convierte tu voz en texto y te
                    permite revisar el comando.
                </div>
            </div>
        </div>

        <div class="instruction">
            <div class="instruction-icon">⚡</div>
            <div>
                <div class="instruction-title">03 · Transmite</div>
                <div class="instruction-text">
                    El mensaje se publica en el tema MQTT para
                    que un dispositivo suscrito pueda recibirlo.
                </div>
            </div>
        </div>

    </div>

    <div class="connection">

        <div class="connection-title">
            ◉ Información de conexión
        </div>

        <div class="connection-line">
            <span class="connection-label">Broker</span>
            <span class="connection-value">
                broker.mqttdashboard.com
            </span>
        </div>

        <div class="connection-line">
            <span class="connection-label">Puerto</span>
            <span class="connection-value">1883</span>
        </div>

        <div class="connection-line">
            <span class="connection-label">Tema MQTT</span>
            <span class="connection-value">voice_ctrl</span>
        </div>

        <div class="connection-line">
            <span class="connection-label">Formato</span>
            <span class="connection-value">JSON</span>
        </div>

    </div>
    """, unsafe_allow_html=True)


# =====================================================
# PIE DE PÁGINA
# =====================================================

st.markdown("""
<div class="footer">
    INTERFACES MULTIMODALES<br>
    CONTROL POR VOZ · COMUNICACIÓN MQTT<br>
    Conectando la voz con el mundo físico.
</div>
""", unsafe_allow_html=True)
