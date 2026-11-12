"""
Dashboard de TanIA.

Lee solo datos agregados (data/agg/*.json): ningún texto de prompts reales vive en el repo.
Tres pestañas, como en el boceto: Uso (TanIA), Cognición (Ketty) y Recomendaciones (Sandra),
más una vista docente agregada y anónima.

Correr en local:  uv run streamlit run app/streamlit_app.py
"""

import base64
import json
import os
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[1]
AGG = RAIZ / "data" / "agg"
sys.path.insert(0, str(RAIZ / "backend"))
load_dotenv(RAIZ / ".env")   # en local, la clave vive en .env (nunca en el repo)

st.set_page_config(page_title="TanIA", page_icon="🌱", layout="wide")

# ---------------------------------------------------------------------------
# 1. Estética: crema cálido, títulos en serif, Cognición con otra paleta
# ---------------------------------------------------------------------------
BAJO, ALTO = "#eb6834", "#2a78d6"   # paleta validada (naranja = bajo aprendizaje, azul = alto)
VIOLETA = "#6250d6"                  # color de la capa cognitiva (vista docente)
MARINO, CELESTE, ESTRELLA = "#14213d", "#a9d8f5", "#f6c945"   # Ketty: noche estrellada
TINTA, TINTA2 = "#1f1d1a", "#52514e"

st.markdown("""
<style>
h1, h2, h3 { font-family: Georgia, 'Times New Roman', serif !important; font-weight: 700 !important; }
.st-key-ketty { background: #14213d; border-radius: 16px; padding: 1.4rem 1.6rem 2.6rem; position: relative; overflow: hidden; }
.st-key-ketty, .st-key-ketty p, .st-key-ketty h2, .st-key-ketty h3, .st-key-ketty li,
.st-key-ketty span, .st-key-ketty summary, .st-key-ketty small, .st-key-ketty div[data-testid="stCaptionContainer"] { color: #ffffff !important; }
.st-key-ketty * { color: #ffffff !important; opacity: 1 !important; }
.st-key-ketty .etiqueta { color: #f6c945 !important; }
.st-key-ketty::before { content: "✦"; position: absolute; top: 14px; right: 26px; color: #f6c945; font-size: 1.3rem; opacity: .9; }
.st-key-ketty::after { content: "✧   ·   ✦"; position: absolute; bottom: 12px; left: 22px; color: #f6c945; font-size: .9rem; opacity: .7; letter-spacing: .3em; }
.st-key-ketty details { border-color: #2c3e66 !important; }
.st-key-sandra { background: #fde7ef; border-radius: 16px; padding: 1.4rem 1.6rem; position: relative; }
.st-key-sandra .tarjeta { background: #fff7fa; border-color: #f4c6d6; }
.st-key-sandra .etiqueta { color: #b04a74 !important; }
.boba { position: absolute; top: 12px; right: 22px; font-size: 1.6rem; }
.ketty-caja { border-left: 3px solid #f6c945; padding: .4rem .9rem; margin: .4rem 0 1rem; background: #1b2b4d; border-radius: 4px; }
.tarjeta { background: #fffdf8; border: 1px solid #e8e0d0; border-radius: 14px;
           padding: 1rem 1.2rem; margin-bottom: .8rem; }
.antes { color: #52514e; text-decoration: line-through; text-decoration-color: #eb6834; }
.etiqueta { font-size: .78rem; letter-spacing: .06em; text-transform: uppercase; color: #898781; }
.hero { background: #fffaf2; border-radius: 22px; padding: 1.8rem 2.1rem 1.6rem; margin-bottom: 1.2rem; border: 1px solid #ece3d3; }
.hero-fila { display: grid; grid-template-columns: 1fr 1.15fr; gap: 2rem; align-items: center; }
.hero-texto { min-width: 0; }
.hero-desc { color: #52514e; text-align: justify; text-align-last: center; margin: 1.3rem 4rem 0 !important;
        padding-top: 1.1rem; border-top: 1px solid #ece3d3; }
@media (max-width: 800px) { .hero-fila { grid-template-columns: 1fr; } .hero-desc { margin: 1rem 0 0 !important; } }
.cinta { background: #fffaf2; border: 1px solid #ece3d3; border-radius: 22px; overflow: hidden; margin-bottom: 1.2rem; }
.cinta img { width: 100%; height: 210px; object-fit: cover; display: block; }
.cinta .cuerpo { padding: 1.6rem 2.1rem 1.8rem; }
.cinta .desc { max-width: 48rem; }
.hero h1, .cinta h1 { font-size: 3.4rem !important; margin: 0 0 .2rem 0; padding: 0; }
.hero .lema, .cinta .lema { font-size: 1.25rem; font-weight: 600; color: #1f1d1a; margin: 0 0 .5rem 0; }
.hero .desc, .cinta .desc { color: #52514e; margin: 0 0 .9rem 0; max-width: 46rem; }
.pastilla { display: inline-block; background: #ffffffb0; border: 1px solid #efcfb7; border-radius: 999px;
            padding: .15rem .7rem; margin: 0 .35rem .35rem 0; font-size: .82rem; color: #52514e; }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: .9rem; margin: .4rem 0 1.2rem; }
.kpi { background: #fffdf8; border: 1px solid #ece3d3; border-radius: 16px; padding: 1rem 1.2rem; }
.kpi .num { font-family: Georgia, serif; font-size: 2.4rem; font-weight: 700; color: #1f1d1a; line-height: 1.1; }
.kpi .lbl { color: #52514e; font-size: .9rem; }
.kpi.alerta .num { color: #eb6834; }
.st-key-tania { background: #fff6ee; border-radius: 16px; padding: 1.4rem 1.6rem; }
.frase { background: #ffffff; border-left: 4px solid #eb6834; border-radius: 10px; padding: 1rem 1.2rem;
         margin: .2rem 0 1.2rem; font-size: 1.05rem; }
.frase b { color: #c4521f; }
.st-key-ingreso { background: #fffaf2;
        border: 1px solid #f3d9c4; border-radius: 24px; padding: 2.4rem 2.2rem 1.6rem; margin-top: 3rem; }
.logo { font-family: Georgia, serif; font-size: 3.6rem; font-weight: 700; text-align: center; color: #1f1d1a; }
.lema-ingreso { text-align: center; font-weight: 600; margin-bottom: 1.4rem; }
.portada { text-align: left; }
.gifbox { min-width: 0; }
.gifbox img { width: 100%; height: auto; display: block; border-radius: 14px; }
.evid, .testimonio, .plan { background: #fffdf8; border: 1px solid #ece3d3; border-radius: 16px;
        padding: 1.1rem 1.2rem; height: 100%; }
.evid .num { font-family: Georgia, serif; font-size: 2.2rem; font-weight: 700; color: #eb6834; }
.cita { color: #898781; font-size: .82rem; margin-top: .6rem; }
.testimonio { border-left: 4px solid #eb6834; font-style: italic; }
.testimonio .cita { font-style: normal; }
.plan-nombre { font-weight: 700; font-size: 1.05rem; }
.plan-precio { font-family: Georgia, serif; font-size: 1.4rem; color: #c4521f; margin: .3rem 0 .5rem; }
.refs { color: #6b6964; font-size: .8rem; margin-top: 1.6rem; border-top: 1px solid #e8e0d0; padding-top: .8rem; }
.refs ol { padding-left: 1.2rem; margin: .3rem 0 0; } .refs li { margin-bottom: .25rem; }
.refs a { color: #6b6964; }
.pie { text-align: center; color: #52514e; font-size: .85rem; margin-top: 2rem; }
.stButton button { background: #1f1d1a; color: #fbf6ec; border-radius: 6px 18px 6px 6px; }
.stButton button[kind="secondary"] { background: transparent; color: #1f1d1a; border: 1.5px solid #1f1d1a; }
</style>
""", unsafe_allow_html=True)

