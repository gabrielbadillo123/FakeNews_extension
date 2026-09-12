# FakeNews Checker — Extensión (Sprint 1 / Semana 1)

Extensión Manifest V3 mínima: manifest, service worker, content script y side panel.
Cumple el criterio de aceptación de la Semana 1: **"Instala sin errores y lee título/URL."**

## Estructura

```
fakenews-extension/
├── manifest.json      # Configuración MV3
├── background.js      # Service worker (abre el side panel)
├── content.js         # Extrae título y URL de la página
├── sidepanel.html      # UI del side panel
├── sidepanel.css
└── sidepanel.js        # Consulta la pestaña activa y pinta el resultado
```

## Cómo probarla en modo desarrollador

1. Abre `chrome://extensions` en Chrome/Chromium.
2. Activa **Modo de desarrollador** (esquina superior derecha).
3. Clic en **Cargar descomprimida** y selecciona esta carpeta (`fakenews-extension/`).
4. Abre cualquier página web normal (no `chrome://...`).
5. Haz clic en el icono de la extensión: se abre el side panel y debe mostrar
   el título y la URL de la pestaña activa en segundos.
6. Verifica en `chrome://extensions` que no haya errores listados para la extensión.

## Flujo Git sugerido (según el cronograma)

```bash
git checkout -b feature/extension-bootstrap
git add fakenews-extension/
git commit -m "feat(extension): bootstrap MV3 - manifest, service worker, content script, side panel"
git push origin feature/extension-bootstrap
# Abrir PR contra main/develop para revisión de Gabriel/directora
```

## Qué falta (próximas semanas)

- Semana 2: extracción robusta de titular/cuerpo vía DOM + fallback de texto
  seleccionado (`feature/content-extractor`).
- Semana 3: contrato JSON + mock de API para desacoplar la extensión del
  backend (`feature/api-client-mock`).

## Notas de seguridad/permisos

- Permisos usados: `activeTab`, `scripting`, `sidePanel` (mínimos necesarios).
- El content script se inyecta en `<all_urls>` pero **no envía datos a ningún
  servidor todavía** — solo lee `document.title` y `window.location.href`
  localmente, como pide el alcance de la Semana 1.
