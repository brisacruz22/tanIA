"""
Ingesta de TanIA: lee los historiales de prompts, se queda con los de programación
y los deja en una tabla ordenada (una fila por prompt).

No usa IA. Es limpieza y preparación de datos, como cargar una base antes de modelar.
"""

import json
import re
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")

# ---------------------------------------------------------------------------
# 1. Familiaridad por proyecto
# Lo decides tú, no la IA: qué tan conocida era la tarea en cada proyecto.
# ---------------------------------------------------------------------------
FAMILIARIDAD = {
    "brisa_tesis": "conocida",          # R y estadística: tu terreno
    "brisa_tesis_2": "conocida",
    "Diplomatura": "en_aprendizaje",    # Python nuevo
    "SIEP-NLP universidad": "nueva",    # NLP: territorio nuevo
}

# ---------------------------------------------------------------------------
# 2. Señales de que un prompt es de programación (reglas simples y baratas)
# ---------------------------------------------------------------------------
PATRONES_CODIGO = [
    r"```", r"Error in", r"Error:", r"Traceback", r"Warning", r"\bError\b",
    r"<-", r"library\(", r"import \w+", r"def \w+\(", r"\w+\(\w*=",
    r"\bsvyglm\b", r"\bggplot\b", r"\bdplyr\b", r"\bpandas\b", r"\bdata\.frame\b",
    r"\bR\b", r"\bpython\b", r"\bscript\b", r"\bc[óo]digo\b", r"\bfunci[óo]n\b",
    r"\bregresi[óo]n\b", r"\bvariable", r"\bdataframe\b", r"\bpip\b", r"\buv\b",
    r"\bgit\b", r"\bstreamlit\b", r"\bmcp\b",
]
RE_CODIGO = re.compile("|".join(PATRONES_CODIGO), re.IGNORECASE)
RE_ERROR = re.compile(r"Error in|Error:|Traceback|Exception|Warning message", re.IGNORECASE)
RE_BLOQUE = re.compile(r"```|<-|library\(|import \w+|def \w+\(")

# ---------------------------------------------------------------------------
# 3. Privacidad: enmascarar lo que no debe salir de tu laptop
# ---------------------------------------------------------------------------
RE_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
RE_CLAVE = re.compile(r"(sk-[A-Za-z0-9_-]{10,}|hf_[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{10,})")
RE_RUTA = re.compile(r"[A-Z]:\\Users\\[^\s\"']+", re.IGNORECASE)


def enmascarar(texto: str) -> str:
    texto = RE_CLAVE.sub("[CLAVE]", texto)
    texto = RE_CORREO.sub("[CORREO]", texto)
    texto = RE_RUTA.sub("[RUTA]", texto)
    return texto


# ---------------------------------------------------------------------------
# 4. Carga de fuentes
# ---------------------------------------------------------------------------
def cargar_json(nombre: str) -> pd.DataFrame:
    ruta = RAW / nombre
    if not ruta.exists():
        print(f"(no encontré {ruta}, la salto)")
        return pd.DataFrame()
    return pd.DataFrame(json.loads(ruta.read_text(encoding="utf-8")))


def cargar_todo() -> pd.DataFrame:
    df = pd.concat(
        [cargar_json("chatgpt_tesis.json"), cargar_json("claude_diplo_nlp.json")],
        ignore_index=True,
    )
    df["texto"] = df["texto"].astype(str).map(enmascarar)
    df["familiaridad"] = df["proyecto"].map(FAMILIARIDAD).fillna("sin_dato")
    return df


# ---------------------------------------------------------------------------
# 5. Variables baratas y filtro de programación
# ---------------------------------------------------------------------------
def preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["conversacion_id", "turno"]).copy()
    df["tiene_error"] = df["texto"].str.contains(RE_ERROR)
    df["tiene_codigo"] = df["texto"].str.contains(RE_BLOQUE)
    df["largo"] = df["texto"].str.len()
    df["es_programacion_regla"] = df["texto"].str.contains(RE_CODIGO)

    # Contexto: el prompt anterior de la misma conversación (para ver dependencia progresiva)
    df["prompt_anterior"] = df.groupby("conversacion_id")["texto"].shift(1).fillna("")

    df["prompt_id"] = df["fuente"].str[:2] + "-" + df["conversacion_id"].str[:8] + "-" + df["turno"].astype(str)
    return df


def prompts_de_programacion() -> pd.DataFrame:
    df = preparar(cargar_todo())
    prog = df[df["es_programacion_regla"]].copy()
    print(f"Prompts totales: {len(df)} | de programación (regla): {len(prog)}")
    print(prog.groupby(["proyecto", "familiaridad"]).size().to_string())
    return prog


if __name__ == "__main__":
    prompts_de_programacion()