NOMBRES_MODO = {
    "delegacion_total": "Delegación total",
    "depuracion_iterativa": "Depuración iterativa",
    "dependencia_progresiva": "Dependencia progresiva",
    "generar_luego_comprender": "Generar y luego comprender",
    "hibrido_codigo_explicacion": "Código con explicación",
    "pregunta_conceptual": "Pregunta conceptual",
    "consultor": "Consultor (preguntas)",
    "contratista": "Contratista (órdenes)",
    "brisa_tesis": "Tesis",
    "SIEP-NLP universidad": "Proyecto NLP",
    "descomponer_problema": "Descomponer el problema",
    "leer_errores_y_depurar": "Leer errores y depurar",
    "disenar_codigo": "Diseñar código",
    "sintaxis_y_librerias": "Sintaxis y librerías",
    "interpretar_resultados": "Interpretar resultados",
    "recordar_y_transferir": "Recordar y transferir",
    "en_aprendizaje": "En aprendizaje",
}
BAJOS = {"delegacion_total", "depuracion_iterativa", "dependencia_progresiva"}
DEFINICIONES = {
    "delegacion_total": "Pides la solución completa sin un intento propio.",
    "depuracion_iterativa": "Pides que arregle o verifique tu código, sin buscar por qué falla.",
    "dependencia_progresiva": "Empiezas preguntando y terminas pidiendo que la IA haga todo.",
    "generar_luego_comprender": "Recibes el código y después preguntas para entenderlo.",
    "hibrido_codigo_explicacion": "En el mismo pedido, pides el código y que te lo explique.",
    "pregunta_conceptual": "Solo preguntas cómo o por qué funciona algo, y lo resuelves tú.",
}


def bonito(clave: str) -> str:
    return NOMBRES_MODO.get(clave, clave.replace("_", " ").capitalize())


