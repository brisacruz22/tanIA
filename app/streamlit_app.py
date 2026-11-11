"""
Dashboard de TanIA.

Lee solo datos agregados (data/agg/*.json): ningún texto de prompts reales vive en el repo.
Tres pestañas, como en el boceto: Uso (TanIA), Cognición (Ketty) y Recomendaciones (Sandra),
más una vista docente agregada y anónima.

Correr en local:  uv run streamlit run app/streamlit_app.py
"""

import json
import os
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
AGG = RAIZ / "data" / "agg"
sys.path.insert(0, str(RAIZ / "backend"))

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
.hero { background: linear-gradient(120deg, #fff4e8 0%, #fde3cf 55%, #f9d5c2 100%);
        border-radius: 22px; padding: 2rem 2.2rem 1.6rem; margin-bottom: 1.2rem; border: 1px solid #f3d9c4; }
.hero h1 { font-size: 3.4rem !important; margin: 0 0 .2rem 0; padding: 0; }
.hero .lema { font-size: 1.25rem; font-weight: 600; color: #1f1d1a; margin: 0 0 .5rem 0; }
.hero .desc { color: #52514e; margin: 0 0 .9rem 0; max-width: 46rem; }
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
.st-key-ingreso { background: linear-gradient(160deg, #fff4e8 0%, #fde3cf 60%, #f9d5c2 100%);
        border: 1px solid #f3d9c4; border-radius: 24px; padding: 2.4rem 2.2rem 1.6rem; margin-top: 3rem; }
.logo { font-family: Georgia, serif; font-size: 3.6rem; font-weight: 700; text-align: center; color: #1f1d1a; }
.lema-ingreso { text-align: center; font-weight: 600; margin-bottom: 1.4rem; }
.pie { text-align: center; color: #52514e; font-size: .85rem; margin-top: 2rem; }
.stButton button { background: #1f1d1a; color: #fbf6ec; border-radius: 6px 18px 6px 6px; }
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
        hovertemplate="%{y}: %{x:.1f} %<extra></extra>",
    ))
    fig.update_layout(
        height=60 + 42 * len(pares), margin=dict(l=10, r=40, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff" if oscuro else TINTA2), bargap=0.45,
        xaxis=dict(title=titulo_x, gridcolor="#2c3e66" if oscuro else "#e1e0d9", zeroline=False),
        yaxis=dict(showgrid=False),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Encabezado
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 2. Ingreso (demo: sin contraseña, con datos de ejemplo)
# ---------------------------------------------------------------------------
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
    st.stop()

if st.sidebar.button("Cerrar sesión"):
    del st.session_state["rol"]
    st.rerun()

st.markdown("""<div class='hero'><h1>TanIA</h1>
<p class='lema'>Haz más con IA, sin dejar de aprender.</p>
<p class='desc'>Leemos tus prompts de programación y te mostramos cómo estás usando la IA: qué habilidades
dejas de practicar, qué procesos de pensamiento te saltas y cómo pedir ayuda sin dejar de aprender.</p>
<span class='pastilla'>🔎 Diagnóstico</span><span class='pastilla'>🌙 Cognición</span>
<span class='pastilla'>🧋 Recomendaciones</span><span class='pastilla'>🔒 Tus prompts no se guardan</span>
</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Vista institucional: otra audiencia (universidades), siempre agregada
# ---------------------------------------------------------------------------
def vista_institucional():
    st.markdown("<span class='etiqueta'>Vista institucional</span>", unsafe_allow_html=True)
    st.subheader("Cómo aprende tu curso con IA")
    st.markdown("Para universidades y diplomaturas: qué modos de uso predominan en cada curso y qué habilidad "
                "practican menos sus estudiantes, para decidir **qué reforzar en clase**.")
    st.caption("Privacidad desde el diseño: solo agregados de 8 personas o más, sin rankings ni datos individuales, "
               "y los prompts con contenido sensible se excluyen antes del análisis.")
    inst = leer("institucional.json")
    if not inst or not inst.get("grupos"):
        st.info("Ejemplo en preparación con datos abiertos de estudiantes (StudyChat).")
    else:
        grupos = inst["grupos"]
        st.plotly_chart(barras({g["grupo"]: g["pct_bajo"] for g in grupos}, BAJO,
                               "% de prompts con bajo aprendizaje"), width="stretch")
        for g in grupos:
            st.markdown(f"**{g['grupo']}** · {g['n_personas']} estudiantes · {g['n_prompts']} prompts · "
                        f"habilidad menos practicada: {bonito(g['habilidad_top'])}")
        if inst.get("ocultos"):
            st.caption(f"{inst['ocultos']} grupo(s) ocultos por tener menos de 8 personas.")
        st.caption(inst.get("fuente", ""))


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
                    width="stretch")
    st.markdown(f"<span style='color:{BAJO}'>■</span> bajo aprendizaje &nbsp;&nbsp; "
                f"<span style='color:{ALTO}'>■</span> alto aprendizaje", unsafe_allow_html=True)

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
    st.plotly_chart(fig, width="stretch")

    if resumen.get("postura_pct"):
        st.subheader("¿Consultas o encargas?")
        st.plotly_chart(barras(resumen["postura_pct"], lambda k: ALTO if k == "consultor" else BAJO),
                        width="stretch")
        st.caption("Sankaranarayanan (2026): quienes trataban a la IA como consultora (preguntando por qué) "
                   "pudieron mantener su código sin IA; quienes la trataban como contratista (dando órdenes), "
                   "en su mayoría no.")

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
    st.plotly_chart(barras(hab, CELESTE, oscuro=True), width="stretch")

    st.subheader("Procesos de pensamiento que te saltas")
    proc = {k: v for k, v in resumen["proceso_omitido_pct"].items() if k != "ninguno"}
    st.plotly_chart(barras(proc, CELESTE, oscuro=True), width="stretch")
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
