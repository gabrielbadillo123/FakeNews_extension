# Proyecto FakeNews — Verificador de noticias políticas colombianas

Extensión de Chrome + backend + modelo ML para apoyar la verificación de
afirmaciones en noticias políticas colombianas. Cronograma de 12 semanas /
6 sprints — ver el cronograma detallado compartido por la directora.

## Estructura

```
.
├── extension/          # Extensión Manifest V3 (Gabriel)
├── backend/             # API FastAPI (Fabián, Semana 5+)
├── ml/                  # Pipeline de datos y modelo (Fabián)
└── backend_config/       # Configuración compartida (pesos de fuentes, etc.)
```

## Estado actual — corte Semana 3 / Sprint 2

| Semana | Tarea | Responsable | Estado | Rama |
|---|---|---|---|---|
| 1 | Bootstrap extensión MV3 (manifest, service worker, content script, side panel) | Gabriel | ✅ Completo | `feature/extension-bootstrap` |
| 1 | Bootstrap backend/ML, requirements, limpieza inicial | Fabián | ✅ Completo | `feature/ml-bootstrap` |
| 2 | Content extractor robusto (JSON-LD, Open Graph, heurística, fallback de selección) | Gabriel | ✅ Completo | `feature/extension-bootstrap` |
| 2 | Balance de clases + split congelado 70/15/15 | Fabián | ✅ Completo | `feature/dataset-pipeline` |
| 3 | Feature Extractor (estilo, entidades, cifras, estructura, legibilidad, subjetividad) | Fabián | ✅ Completo | `feature/feature-extractor` |
| 3 | Contrato JSON + mock API | Gabriel | ✅ Completo | `feature/api-client-mock` |
| 6 | Config de fuentes de fact-checking (adelanto) | — | 🟡 Solo configuración, falta el motor | `feature/evidence-engine` |
| 4+ | Entrenamiento RF, backend real, integración, QA, deploy | — | ❌ No iniciado | — |

### Detalle de lo construido

**Extensión (`extension/`)**
- Manifest V3 funcional: manifest, service worker, content script, side panel.
- Extracción de titular/cuerpo en cascada: JSON-LD schema.org → Open Graph →
  heurística de `<article>` → fallback de texto seleccionado manualmente.
- Botón de verificación conectado a un mock de API que respeta el contrato
  real (`CONTRATO_API.md`), con estados de éxito, "insuficiente" y error.
- Probada manualmente en El Tiempo y El Espectador.

**ML (`ml/`)**
- Pipeline de limpieza (`clean.py`) y split congelado con semilla fija
  (`split.py`), validados con una muestra sintética de 15 filas (ver
  limitación de red más abajo).
- Script de adquisición real vía ClaimReview de ColombiaCheck
  (`acquisition_colombiacheck.py`), listo pero **no ejecutado** contra datos
  reales todavía.
- Feature Extractor (`feature_extractor.py`): 21 features en 6 categorías,
  con 9/9 tests automatizados y verificación explícita de que no hay fuga
  de etiqueta. Catálogo completo en `FEATURE_CATALOG.md`.

**Config compartida (`backend_config/`)**
- Pesos de fuentes de fact-checking colombianas para el futuro Evidence
  Engine (`fuentes_colombia.yaml`) — la configuración existe, el módulo que
  la consume (`evidence_engine.py`) todavía no se ha construido.

### Limitación de entorno, documentada honestamente

El entorno donde se desarrolló este código no tiene acceso a internet
general (solo a un puñado de dominios técnicos: GitHub, PyPI, npm). Por
eso:
- El dataset se probó con una **muestra sintética** de 15 filas, no con los
  ~2900 chequeos reales de ColombiaCheck.
- El modelo de spaCy en español sí se pudo instalar (se descarga desde un
  release de GitHub, que sí está permitido).

Antes de entrenar el modelo real (Semana 4), alguien del equipo con acceso
a internet normal debe correr `ml/acquisition_colombiacheck.py` para
obtener el dataset real.

## Cómo correr cada parte

Ver el `README.md` dentro de cada carpeta (`extension/`, `ml/`), y:
- `ml/README_dataset_colombia.md` — metodología del dataset real
- `ml/README_pipeline_semana1_2.md` — evidencia de ejecución Semana 1-2
- `ml/FEATURE_CATALOG.md` — catálogo y justificación de cada feature
- `extension/CONTRATO_API.md` — contrato JSON entre extensión y backend

## Ramas

Cada semana/tarea del cronograma corresponde a una rama `feature/...`,
consistente con la columna "Rama / artefacto" del cronograma oficial:

- `main` — integración de todo el código
- `feature/extension-bootstrap` — Semana 1-2, Gabriel (extensión completa)
- `feature/ml-bootstrap` — Semana 1, Fabián
- `feature/dataset-pipeline` — Semana 2, Fabián
- `feature/feature-extractor` — Semana 3, Fabián
- `feature/api-client-mock` — Semana 3, Gabriel
- `feature/evidence-engine` — adelanto de configuración, Semana 6

## Próximos pasos (Semana 4)

- Entrenar baselines y Random Forest sobre las features extraídas; medir
  Accuracy, Precision, Recall, F1 y matriz de confusión.
- Completar el side panel: estados de loading/error más pulidos y origen
  del contenido.
