# Pipeline ML — Semana 1 y 2 (Fabián)

## Semana 1 — Bootstrap (`feature/ml-bootstrap`)

**Criterio de aceptación:** "Instala dependencias y procesa muestra sin errores."

### Qué se construyó
- `/backend` — estructura mínima con FastAPI (placeholder; el backend real
  con endpoints `/health` y `/api/v1/verify` se construye en la Semana 5).
- `/ml` — estructura para el pipeline de datos y modelado.
- `ml/requirements.txt` — pandas, scikit-learn, pyyaml, requests,
  beautifulsoup4, jupyter.
- `ml/clean.py` — script de limpieza inicial.
- `ml/data/raw/sample_claims.csv` — **muestra sintética** (15 filas) para
  probar el pipeline sin depender de acceso a internet. Incluye a propósito
  una fila vacía y una fila duplicada, para verificar que la limpieza las
  detecta.

### Evidencia de ejecución (para pantallazo de tesis)

```
$ pip install pandas scikit-learn pyyaml --break-system-packages
$ python3 clean.py

Cargando: data/raw/sample_claims.csv
=== Reporte de limpieza ===
  filas_originales: 15
  descartadas_texto_vacio: 1
  descartadas_label_invalida: 0
  labels_invalidas_encontradas: []
  descartadas_duplicadas: 1
  fechas_no_parseables: 0
  filas_finales: 13

Guardado: data/processed/claims_clean.csv (13 filas)
```

**Por qué esto cumple el criterio:** instaló las dependencias sin error y
procesó la muestra de punta a punta sin fallar, detectando correctamente
los 2 problemas de calidad de datos sembrados a propósito en la muestra
(fila vacía, fila duplicada).

## Semana 2 — Limpieza avanzada, balance y split (`feature/dataset-pipeline`)

**Criterio de aceptación:** "Test congelado, etiquetas consistentes y sin
fuga evidente."

### Qué se construyó
- `ml/split.py` — calcula el balance de clases y genera un split
  estratificado 70/15/15 con **semilla fija (42)**, guardado como
  `data/processed/split_seed42.json` (solo índices, no duplica los datos).
- El script **se niega a sobreescribir** un split ya generado — si intentas
  correrlo de nuevo, avisa que el split está congelado y hay que borrarlo
  a mano y justificarlo en el PR. Esto es justamente lo que exige el
  criterio de "test congelado".

### Hallazgo real durante las pruebas (bueno para la sección de resultados
de la tesis)

Con la muestra sintética de solo 13 filas, el split falló al intentar
estratificar `val`/`test` porque las clases minoritarias (`Cuestionable`,
`Verdadero`) no tenían ni 2 ejemplos para dividir:

```
ValueError: The least populated classes in y have only 1 member...
```

Esto **no es un bug** — es el desbalance de clases real que ya anticipamos
en `ml/README_dataset_colombia.md` a partir del proyecto de referencia
(76% Falso / 20% Cuestionable / 3% Verdadero). Se resolvió con un
*fallback* explícito: si no se puede estratificar, se usa split aleatorio
simple para ese paso y se imprime una advertencia — el script nunca falla
en silencio. Con el dataset real (~2900 filas) este fallback no debería
activarse porque hay suficientes ejemplos por clase.

Esto es un buen ejemplo para tu tesis de **por qué las pruebas con muestra
pequeña importan**: revelan casos límite (edge cases) que un dataset grande
esconde.

### Evidencia de ejecución (para pantallazo de tesis)

```
$ python3 split.py

=== Balance de clases (antes del split) ===
              n     %
label
Falso         6  46.2
Cuestionable  4  30.8
Verdadero     3  23.1

[aviso] No se pudo estratificar val/test (muestra muy pequeña)...
        Se usa split aleatorio simple para este paso...

=== Split congelado (seed=42) ===
  train: 9 filas
  val:   2 filas
  test:  2 filas

Guardado: data/processed/split_seed42.json
```

## Qué falta para que esto sea el dataset REAL (no la muestra sintética)

1. Correr `ml/acquisition_colombiacheck.py` desde una máquina con acceso
   normal a internet (este entorno de desarrollo tiene la red restringida
   a unos pocos dominios técnicos, por eso se probó con muestra sintética).
2. Apuntar `clean.py --input data/raw/dataset_colombiacheck.csv` al
   resultado real.
3. Volver a correr `split.py` — con ~2900 filas reales, el desbalance sigue
   existiendo pero ya no debería fallar la estratificación de val/test.
4. A partir de ahí, `split_seed42.json` queda **congelado de verdad** para
   todo el proyecto — todos los experimentos de modelado (Semana 4 en
   adelante) deben usar ese mismo split para que los resultados sean
   comparables entre sí.
