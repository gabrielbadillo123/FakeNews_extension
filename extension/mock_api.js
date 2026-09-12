// mock_api.js — Mock del backend de verificación (Semana 3, Gabriel)
// Rama: feature/api-client-mock
//
// Implementa EXACTAMENTE el contrato definido en CONTRATO_API.md, para que
// la extensión pueda avanzar desacoplada del backend real (que se
// construye en la Semana 5). Cuando el backend exista, solo hay que
// reemplazar mockVerifyClaim() por un fetch() real a /api/v1/verify — la
// UI (sidepanel.js) no debería necesitar cambios porque consume el mismo
// contrato.

const MOCK_LATENCY_MS = 900;

// Palabras clave para simular un veredicto "creíble" según el contenido,
// solo para que la demo no sea siempre el mismo resultado fijo.
const _PALABRAS_FALSO = ["falso", "mentira", "nunca", "jamás", "inventado"];
const _PALABRAS_VERDADERO = ["confirmado", "oficial", "certificado", "verificado"];

function _elegirVeredictoSimulado(claimText) {
  const texto = (claimText || "").toLowerCase();

  if (_PALABRAS_FALSO.some((p) => texto.includes(p))) {
    return {
      status: "ok",
      score: 0.85,
      veredicto: "Falso",
      confianza: "alta",
      fuentes: [
        { nombre: "ColombiaCheck", url: "https://colombiacheck.com", peso: 1.0 },
      ],
    };
  }

  if (_PALABRAS_VERDADERO.some((p) => texto.includes(p))) {
    return {
      status: "ok",
      score: 0.78,
      veredicto: "Verdadero",
      confianza: "media",
      fuentes: [
        { nombre: "El Tiempo", url: "https://www.eltiempo.com", peso: 0.4 },
      ],
    };
  }

  // Caso por defecto: sin señales claras -> insuficiente, para que la UI
  // pruebe también ese estado (no solo el "feliz").
  if (texto.length < 15) {
    return { status: "insuficiente", score: null, veredicto: null, confianza: null, fuentes: [] };
  }

  return {
    status: "ok",
    score: 0.55,
    veredicto: "Cuestionable",
    confianza: "media",
    fuentes: [
      { nombre: "La Silla Vacía — Detector de Mentiras", url: "https://lasillavacia.com/detector-de-mentiras", peso: 0.95 },
    ],
  };
}

/**
 * Simula la llamada POST /api/v1/verify. Devuelve una Promise que resuelve
 * con el mismo shape que devolvería el backend real (ver CONTRATO_API.md).
 *
 * @param {{claim_text: string, url?: string, title?: string}} payload
 * @returns {Promise<object>}
 */
function mockVerifyClaim(payload) {
  const startedAt = Date.now();

  return new Promise((resolve, reject) => {
    if (!payload || typeof payload.claim_text !== "string" || payload.claim_text.trim().length === 0) {
      setTimeout(() => {
        resolve({
          status: "error",
          error_code: "INVALID_INPUT",
          error_message: "claim_text es requerido y no puede estar vacío.",
          latencia_ms: Date.now() - startedAt,
        });
      }, 200);
      return;
    }

    // Simula un timeout ocasional (1 de cada 10) para que la UI también
    // pruebe ese camino de error, tal como pide el criterio de aceptación.
    const simularTimeout = Math.random() < 0.1;

    setTimeout(() => {
      if (simularTimeout) {
        resolve({
          status: "error",
          error_code: "TIMEOUT",
          error_message: "El servicio de verificación no respondió a tiempo.",
          latencia_ms: Date.now() - startedAt,
        });
        return;
      }

      const resultado = _elegirVeredictoSimulado(payload.claim_text);
      resolve({ ...resultado, latencia_ms: Date.now() - startedAt });
    }, MOCK_LATENCY_MS);
  });
}
