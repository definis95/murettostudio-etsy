"""Client minimale per Etsy Open API v3.

Le credenziali vengono lette da .env a runtime e non vengono mai stampate.
I token OAuth sono salvati in .etsy_tokens.json (anch'esso da non condividere).
"""
import json
import time
from pathlib import Path

try:  # usa i certificati di Windows (evita CERTIFICATE_VERIFY_FAILED con antivirus/proxy)
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import requests
from dotenv import dotenv_values

BASE_URL = "https://openapi.etsy.com/v3"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
ROOT = Path(__file__).parent
TOKEN_FILE = ROOT / ".etsy_tokens.json"


def load_credentials():
    """Restituisce (keystring, shared_secret) da .env, accettando qualsiasi maiuscola/minuscola."""
    env = {k.lower(): (v or "").strip() for k, v in dotenv_values(ROOT / ".env").items()}
    keystring = env.get("etsy_keystring") or env.get("keystring")
    shared_secret = env.get("etsy_shared_secret") or env.get("shared_secret")
    if not keystring or not shared_secret:
        raise SystemExit("In .env mancano le variabili 'ETSY_KEYSTRING' e/o 'ETSY_SHARED_SECRET'.")
    return keystring, shared_secret


def api_key_header():
    # Etsy richiede "keystring:shared_secret" nell'header x-api-key
    keystring, shared_secret = load_credentials()
    return f"{keystring}:{shared_secret}"


def save_tokens(data):
    data["expires_at"] = time.time() + int(data.get("expires_in", 3600)) - 60
    TOKEN_FILE.write_text(json.dumps(data), encoding="utf-8")


def load_tokens():
    if not TOKEN_FILE.exists():
        raise SystemExit("Nessun token: esegui prima  python etsy_auth.py")
    return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))


def refresh_tokens(tokens):
    keystring, _ = load_credentials()
    r = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "client_id": keystring,
        "refresh_token": tokens["refresh_token"],
    }, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f"Refresh token fallito ({r.status_code}): rifai il login con  python etsy_auth.py")
    new = r.json()
    save_tokens(new)
    return new


def access_token():
    tokens = load_tokens()
    if time.time() >= tokens.get("expires_at", 0):
        tokens = refresh_tokens(tokens)
    return tokens["access_token"]


def user_id():
    # L'access token Etsy ha la forma "<user_id>.<token>"
    return access_token().split(".", 1)[0]


def request(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["x-api-key"] = api_key_header()
    headers["Authorization"] = f"Bearer {access_token()}"
    r = requests.request(method, BASE_URL + path, headers=headers, timeout=60, **kwargs)
    time.sleep(0.12)  # resta sotto le 10 richieste/secondo
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
    return r.json() if r.content else None


def get(path, **params):
    return request("GET", path, params=params)


def get_shop_id():
    me = get(f"/application/users/{user_id()}/shops")
    return me["shop_id"], me