@st.cache_data(ttl=300)   # se refresca si cambian los datos
def leer(nombre: str):
    ruta = AGG / nombre
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def barras(datos: dict, color, titulo_x="% de tus prompts", oscuro=False):
    """Barras horizontales finas, ordenadas, con tooltip. color: str o función clave->color."""
    pares = sorted(datos.items(), key=lambda kv: kv[1])
    etiquetas = [bonito(k) for k, _ in pares]
    valores = [v for _, v in pares]
    colores = [color(k) if callable(color) else color for k, _ in pares]
    fig = go.Figure(go.Bar(
        x=valores, y=etiquetas, orientation="h", marker_color=colores,
        text=[f"{v:.0f} %" for v in valores], textposition="outside",
        textfont=dict(color="#ffffff" if oscuro else TINTA2),
        hovertemplate="%{y}: %{x:.1f} %<extra></extra>",
    ))
    fig.update_layout(
        height=60 + 42 * len(pares), margin=dict(l=10, r=40, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff" if oscuro else TINTA2), bargap=0.45,
        xaxis=dict(title=dict(text=titulo_x, font=dict(color="#ffffff" if oscuro else TINTA2)),
                   tickfont=dict(color="#ffffff" if oscuro else TINTA2),
                   gridcolor="#2c3e66" if oscuro else "#e1e0d9", zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(color="#ffffff" if oscuro else TINTA2)),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Encabezado
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 2. Ingreso (demo: sin contraseña, con datos de ejemplo)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 2. Portada (lo primero que se ve) e ingreso
# ---------------------------------------------------------------------------
GIF = RAIZ / "app" / "assets" / "encabezado.gif"   # si existe, se muestra en la portada


def gif_html() -> str:
    if not GIF.exists():
        return ""
    datos = base64.b64encode(GIF.read_bytes()).decode()
    return f"<div class='gifbox'><img src='data:image/gif;base64,{datos}' alt='TanIA'></div>"


REFERENCIAS = """<div class='refs'><b>Referencias</b><ol>
<li>Shen, J. H. y Tamkin, A. (2026, febrero). <i>How AI impacts skill formation</i>. arXiv:2601.20245.
<a href='https://arxiv.org/abs/2601.20245'>arxiv.org/abs/2601.20245</a></li>
<li>Bastani, H. et al. (2025, junio). Generative AI without guardrails can harm learning: evidence from high
school mathematics. <i>PNAS</i>, 122(26). <a href='https://doi.org/10.1073/pnas.2422633122'>doi.org/10.1073/pnas.2422633122</a></li>
<li>Sankaranarayanan, S. (2026, marzo). Mitigating "epistemic debt" in generative AI-scaffolded novice programming
using metacognitive scripts. <i>L@S 2026</i>. <a href='https://arxiv.org/abs/2602.20206'>arxiv.org/abs/2602.20206</a></li>
<li>Bjork, E. L. y Bjork, R. A. (2011). Making things hard on yourself, but in a good way. En <i>Psychology and the Real World</i>.</li>
<li>Kruger, J. y Dunning, D. (1999). Unskilled and unaware of it. <i>Journal of Personality and Social Psychology</i>, 77(6).</li>
</ol></div>"""


def gif_img() -> str:
    if not GIF.exists():
        return ""
    return f"<img src='data:image/gif;base64,{base64.b64encode(GIF.read_bytes()).decode()}' alt='TanIA'>"


def ir_a_ingreso():
    st.session_state["pantalla"] = "ingreso"


# Portadas de impacto: (pregunta, a quién le habla, archivo de fondo opcional en app/assets/)
PORTADAS = [
    ("¿Haciendo más, pero aprendiendo menos?", "Para ti", "portada-1.jpg"),
    ("¿Qué harías si te dijeran que tus estudiantes entregan mejores tareas, pero no están aprendiendo más?",
     "Para tu institución", "portada-2.jpg"),
]

PARRAFO_INSTITUCION = ("TanIA parte de un paradigma que diferencia el desempeño del aprendizaje. Con IA, tus "
    "estudiantes entregan mejores tareas, pero en los experimentos rinden hasta 17 % menos cuando la IA ya no "
    "está, y no lo notan. Prohibirla no funciona; detectarla no es suficiente. TanIA le muestra a tu institución "
    "cómo la están usando sus estudiantes y qué habilidades están dejando de practicar, curso por curso, para que "
    "sepas qué reforzar en clase. Siempre con datos agregados, sin rankings ni vigilancia individual.")


def fondo(nombre: str) -> str:
    ruta = RAIZ / "app" / "assets" / nombre
    if not ruta.exists():
        return ""
    tipo = "png" if ruta.suffix == ".png" else "jpeg"
    return f"background-image: url('data:image/{tipo};base64,{base64.b64encode(ruta.read_bytes()).decode()}');"


def portada_impacto():
    n = len(PORTADAS)
    ciclo = 6 * n
    diapos = "".join(
        f"<div class='diapo' style='animation-delay:{i * 6}s'><div class='foto' style=\"{fondo(f)}\"></div><div class='velo'></div>"
        f"<div class='diapo-txt'><span class='para'>{para}</span><p class='pregunta'>{preg}</p></div></div>"
        for i, (preg, para, f) in enumerate(PORTADAS))
    st.markdown(f"""<style>
.impacto {{ position: relative; height: calc(100vh - 5rem); min-height: 520px; border-radius: 26px;
           overflow: hidden; margin: -1rem 0 4rem; background: #111; }}
.foto {{ position: absolute; inset: -12px; background-size: cover; background-position: center; filter: blur(7px); }}
.diapo {{ position: absolute; inset: 0;
         opacity: 0; animation: fundido {ciclo}s infinite; display: flex; align-items: center; justify-content: center; }}
.diapo:first-child {{ opacity: 1; }}
.velo {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.58), rgba(0,0,0,.72)); }}
.diapo-txt {{ position: relative; max-width: 64rem; padding: 0 2.5rem; text-align: center; }}
.para {{ font-size: 1rem !important; letter-spacing: .2em; text-transform: uppercase; color: #f6c945; }}
.pregunta {{ font-family: Georgia, serif; font-weight: 700; color: #ffffff; line-height: 1.12;
            font-size: clamp(2.6rem, 5.4vw, 5rem) !important; margin: 1rem 0 0 !important; text-shadow: 0 2px 24px rgba(0,0,0,.45); }}
@keyframes fundido {{ 0% {{opacity:0}} 6% {{opacity:1}} {100/n - 6:.0f}% {{opacity:1}} {100/n:.0f}% {{opacity:0}} 100% {{opacity:0}} }}
.firma {{ position: absolute; left: 2rem; bottom: 1.6rem; font-family: Georgia, serif; font-weight: 700;
         color: #ffffff; font-size: 1.2rem; z-index: 2; }}
.firma span {{ font-family: sans-serif; font-weight: 400; color: #ffffffb3; font-size: .85rem; margin-left: .3rem; }}
.bajar {{ position: absolute; left: 50%; bottom: 1.4rem; transform: translateX(-50%); z-index: 2; color: #ffffffcc;
         font-size: .8rem; letter-spacing: .12em; text-transform: uppercase; text-align: center;
         animation: flotar 2.2s ease-in-out infinite; }}
.bajar b {{ display: block; font-size: 1.8rem; color: #f6c945; }}
@keyframes flotar {{ 0%,100% {{transform: translate(-50%, 0)}} 50% {{transform: translate(-50%, 8px)}} }}
</style>
<div class='impacto'>{diapos}<div class='firma'>TanIA<span>demo</span></div>
<div class='bajar'>Desliza<b>↓</b></div></div>""", unsafe_allow_html=True)


def portada():
    portada_impacto()
    st.markdown("""<style>
.landing h2 { font-size: 2.1rem !important; margin: 0 0 1.4rem; }
.landing .kicker { font-size: .78rem; letter-spacing: .16em; text-transform: uppercase; color: #c4521f; margin-bottom: .4rem; }
.seccion { margin: 0 0 5rem; }
.cifras { display: grid; grid-template-columns: repeat(3, 1fr); }
.cifra { padding: 0 1.8rem; border-left: 1px solid #e3d9c6; }
.cifra:first-child { border-left: 0; padding-left: 0; }
.cifra .num { font-family: Georgia, serif; font-size: 3.4rem; font-weight: 700; color: #eb6834; line-height: 1; }
.cifra .que { font-size: 1.05rem; font-weight: 600; color: #1f1d1a; margin: .7rem 0 .3rem; }
.cifra .det { color: #52514e; font-size: .92rem; }
.cifra sup, .voz sup { color: #c4521f; }
.voces { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.4rem; }
.voz p { font-family: Georgia, serif; font-style: italic; font-size: 1.12rem; line-height: 1.5; color: #1f1d1a; margin: 0; }
.voz .quien { font-variant: small-caps; letter-spacing: .05em; color: #898781; margin-top: .8rem; font-size: .95rem; }
.pasos { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; counter-reset: paso; }
.paso::before { counter-increment: paso; content: counter(paso); display: inline-flex; width: 2.4rem; height: 2.4rem;
        border-radius: 50%; border: 1.5px solid #eb6834; color: #eb6834; align-items: center; justify-content: center;
        font-family: Georgia, serif; font-weight: 700; margin-bottom: .8rem; }
.paso b { display: block; font-size: 1.1rem; color: #1f1d1a; margin-bottom: .2rem; }
.paso span { color: #52514e; font-size: .95rem; }
.institucion { background: #14213d; border-radius: 26px; padding: 3.2rem 3.4rem; position: relative; overflow: hidden; }
.institucion::before { content: "✦"; position: absolute; top: 1.4rem; right: 2rem; color: #f6c945; font-size: 1.4rem; }
.institucion .kicker { color: #f6c945; }
.institucion h2 { color: #ffffff !important; }
.institucion p { color: #e6ebf5; font-size: 1.12rem; line-height: 1.65; max-width: 46rem; text-align: justify; margin: 0; }
.planes { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.plan2 { border: 1px solid #e3d9c6; border-radius: 18px; padding: 1.4rem 1.3rem; background: #fffdf8; }
.plan2.destacado { border: 2px solid #eb6834; background: #fff6ee; position: relative; }
.plan2.destacado::before { content: "Recomendado"; position: absolute; top: -.75rem; left: 1.2rem; background: #eb6834;
        color: #fff; font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; padding: .15rem .6rem; border-radius: 999px; }
.plan2 .n { font-weight: 700; color: #1f1d1a; }
.plan2 .p { font-family: Georgia, serif; font-size: 1.6rem; font-weight: 700; color: #1f1d1a; margin: .4rem 0; }
.plan2 .p small { font-family: sans-serif; font-size: .8rem; font-weight: 400; color: #898781; }
.plan2 .d { color: #52514e; font-size: .9rem; }
.landing details { color: #6b6964; font-size: .82rem; border-top: 1px solid #e3d9c6; padding-top: .8rem; }
.landing details summary { cursor: pointer; }
.landing details ol { padding-left: 1.2rem; } .landing details li { margin-bottom: .3rem; } .landing details a { color: #6b6964; }
@media (max-width: 800px) { .cifras, .voces, .pasos, .planes { grid-template-columns: 1fr; gap: 1.6rem; }
  .cifra { border-left: 0; padding: 0; } .institucion { padding: 2rem 1.6rem; } }
</style>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='landing'>
<div class='cinta seccion'>{gif_img()}<div class='cuerpo'><h1>TanIA</h1>
<p class='lema'>Haz más con IA, sin dejar de aprender.</p>
<p class='desc'>Leemos tus prompts y te mostramos qué dejas de practicar cuando la IA lo hace por ti.</p></div></div>

<div class='seccion'><div class='kicker'>Lo que dice la evidencia</div><h2>No es si usas IA, sino cómo.</h2>
<div class='cifras'>
<div class='cifra'><div class='num'>24–39 %</div><div class='que'>frente a 65–86 %, según cómo preguntas</div>
<div class='det'>Delegar o pedir que arregle tu código deja poco aprendizaje; preguntar para entender, mucho.<sup>1</sup></div></div>
<div class='cifra'><div class='num'>−17 %</div><div class='que'>cuando la IA ya no está, y nadie lo nota</div>
<div class='det'>Practicaron mejor con ChatGPT, pero rindieron menos en el examen sin él.<sup>2</sup></div></div>
<div class='cifra'><div class='num'>77 %</div><div class='que'>no pudo arreglar su propio código</div>
<div class='det'>Con una pausa para explicarlo antes de aceptarlo, la cifra baja a 39 %.<sup>3</sup></div></div>
</div></div>

<div class='seccion'><div class='kicker'>Lo que nos dijeron</div><h2>Lo sienten, aunque no lo midan.</h2>
<div class='voces'>
<div class='voz'><p>“Mi capacidad intelectual alrededor del código ha empeorado, mi materia gris está en descanso. […] Es como con cualquier cosa: si no me pusiera a hablar inglés en un año, no podría hablar muy bien el inglés ahorita, ¿no?”</p><div class='quien'>Sofía, analista de datos</div></div>
<div class='voz'><p>“Se siente como estar exponiendo algo que tú has hecho el 30 % y otra persona hizo el 70 %; y si te hacen una pregunta, you're dead.”</p><div class='quien'>Mariana, asistente de investigación, sobre presentar código hecho con IA</div></div>
<div class='voz'><p>“Yo creo que sí lo usarían. Y creo que sería útil que lo usen. Porque ya, tú no puedes evitar que la gente use IA. No lo vas a hacer nunca. Ya no se puede.”</p><div class='quien'>Tiago, investigador, sobre el potencial de TanIA en universidades</div></div>
</div></div>

<div class='seccion'><div class='kicker'>Cómo funciona</div><h2>Tres pasos, sin cambiar cómo trabajas.</h2>
<div class='pasos'>
<div class='paso'><b>Subes tu historial</b><span>Exportas tus chats con la IA. Nada se guarda.</span></div>
<div class='paso'><b>Ves tu diagnóstico</b><span>Cómo pides ayuda y qué habilidades dejas de practicar.</span></div>
<div class='paso'><b>Practicas con un plan</b><span>Prompts reformulados, ejercicios y una mini prueba sin IA.</span></div>
</div></div>

<div class='seccion institucion'><div class='kicker'>Para universidades y diplomaturas</div>
<h2>¿Eres una institución?</h2><p>{PARRAFO_INSTITUCION}</p></div>

<div class='seccion'><div class='kicker'>Planes</div><h2>Empieza gratis.</h2>
<div class='planes'>
<div class='plan2'><div class='n'>Prueba</div><div class='p'>Gratis</div><div class='d'>Hasta 200 prompts. Tu diagnóstico de uso y cognición.</div></div>
<div class='plan2'><div class='n'>Pro</div><div class='p'>US$ 4 <small>/ mes</small></div><div class='d'>Programación: reformulaciones, ejercicios y mini prueba sin IA.</div></div>
<div class='plan2 destacado'><div class='n'>Pro Completo</div><div class='p'>US$ 8 <small>/ mes</small></div><div class='d'>Programación y escritura, con plan de repaso y recordatorios.</div></div>
<div class='plan2'><div class='n'>Institucional</div><div class='p'>US$ 3–4 <small>/ estudiante / año</small></div><div class='d'>Vista agregada por curso, privacidad desde el diseño.</div></div>
</div></div>
</div>""", unsafe_allow_html=True)

    _, b1, b2, _ = st.columns([2, 1, 1, 2])
    b1.button("Empieza gratis", type="primary", width="stretch", on_click=ir_a_ingreso, key="ini2")
    b2.button("Iniciar sesión", width="stretch", on_click=ir_a_ingreso, key="ini1")
    st.caption("Citas de entrevistas de investigación (7–9 de noviembre de 2026), con nombres cambiados; no son reseñas de clientes.")
    refs = REFERENCIAS.replace("<div class='refs'><b>Referencias</b>", "<div class='landing'><details><summary>Fuentes</summary>").replace("</ol></div>", "</ol></details></div>")
    st.markdown(refs, unsafe_allow_html=True)


if "rol" not in st.session_state and st.session_state.get("pantalla") != "ingreso":
    portada()
    st.markdown("<div class='pie'>TanIA demo · 🔒 Tus prompts no se guardan; las instituciones solo ven datos agregados.</div>",
                unsafe_allow_html=True)
    st.stop()

if "rol" not in st.session_state:
    _, centro, _ = st.columns([1, 1.6, 1])
    with centro, st.container(key="ingreso"):
        st.markdown("<div class='logo'>TanIA</div>"
                    "<p class='lema-ingreso'>Haz más con IA, sin dejar de aprender.</p>",
                    unsafe_allow_html=True)
        rol = st.radio("¿Cómo quieres entrar?", ["Soy estudiante o profesional", "Soy una institución"],
                       label_visibility="collapsed")
        st.text_input("Correo", placeholder="tu@correo.com")
        if st.button("Entrar", type="primary", width="stretch"):
            st.session_state["rol"] = rol
            st.rerun()
        st.caption("Versión demo: no necesitas cuenta ni contraseña y verás datos de ejemplo. "
                   "En la versión final, cada persona solo ve su propio diagnóstico.")
        if st.button("← Volver", key="volver"):
            st.session_state["pantalla"] = "portada"
            st.rerun()
    st.stop()

if st.sidebar.button("Cerrar sesión"):
    del st.session_state["rol"]
    st.session_state["pantalla"] = "portada"
    st.rerun()

st.markdown(f"""<div class='hero'><div class='hero-fila'><div class='hero-texto'><h1>TanIA</h1>
<p class='lema'>Haz más con IA, sin dejar de aprender.</p>
<span class='pastilla'>🔎 Diagnóstico</span><span class='pastilla'>🌙 Cognición</span>
<span class='pastilla'>🧋 Recomendaciones</span><span class='pastilla'>🔒 Tus prompts no se guardan</span>
</div>{gif_html()}</div>
<p class='hero-desc'>Leemos tus prompts de programación y te mostramos cómo estás usando la IA: qué habilidades
dejas de practicar, qué procesos de pensamiento te saltas y cómo pedir ayuda sin dejar de aprender.</p>
</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Vista institucional: otra audiencia (universidades), siempre agregada
# ---------------------------------------------------------------------------
def escala_naranja(v, vmin, vmax):
    """Escala secuencial de un solo tono: más intenso = más bajo aprendizaje."""
    t = 0 if vmax == vmin else (v - vmin) / (vmax - vmin)
    a, b = (250, 208, 184), (184, 68, 26)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def lienzo(fig, alto=320, oscuro=False):
    tinta = "#ffffff" if oscuro else TINTA2
    fig.update_layout(height=alto, margin=dict(l=10, r=30, t=10, b=30), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(color=tinta),
                      legend=dict(orientation="h", y=1.14, font=dict(color=tinta)),
                      xaxis=dict(showgrid=False, tickfont=dict(color=tinta)),
                      yaxis=dict(gridcolor="#2c3e66" if oscuro else "#e1e0d9", zeroline=False, tickfont=dict(color=tinta)))
    return fig


SIN_BARRA = {"displayModeBar": False}


def vista_institucional():
    inst = leer("institucional.json")
    if not inst or not inst.get("curso"):
        st.info("Ejemplo en preparación con datos abiertos de estudiantes (StudyChat).")
        return
    c, grupos = inst["curso"], inst["grupos"]
    st.markdown("<span class='etiqueta'>Vista institucional</span>", unsafe_allow_html=True)
    st.subheader("Cómo aprende tu curso con IA")
    st.selectbox("Curso", ["Introducción a la programación · semestre de ejemplo (StudyChat)"],
                 label_visibility="collapsed")
    st.markdown(f"""<div class='kpis' style='grid-template-columns: repeat(4, 1fr)'>
<div class='kpi'><div class='num'>{c['n_personas']}</div><div class='lbl'>estudiantes · {c['n_prompts']} prompts de programación</div></div>
<div class='kpi alerta'><div class='num'>{c['pct_bajo']:.0f} %</div><div class='lbl'>en modos de bajo aprendizaje</div></div>
<div class='kpi alerta'><div class='num'>{c['postura_pct'].get('contratista', 0):.0f} %</div><div class='lbl'>le dan órdenes a la IA (contratistas)</div></div>
<div class='kpi'><div class='num'>{c['esfuerzo_previo_pct']:.0f} %</div><div class='lbl'>muestran un intento propio</div></div>
</div>""", unsafe_allow_html=True)

    peor = max(grupos, key=lambda g: g["pct_bajo"])
    app = c["aprendizaje_por_postura_pct"]
    uso, cognicion, reforzar = st.tabs(["🔎 Uso", "🌙 Cognición", "🧋 Qué reforzar"])

    with uso, st.container(key="tania"):
        st.markdown("<span class='etiqueta'>🔎 Cómo usa tu curso la IA</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='frase'>En tu curso, <b>{c['pct_bajo']:.0f} %</b> de los prompts de programación "
                    f"están en modos de bajo aprendizaje. La diferencia la hace la postura: cuando preguntan como "
                    f"<b style='color:#2a78d6'>consultores</b>, el {app['consultor']['alto']:.0f} % de sus prompts es de alto "
                    f"aprendizaje; cuando dan órdenes como <b>contratistas</b>, el {app['contratista']['bajo']:.0f} % es de bajo "
                    "aprendizaje (Sankaranarayanan, 2026) <sup>3</sup>.</div>", unsafe_allow_html=True)

        st.subheader("A lo largo del semestre")
        x = [g["grupo"] for g in grupos]
        fig = go.Figure()
        fig.add_scatter(x=x, y=[g["pct_bajo"] for g in grupos], name="Bajo aprendizaje", mode="lines+markers",
                        line=dict(color=BAJO, width=2, shape="spline"), marker=dict(size=9, line=dict(color="#fff6ee", width=2)),
                        hovertemplate="%{x}: %{y:.0f} %<extra>Bajo aprendizaje</extra>")
        fig.add_scatter(x=x, y=[g["pct_contratista"] for g in grupos], name="Postura contratista", mode="lines+markers",
                        line=dict(color="#6b6964", width=2, dash="dot", shape="spline"), marker=dict(size=8),
                        hovertemplate="%{x}: %{y:.0f} %<extra>Contratista</extra>")
        fig.update_yaxes(title="% de prompts", range=[0, 100])
        st.plotly_chart(lienzo(fig), width="stretch", config=SIN_BARRA)
        st.caption("Cada punto es una tarea del curso, en el orden en que se entregaron.")

        st.subheader("¿En qué tarea se apoyan más en la IA?")
        vals = [g["pct_bajo"] for g in grupos]
        orden = sorted(grupos, key=lambda g: g["pct_bajo"])
        fig = go.Figure(go.Bar(
            x=[g["pct_bajo"] for g in orden], y=[g["grupo"] for g in orden], orientation="h",
            marker_color=[escala_naranja(g["pct_bajo"], min(vals), max(vals)) for g in orden],
            text=[f"{g['pct_bajo']:.0f} %" + ("  ← la más crítica" if g is peor else "") for g in orden],
            textposition="outside", cliponaxis=False,
            customdata=[[g["n_personas"], bonito(g["habilidad_top"])] for g in orden],
            hovertemplate="%{y}: %{x:.0f} %<br>%{customdata[0]} estudiantes<br>Menos practicada: %{customdata[1]}<extra></extra>"))
        fig.update_xaxes(title="% de prompts con bajo aprendizaje", range=[0, 100], showgrid=True, gridcolor="#e1e0d9")
        fig.update_layout(bargap=0.45)
        st.plotly_chart(lienzo(fig, 290), width="stretch", config=SIN_BARRA)

        st.subheader("¿Cómo le piden las cosas a la IA?")
        st.plotly_chart(barras(c["modo_pct"], lambda k: BAJO if k in BAJOS else ALTO, "% de los prompts del curso"),
                        width="stretch", config=SIN_BARRA)
        st.markdown(f"<span style='color:{BAJO}'>■</span> bajo aprendizaje &nbsp;&nbsp; "
                    f"<span style='color:{ALTO}'>■</span> alto aprendizaje", unsafe_allow_html=True)

    with cognicion, st.container(key="ketty"):
        st.markdown("<span class='etiqueta'>🌙 Ketty · lo que el curso deja de practicar</span>", unsafe_allow_html=True)
        hab_top = max(c["habilidad_pct"], key=c["habilidad_pct"].get)
        proc_top = max(c["proceso_pct"], key=c["proceso_pct"].get)
        st.markdown(f"<div class='ketty-caja'>La habilidad que más delegan es <b>{bonito(hab_top).lower()}</b> "
                    f"({c['habilidad_pct'][hab_top]:.0f} %), y el proceso que más se saltan es <b>{bonito(proc_top).lower()}</b> "
                    f"({c['proceso_pct'][proc_top]:.0f} %): piden la solución antes de decidir cómo abordar el problema.</div>",
                    unsafe_allow_html=True)
        st.subheader("Habilidades que dejan de practicar")
        st.plotly_chart(barras(c["habilidad_pct"], CELESTE, "% de los prompts", oscuro=True), width="stretch", config=SIN_BARRA)
        st.subheader("Procesos de pensamiento que se saltan")
        st.plotly_chart(barras(c["proceso_pct"], CELESTE, "% de los prompts", oscuro=True), width="stretch", config=SIN_BARRA)

    with reforzar, st.container(key="sandra"):
        st.markdown("<span class='etiqueta'>📓✏️ Sandra · qué reforzar en clase</span><span class='boba'>🧋</span>",
                    unsafe_allow_html=True)
        recs = [
            (f"Antes de la {peor['grupo']}", f"Es la tarea con más bajo aprendizaje ({peor['pct_bajo']:.0f} %). Dedica 15 minutos "
             "a leer un traceback en voz alta con el curso antes de que la entreguen."),
            ("Planificar antes de pedir", f"El {c['proceso_pct'].get('planificar', 0):.0f} % se salta la planificación. Pide un "
             "plan de tres pasos escrito a mano antes de abrir la IA."),
            ("Enseñar a preguntar", f"Preguntar como consultor multiplica el aprendizaje ({app['consultor']['alto']:.0f} % frente a "
             f"{app['contratista']['alto']:.0f} %). Muestra en clase cómo reformular una orden en una pregunta."),
        ]
        for titulo, texto in recs:
            st.markdown(f"<div class='tarjeta'><b>{titulo}</b><br>{texto}</div>", unsafe_allow_html=True)

        st.subheader("Lo que verías con TanIA en uso")
        st.markdown("<span class='etiqueta'>Datos simulados · ilustración de funciones futuras</span>", unsafe_allow_html=True)
        sem = ["Semana 1", "Semana 4", "Semana 8"]
        fig = go.Figure()
        fig.add_bar(x=sem, y=[64, 55, 46], name="Bajo aprendizaje (simulado)",
                    marker=dict(color="#f4c6d6", line=dict(color="#b04a74", width=1.5), pattern=dict(shape="/", fgcolor="#b04a74")))
        fig.add_bar(x=sem, y=[71, 63, 58], name="Confianza autodeclarada en la mini prueba (simulado)",
                    marker=dict(color="#ffffff", line=dict(color="#898781", width=1.5), pattern=dict(shape="\\", fgcolor="#898781")))
        fig.add_scatter(x=sem, y=[48, 55, 61], name="Nota real en la mini prueba sin IA (simulado)", mode="lines+markers",
                        line=dict(color="#1f1d1a", width=2, dash="dash"), marker=dict(size=8))
        fig.update_yaxes(title="%", range=[0, 100])
        fig.update_layout(barmode="group", bargap=0.35)
        st.plotly_chart(lienzo(fig, 340), width="stretch", config=SIN_BARRA)
        st.caption("Simulado: así se vería el curso si usa los planes de repaso y la mini prueba sin IA. Al inicio creen saber "
                   "más de lo que saben (Kruger y Dunning, 1999); la brecha entre confianza y nota se cierra con práctica.")

    st.markdown(f"""<div class='tarjeta' style='margin-top:1.4rem'><b>🔒 Privacidad desde el diseño</b><br>
Solo se muestran grupos de 8 personas o más, sin rankings ni datos individuales, y los prompts con contenido sensible
se excluyen antes del análisis. {inst.get('fuente', '')}</div>""", unsafe_allow_html=True)


PIE = ("<div class='pie'>🔒 Privacidad absoluta: tus prompts no se guardan ni se comparten. "
       "Las instituciones solo ven datos agregados.</div>")

if st.session_state["rol"] == "Soy una institución":
    vista_institucional()
    st.markdown(PIE, unsafe_allow_html=True)
    st.stop()

resumen = leer("resumen.json")

# ---------------------------------------------------------------------------
# 4. Vista individual
# ---------------------------------------------------------------------------
if not resumen:
    st.info("Todavía no hay resultados. Corre `backend/clasificador.py` para generarlos.")
    st.stop()

pct_bajo = sum(v for k, v in resumen["modo_pct"].items() if k in BAJOS)
st.markdown(f"""<div class='kpis'>
<div class='kpi'><div class='num'>{resumen['n_prompts']}</div><div class='lbl'>prompts de programación analizados</div></div>
<div class='kpi alerta'><div class='num'>{pct_bajo:.0f} %</div><div class='lbl'>en modos de bajo aprendizaje</div></div>
<div class='kpi'><div class='num'>{resumen['esfuerzo_previo_pct']:.0f} %</div><div class='lbl'>muestran un intento propio</div></div>
</div>""", unsafe_allow_html=True)

uso, cognicion, recomendaciones = st.tabs(["🔎 Uso", "🌙 Cognición", "🧋 Recomendaciones"])

# --- Uso (TanIA): cómo le pides las cosas a la IA ---
with uso, st.container(key="tania"):
    st.markdown("<span class='etiqueta'>🔎 TanIA · tu forma de usar la IA</span>", unsafe_allow_html=True)
    modo_top = max(resumen["modo_pct"], key=resumen["modo_pct"].get)
    frase = (f"Tu modo más frecuente es <b>{bonito(modo_top).lower()}</b> "
             f"({resumen['modo_pct'][modo_top]:.0f} % de tus prompts).")
    post = resumen.get("postura_pct", {})
    if post.get("contratista"):
        frase += (f" Le hablas a la IA como <b>contratista</b> en el {post['contratista']:.0f} % de los casos: "
                  "das órdenes más que preguntas.")
    st.markdown(f"<div class='frase'>{frase}</div>", unsafe_allow_html=True)
    st.subheader("¿Cómo le pides las cosas a la IA?")
    st.plotly_chart(barras(resumen["modo_pct"], lambda k: BAJO if k in BAJOS else ALTO),
                    width="stretch", config={"displayModeBar": False})
    st.markdown(f"<span style='color:{BAJO}'>■</span> bajo aprendizaje &nbsp;&nbsp; "
                f"<span style='color:{ALTO}'>■</span> alto aprendizaje", unsafe_allow_html=True)
    st.markdown("<div class='frase'>Estos seis modos vienen de un experimento de Anthropic: quienes usaban los "
                "<b>modos naranjas</b> sacaron entre 24 y 39 % en la prueba posterior; quienes usaban los "
                "<b style='color:#2a78d6'>azules</b>, entre 65 y 86 %. La diferencia no está en cuánto usas la IA, sino en cómo "
                "(Shen y Tamkin, 2026) <sup>1</sup>.</div>", unsafe_allow_html=True)

    st.subheader("¿Cambia según qué tan conocida es la tarea?")
    fam = resumen.get("aprendizaje_por_familiaridad_pct", {})
    orden = [f for f in ["conocida", "en_aprendizaje", "nueva"] if f in fam]
    fig = go.Figure()
    for nivel, color in [("bajo", BAJO), ("alto", ALTO)]:
        fig.add_bar(name=f"{nivel.capitalize()} aprendizaje", x=[f.replace("_", " ") for f in orden],
                    y=[fam[f].get(nivel, 0) for f in orden], marker_color=color,
                    hovertemplate="%{x}: %{y:.1f} %<extra></extra>")
    fig.update_layout(barmode="group", height=320, margin=dict(l=10, r=10, t=10, b=30),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      yaxis=dict(title="% de prompts", gridcolor="#e1e0d9"), bargap=0.35,
                      legend=dict(orientation="h", y=1.12), font=dict(color=TINTA2))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.markdown("<div class='frase'>Delegar cuando la tarea es <b>nueva</b> es lo que más cuesta: en el mismo "
                "experimento, aprender una librería desconocida con IA dejó un <b>17 % menos</b> de aprendizaje, "
                "y la mayor brecha estuvo en depurar (Shen y Tamkin, 2026). Y como el desempeño sube igual, "
                "casi nadie lo nota (Bastani et al., 2025) <sup>2</sup>.</div>", unsafe_allow_html=True)

    if resumen.get("postura_pct"):
        st.subheader("¿Consultas o encargas?")
        st.plotly_chart(barras(resumen["postura_pct"], lambda k: ALTO if k == "consultor" else BAJO),
                        width="stretch", config={"displayModeBar": False})
        st.markdown("<div class='frase'>Quienes tratan a la IA como <b>consultora</b> (\"¿por qué usaste esto?\") "
                    "pueden mantener su código sin ella; quienes la tratan como <b>contratista</b> (\"haz que el "
                    "botón sea azul\"), en su mayoría no. Sin andamiaje, el 77 % no pudo arreglar su propio código "
                    "sin IA; con una pausa para explicarlo, el 39 % (Sankaranarayanan, 2026) <sup>3</sup>.</div>",
                    unsafe_allow_html=True)

    st.markdown(REFERENCIAS, unsafe_allow_html=True)
    with st.expander("Entender mejor"):
        st.markdown("**Modos por proyecto** (% de prompts de cada proyecto)")
        por_proy = resumen.get("modo_por_proyecto_pct", {})
        if por_proy:
            import pandas as pd
            tabla = pd.DataFrame(por_proy).fillna(0).round(0).astype(int)
            tabla.index = [bonito(i) for i in tabla.index]
            tabla.columns = [bonito(c) for c in tabla.columns]
            st.dataframe(tabla, width="stretch")

        st.markdown("**Qué significa cada modo**")
        for k, d in DEFINICIONES.items():
            st.markdown(f"- **{bonito(k)}** ({'bajo' if k in BAJOS else 'alto'} aprendizaje): {d}")
        st.caption("Tipología de Shen y Tamkin (2026): en su experimento, los tres modos de bajo aprendizaje "
                   "obtuvieron 24-39 % en la prueba posterior y los de alto aprendizaje, 65-86 %.")

# --- Cognición (Ketty): procesos de pensamiento que te saltas ---
with cognicion, st.container(key="ketty"):
    st.markdown("<span class='etiqueta'>Ketty · capa cognitiva</span>", unsafe_allow_html=True)
    st.markdown("<div class='ketty-caja'><b>Desempeño no es aprendizaje.</b> Lo que logras con IA es tu "
                "desempeño; lo que puedes hacer sin ella es tu aprendizaje (Bjork y Bjork, 2011). "
                "Con IA, el desempeño sube aunque el aprendizaje baje, y casi nadie lo nota "
                "(Bastani et al., 2025; Kruger y Dunning, 1999).</div>", unsafe_allow_html=True)
    st.subheader("Habilidades técnicas que estás dejando de practicar")
    hab = {k: v for k, v in resumen["habilidad_no_ejercitada_pct"].items() if k != "ninguna"}
    st.plotly_chart(barras(hab, CELESTE, oscuro=True), width="stretch", config={"displayModeBar": False})

    st.subheader("Procesos de pensamiento que te saltas")
    proc = {k: v for k, v in resumen["proceso_omitido_pct"].items() if k != "ninguno"}
    st.plotly_chart(barras(proc, CELESTE, oscuro=True), width="stretch", config={"displayModeBar": False})
    st.caption("Metacognición: planificar antes de hacer, monitorear qué falla y evaluar "
               "si la respuesta tiene sentido. Es lo que la IA hace por ti cuando delegas.")

    with st.expander("Entender mejor"):
        st.markdown("**¿Eres una experta frágil?** Sankaranarayanan (2026) llama así a quien produce código "
                    "que funciona pero no puede mantenerlo sin IA: la deuda epistémica. En su experimento, "
                    "el 77 % de quienes usaron IA sin restricciones no pudo arreglar su propio código sin ella; "
                    "con una pausa para explicar el código, el 39 %.")
        st.markdown("**Ilusión de competencia.** Prather et al. (2024) observaron que quienes tenían dificultades "
                    "creían que les había ido mejor de lo que les fue. Dos dificultades nuevas con IA: "
                    "*progression* (ir atrasada sin notarlo) y *mislead* (la herramienta te lleva por mal camino).")
        st.markdown("**Ponte a prueba** en la pestaña Recomendaciones: la mini prueba sin IA mide tu brecha.")

# --- Recomendaciones (Sandra): cómo pedir mejor ---
with recomendaciones, st.container(key="sandra"):
    st.markdown("<span class='etiqueta'>📓✏️ Sandra · recomendaciones</span><span class='boba'>🧋</span>", unsafe_allow_html=True)
    st.subheader("Mejores prompts")
    ejemplos = leer("ejemplos.json") or []
    if not ejemplos:
        st.caption("Aún no hay ejemplos seleccionados.")
    for e in ejemplos:
        st.markdown(
            f"<div class='tarjeta'><div class='etiqueta'>{bonito(e.get('modo', ''))}</div>"
            f"<p class='antes'>{e['antes']}</p><p><b>Mejor:</b> {e['despues']}</p>"
            + (f"<p><b>Ejercicio:</b> {e['ejercicio']}</p>" if e.get("ejercicio") else "")
            + "</div>", unsafe_allow_html=True)

    izq, der = st.columns(2)
    with izq:
        st.subheader("Plan de repaso")
        st.markdown("- **Hoy:** el ejercicio de tu modo más frecuente, sin IA.\n"
                    "- **En 3 días:** repítelo con un dato distinto.\n"
                    "- **En 7 días:** explícaselo a alguien (o a ti misma, en voz alta).")
    with der:
        st.subheader("Referencias para consultar")
        st.markdown(
            "- [R for Data Science, cap. *Workflow: getting help*](https://r4ds.hadley.nz/workflow-help.html)\n"
            "- [Python: errores y excepciones (tutorial oficial)](https://docs.python.org/es/3/tutorial/errors.html)\n"
            "- [pandas: guía de usuario](https://pandas.pydata.org/docs/user_guide/index.html)")

    st.subheader("Explícalo con tus palabras")
    st.caption("Antes de aceptar código de la IA, escribe en 2 líneas qué hace y por qué. "
               "Es la \"puerta de explicación\" que redujo los fallos de 77 % a 39 % (Sankaranarayanan, 2026).")

    st.subheader("Mini prueba sin IA")
    st.caption("Tres preguntas sobre el código de esta misma app, hecho con ayuda de IA. "
               "Primero estima cuánto vas a acertar; al final comparamos.")
    PREGUNTAS = [
        ("df['prompt_anterior'] = df.groupby('conversacion_id')['texto'].shift(1).fillna('')",
         "¿Qué queda en `prompt_anterior` para el primer prompt de cada conversación?",
         ["El último prompt de la conversación anterior", "Un texto vacío", "El mismo prompt", "Un error"], 1),
        ("pendientes = df[~df['prompt_id'].isin(hechos)]",
         "¿Qué prompts quedan en `pendientes`?",
         ["Los que ya se clasificaron", "Todos", "Los que todavía no se clasificaron", "Ninguno"], 2),
        ("for intento in (1, 2):\n    try:\n        c = clasificar(cliente, fila)\n        break\n"
         "    except Exception as e:\n        error = str(e)\nif c is None:\n    continue",
         "Si los dos intentos fallan, ¿qué pasa con ese prompt?",
         ["Se detiene todo el programa", "Se guarda vacío", "Se reintenta sin fin", "Se salta y no se guarda"], 3),
    ]
    with st.form("prueba"):
        estimacion = st.slider("¿Cuántas crees que vas a acertar?", 0, 3, 2)
        respuestas = []
        for i, (codigo, pregunta, opciones, _) in enumerate(PREGUNTAS):
            st.code(codigo, language="python")
            respuestas.append(st.radio(pregunta, opciones, index=None, key=f"p{i}"))
        enviar = st.form_submit_button("Ver resultado")
    if enviar:
        aciertos = sum(r == p[2][p[3]] for r, p in zip(respuestas, PREGUNTAS))
        st.metric("Aciertos sin IA", f"{aciertos} de 3", delta=f"{aciertos - estimacion:+d} frente a tu estimación")
        if aciertos < estimacion:
            st.warning("Te sobreestimaste: es la brecha entre desempeño y aprendizaje. Repasa este código sin IA.")
        elif aciertos > estimacion:
            st.success("Sabías más de lo que creías.")
        else:
            st.success("Te calibraste bien.")

    st.subheader("Prueba con un prompt tuyo")
    prompt = st.text_area("Pega un prompt que le harías a la IA", height=110,
                          placeholder="Ej.: no funciona, arréglalo + el error")
    st.session_state.setdefault("usos", 0)
    if st.button("Analizar con TanIA", disabled=not prompt.strip()):
        if st.session_state["usos"] >= 5:
            st.warning("Llegaste al límite de 5 análisis en esta sesión.")
        else:
            try:
                clave = st.secrets.get("ANTHROPIC_API_KEY")   # en Streamlit Cloud
            except Exception:                                  # en local no hay secrets.toml
                clave = None
            clave = clave or os.getenv("ANTHROPIC_API_KEY")
            if not clave:
                st.error("Falta configurar la clave de la API.")
            else:
                os.environ["ANTHROPIC_API_KEY"] = clave
                import anthropic
                import pandas as pd
                from clasificador import BAJO_APRENDIZAJE, clasificar
                with st.spinner("Leyendo tu prompt..."):
                    c = clasificar(anthropic.Anthropic(), pd.Series({"texto": prompt, "prompt_anterior": ""}))
                st.session_state["usos"] += 1
                nivel = "bajo" if c.modo in BAJO_APRENDIZAJE else "alto"
                st.markdown(f"**Modo:** {bonito(c.modo)} ({nivel} aprendizaje)")
                if c.habilidad_no_ejercitada != "ninguna":
                    st.markdown(f"**Habilidad que no practicas:** {bonito(c.habilidad_no_ejercitada)}")
                if c.proceso_cognitivo_omitido != "ninguno":
                    st.markdown(f"**Proceso que te saltas:** {bonito(c.proceso_cognitivo_omitido)}")
                if c.reformulacion:
                    st.success(f"**Prueba así:** {c.reformulacion}")
                if c.ejercicio:
                    st.info(f"**Ejercicio:** {c.ejercicio}")
    st.caption("Tu prompt se analiza en el momento y no se guarda.")

st.markdown(PIE, unsafe_allow_html=True)
