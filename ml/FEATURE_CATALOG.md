# Catálogo de Features — Feature Extractor (Semana 3, Fabián)

Rama: `feature/feature-extractor`
Evidencia a entregar (cronograma): "Módulo + pruebas + catálogo de features."

## Verificación anti-fuga de etiqueta (data leakage)

**Declaración explícita para revisión de la directora:** `extract_features()`
recibe **únicamente** `claim_text` (el texto de la afirmación) como
parámetro. Ninguna feature de este módulo lee, referencia o se deriva del
campo `label`/`rating`/veredicto del dataset. Esto se verifica también con
una prueba automática (`test_no_usa_el_label_como_input`) que inspecciona
la firma de la función.

Esto es importante porque, como se documentó en `README_dataset_colombia.md`,
el titular del chequeo SÍ filtra la etiqueta (dice "esto es falso"); por eso
el dataset usa `claim_reviewed` (la afirmación neutral) y no el titular. Este
módulo respeta esa misma disciplina a nivel de features.

## Catálogo por categoría

### 1. Estilo

| Feature | Qué mide | Por qué podría ayudar a distinguir Falso/Cuestionable/Verdadero |
|---|---|---|
| `n_caracteres`, `n_palabras` | Longitud del texto | Afirmaciones falsas virales tienden a ser más cortas y directas (fáciles de compartir) |
| `longitud_promedio_palabra` | Complejidad léxica | Proxy simple de formalidad del lenguaje |
| `ratio_mayusculas` | % de letras en mayúscula | Texto "GRITADO" (todo en mayúsculas) es una señal informal asociada a desinformación viral |
| `n_signos_exclamacion`, `n_signos_interrogacion` | Carga emocional/retórica | Exceso de "!" es común en titulares sensacionalistas |
| `n_comillas` | Presencia de citas textuales | Afirmaciones que citan literalmente a alguien pueden ser más verificables |

### 2. Entidades (spaCy `es_core_news_sm`)

| Feature | Qué mide |
|---|---|
| `n_entidades_persona` | Cuántas personas nombradas aparecen (PER) |
| `n_entidades_lugar` | Cuántos lugares aparecen (LOC) |
| `n_entidades_organizacion` | Cuántas organizaciones aparecen (ORG) |
| `n_entidades_total` | Total de entidades nombradas detectadas |

**Limitación conocida:** el modelo `es_core_news_sm` es el más pequeño y
rápido de spaCy en español; puede perder entidades poco frecuentes (ej.
nombres de políticos regionales menos conocidos). Si el modelo entrenado
en Sprint 4 muestra que estas features importan mucho, vale la pena
evaluar `es_core_news_md` o `es_core_news_lg` (más precisos, más lentos).

### 3. Cifras

| Feature | Qué mide |
|---|---|
| `n_numeros` | Cantidad de números mencionados |
| `n_porcentajes` | Cantidad de cifras con "%" |
| `n_fechas_mencionadas` | Fechas o años mencionados |
| `contiene_cifra_grande` | Si menciona "millones"/"miles de millones" |

Justificación: afirmaciones políticas que citan cifras específicas
("40% de desempleo", "3 millones de pesos") son un patrón común tanto en
afirmaciones verificables como en manipulaciones con números inventados o
descontextualizados — el Feature Extractor no decide cuál es cuál, solo
expone la señal para que el modelo aprenda el patrón con las etiquetas.

### 4. Estructura

| Feature | Qué mide |
|---|---|
| `n_oraciones` | Cantidad de oraciones |
| `longitud_promedio_oracion` | Palabras por oración |
| `n_conectores_logicos` | Presencia de conectores argumentativos ("porque", "sin embargo", "por lo tanto"...) |

Justificación: afirmaciones que argumentan con conectores lógicos
("X porque Y") tienen una estructura distinta a afirmaciones que solo
declaran un hecho sin justificación.

### 5. Legibilidad

| Feature | Qué mide |
|---|---|
| `promedio_silabas_por_palabra` | Complejidad silábica |
| `indice_legibilidad_fernandez_huerta` | Adaptación española del índice Flesch de legibilidad (más alto = más fácil de leer) |

**Nota metodológica:** el conteo de sílabas usa una aproximación simple
(conteo de grupos vocálicos), no un silabeador lingüístico completo — es
suficientemente preciso para un índice de legibilidad agregado, pero no
debe usarse para separación silábica ortográfica exacta.

### 6. Subjetividad

| Feature | Qué mide |
|---|---|
| `n_palabras_subjetivas` | Cuántas palabras del léxico heurístico aparecen |
| `ratio_palabras_subjetivas` | Proporción sobre el total de palabras |

**Limitación conocida y explícita:** el léxico de subjetividad
(`_PALABRAS_SUBJETIVAS` en el código) es una lista corta hecha a mano de
~20 palabras, **no** un lexicón de opinión validado lingüísticamente (como
existen para inglés, ej. MPQA). Es un punto de partida razonable para el
Sprint 2, pero debe tratarse como una feature "ruidosa" — el modelo de
Sprint 4 debería poder decirnos si aporta señal real o si conviene
reemplazarla por un lexicón más robusto (ej. ML-SentiCon en español).

## Resumen de la validación (Semana 3)

- ✅ 9/9 pruebas automatizadas pasan (`pytest tests/test_feature_extractor.py`)
- ✅ Determinismo verificado: misma entrada → mismo vector, en cada corrida
- ✅ 21 features en 6 categorías, todas derivadas solo de `claim_text`
- ✅ Sin fuga de etiqueta (verificado por inspección de firma + test automático)
- ⚠️ Léxico de subjetividad y modelo de entidades son heurísticos de punto de
  partida — señalados explícitamente para revisión futura, no para ocultar
  la limitación
