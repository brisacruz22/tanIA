"""
Vista institucional con datos abiertos: StudyChat (McNichols, Ikram y Lan, 2026), CC BY 4.0.
https://huggingface.co/datasets/wmcnicho/StudyChat

Toma una muestra de mensajes de estudiantes, los clasifica con la MISMA tipología de TanIA
y guarda solo agregados por grupo (tarea o semestre), ocultando grupos de menos de 8 personas.

Uso:
    uv run python backend/studychat.py --columnas      # primero: ver qué columnas trae
    uv run python backend/studychat.py --n 300         # clasificar una muestra
"""

import argparse
import json
import os
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

from clasificador import BAJO_APRENDIZAJE, clasificar

load_dotenv()

LOCAL = Path("data/raw/studychat.parquet")
REMOTO = "hf://datasets/wmcnicho/StudyChat/data.jsonl"
SALIDA = Path("data/processed/studychat_clasificados.jsonl")
AGREGADO = Path("data/agg/institucional.json")
MINIMO_GRUPO = 8
# Contenido sensible: se excluye antes de clasificar (salud mental, autolesión, abuso, etc.)
SENSIBLE = r"(?i)suicid|self[- ]?harm|kill myself|depress|anxiety|panic attack|abuse|assault|harass|therap|medicat|pregnan|suicid|autolesi|ansiedad|depresi|abuso|acoso"

# Nombres posibles de columnas (el script elige el primero que exista)
COL_TEXTO = ["prompt", "user_message", "student_message", "message", "content", "text", "input"]
COL_PERSONA = ["student_id", "user_id", "userId", "user_hash", "hashed_user", "user", "anon_id", "student", "chat_user"]
COL_GRUPO = ["topic", "assignment", "assignment_id", "assignment_name", "semester", "term", "course"]
COL_ROL = ["role", "sender", "author"]


def cargar() -> pd.DataFrame:
    if LOCAL.exists():
        return pd.read_parquet(LOCAL)
    token = os.getenv("HF_TOKEN")                  # el dataset es restringido: va en .env, nunca en el repo
    if not token:
        raise SystemExit("Falta HF_TOKEN en el archivo .env")
    df = pd.read_json(REMOTO, lines=True, storage_options={"token": token})
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(LOCAL)
    return df


def elegir(df, opciones):
    for c in opciones:
        if c in df.columns:
            return c
    return None


def preparar(df: pd.DataFrame) -> tuple[pd.DataFrame, str, str]:
    texto, persona, grupo, rol = (elegir(df, x) for x in (COL_TEXTO, COL_PERSONA, COL_GRUPO, COL_ROL))
    if not (texto and persona and grupo):
        raise SystemExit(f"No reconocí las columnas. Corre con --columnas y ajusta las listas. Columnas: {list(df.columns)}")
    if rol:  # quedarse solo con mensajes del estudiante
        df = df[df[rol].astype(str).str.lower().isin(["user", "human", "student"])]
    df = df[[texto, persona, grupo]].dropna().rename(columns={texto: "texto", persona: "persona", grupo: "grupo"})
    df["texto"] = df["texto"].astype(str)
    sensibles = df["texto"].str.contains(SENSIBLE, regex=True)
    print(f"Excluidos por contenido sensible: {int(sensibles.sum())}")
    df = df[~sensibles]
    return df, persona, grupo


def correr(n: int):
    df, _, _ = preparar(cargar())
    # Muestra estratificada: los 5 grupos con más estudiantes y hasta 2 mensajes por estudiante,
    # para que cada grupo supere el mínimo de 8 personas y se pueda mostrar.
    top = df.groupby("grupo")["persona"].nunique().nlargest(5).index
    base = df[df["grupo"].isin(top)].sample(frac=1, random_state=42)
    base = base.groupby(["grupo", "persona"]).head(2)
    muestra = base.groupby("grupo").head(n // len(top))   # head conserva la columna grupo
    hechos = set()
    if SALIDA.exists():
        hechos = {json.loads(l)["i"] for l in SALIDA.read_text(encoding="utf-8").splitlines() if l.strip()}
    cliente = anthropic.Anthropic()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with SALIDA.open("a", encoding="utf-8") as f:
        for i, fila in muestra.iterrows():
            if int(i) in hechos:
                continue
            try:
                c = clasificar(cliente, pd.Series({"texto": fila["texto"], "prompt_anterior": ""}))
            except Exception as e:
                print(f"  falló {i}: {str(e).splitlines()[0]}")
                continue
            f.write(json.dumps({"i": int(i), "persona": str(fila["persona"]), "grupo": str(fila["grupo"]),
                                **c.model_dump()}, ensure_ascii=False) + "\n")


def agregar():
    df = pd.DataFrame([json.loads(l) for l in SALIDA.read_text(encoding="utf-8").splitlines() if l.strip()])
    df = df[df["es_programacion"]]
    df["bajo"] = df["modo"].isin(BAJO_APRENDIZAJE)
    grupos, ocultos = [], 0
    for g, d in df.groupby("grupo"):
        if d["persona"].nunique() < MINIMO_GRUPO:      # regla de privacidad
            ocultos += 1
            continue
        hab = d.loc[d["habilidad_no_ejercitada"] != "ninguna", "habilidad_no_ejercitada"]
        nombre = f"Tarea {g[1:]}" if str(g)[:1] == "a" and str(g)[1:].isdigit() else str(g)
        grupos.append({"grupo": nombre, "n_personas": int(d["persona"].nunique()), "n_prompts": int(len(d)),
                       "pct_bajo": round(d["bajo"].mean() * 100, 1),
                       "habilidad_top": hab.mode().iat[0] if len(hab) else "ninguna"})
    AGREGADO.parent.mkdir(parents=True, exist_ok=True)
    AGREGADO.write_text(json.dumps({
        "grupos": grupos, "ocultos": ocultos,
        "fuente": "Datos: StudyChat (McNichols, Ikram y Lan, 2026), CC BY 4.0. Muestra reclasificada con la tipología de TanIA.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(grupos)} grupos visibles, {ocultos} ocultos")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--columnas", action="store_true")
    p.add_argument("--n", type=int, default=300)
    a = p.parse_args()
    if a.columnas:
        d = cargar()
        print(d.columns.tolist())
        print(d.head(3).T)
    else:
        correr(a.n)
        agregar()
