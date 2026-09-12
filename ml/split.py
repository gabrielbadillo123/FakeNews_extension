"""
split.py — Semana 2 (Fabián), rama feature/dataset-pipeline

Toma el dataset limpio (data/processed/claims_clean.csv), reporta el
balance de clases, y genera un split estratificado 70/15/15 con semilla
FIJA (congelada) para que nadie lo regenere por accidente con otra
semilla y rompa la comparabilidad de resultados entre experimentos.

Uso:
    python split.py
    python split.py --input data/processed/claims_clean.csv --seed 42
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

DEFAULT_INPUT = Path(__file__).parent / "data" / "processed" / "claims_clean.csv"
DEFAULT_SPLIT_OUTPUT = Path(__file__).parent / "data" / "processed" / "split_seed42.json"
DEFAULT_SEED = 42


def class_balance_report(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["label"].value_counts()
    pct = (counts / len(df) * 100).round(1)
    return pd.DataFrame({"n": counts, "%": pct})


def stratified_split(df: pd.DataFrame, seed: int) -> dict[str, list[int]]:
    """
    Split 70/15/15 estratificado por label, con semilla fija.
    Devuelve un diccionario de índices (no los datos en sí) para poder
    congelar el split sin duplicar el dataset en disco.

    Si alguna clase tiene muy pocos ejemplos para estratificar en 3 partes
    (típico en muestras pequeñas de prueba, NO esperado en el dataset real
    de ~2900 afirmaciones), cae a split sin estratificar en el segundo paso
    y lo advierte explícitamente — nunca falla en silencio.
    """
    idx = df.index.to_numpy()
    labels = df["label"].to_numpy()

    idx_train, idx_temp, y_train, y_temp = train_test_split(
        idx, labels, test_size=0.30, stratify=labels, random_state=seed
    )

    try:
        idx_val, idx_test, _, _ = train_test_split(
            idx_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=seed
        )
    except ValueError as err:
        print(
            f"[aviso] No se pudo estratificar val/test (muestra muy pequeña: {err})."
            " Se usa split aleatorio simple para este paso — con el dataset real"
            " (~2900 filas) esto no debería ocurrir."
        )
        idx_val, idx_test = train_test_split(idx_temp, test_size=0.50, random_state=seed)

    return {
        "seed": seed,
        "train": sorted(idx_train.tolist()),
        "val": sorted(idx_val.tolist()),
        "test": sorted(idx_test.tolist()),
    }


def main():
    parser = argparse.ArgumentParser(description="Balance de clases + split congelado 70/15/15.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_SPLIT_OUTPUT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    if args.output.exists():
        print(f"[aviso] {args.output} ya existe — el split está CONGELADO y no se regenera.")
        print("        Si de verdad necesitas cambiarlo, bórralo manualmente primero")
        print("        y documenta por qué en el PR (esto invalida comparaciones previas).")
        return

    df = pd.read_csv(args.input)
    if len(df) == 0:
        raise ValueError("El dataset de entrada está vacío.")

    print(f"Cargado: {args.input} ({len(df)} filas)\n")

    print("=== Balance de clases (antes del split) ===")
    print(class_balance_report(df).to_string())

    # Aviso de desbalance severo, como reporta el proyecto de referencia
    # (POLUX89/NLP-Fake-News-Colombia) sobre datasets de ColombiaCheck.
    min_class_pct = (df["label"].value_counts() / len(df) * 100).min()
    if min_class_pct < 10:
        print(
            f"\n[aviso] Desbalance severo detectado (clase minoritaria = {min_class_pct:.1f}%)."
            " Usar macro-F1 como métrica principal y class_weight al entrenar,"
            " no solo Accuracy."
        )

    split = stratified_split(df, seed=args.seed)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(split, indent=2), encoding="utf-8")

    print(f"\n=== Split congelado (seed={args.seed}) ===")
    print(f"  train: {len(split['train'])} filas")
    print(f"  val:   {len(split['val'])} filas")
    print(f"  test:  {len(split['test'])} filas")
    print(f"\nGuardado: {args.output}")
    print("Este archivo es el TEST CONGELADO — no se debe volver a generar con otra semilla.")


if __name__ == "__main__":
    main()
