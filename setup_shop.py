"""Carica su Etsy le informazioni del negozio da shop_content_en.json.

Uso:
  python setup_shop.py --dry-run   (mostra cosa farebbe, senza modificare nulla)
  python setup_shop.py             (applica le modifiche)

Si può rilanciare senza problemi: sezioni e return policy già presenti vengono saltate;
le sezioni non più elencate nel JSON vengono eliminate solo se non contengono inserzioni.
"""
import json
import sys

from etsy_client import get, get_shop_id, request

LIMITS = {"title": 55}  # limite Etsy per il titolo del negozio
SECTION_MAX = 24


def main():
    dry = "--dry-run" in sys.argv
    content = json.load(open("shop_content_en.json", encoding="utf-8"))
    shop_id, shop = get_shop_id()
    print(f"Negozio {shop['shop_name']} (id {shop_id}){'  [DRY RUN]' if dry else ''}")

    # 1. Testi del negozio
    fields = content["shop"]
    for k, max_len in LIMITS.items():
        if len(fields[k]) > max_len:
            raise SystemExit(f"'{k}' supera {max_len} caratteri ({len(fields[k])})")
    changed = {k: v for k, v in fields.items() if (shop.get(k) or "") != v}
    print(f"- Testi negozio da aggiornare: {', '.join(changed) or 'nessuno'}")
    if changed and not dry:
        request("PUT", f"/application/shops/{shop_id}", data=changed)

    # 2. Sezioni: toglie quelle non piu' previste (solo se vuote), poi crea le mancanti
    sections = get(f"/application/shops/{shop_id}/sections")["results"]
    for s in sections:
        if s["title"] in content["sections"]:
            continue
        if s.get("active_listing_count"):
            print(f"- Sezione obsoleta ma con inserzioni, la lascio: {s['title']}")
            continue
        print(f"- Elimino sezione vuota: {s['title']}")
        if not dry:
            request("DELETE", f"/application/shops/{shop_id}/sections/{s['shop_section_id']}")
    existing = {s["title"] for s in sections}
    for title in content["sections"]:
        if len(title) > SECTION_MAX:
            raise SystemExit(f"Sezione troppo lunga: {title}")
        if title in existing:
            print(f"- Sezione già presente: {title}")
            continue
        print(f"- Creo sezione: {title}")
        if not dry:
            request("POST", f"/application/shops/{shop_id}/sections", data={"title": title})

    # 3. Return policy
    policies = get(f"/application/shops/{shop_id}/policies/return")["results"]
    rp = content["return_policy"]
    if policies:
        print(f"- Return policy già presente (id {policies[0]['return_policy_id']}), salto")
    else:
        print(f"- Creo return policy: resi {rp['return_deadline']} giorni, cambi {'sì' if rp['accepts_exchanges'] else 'no'}")
        if not dry:
            data = {k: str(v).lower() if isinstance(v, bool) else v for k, v in rp.items()}
            request("POST", f"/application/shops/{shop_id}/policies/return", data=data)

    print("Fatto." if not dry else "Nessuna modifica applicata (dry run).")


if __name__ == "__main__":
    main()
