"""
clean.py — Semana 1 (Fabián), rama feature/ml-bootstrap

Carga la muestra cruda (data/raw/sample_claims.csv) y aplica limpieza
inicial. Es intencionalmente simple: el objetivo de la Semana 1 es que el
pipeline "instale dependencias y procese una muestra sin errores", no un
pipeline de producción todavía.

IMPORTANTE: sample_claims.csv contiene datos SINTÉTICOS de prueba, no
chequeos reales de ColombiaCheck. Para el dataset real, correr primero
ml/acquisition_colombiacheck.py (requiere acceso a internet normal) y
apuntar este script a data/raw/dataset_colombiacheck.csv en su lugar.

Uso:
    python clean.py
    python clean.py --input data/raw/dataset_colombiacheck.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

VALID_LABELS = {"Falso", "Cuestionable", "Verdadero"}

DEFAULT_INPUT = Path(__file__).parent / "data" / "raw" / "sample_claims.csv"
DEFAULT_OUTPUT = Path(__file__).parent / "data" / "processed" / "claims_clean.csv"


def load_raw(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {path}")
    df = pd.read_csv(path)
    expected_cols = {"claim_text", "label", "date_published", "source_url"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas esperadas en el CSV: {missing}")
    return df


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Aplica limpieza y devuelve (df_limpio, reporte_de_pasos)."""
    report = {"filas_originales": len(df)}

    # 1. Quitar espacios en blanco sobrantes en el texto de la afirmación.
    df["claim_text"] = df["claim_text"].astype(str).str.strip()

    # 2. Descartar filas sin texto de afirmación (vacías o solo espacios).
    before = len(df)
    df = df[df["claim_text"].str.len() > 0]
    report["descartadas_texto_vacio"] = before - len(df)

    # 3. Validar que la etiqueta esté dentro del conjunto esperado.
    before = len(df)
    invalid_labels = sorted(set(df["label"].dropna()) - VALID_LABELS)
    df = df[df["label"].isin(VALID_LABELS)]
    report["descartadas_label_invalida"] = before - len(df)
    report["labels_invalidas_encontradas"] = invalid_labels

    # 4. Eliminar duplicados exactos de texto de afirmación (conserva el primero).
    before = len(df)
    df = df.drop_duplicates(subset=["claim_text"], keep="first")
    report["descartadas_duplicadas"] = before - len(df)

    # 5. Normalizar fecha a formato ISO (si falla el parseo, se deja como NaT
    #    y se reporta, no se descarta la fila por esto).
    df["date_published"] = pd.to_datetime(df["date_published"], errors="coerce")
    report["fechas_no_parseables"] = int(df["date_published"].isna().sum())

    df = df.reset_index(drop=True)
    report["filas_finales"] = len(df)
    return df, report


def print_report(report: dict) -> None:
    print("=== Reporte de limpieza ===")
    for key, value in report.items():
        print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(description="Limpieza inicial del dataset de afirmaciones.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    print(f"Cargando: {args.input}")
    df_raw = load_raw(args.input)

    df_clean, report = clean(df_raw)
    print_report(report)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(args.output, index=False)
    print(f"\nGuardado: {args.output} ({len(df_clean)} filas)")


if __name__ == "__main__":
    main()
