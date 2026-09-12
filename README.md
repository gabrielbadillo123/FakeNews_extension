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

## Estado actual (ver detalle en cada carpeta)

- ✅ Semana 1-2 — Extensión: bootstrap MV3 + content extractor robusto
- ✅ Semana 1-2 — ML: bootstrap + limpieza + split congelado (probado con
  muestra sintética; falta correr la adquisición real, ver
  `ml/README_dataset_colombia.md`)
- 🟡 Adelanto — config de fuentes de fact-checking para el Evidence Engine
  (`backend_config/fuentes_colombia.yaml`), que se conecta en Semana 6
- ❌ Resto de sprints — pendientes

## Cómo correr cada parte

Ver el `README.md` dentro de cada carpeta (`extension/`, `ml/`).

## Ramas

Cada semana/tarea del cronograma corresponde a una rama `feature/...`,
consistente con la columna "Rama / artefacto" del cronograma oficial.
