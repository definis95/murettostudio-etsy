"""Client minimale per Printify API v1.

Il token (Personal Access Token) viene letto da .env (variabile PRINTIFY_TOKEN) a runtime
e non viene mai stampato.
"""
import time
from pathlib import Path

try:  # usa i certificati di Windows (evita CERTIFICATE_VERIFY_FAILED con antivirus/proxy)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import requests
from dotenv import dotenv_values

BASE_URL = "https://api.printify.com/v1"
ROOT = Path(__file__).parent


def load_token():
    env = {k.lower(): (v or "").strip() for k, v in dotenv_values(ROOT / ".env").items()}
    token = env.get("printify_token")
    if not token:
        raise SystemExit("In .env manca la variabile 'PRINTIFY_TOKEN'.")
    return token


_session = None


def session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "Authorization": f"Bearer {load_token()}",
            "User-Agent": "MurettoStudio-tools",
        })
    return _session


def request(method, path, **kwargs):
    for attempt in range(6):  # il catalogo ha un limite di richieste al minuto: aspetta e riprova
        r = session().request(method, BASE_URL + path, timeout=60, **kwargs)
        if r.status_code != 429:
            break
        time.sleep(int(r.headers.get("Retry-After") or 15 * (attempt + 1)))
    if r.status_code >= 400:
        raise SystemExit(f"Printify {method} {path} -> {r.status_code}: {r.text[:500]}")
    return r.json() if r.content else None


def get(path, **params):
    return request("GET", path, params=params or None)


def get_shop():
    """Restituisce il negozio Printify collegato a Etsy (o il primo disponibile)."""
    shops = get("/shops.json")
    if not shops:
        raise SystemExit("Nessun negozio trovato su Printify.")
    etsy = [s for s in shops if s.get("sales_channel") == "etsy"]
    return (etsy or shops)[0]
