"""
tests/test_feature_extractor.py — Semana 3 (Fabián)

Verifica el criterio de aceptación: "Misma entrada produce mismo vector;
pruebas pasan."

Uso:
    pip install pytest --break-system-packages
    pytest tests/test_feature_extractor.py -v
"""

import sys
from dataclasses import asdict
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from feature_extractor import extract_features, extract_features_dict  # noqa: E402


CLAIM_EJEMPLO = (
    "¡Escandaloso! Un candidato afirmó que redujo el desempleo en un 40% "
    "durante 2023, según cifras oficiales del DANE."
)


def test_determinismo_misma_entrada_mismo_vector():
    """Criterio de aceptación explícito: correr 2 veces debe dar el mismo resultado."""
    v1 = extract_features_dict(CLAIM_EJEMPLO)
    v2 = extract_features_dict(CLAIM_EJEMPLO)
    assert v1 == v2


def test_devuelve_todas_las_categorias_de_features():
    v = extract_features_dict(CLAIM_EJEMPLO)
    categorias_esperadas = {
        # estilo
        "n_caracteres", "n_palabras", "longitud_promedio_palabra",
        "ratio_mayusculas", "n_signos_exclamacion", "n_signos_interrogacion",
        "n_comillas",
        # entidades
        "n_entidades_persona", "n_entidades_lugar",
        "n_entidades_organizacion", "n_entidades_total",
        # cifras
        "n_numeros", "n_porcentajes", "n_fechas_mencionadas",
        "contiene_cifra_grande",
        # estructura
        "n_oraciones", "longitud_promedio_oracion", "n_conectores_logicos",
        # legibilidad
        "promedio_silabas_por_palabra", "indice_legibilidad_fernandez_huerta",
        # subjetividad
        "n_palabras_subjetivas", "ratio_palabras_subjetivas",
    }
    assert categorias_esperadas.issubset(set(v.keys()))


def test_detecta_porcentaje():
    v = extract_features_dict("Se redujo el desempleo en un 40%.")
    assert v["n_porcentajes"] == 1
    assert v["n_numeros"] >= 1


def test_detecta_entidad_persona():
    v = extract_features_dict("Gustavo Petro dijo que la reforma avanza.")
    assert v["n_entidades_persona"] >= 1


def test_detecta_palabra_subjetiva():
    v = extract_features_dict("Esto es un escándalo terrible y alarmante.")
    assert v["n_palabras_subjetivas"] >= 2


def test_texto_vacio_lanza_error():
    with pytest.raises(ValueError):
        extract_features("")
    with pytest.raises(ValueError):
        extract_features("   ")


def test_tipo_invalido_lanza_error():
    with pytest.raises(TypeError):
        extract_features(12345)  # type: ignore


def test_texto_sin_signos_no_falla():
    """Caso límite: texto sin puntuación no debe romper el conteo de oraciones."""
    v = extract_features_dict("un texto sin ningun signo de puntuacion")
    assert v["n_oraciones"] >= 1
    assert v["longitud_promedio_oracion"] > 0


def test_no_usa_el_label_como_input():
    """
    Verificación explícita anti-fuga de etiqueta: la firma de la función
    solo acepta el texto de la afirmación, nunca un label/veredicto.
    """
    import inspect
    firma = inspect.signature(extract_features)
    assert list(firma.parameters.keys()) == ["claim_text"]
