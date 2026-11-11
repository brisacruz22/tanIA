"""
Clasificador de TanIA: etiqueta cada prompt de programación con la tipología
(modo de uso, habilidad técnica, proceso cognitivo) y propone una reformulación.

Funciona como un clasificador zero-shot: no se entrena, se le da la tipología
en las instrucciones y se le exige una salida con un esquema fijo (Pydantic).

Uso:
    uv run python backend/clasificador.py --max 20      # prueba con 20 prompts
    uv run python backend/clasificador.py               # todos
    uv run python backend/clasificador.py --resumen     # solo recalcula los agregados
"""

import argparse
import json
from pathlib import Path
from typing import Literal

import anthropic
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from ingesta import prompts_de_programacion

load_dotenv()  # lee ANTHROPIC_API_KEY desde .env

MODELO = "claude-haiku-5-5"
SALIDA = Path("data/processed/clasificados.jsonl")   # NO se sube (tiene texto)
AGREGADOS = Path("data/agg/resumen.json")            # SÍ se sube (solo conteos)
MAX_CARACTERES = 3000                                # recorta prompts muy largos

# ---------------------------------------------------------------------------
# 1. Esquema de salida: lo que el modelo DEBE devolver por cada prompt
# ---------------------------------------------------------------------------
Modo = Literal[
    "delegacion_total", "depuracion_iterativa", "dependencia_progresiva",   # bajo aprendizaje
    "generar_y_explicar", "pregunta_conceptual", "verificar_lo_propio",     # alto aprendizaje
]
Habilidad = Literal[
    "descomponer_problema", "leer_errores_y_depurar", "disenar_codigo",
    "sintaxis_y_librerias", "interpretar_resultados", "ninguna",
]
Proceso = Literal["planificar", "monitorear", "evaluar", "recordar_y_transferir", "persistir", "ninguno"]
Contexto = Literal["enunciado_pegado", "pedido_reformulado", "pregunta_propia"]

BAJO_APRENDIZAJE = {"delegacion_total", "depuracion_iterativa", "dependencia_progresiva"}


class Clasificacion(BaseModel):
    es_programacion: bool = Field(description="True si el prompt trata de escribir, entender o arreglar código")
    modo: Modo
    habilidad_no_ejercitada: Habilidad = Field(description="Habilidad técnica que el usuario deja de practicar; 'ninguna' si el modo es de alto aprendizaje")
    proceso_cognitivo_omitido: Proceso = Field(description="Proceso metacognitivo que el prompt se salta; 'ninguno' si no se salta ninguno")
    contexto_aportado: Contexto
    esfuerzo_previo_visible: bool = Field(description="True si el prompt muestra un intento propio")
    reformulacion: str = Field(default="", description="Versión del prompt que conserva la productividad pero obliga a pensar. Vacío si el modo es de alto aprendizaje. Mismo idioma del prompt.")
    ejercicio: str = Field(default="", description="Un ejercicio corto para practicar la habilidad no ejercitada. Vacío si no aplica.")
    confianza: float | None = Field(default=None, ge=0, le=1)


# ---------------------------------------------------------------------------
# 2. Instrucciones: la tipología de la revisión de literatura
# ---------------------------------------------------------------------------
INSTRUCCIONES = """Eres un clasificador de prompts que una persona le hizo a un asistente de IA mientras programaba.
Tu tarea es identificar CÓMO está usando la IA, según una tipología basada en investigación
(Shen y Tamkin 2026; Rahe et al. 2025; Amoozadeh et al. 2024).

Modos de BAJO aprendizaje:
- delegacion_total: pide la solución completa sin intento propio ("hazme una función que...", enunciado pegado).
- depuracion_iterativa: pega un error o código y pide que lo arregle, sin intentar entender por qué falla.
- dependencia_progresiva: empezó preguntando, pero ahora pide que la IA lo haga todo (mira el prompt anterior).

Modos de ALTO aprendizaje:
- generar_y_explicar: pide código Y explicación para entenderlo.
- pregunta_conceptual: pregunta cómo o por qué funciona algo.
- verificar_lo_propio: muestra su propio intento y pide revisión.

Procesos cognitivos (metacognición): planificar (decidir pasos antes de hacer), monitorear
(darse cuenta de qué falla), evaluar (juzgar si la respuesta tiene sentido), recordar_y_transferir
(usar lo ya aprendido), persistir (sostener el esfuerzo ante la dificultad).

Reglas:
- Si el prompt no es de programación, marca es_programacion=false y clasifica lo mejor que puedas.
- La reformulación debe sonar natural, como la escribiría la persona, y pedir ayuda para pensar, no la respuesta final.
- No juzgues a la persona. Describe el patrón."""

