// sidepanel.js — Lógica del Side Panel
// Sprint 1 / Semana 1: consulta la pestaña activa vía content script
// y muestra título/URL. Maneja estados de loading y error explícitamente,
// tal como pide el criterio de aceptación de la Semana 1.

const els = {
  loading: document.getElementById("state-loading"),
  error: document.getElementById("state-error"),
  errorText: document.getElementById("error-text"),
  result: document.getElementById("state-result"),
  title: document.getElementById("page-title"),
  url: document.getElementById("page-url"),
  body: document.getElementById("page-body"),
  method: document.getElementById("extraction-method"),
  retryBtn: document.getElementById("retry-btn"),
  refreshBtn: document.getElementById("refresh-btn"),
  useSelectionBtn: document.getElementById("use-selection-btn"),
  verifyBtn: document.getElementById("verify-btn"),
  verifyLoading: document.getElementById("state-verify-loading"),
  verifyError: document.getElementById("state-verify-error"),
  verifyErrorText: document.getElementById("verify-error-text"),
  verifyInsuficiente: document.getElementById("state-verify-insuficiente"),
  verifyResult: document.getElementById("state-verify-result"),
  verifyVeredicto: document.getElementById("verify-veredicto"),
  verifyScore: document.getElementById("verify-score"),
  verifyFuentes: document.getElementById("verify-fuentes"),
};

let _ultimoClaimText = null; // guardamos el último cuerpo extraído para poder verificarlo

function showState(state) {
  els.loading.classList.toggle("hidden", state !== "loading");
  els.error.classList.toggle("hidden", state !== "error");
  els.result.classList.toggle("hidden", state !== "result");
}

function showError(message) {
  els.errorText.textContent = message;
  showState("error");
}

function showResult(data) {
  els.title.textContent = data.title;
  els.url.textContent = data.url;
  els.body.textContent = data.body || "(no se encontró cuerpo de artículo en esta página)";
  els.method.textContent = data.extractionMethod;
  _ultimoClaimText = data.body || data.title; // lo que se enviará al verificador
  showState("result");
  hideVerifyStates();
}

function hideVerifyStates() {
  els.verifyLoading.classList.add("hidden");
  els.verifyError.classList.add("hidden");
  els.verifyInsuficiente.classList.add("hidden");
  els.verifyResult.classList.add("hidden");
}

function veredictoClass(veredicto) {
  if (veredicto === "Falso") return "veredicto-falso";
  if (veredicto === "Cuestionable") return "veredicto-cuestionable";
  if (veredicto === "Verdadero") return "veredicto-verdadero";
  return "";
}

async function verificarAfirmacion() {
  if (!_ultimoClaimText) {
    hideVerifyStates();
    els.verifyErrorText.textContent = "No hay texto extraído para verificar. Actualiza primero.";
    els.verifyError.classList.remove("hidden");
    return;
  }

  hideVerifyStates();
  els.verifyLoading.classList.remove("hidden");

  const response = await mockVerifyClaim({
    claim_text: _ultimoClaimText,
    url: els.url.textContent,
    title: els.title.textContent,
  });

  hideVerifyStates();

  // Maneja los 3 estados del contrato: ok / insuficiente / error.
  if (response.status === "error") {
    els.verifyErrorText.textContent = `[${response.error_code}] ${response.error_message}`;
    els.verifyError.classList.remove("hidden");
    return;
  }

  if (response.status === "insuficiente") {
    els.verifyInsuficiente.classList.remove("hidden");
    return;
  }

  // status === "ok"
  els.verifyVeredicto.textContent = response.veredicto;
  els.verifyVeredicto.className = `value veredicto-tag ${veredictoClass(response.veredicto)}`;
  els.verifyScore.textContent = `${(response.score * 100).toFixed(0)}% — confianza ${response.confianza}`;
  els.verifyFuentes.textContent = response.fuentes.map((f) => `${f.nombre} (peso ${f.peso})`).join(", ") || "—";
  els.verifyResult.classList.remove("hidden");
}

els.verifyBtn.addEventListener("click", verificarAfirmacion);

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function loadPageInfo(messageType = "GET_PAGE_INFO") {
  showState("loading");

  let tab;
  try {
    tab = await getActiveTab();
  } catch (err) {
    showError("No se pudo acceder a la pestaña activa.");
    return;
  }

  if (!tab || !tab.id) {
    showError("No hay una pestaña activa disponible.");
    return;
  }

  // Páginas internas de Chrome (chrome://, Web Store, etc.) no permiten
  // content scripts; lo cubrimos como caso de error controlado.
  if (tab.url && /^(chrome|chrome-extension|edge|about):/.test(tab.url)) {
    showError("Esta página del navegador no se puede leer. Abre una página web normal.");
    return;
  }

  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: messageType });
    if (response && response.ok) {
      showResult(response.data);
    } else {
      showError("El content script no devolvió datos válidos.");
    }
  } catch (err) {
    showError("No se pudo leer esta página. Recarga la pestaña e inténtalo de nuevo.");
  }
}

els.retryBtn.addEventListener("click", () => loadPageInfo());
els.refreshBtn.addEventListener("click", () => loadPageInfo());
els.useSelectionBtn.addEventListener("click", () => loadPageInfo("GET_SELECTION_INFO"));
document.addEventListener("DOMContentLoaded", () => loadPageInfo());
