"""Crea o aggiorna su Printify un prodotto (NON pubblicato) a partire da un file inserzione JSON.

Uso:
  python printify_create.py inserzioni/02_decorazione.json            (crea o aggiorna la bozza)
  python printify_create.py inserzioni/02_decorazione.json --dry-run  (controlla soltanto)
  python printify_create.py inserzioni/02_decorazione.json --solo-stampa  (aggiorna solo i file di stampa)

Formato del JSON:
  {
    "title": "...", "description": "...", "tags": ["..."],          (max 13 tag, max 20 caratteri ciascuno)
    "blueprint_id": 1676, "print_provider_id": 94,
    "variants": {"<titolo variante o *>": prezzo_in_centesimi},       (le varianti non elencate restano disattivate)
    "colori": ["Red", "Navy"],                                       (facoltativo: attiva solo questi colori)
    "images": {"front": "grafiche/.../file.png"},                    (posizione -> file; "*" = tutte le posizioni)
    "variant_images": {"11oz": {"front": "..."}},                    (facoltativo: file diversi per variante)
    "printify_product_id": null                                      (scritto dallo script dopo la creazione)
  }
Non pubblica nulla su Etsy: la pubblicazione si fa a parte, dopo l'ok.
"""
import base64
import json
import sys
from pathlib import Path

from printify_client import get, get_shop, request

ROOT = Path(__file__).parent
TITLE_MAX, TAGS_MAX, TAG_LEN = 140, 13, 20


def check(listing):
    errors = []
    if len(listing["title"]) > TITLE_MAX:
        errors.append(f"titolo troppo lungo ({len(listing['title'])} > {TITLE_MAX})")
    if len(listing["tags"]) > TAGS_MAX:
        errors.append(f"troppi tag ({len(listing['tags'])} > {TAGS_MAX})")
    errors += [f"tag troppo lungo: '{t}'" for t in listing["tags"] if len(t) > TAG_LEN]
    paths = list(listing.get("images", {}).values())
    paths += [p for imgs in listing.get("variant_images", {}).values() for p in imgs.values()]
    errors += [f"file mancante: {p}" for p in paths if not (ROOT / p).exists()]
    return errors


def upload(path):
    data = (ROOT / path).read_bytes()
    res = request("POST", "/uploads/images.json",
                  json={"file_name": Path(path).name, "contents": base64.b64encode(data).decode()})
    print(f"  caricato {path} -> {res['id']}")
    return res["id"]


def build_body(listing, catalog_variants):
    prices = listing["variants"]
    colori = listing.get("colori")  # se presente, solo questi colori vengono attivati
    variants, enabled = [], []
    for v in catalog_variants:
        price = prices.get(v["title"], prices.get("*"))
        if colori and v.get("options", {}).get("color") not in colori:
            price = None
        variants.append({"id": v["id"], "price": price or 99900, "is_enabled": price is not None})
        if price is not None:
            enabled.append(v)
    if not enabled:
        raise SystemExit("Nessuna variante corrisponde: titoli disponibili:\n  " +
                         "\n  ".join(v["title"] for v in catalog_variants))

    # "images" vale per tutte le varianti; "variant_images" (titolo variante -> posizioni) ha la precedenza
    uploaded = {}

    def image_id(path):
        if path not in uploaded:
            uploaded[path] = upload(path)
        return uploaded[path]

    groups = {}  # immagini per posizione -> varianti che le usano
    for v in enabled:
        images = {**listing.get("images", {}), **listing.get("variant_images", {}).get(v["title"], {})}
        key = tuple(sorted(images.items()))
        groups.setdefault(key, []).append(v)
    print_areas = []
    for key, group in groups.items():
        images = dict(key)
        placeholders = []
        for pos in sorted({ph["position"] for v in group for ph in v["placeholders"]}):
            path = images.get(pos) or images.get("*")
            if path:
                placeholders.append({"position": pos, "images": [
                    {"id": image_id(path), "x": 0.5, "y": 0.5, "scale": 1, "angle": 0}]})
        print_areas.append({"variant_ids": [v["id"] for v in group], "placeholders": placeholders})
    return {
        "title": listing["title"],
        "description": listing["description"],
        "tags": listing["tags"],
        "blueprint_id": listing["blueprint_id"],
        "print_provider_id": listing["print_provider_id"],
        "variants": variants,
        "print_areas": print_areas,
    }


def main():
    path = Path(sys.argv[1])
    dry = "--dry-run" in sys.argv
    listing = json.loads(path.read_text(encoding="utf-8"))
    errors = check(listing)
    if errors:
        raise SystemExit("Errori:\n  " + "\n  ".join(errors))
    print(f"{path.name}: titolo {len(listing['title'])} car., {len(listing['tags'])} tag - ok")
    if dry:
        return

    shop_id = get_shop()["id"]
    catalog = get(f"/catalog/blueprints/{listing['blueprint_id']}/print_providers/"
                  f"{listing['print_provider_id']}/variants.json")["variants"]
    body = build_body(listing, catalog)
    pid = listing.get("printify_product_id")
    if pid and "--solo-stampa" in sys.argv:
        # aggiorna solo i file di stampa: titolo, descrizione, GPSR e prezzi restano come sono su Printify
        attuale = get(f"/shops/{shop_id}/products/{pid}.json")
        varianti = [{"id": v["id"], "price": v["price"], "is_enabled": v["is_enabled"]} for v in attuale["variants"]]
        # Printify vuole un'area per OGNI variante (anche disattivate): tiene i gruppi attuali e cambia le immagini
        nuove = {vid: pa["placeholders"] for pa in body["print_areas"] for vid in pa["variant_ids"]}
        predefinite = body["print_areas"][0]["placeholders"]
        aree = [{"variant_ids": pa["variant_ids"],
                 "placeholders": next((nuove[v] for v in pa["variant_ids"] if v in nuove), predefinite)}
                for pa in attuale["print_areas"]]
        product = request("PUT", f"/shops/{shop_id}/products/{pid}.json",
                          json={"variants": varianti, "print_areas": aree})
        print(f"Aggiornati solo i file di stampa del prodotto {pid}")
    elif pid:
        # se su Printify la descrizione contiene testo aggiunto dopo (es. sezione GPSR), non lo cancella
        attuale = get(f"/shops/{shop_id}/products/{pid}.json").get("description") or ""
        if len(attuale) > len(body["description"]) and "safety" in attuale.lower():
            body["description"] = attuale
            print("  descrizione su Printify con info di sicurezza (GPSR): mantenuta quella di Printify")
        product = request("PUT", f"/shops/{shop_id}/products/{pid}.json", json=body)
        print(f"Aggiornato prodotto {pid}")
    else:
        product = request("POST", f"/shops/{shop_id}/products.json", json=body)
        listing["printify_product_id"] = product["id"]
        path.write_text(json.dumps(listing, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Creato prodotto {product['id']} (non pubblicato)")
    for v in product["variants"]:
        if v.get("is_enabled"):
            print(f"  {v['title']}: prezzo {v['price'] / 100:.2f}, costo {v.get('cost', 0) / 100:.2f}")
    print("Controllalo su printify.com -> My products (stato: non pubblicato)")


if __name__ == "__main__":
    main()
