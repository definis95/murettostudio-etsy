"""Cerca prodotti nel catalogo Printify e mostra gli stampatori, con area di stampa e spedizione.

Uso:
  python printify_catalog.py --check              (verifica il token e mostra il negozio collegato)
  python printify_catalog.py ornament             (cerca "ornament" nel titolo dei prodotti)
  python printify_catalog.py ornament --eu        (solo stampatori in Europa)
  python printify_catalog.py --blueprint 1234     (dettaglio di un prodotto per id)

Salva anche il risultato completo in printify_dati/catalogo_<ricerca>.json.
"""
import argparse
import json
from pathlib import Path

from printify_client import get, get_shop

EUROPE = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
          "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "GB", "UK", "NO", "CH"}
OUT_DIR = Path(__file__).parent / "printify_dati"


def money(c):
    return f"{c['cost'] / 100:.2f} {c.get('currency', '')}".strip() if c else "-"


def shipping_to(shipping, country="IT"):
    """Primo articolo / articoli aggiuntivi verso il paese indicato (o REST_OF_THE_WORLD)."""
    for want in (country, "REST_OF_THE_WORLD"):
        for p in shipping.get("profiles", []):
            if want in p.get("countries", []):
                return f"{money(p.get('first_item'))} (+{money(p.get('additional_items'))} per articolo in più)"
    return "non spedisce in IT"


def describe(bp, providers_loc, eu_only):
    bid = bp["id"]
    info = {"id": bid, "title": bp["title"], "brand": bp.get("brand"), "providers": []}
    print(f"\n=== [{bid}] {bp['title']} ({bp.get('brand', '')})")
    for pp in get(f"/catalog/blueprints/{bid}/print_providers.json"):
        loc = providers_loc.get(pp["id"], {})
        country = (loc.get("country") or "?").upper()
        if eu_only and country not in EUROPE:
            continue
        variants = get(f"/catalog/blueprints/{bid}/print_providers/{pp['id']}/variants.json")["variants"]
        shipping = get(f"/catalog/blueprints/{bid}/print_providers/{pp['id']}/shipping.json")
        handling = shipping.get("handling_time", {})
        areas = sorted({f"{ph['position']} {ph['width']}x{ph['height']}"
                        for v in variants for ph in v.get("placeholders", [])})
        print(f"  - [{pp['id']}] {pp['title']} | {country} {loc.get('city', '')}"
              f" | produzione {handling.get('value', '?')} {handling.get('unit', '')}"
              f" | spedizione IT: {shipping_to(shipping)}")
        print(f"      varianti: {', '.join(v['title'] for v in variants[:8])}{' ...' if len(variants) > 8 else ''}")
        print(f"      area di stampa (px): {'; '.join(areas)}")
        info["providers"].append({"id": pp["id"], "title": pp["title"], "location": loc,
                                  "variants": variants, "shipping": shipping})
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?")
    ap.add_argument("--eu", action="store_true")
    ap.add_argument("--blueprint", type=int)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    if a.check:
        shop = get_shop()
        print(f"Token ok. Negozio Printify: {shop['title']} (id {shop['id']}, canale {shop.get('sales_channel')})")
        return

    providers_loc = {p["id"]: p.get("location") or {} for p in get("/catalog/print_providers.json")}
    blueprints = get("/catalog/blueprints.json")
    if a.blueprint:
        found = [b for b in blueprints if b["id"] == a.blueprint]
        name = f"blueprint_{a.blueprint}"
    elif a.query:
        words = a.query.lower().split()
        found = [b for b in blueprints if all(w in b["title"].lower() for w in words)]
        name = "_".join(words)
    else:
        ap.error("indica una ricerca, --blueprint o --check")
    print(f"{len(found)} prodotti trovati")

    result = [describe(b, providers_loc, a.eu) for b in found]
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"catalogo_{name}{'_eu' if a.eu else ''}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDettagli salvati in {out.name}")


if __name__ == "__main__":
    main()
