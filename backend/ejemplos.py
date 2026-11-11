"""
Ejemplos para la pestaña Recomendaciones: TÚ eliges cuáles se muestran.

Paso 1:  uv run python backend/ejemplos.py --candidatos
         -> crea data/processed/ejemplos_candidatos.csv (privado, no se sube)
Paso 2:  ábrelo en Excel, pon 1 en la columna "usar" en 5 o 6 filas.
         Puedes editar "antes" para parafrasear o quitar datos sensibles.
Paso 3:  uv run python backend/ejemplos.py --publicar
         -> crea data/agg/ejemplos.json (este sí se sube y lo lee el dashboard)
"""

import argparse
import json
from pathlib import Path

import pandas as pd

CLASIFICADOS = Path("data/processed/clasificados.jsonl")
CANDIDATOS = Path("data/processed/ejemplos_candidatos.csv")
PUBLICO = Path("data/agg/ejemplos.json")


def candidatos():
    df = pd.DataFrame([json.loads(l) for l in CLASIFICADOS.read_text(encoding="utf-8").splitlines() if l.strip()])
    df = df[(df["es_programacion"]) & (df["reformulacion"].str.len() > 0) & (df["texto"].str.len() < 400)]
    df = df.groupby("modo", group_keys=False).apply(lambda d: d.head(8))   # hasta 8 por modo
    out = df[["prompt_id", "proyecto", "modo", "texto", "reformulacion", "ejercicio"]].rename(
        columns={"texto": "antes", "reformulacion": "despues"})
    out.insert(0, "usar", 0)
    out.to_csv(CANDIDATOS, index=False, encoding="utf-8-sig")
    print(f"{len(out)} candidatos en {CANDIDATOS}")


def publicar():
    df = pd.read_csv(CANDIDATOS, encoding="utf-8-sig")
    elegidos = df[df["usar"] == 1][["modo", "antes", "despues", "ejercicio"]].fillna("")
    PUBLICO.parent.mkdir(parents=True, exist_ok=True)
    PUBLICO.write_text(json.dumps(elegidos.to_dict(orient="records"), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(elegidos)} ejemplos publicados en {PUBLICO}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--candidatos", action="store_true")
    p.add_argument("--publicar", action="store_true")
    a = p.parse_args()
    candidatos() if a.candidatos else publicar()
