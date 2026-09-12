// background.js — Service Worker (Manifest V3)
// Sprint 1 / Semana 1: estructura mínima, sin lógica de negocio todavía.

chrome.runtime.onInstalled.addListener((details) => {
  console.log("[FakeNews Checker] Extensión instalada/actualizada:", details.reason);

  // Al hacer clic en el icono de la extensión, se abre el side panel
  // en lugar de un popup clásico.
  chrome.sidePanel
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((err) => console.error("[FakeNews Checker] Error configurando side panel:", err));
});

// Punto de extensión futuro (Sprint 3): aquí se agregará la comunicación
// con el backend (fetch a /api/v1/verify) una vez exista el contrato API.
