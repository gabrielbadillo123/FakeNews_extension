// content.js — Content Script (Manifest V3)
// Sprint 2 / Semana 3: extracción robusta de titular/cuerpo para medios
// políticos colombianos (El Tiempo, Semana, El Espectador, RCN, Caracol, etc.)
//
// Estrategia en cascada (de más a menos confiable). No usamos selectores CSS
// fijos por sitio (ej. ".articulo-cuerpo") porque cada medio los cambia sin
// aviso; en su lugar usamos estándares que casi todo medio digital respeta
// por SEO: JSON-LD schema.org y meta Open Graph.
//
//   1. JSON-LD schema.org NewsArticle/Article  (headline, articleBody)
//   2. Meta tags Open Graph / Twitter Card     (og:title, og:description)
//   3. Heurística de <article> / <main>        (párrafos visibles más largos)
//   4. Texto seleccionado manualmente por el usuario (fallback explícito)

function fromJsonLd() {
  const scripts = document.querySelectorAll('script[type="application/ld+json"]');
  for (const script of scripts) {
    try {
      const parsed = JSON.parse(script.textContent);
      const candidates = Array.isArray(parsed) ? parsed : [parsed, ...(parsed["@graph"] || [])];
      for (const item of candidates) {
        const type = item?.["@type"];
        const isArticle =
          type === "NewsArticle" || type === "Article" ||
          (Array.isArray(type) && (type.includes("NewsArticle") || type.includes("Article")));
        if (isArticle && (item.headline || item.articleBody)) {
          return {
            title: item.headline || null,
            body: item.articleBody || item.description || null,
            source: "json-ld",
          };
        }
      }
    } catch (_) {
      // JSON-LD mal formado en esta página: seguimos con la siguiente estrategia.
    }
  }
  return null;
}

function fromOpenGraph() {
  const ogTitle = document.querySelector('meta[property="og:title"]')?.content;
  const ogDesc =
    document.querySelector('meta[property="og:description"]')?.content ||
    document.querySelector('meta[name="description"]')?.content;
  if (ogTitle || ogDesc) {
    return { title: ogTitle || null, body: ogDesc || null, source: "open-graph" };
  }
  return null;
}

function fromArticleHeuristic() {
  const container = document.querySelector("article") || document.querySelector("main");
  if (!container) return null;

  const paragraphs = Array.from(container.querySelectorAll("p"))
    .map((p) => p.innerText.trim())
    .filter((t) => t.length > 40); // descarta pies de foto, créditos, etc.

  if (paragraphs.length === 0) return null;

  return {
    title: document.title || null,
    body: paragraphs.slice(0, 6).join("\n\n"),
    source: "article-heuristic",
  };
}

function fromSelection() {
  const selected = window.getSelection()?.toString().trim();
  if (selected && selected.length > 0) {
    return { title: document.title || null, body: selected, source: "user-selection" };
  }
  return null;
}

// Combina estrategias: usa la primera que tenga título Y cuerpo; si una
// estrategia sólo aporta uno de los dos campos, lo completa con la siguiente.
function getPageInfo({ preferSelection = false } = {}) {
  const strategies = preferSelection
    ? [fromSelection, fromJsonLd, fromOpenGraph, fromArticleHeuristic]
    : [fromJsonLd, fromOpenGraph, fromArticleHeuristic, fromSelection];

  let title = null;
  let body = null;
  let sourcesUsed = [];

  for (const strategy of strategies) {
    const result = strategy();
    if (!result) continue;
    if (!title && result.title) {
      title = result.title;
      sourcesUsed.push(`title:${result.source}`);
    }
    if (!body && result.body) {
      body = result.body;
      sourcesUsed.push(`body:${result.source}`);
    }
    if (title && body) break;
  }

  return {
    title: title || document.title || "(sin título)",
    body: body || null,
    url: window.location.href,
    extractionMethod: sourcesUsed.join(", ") || "fallback-minimo",
    extractedAt: new Date().toISOString(),
  };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message && message.type === "GET_PAGE_INFO") {
    try {
      sendResponse({ ok: true, data: getPageInfo() });
    } catch (err) {
      sendResponse({ ok: false, error: String(err) });
    }
  }
  if (message && message.type === "GET_SELECTION_INFO") {
    try {
      sendResponse({ ok: true, data: getPageInfo({ preferSelection: true }) });
    } catch (err) {
      sendResponse({ ok: false, error: String(err) });
    }
  }
  return true; // respuesta asíncrona
});
