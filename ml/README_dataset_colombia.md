# Dataset de noticias políticas colombianas — Semana 2 (Fabián)

## Hallazgo clave de la investigación

Existe un proyecto real y documentado que ya resolvió este mismo problema:
**[POLUX89/NLP-Fake-News-Colombia](https://github.com/POLUX89/NLP-Fake-News-Colombia)**
(licencia MIT para el código). Construye un corpus a partir de los chequeos de
**ColombiaCheck**, y sus decisiones metodológicas nos ahorran errores
comunes. Vale la pena adoptar (no copiar el texto, sí el enfoque) su
arquitectura de adquisición.

## Decisiones metodológicas que deberíamos replicar

1. **Fuente de datos: ClaimReview (JSON-LD schema.org), no scraping de texto
   completo.** Cada chequeo de ColombiaCheck publica metadatos estructurados
   `ClaimReview` en su HTML. Esto es información pública pensada para ser
   leída por máquinas (así la leen los buscadores) — mucho más estable y
   éticamente más claro que raspar el artículo completo.
2. **El input del modelo debe ser la afirmación (`claim_reviewed`), no el
   titular del artículo.** El titular del chequeo casi siempre revela el
   veredicto (ej. "No, esta imagen no muestra..."), lo que causa **fuga de
   etiqueta** (data leakage): el modelo "haría trampa" aprendiendo del
   titular en vez del contenido. Es exactamente el riesgo que el cronograma
   ya señala como criterio de aceptación de la Semana 3 ("Revisar
   significado de features y fuga de etiqueta").
3. **La etiqueta debe venir de `reviewRating` (dato estructurado), no de un
   parseo heurístico del texto de la tarjeta del listado.** Un heurístico de
   "primera coincidencia de palabra" es frágil (falla, por ejemplo, si el
   titular contiene la palabra "verdadero" dentro de una negación).
4. **Desbalance de clases severo es de esperar.** En el proyecto de
   referencia: ~76% Falso, ~20% Cuestionable, ~3% Verdadero. Esto no es un
   error de recolección — así es la distribución real de lo que se verifica
   (rara vez se verifica algo que ya se sabe que es cierto). Hay que:
   - Usar **macro-F1** como métrica principal (no solo Accuracy).
   - Aplicar **class weighting** durante el entrenamiento.
   - Documentar la limitación explícitamente (no prometer que el modelo
     detecta "verdad", sino que aprende patrones asociados a cómo un
     verificador específico clasificó cada caso).
5. **Split 70/15/15 congelado con semilla fija**, tal como pide el criterio
   de aceptación de la Semana 3 ("Test congelado, etiquetas consistentes").
6. **No redistribuir el texto de los chequeos.** El proyecto de referencia
   mantiene `data/` fuera del repositorio (git-ignored) porque el texto es
   propiedad de ColombiaCheck; solo se usan los metadatos estructurados
   públicos. Deberíamos seguir la misma política y, si en algún momento se
   necesita texto completo para features más ricos, contactar primero a la
   organización (así lo indica su propio repositorio).

## Qué NO deberíamos hacer

- ❌ Raspar el HTML completo de artículos de El Tiempo/Semana/etc. para
  construir el dataset de entrenamiento sin permiso — distinto es leer
  *una sola* página en vivo cuando el usuario la está consultando con la
  extensión (eso es un uso transitorio y personal, no una base de datos
  redistribuida).
- ❌ Usar el titular del chequeo como texto de entrada del modelo.
- ❌ Reportar solo Accuracy con un dataset tan desbalanceado — es engañoso
  (un modelo que dijera "Falso" siempre tendría ~76% de accuracy sin haber
  aprendido nada).

## Próximo paso concreto para Fabián (Semana 2)

1. Adaptar (no copiar literalmente) el patrón de
   [`acquisition.py`](https://github.com/POLUX89/NLP-Fake-News-Colombia/blob/main/src/fake_news_co/acquisition.py)
   del proyecto de referencia: recorrer `/chequeos` de ColombiaCheck
   respetando `robots.txt`, identificarse con un User-Agent propio, cachear
   localmente y aplicar throttle (≥1.5s entre requests).
2. Extraer únicamente el bloque `ClaimReview` (JSON-LD) de cada chequeo:
   `claimReviewed`, `reviewRating`, `datePublished`, `url`.
3. Construir `data/processed/dataset.csv` con columnas:
   `claim_text, label, date, source_url`.
4. Aplicar el split 70/15/15 con semilla fija y guardarlo congelado
   (ej. `data/processed/split_seed42.json`) para que nadie lo regenere por
   accidente con otra semilla.
5. Documentar el desbalance de clases en el EDA (notebook) antes de entrenar
   nada, como pide el criterio de aceptación.

## Referencia de pesos de fuentes (para cuando el dataset se combine con el
Evidence Engine en el Sprint 3)

Ver [`backend_config/fuentes_colombia.yaml`](../backend_config/fuentes_colombia.yaml)
para la lista de verificadores colombianos vigentes con sus pesos
sugeridos (ColombiaCheck, Detector de Mentiras de La Silla Vacía, AFP
Factual, etc.), verificada en septiembre de 2026.