HERRAMIENTA = {
    "name": "registrar_clasificacion",
    "description": "Registra la clasificación del prompt.",
    "input_schema": Clasificacion.model_json_schema(),
}


# ---------------------------------------------------------------------------
# 3. Llamada al modelo (una por prompt) con salida estructurada
# ---------------------------------------------------------------------------
def clasificar(cliente: anthropic.Anthropic, fila: pd.Series) -> Clasificacion:
    mensaje = (
        f"Prompt anterior en la conversación (contexto):\n{fila['prompt_anterior'][:800]}\n\n"
        f"PROMPT A CLASIFICAR:\n{fila['texto'][:MAX_CARACTERES]}"
    )
    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=1200,
        system=INSTRUCCIONES,
        tools=[HERRAMIENTA],
        tool_choice={"type": "tool", "name": "registrar_clasificacion"},
        messages=[{"role": "user", "content": mensaje}],
    )
    datos = next(b.input for b in respuesta.content if b.type == "tool_use")
    return Clasificacion.model_validate(datos)   # si no cumple el esquema, falla aquí


# ---------------------------------------------------------------------------
# 4. Bucle: clasifica, guarda línea por línea y retoma donde se quedó
# ---------------------------------------------------------------------------
def ya_clasificados() -> set:
    if not SALIDA.exists():
        return set()
    return {json.loads(l)["prompt_id"] for l in SALIDA.read_text(encoding="utf-8").splitlines() if l.strip()}


def correr(max_prompts: int | None):
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df = prompts_de_programacion()
    hechos = ya_clasificados()
    pendientes = df[~df["prompt_id"].isin(hechos)]
    if max_prompts:  # muestra aleatoria (reproducible) para que entren todos los proyectos
        pendientes = pendientes.sample(min(max_prompts, len(pendientes)), random_state=42)
    print(f"Por clasificar: {len(pendientes)} (ya hechos: {len(hechos)})")

    cliente = anthropic.Anthropic()
    with SALIDA.open("a", encoding="utf-8") as f:
        for i, (_, fila) in enumerate(pendientes.iterrows(), 1):
            c = None
            for intento in (1, 2):  # si el modelo se equivoca de formato, reintenta una vez
                try:
                    c = clasificar(cliente, fila)
                    break
                except Exception as e:
                    error = str(e).splitlines()[0]
            if c is None:
                print(f"  falló {fila['prompt_id']}: {error}")
                continue
            registro = {
                "prompt_id": fila["prompt_id"], "fuente": fila["fuente"], "proyecto": fila["proyecto"],
                "familiaridad": fila["familiaridad"], "timestamp": fila["timestamp"],
                "texto": fila["texto"], "tiene_error": bool(fila["tiene_error"]),
                **c.model_dump(),
            }
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")
            if i % 20 == 0:
                print(f"  {i}/{len(pendientes)}")


# ---------------------------------------------------------------------------
# 5. Agregados para el dashboard y el repo (sin texto de prompts)
# ---------------------------------------------------------------------------
def resumir():
    filas = [json.loads(l) for l in SALIDA.read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(filas)
    df = df[df["es_programacion"]]
    df["aprendizaje"] = df["modo"].map(lambda m: "bajo" if m in BAJO_APRENDIZAJE else "alto")

    def pct(col, por=None):
        if por is None:
            return (df[col].value_counts(normalize=True) * 100).round(1).to_dict()
        return (df.groupby(por)[col].value_counts(normalize=True) * 100).round(1).unstack(fill_value=0).to_dict(orient="index")

    resumen = {
        "n_prompts": int(len(df)),
        "modo_pct": pct("modo"),
        "aprendizaje_por_familiaridad_pct": pct("aprendizaje", "familiaridad"),
        "modo_por_proyecto_pct": pct("modo", "proyecto"),
        "habilidad_no_ejercitada_pct": pct("habilidad_no_ejercitada"),
        "proceso_omitido_pct": pct("proceso_cognitivo_omitido"),
        "esfuerzo_previo_pct": round(df["esfuerzo_previo_visible"].mean() * 100, 1),
    }
    AGREGADOS.parent.mkdir(parents=True, exist_ok=True)
    AGREGADOS.write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=None, help="clasificar solo N prompts (para probar)")
    p.add_argument("--resumen", action="store_true", help="solo recalcular agregados")
    a = p.parse_args()
    if not a.resumen:
        correr(a.max)
    resumir()
