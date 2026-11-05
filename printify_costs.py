"""Legge i costi di produzione Printify creando un prodotto di prova NON pubblicato, poi lo cancella.

Il catalogo Printify non espone i prezzi: l'unico modo è creare un prodotto (bozza invisibile su Etsy)
e leggere il campo "cost" delle varianti.

Uso:
  python printify_costs.py 1368:94 1676:94 ...      (coppie blueprint:print_provider)
  python printify_costs.py --preset                  (tutti i candidati del negozio)
  python printify_costs.py 586:99 --solo front       (stampa solo in quella posizione, come i prodotti veri)

Risultato in printify_dati/costi.json (costi in centesimi USD, come li dà Printify).
"""
import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

from printify_client import get, get_shop, request

OUT = Path(__file__).parent / "printify_dati" / "costi.json"

PRESET = {
    "Calendario Harrier UK": (1368, 94),
    "Decorazione ceramica Harrier UK": (1676, 94),
    "Poster OPT CZ": (443, 30),
    "Poster Posterflow DE": (1033, 220),
    "Poster cornice Print Pigeons LV": (492, 36),
    "Tazza OPT CZ": (441, 30),
    "Tazza Textildruck DE": (1016, 26),
    "Tote Textildruck DE": (731, 26),
    "Desk mat cucito Printify Choice US": (10665, 99),
    "Desk mat SPOKE US": (488, 1),
    "Telo mare SPOKE US": (352, 1),
    "Puzzle District Photo US": (1149, 28),
    "Puzzle con scatola in latta US": (532, 59),
}


def upload_placeholder():
    buf = io.BytesIO()
    Image.new("RGB", (1200, 1200), (200, 196, 188)).save(buf, "PNG")
    res = request("POST", "/uploads/images.json", json={
        "file_name": "muretto_placeholder.png",
        "contents": base64.b64encode(buf.getvalue()).decode()})
    return res["id"]


def probe(shop_id, image_id, blueprint, provider, solo=None):
    variants = get(f"/catalog/blueprints/{blueprint}/print_providers/{provider}/variants.json")["variants"]
    positions = sorted({ph["position"] for v in variants for ph in v.get("placeholders", [])})
    if solo:
        positions = [p for p in positions if p == solo]
    body = {
        "title": f"PROVA COSTI {blueprint}-{provider} (da cancellare)",
        "description": "Prodotto temporaneo per leggere i costi.",
        "blueprint_id": blueprint,
        "print_provider_id": provider,
        "variants": [{"id": v["id"], "price": 99900, "is_enabled": True} for v in variants],
        "print_areas": [{
            "variant_ids": [v["id"] for v in variants],
            "placeholders": [{"position": pos, "images": [{"id": image_id, "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]}
                             for pos in positions],
        }],
    }
    product = request("POST", f"/shops/{shop_id}/products.json", json=body)
    try:
        return [{"title": v["title"], "cost": v.get("cost")} for v in product["variants"] if v.get("is_enabled")]
    finally:
        request("DELETE", f"/shops/{shop_id}/products/{product['id']}.json")


def main():
    solo = None
    if "--preset" in sys.argv:
        targets = PRESET
    else:
        targets = {a: tuple(map(int, a.split(":"))) for a in sys.argv[1:] if ":" in a}
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    if not targets:
        raise SystemExit(__doc__)
    shop_id = get_shop()["id"]
    image_id = upload_placeholder()
    results = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for name, (bp, pp) in targets.items():
        try:
            costs = probe(shop_id, image_id, bp, pp, solo)
        except SystemExit as e:  # un prodotto che fallisce non blocca gli altri
            print(f"\n## {name} [{bp}:{pp}] ERRORE: {e}")
            continue
        results[name] = {"blueprint": bp, "provider": pp, "posizione": solo or "tutte", "variants": costs}
        print(f"\n## {name} [{bp}:{pp}]")
        for c in costs:
            print(f"   {c['title']}: {c['cost'] / 100:.2f} USD" if c["cost"] is not None else f"   {c['title']}: ?")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSalvato in {OUT.name}")


if __name__ == "__main__":
    main()
