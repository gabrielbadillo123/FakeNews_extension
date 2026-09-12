"""
acquisition_colombiacheck.py — Sprint 1/2, Semana 2 (Fabián)

Recolecta el corpus de afirmaciones políticas verificadas por ColombiaCheck
a partir de los metadatos estructurados ClaimReview (schema.org JSON-LD) que
el sitio publica en cada artículo de chequeo.

Principios éticos (seguidos del proyecto de referencia POLUX89/NLP-Fake-News-Colombia):
  - Respeta robots.txt antes de recorrer nada.
  - Se identifica con un User-Agent propio y honesto.
  - Aplica throttle entre requests (no golpea el servidor).
  - Sólo extrae metadatos estructurados públicos (ClaimReview), NUNCA el
    cuerpo completo del artículo -> evita fuga de etiqueta y respeta
    derechos de autor del texto periodístico.
  - Cachea localmente para no repetir requests innecesarios.

USO:
    python acquisition_colombiacheck.py --limit 5      # smoke test
    python acquisition_colombiacheck.py                # recolección completa

Requiere: requests, beautifulsoup4, urllib3
    pip install requests beautifulsoup4 --break-system-packages
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.robotparser as robotparser
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://colombiacheck.com"
LISTING_PATH = "/chequeos"
USER_AGENT = "FakeNewsProyectoAcademico/0.1 (+contacto: equipo-proyecto@example.edu.co)"
THROTTLE_SECONDS = 1.5
CACHE_DIR = Path(__file__).parent / "data" / "raw" / "colombiacheck_cache"
OUTPUT_CSV = Path(__file__).parent / "data" / "processed" / "dataset_colombiacheck.csv"


@dataclass
class ClaimRecord:
    claim_text: str
    label: str | None
    date_published: str | None
    source_url: str


def can_fetch(url: str) -> bool:
    """Verifica robots.txt antes de acceder a cualquier ruta del sitio."""
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(BASE_URL, "/robots.txt"))
    rp.read()
    return rp.can_fetch(USER_AGENT, url)


def fetch_with_cache(url: str, session: requests.Session) -> str:
    """Descarga una URL con cache local en disco, para no repetir requests."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_key = url.replace("https://", "").replace("/", "_") + ".html"
    cache_path = CACHE_DIR / cache_key

    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    if not can_fetch(url):
        raise PermissionError(f"robots.txt no permite acceder a: {url}")

    resp = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    cache_path.write_text(resp.text, encoding="utf-8")
    time.sleep(THROTTLE_SECONDS)  # throttle obligatorio entre requests
    return resp.text


def extract_claim_review(html: str, source_url: str) -> ClaimRecord | None:
    """
    Extrae el bloque ClaimReview (JSON-LD) de una página de chequeo.
    Devuelve None si la página no trae un ClaimReview (caso frecuente:
    ~38% de los chequeos no incluyen claimReviewed, según el proyecto de
    referencia).
    """
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if item.get("@type") == "ClaimReview":
                claim_text = item.get("claimReviewed")
                rating = item.get("reviewRating", {})
                label = rating.get("alternateName") or rating.get("ratingValue")
                if claim_text:
                    return ClaimRecord(
                        claim_text=claim_text.strip(),
                        label=str(label).strip() if label else None,
                        date_published=item.get("datePublished"),
                        source_url=source_url,
                    )
    return None


def discover_chequeo_urls(session: requests.Session, max_pages: int | None) -> list[str]:
    """
    Recorre el listado paginado de /chequeos y recolecta las URLs de cada
    artículo individual. Se detiene si max_pages está definido (smoke test).
    """
    urls: list[str] = []
    page = 1
    while True:
        listing_url = f"{BASE_URL}{LISTING_PATH}?page={page}"
        try:
            html = fetch_with_cache(listing_url, session)
        except (requests.RequestException, PermissionError) as err:
            print(f"  [aviso] no se pudo leer página {page}: {err}")
            break

        soup = BeautifulSoup(html, "html.parser")
        links = [
            urljoin(BASE_URL, a["href"])
            for a in soup.select("a[href]")
            if "/chequeos/" in a.get("href", "")
        ]
        links = sorted(set(links))
        if not links:
            break

        urls.extend(links)
        print(f"  página {page}: {len(links)} enlaces encontrados (total: {len(urls)})")

        if max_pages and page >= max_pages:
            break
        page += 1

    return sorted(set(urls))


def main():
    parser = argparse.ArgumentParser(description="Recolecta corpus de ColombiaCheck vía ClaimReview.")
    parser.add_argument("--limit", type=int, default=None, help="Límite de artículos (smoke test).")
    parser.add_argument("--max-pages", type=int, default=None, help="Límite de páginas del listado.")
    args = parser.parse_args()

    session = requests.Session()

    print("Descubriendo URLs de chequeos...")
    chequeo_urls = discover_chequeo_urls(session, args.max_pages)
    if args.limit:
        chequeo_urls = chequeo_urls[: args.limit]
    print(f"Total de artículos a procesar: {len(chequeo_urls)}")

    records: list[ClaimRecord] = []
    for i, url in enumerate(chequeo_urls, start=1):
        try:
            html = fetch_with_cache(url, session)
        except (requests.RequestException, PermissionError) as err:
            print(f"  [{i}/{len(chequeo_urls)}] error en {url}: {err}")
            continue

        record = extract_claim_review(html, url)
        if record:
            records.append(record)
            print(f"  [{i}/{len(chequeo_urls)}] OK — label={record.label}")
        else:
            print(f"  [{i}/{len(chequeo_urls)}] sin ClaimReview, se descarta")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    import csv

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["claim_text", "label", "date_published", "source_url"])
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))

    print(f"\nListo: {len(records)} afirmaciones guardadas en {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
