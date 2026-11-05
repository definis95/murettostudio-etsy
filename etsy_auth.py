"""Login OAuth 2.0 + PKCE con Etsy.

Uso:  python etsy_auth.py
Apre il browser sulla pagina di autorizzazione Etsy; dopo che clicchi "Allow access",
Etsy rimanda il browser a http://localhost:3003/oauth/redirect, dove questo script
riceve il codice e lo scambia con access token + refresh token (salvati in .etsy_tokens.json).
"""
import base64
import hashlib
import http.server
import secrets
import urllib.parse
import webbrowser

import requests

from etsy_client import TOKEN_URL, load_credentials, save_tokens

PORT = 3003
REDIRECT_URI = f"http://localhost:{PORT}/oauth/redirect"
SCOPES = "shops_r shops_w listings_r listings_w listings_d transactions_r profile_r"


def main():
    keystring, _ = load_credentials()
    verifier = secrets.token_urlsafe(64)[:96]
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)

    auth_url = "https://www.etsy.com/oauth/connect?" + urllib.parse.urlencode({
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "client_id": keystring,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    })

    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in qs.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Login completato, puoi chiudere questa scheda." if "code" in qs else "Errore: " + str(qs)
            self.wfile.write(f"<h2>{msg}</h2>".encode())

        def log_message(self, *args):
            pass

    print("Apro il browser per autorizzare l'app su Etsy...")
    webbrowser.open(auth_url)
    with http.server.HTTPServer(("localhost", PORT), Handler) as server:
        while "code" not in result and "error" not in result:
            server.handle_request()

    if "error" in result:
        raise SystemExit(f"Autorizzazione negata: {result.get('error')} {result.get('error_description', '')}")
    if result.get("state") != state:
        raise SystemExit("State non corrispondente: login annullato per sicurezza.")

    r = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "client_id": keystring,
        "redirect_uri": REDIRECT_URI,
        "code": result["code"],
        "code_verifier": verifier,
    }, timeout=30)
    if r.status_code != 200:
        raise SystemExit(f"Scambio del codice fallito ({r.status_code}): {r.text[:300]}")
    save_tokens(r.json())
    print("OK: token salvati in .etsy_tokens.json (validi 1 ora, rinnovo automatico per 90 giorni).")


if __name__ == "__main__":
    main()
