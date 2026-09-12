"""
feature_extractor.py — Semana 3 (Fabián), rama feature/feature-extractor

Convierte una afirmación de texto en un vector de features numéricas para
alimentar el modelo (Random Forest, Semana 4). Categorías pedidas por el
cronograma: estilo, entidades, cifras, estructura, legibilidad y subjetividad.

Criterio de aceptación: "Misma entrada produce mismo vector; pruebas pasan."
→ Por diseño, todas las funciones aquí son puras (mismo input → mismo
  output), sin aleatoriedad ni estado compartido entre llamadas.

Nota sobre fuga de etiqueta (data leakage) — pedido explícito de revisión
por la directora: ninguna feature de este módulo usa el veredicto/label
como insumo. Todas se calculan ÚNICAMENTE a partir de `claim_text`. Ver
FEATURE_CATALOG.md para la justificación de cada feature individual.

Uso:
    from feature_extractor import extract_features
    vector = extract_features("Un candidato afirmó que redujo el desempleo en un 40%.")
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass

import spacy

_NLP = None  # carga perezosa (lazy) del modelo de spaCy, es costoso de inicializar


def _get_nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("es_core_news_sm")
    return _NLP


# --- Léxico de subjetividad (heurístico, Semana 3) ---------------------------
# Lista corta y explícita a propósito: es un punto de partida heurístico, no
# un lexicón validado lingüísticamente. Se documenta como limitación conocida
# en FEATURE_CATALOG.md — ampliarlo es trabajo de Sprint futuro si el modelo
# lo justifica.
_PALABRAS_SUBJETIVAS = {
    "escandaloso", "terrible", "maravilloso", "increíble", "vergonzoso",
    "urgente", "grave", "alarmante", "peligroso", "corrupto", "mentiroso",
    "traidor", "héroe", "desastre", "catástrofe", "genial", "pésimo",
    "lamentable", "indignante", "sospechoso",
}

_VOCALES = set("aeiouáéíóúü")


@dataclass
class FeatureVector:
    # --- Estilo ---
    n_caracteres: int
    n_palabras: int
    longitud_promedio_palabra: float
    ratio_mayusculas: float
    n_signos_exclamacion: int
    n_signos_interrogacion: int
    n_comillas: int

    # --- Entidades (spaCy es_core_news_sm) ---
    n_entidades_persona: int
    n_entidades_lugar: int
    n_entidades_organizacion: int
    n_entidades_total: int

    # --- Cifras ---
    n_numeros: int
    n_porcentajes: int
    n_fechas_mencionadas: int
    contiene_cifra_grande: bool  # ej. millones, miles de millones

    # --- Estructura ---
    n_oraciones: int
    longitud_promedio_oracion: float
    n_conectores_logicos: int  # "porque", "sin embargo", "además", etc.

    # --- Legibilidad ---
    promedio_silabas_por_palabra: float
    indice_legibilidad_fernandez_huerta: float  # adaptación española del Flesch

    # --- Subjetividad ---
    n_palabras_subjetivas: int
    ratio_palabras_subjetivas: float


def _contar_silabas_es(palabra: str) -> int:
    """Aproximación simple de conteo silábico en español: cuenta grupos de vocales."""
    palabra = unicodedata.normalize("NFC", palabra.lower())
    silabas = 0
    prev_vocal = False
    for ch in palabra:
        es_vocal = ch in _VOCALES
        if es_vocal and not prev_vocal:
            silabas += 1
        prev_vocal = es_vocal
    return max(silabas, 1)


def _features_estilo(text: str) -> dict:
    palabras = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    n_palabras = len(palabras) or 1  # evita división por cero
    letras = [c for c in text if c.isalpha()]
    mayusculas = [c for c in letras if c.isupper()]
    return {
        "n_caracteres": len(text),
        "n_palabras": len(palabras),
        "longitud_promedio_palabra": sum(len(p) for p in palabras) / n_palabras,
        "ratio_mayusculas": (len(mayusculas) / len(letras)) if letras else 0.0,
        "n_signos_exclamacion": text.count("!") + text.count("¡"),
        "n_signos_interrogacion": text.count("?") + text.count("¿"),
        "n_comillas": text.count('"') + text.count("'") + text.count("«"),
    }


def _features_entidades(text: str) -> dict:
    doc = _get_nlp()(text)
    labels = [ent.label_ for ent in doc.ents]
    return {
        "n_entidades_persona": labels.count("PER"),
        "n_entidades_lugar": labels.count("LOC"),
        "n_entidades_organizacion": labels.count("ORG"),
        "n_entidades_total": len(labels),
    }


_PATRON_PORCENTAJE = re.compile(r"\d+(?:[.,]\d+)?\s*%")
_PATRON_NUMERO = re.compile(r"\d+(?:[.,]\d+)?")
_PATRON_FECHA = re.compile(
    r"\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    r"septiembre|octubre|noviembre|diciembre)\b|\b\d{4}\b",
    flags=re.IGNORECASE,
)
_PATRON_CIFRA_GRANDE = re.compile(
    r"\b(mill[oó]n(?:es)?|billones?|miles\s+de\s+millones)\b", flags=re.IGNORECASE
)


def _features_cifras(text: str) -> dict:
    return {
        "n_numeros": len(_PATRON_NUMERO.findall(text)),
        "n_porcentajes": len(_PATRON_PORCENTAJE.findall(text)),
        "n_fechas_mencionadas": len(_PATRON_FECHA.findall(text)),
        "contiene_cifra_grande": bool(_PATRON_CIFRA_GRANDE.search(text)),
    }


_CONECTORES = {
    "porque", "sin embargo", "además", "por lo tanto", "aunque",
    "no obstante", "en consecuencia", "debido a", "ya que", "mientras que",
}


def _features_estructura(text: str) -> dict:
    oraciones = [o for o in re.split(r"[.!?]+", text) if o.strip()]
    n_oraciones = len(oraciones) or 1
    palabras_totales = len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))
    text_lower = text.lower()
    n_conectores = sum(1 for c in _CONECTORES if c in text_lower)
    return {
        "n_oraciones": len(oraciones),
        "longitud_promedio_oracion": palabras_totales / n_oraciones,
        "n_conectores_logicos": n_conectores,
    }


def _features_legibilidad(text: str) -> dict:
    palabras = re.findall(r"\b\w+\b", text, flags=re.UNICODE)
    n_palabras = len(palabras) or 1
    n_oraciones = len([o for o in re.split(r"[.!?]+", text) if o.strip()]) or 1
    silabas_totales = sum(_contar_silabas_es(p) for p in palabras)
    promedio_silabas = silabas_totales / n_palabras

    # Fórmula de Fernández Huerta (adaptación española del índice Flesch):
    # 206.84 - 0.60*P - 1.02*F
    # P = sílabas por cada 100 palabras, F = palabras por oración
    p = (silabas_totales / n_palabras) * 100
    f = n_palabras / n_oraciones
    indice = 206.84 - (0.60 * p) - (1.02 * f)

    return {
        "promedio_silabas_por_palabra": promedio_silabas,
        "indice_legibilidad_fernandez_huerta": indice,
    }


def _features_subjetividad(text: str) -> dict:
    palabras = re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)
    n_palabras = len(palabras) or 1
    n_subjetivas = sum(1 for p in palabras if p in _PALABRAS_SUBJETIVAS)
    return {
        "n_palabras_subjetivas": n_subjetivas,
        "ratio_palabras_subjetivas": n_subjetivas / n_palabras,
    }


def extract_features(claim_text: str) -> FeatureVector:
    """
    Función principal: recibe el texto de una afirmación y devuelve su
    vector de features. Determinista: la misma entrada SIEMPRE produce
    el mismo vector (no hay aleatoriedad ni estado externo).
    """
    if not isinstance(claim_text, str):
        raise TypeError(f"claim_text debe ser str, se recibió {type(claim_text)}")

    text = claim_text.strip()
    if not text:
        raise ValueError("claim_text no puede estar vacío.")

    values = {}
    values.update(_features_estilo(text))
    values.update(_features_entidades(text))
    values.update(_features_cifras(text))
    values.update(_features_estructura(text))
    values.update(_features_legibilidad(text))
    values.update(_features_subjetividad(text))

    return FeatureVector(**values)


def extract_features_dict(claim_text: str) -> dict:
    """Igual que extract_features pero devuelve un dict plano (útil para pandas)."""
    return asdict(extract_features(claim_text))


if __name__ == "__main__":
    ejemplo = "¡Escandaloso! Un candidato afirmó que redujo el desempleo en un 40% durante 2023, según cifras oficiales."
    vector = extract_features(ejemplo)
    print(f"Texto: {ejemplo}\n")
    for campo, valor in asdict(vector).items():
        print(f"  {campo}: {valor}")
