# Contrato de API — Verificación de afirmaciones (v1)

Rama: `feature/api-client-mock`
Evidencia a entregar (cronograma): "UI consume respuesta simulada."
Criterio de aceptación: "Muestra score/estado/error correctamente."

Este documento define el contrato JSON que la extensión y el backend real
(Semana 5, `feature/backend-api`) deben respetar. Mientras el backend no
existe, la extensión consume un **mock local** (`extension/mock_api.js`)
que respeta exactamente este mismo contrato — así, cuando el backend real
esté listo, solo hay que cambiar la URL, no la lógica de la UI.

## Endpoint

```
POST /api/v1/verify
```

## Request

```json
{
  "claim_text": "Un candidato afirmó que redujo el desempleo en un 40%",
  "url": "https://www.eltiempo.com/politica/articulo-123",
  "title": "Título de la noticia de origen"
}
```

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `claim_text` | string | Sí | Texto a verificar (extraído por content.js o seleccionado manualmente) |
| `url` | string | No | URL de origen, para trazabilidad |
| `title` | string | No | Título de la página de origen |

## Response — caso éxito

```json
{
  "status": "ok",
  "score": 0.82,
  "veredicto": "Falso",
  "confianza": "alta",
  "fuentes": [
    { "nombre": "ColombiaCheck", "url": "https://colombiacheck.com/chequeos/ejemplo", "peso": 1.0 }
  ],
  "latencia_ms": 340
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `status` | `"ok"` \| `"error"` \| `"insuficiente"` | Estado general de la respuesta |
| `score` | number (0-1) | Score de confianza del veredicto |
| `veredicto` | `"Falso"` \| `"Cuestionable"` \| `"Verdadero"` \| `null` | Veredicto (null si status es "insuficiente") |
| `confianza` | `"alta"` \| `"media"` \| `"baja"` | Nivel de confianza cualitativo |
| `fuentes` | array de `{nombre, url, peso}` | Fuentes consultadas, ver `backend_config/fuentes_colombia.yaml` |
| `latencia_ms` | number | Tiempo que tomó el backend en procesar (para monitoreo) |

## Response — caso insuficiente

Cuando ninguna fuente tiene información suficiente (ver
`configuracion_motor.fallback_si_todas_fallan` en `fuentes_colombia.yaml`):

```json
{
  "status": "insuficiente",
  "score": null,
  "veredicto": null,
  "confianza": null,
  "fuentes": [],
  "latencia_ms": 210
}
```

## Response — caso error

```json
{
  "status": "error",
  "error_code": "TIMEOUT" ,
  "error_message": "El servicio de verificación no respondió a tiempo.",
  "latencia_ms": 4000
}
```

Códigos de error esperados: `TIMEOUT`, `INVALID_INPUT`, `SERVER_ERROR`,
`RATE_LIMITED`.

## Por qué este contrato (justificación para la aprobación de la directora)

- **`status` explícito de 3 estados** (no solo true/false) porque el
  Evidence Engine (Semana 6) puede legítimamente no encontrar evidencia
  suficiente — eso es distinto de un error técnico, y la UI debe
  distinguirlos (criterio de aceptación: "score/estado/error").
- **`fuentes` como array de objetos, no solo strings** — cada fuente trae
  su propio peso (de `fuentes_colombia.yaml`), para que la UI pueda mostrar
  cuán confiable es cada una, no solo su nombre.
- **`latencia_ms` en toda respuesta** — para poder medir performance real
  en Semana 5 sin tener que instrumentar después.
