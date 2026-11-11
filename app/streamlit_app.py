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
VIOLETA = "#6250d6"                  # color de la capa cognitiva
TINTA, TINTA2 = "#1f1d1a", "#52514e"

st.markdown("""
<style>
h1, h2, h3 { font-family: Georgia, 'Times New Roman', serif !important; font-weight: 700 !important; }
.st-key-ketty { background: #f1eefb; border-radius: 16px; padding: 1.2rem 1.4rem; }
.tarjeta { background: #fffdf8; border: 1px solid #e8e0d0; border-radius: 14px;
           padding: 1rem 1.2rem; margin-bottom: .8rem; }
.antes { color: #52514e; text-decoration: line-through; text-decoration-color: #eb6834; }
.etiqueta { font-size: .78rem; letter-spacing: .06em; text-transform: uppercase; color: #898781; }
.pie { text-align: center; color: #52514e; font-size: .85rem; margin-top: 2rem; }
.stButton button { background: #1f1d1a; color: #fbf6ec; border-radius: 6px 18px 6px 6px; }
</style>
""", unsafe_allow_html=True)

NOMBRES_MODO = {
    "delegacion_total": "Delegación total",
    "depuracion_iterativa": "Depuración iterativa",
    "dependencia_progresiva": "Dependencia progresiva",
    "generar_y_explicar": "Generar y explicar",
    "pregunta_conceptual": "Pregunta conceptual",
    "verificar_lo_propio": "Verificar lo propio",
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
    "depuracion_iterativa": "Pegas el error y pides que lo arregle, sin buscar por qué falla.",
    "dependencia_progresiva": "Empiezas preguntando y terminas pidiendo que la IA haga todo.",
    "generar_y_explicar": "Pides el código y también que te lo explique.",
    "pregunta_conceptual": "Preguntas cómo o por qué funciona algo.",
    "verificar_lo_propio": "Muestras tu intento y pides que lo revise.",
}


def bonito(clave: str) -> str:
    return NOMBRES_MODO.get(clave, clave.replace("_", " ").capitalize())


@st.cache_data
def leer(nombre: str):
    ruta = AGG / nombre
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def barras(datos: dict, color, titulo_x="% de tus prompts"):
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
        font=dict(color=TINTA2), bargap=0.45,
        xaxis=dict(title=titulo_x, gridcolor="#e1e0d9", zeroline=False),
        yaxis=dict(showgrid=False),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Encabezado
# ---------------------------------------------------------------------------
st.title("TanIA")
st.markdown("**Haz más con IA, sin dejar de aprender.**")
st.caption("TanIA lee tus prompts de programación y te muestra cómo estás usando la IA: "
           "qué habilidades dejas de practicar, qué procesos de pensamiento te saltas "
           "y cómo pedir ayuda sin dejar de aprender.")

vista = st.sidebar.radio("Vista", ["Mi diagnóstico", "Vista docente (agregada)"])
resumen = leer("resumen.json")

# ---------------------------------------------------------------------------
# 3. Vista individual: tres pestañas
# ---------------------------------------------------------------------------
if vista == "Mi diagnóstico":
    if not resumen:
        st.info("Todavía no hay resultados. Corre `backend/clasificador.py` para generarlos.")
        st.stop()

    pct_bajo = sum(v for k, v in resumen["modo_pct"].items() if k in BAJOS)
    c1, c2, c3 = st.columns(3)
    c1.metric("Prompts de programación analizados", resumen["n_prompts"])
    c2.metric("Con bajo aprendizaje", f"{pct_bajo:.0f} %")
    c3.metric("Muestran un intento propio", f"{resumen['esfuerzo_previo_pct']:.0f} %")

    uso, cognicion, recomendaciones = st.tabs(["Uso", "Cognición", "Recomendaciones"])

    # --- Uso (TanIA): cómo le pides las cosas a la IA ---
    with uso:
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
        st.caption("Delegar lo que ya dominas es un alivio sano. Lo que importa es "
                   "qué haces cuando la tarea es nueva.")

        with st.expander("¿Qué significa cada modo?"):
            for k, d in DEFINICIONES.items():
                st.markdown(f"**{bonito(k)}** ({'bajo' if k in BAJOS else 'alto'} aprendizaje): {d}")
            st.caption("Tipología basada en Shen y Tamkin (2026), Rahe et al. (2025) y Amoozadeh et al. (2024).")

    # --- Cognición (Ketty): procesos de pensamiento que te saltas ---
    with cognicion, st.container(key="ketty"):
        st.markdown("<span class='etiqueta'>Ketty · capa cognitiva</span>", unsafe_allow_html=True)
        st.subheader("Habilidades técnicas que estás dejando de practicar")
        hab = {k: v for k, v in resumen["habilidad_no_ejercitada_pct"].items() if k != "ninguna"}
        st.plotly_chart(barras(hab, VIOLETA), width="stretch")

        st.subheader("Procesos de pensamiento que te saltas")
        proc = {k: v for k, v in resumen["proceso_omitido_pct"].items() if k != "ninguno"}
        st.plotly_chart(barras(proc, VIOLETA), width="stretch")
        st.caption("Metacognición: planificar antes de hacer, monitorear qué falla y evaluar "
                   "si la respuesta tiene sentido. Es lo que la IA hace por ti cuando delegas.")

    # --- Recomendaciones (Sandra): cómo pedir mejor ---
    with recomendaciones:
        st.markdown("<span class='etiqueta'>Sandra · recomendaciones</span>", unsafe_allow_html=True)
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

        st.subheader("Prueba con un prompt tuyo")
        prompt = st.text_area("Pega un prompt que le harías a la IA", height=110,
                              placeholder="Ej.: no funciona, arréglalo + el error")
        st.session_state.setdefault("usos", 0)
        if st.button("Analizar con TanIA", disabled=not prompt.strip()):
            if st.session_state["usos"] >= 5:
                st.warning("Llegaste al límite de 5 análisis en esta sesión.")
            else:
                clave = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
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

# ---------------------------------------------------------------------------
# 4. Vista docente: siempre agregada, nunca individual
# ---------------------------------------------------------------------------
else:
    st.subheader("Vista docente")
    st.caption("Menos información, y siempre agregada: solo se muestran grupos de 8 personas o más.")
    inst = leer("institucional.json")
    if not inst:
        st.info("Todavía no hay datos institucionales. Corre `backend/studychat.py`.")
        st.stop()
    grupos = inst["grupos"]
    st.plotly_chart(barras({g["grupo"]: g["pct_bajo"] for g in grupos}, BAJO,
                           "% de prompts con bajo aprendizaje"), width="stretch")
    for g in grupos:
        st.markdown(f"**{g['grupo']}** · {g['n_personas']} personas · "
                    f"habilidad menos practicada: {bonito(g['habilidad_top'])}")
    if inst.get("ocultos"):
        st.caption(f"{inst['ocultos']} grupo(s) ocultos por tener menos de 8 personas.")
    st.caption(inst.get("fuente", ""))

st.markdown("<div class='pie'>🔒 Privacidad absoluta: tus prompts no se guardan ni se comparten. "
            "Las instituciones solo ven datos agregados.</div>", unsafe_allow_html=True)
