"""
app/main.py — Semana 1 (bootstrap)

Esto es solo un placeholder para que la estructura /backend exista y
`pip install -r requirements.txt` + import funcione sin errores, tal como
pide el criterio de aceptación de la Semana 1.

El backend real (endpoints /health y /api/v1/verify, carga del modelo
Random Forest, etc.) se construye en la Semana 5 — feature/backend-api.
"""

from fastapi import FastAPI

app = FastAPI(
    title="FakeNews Checker API",
    description="Placeholder de bootstrap — Semana 1. Endpoints reales en Semana 5.",
    version="0.0.1",
)


@app.get("/")
def root():
    return {"status": "bootstrap-ok", "note": "Backend real se construye en Semana 5."}
