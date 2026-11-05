"""Mostra lo stato attuale del negozio: info, policy, spedizioni, partner di produzione, inserzioni.

Uso:  python inspect_shop.py   (scrive anche shop_snapshot.json)
"""
import json

from etsy_client import get, get_shop_id

SHOP_FIELDS = [
    "shop_id", "shop_name", "title", "announcement", "sale_message", "digital_sale_message",
    "currency_code", "is_vacation", "policy_additional", "url", "icon_url_fullxfull",
    "listing_active_count", "digital_listing_count", "languages", "accepts_custom_requests",
]


def safe(label, fn):
    try:
        return fn()
    except Exception as e:  # una sezione che fallisce non blocca le altre
        return {"_error": f"{label}: {e}"}


def main():
    shop_id, shop = get_shop_id()
    snapshot = {
        "shop": {k: shop.get(k) for k in SHOP_FIELDS},
        "sections": safe("sections", lambda: get(f"/application/shops/{shop_id}/sections")),
        "shipping_profiles": safe("shipping", lambda: get(f"/application/shops/{shop_id}/shipping-profiles")),
        "return_policies": safe("returns", lambda: get(f"/application/shops/{shop_id}/policies/return")),
        "production_partners": safe("partners", lambda: get(f"/application/shops/{shop_id}/production-partners")),
        "readiness_states": safe("readiness", lambda: get(f"/application/shops/{shop_id}/readiness-state-definitions")),
        "listings_active": safe("active", lambda: get(f"/application/shops/{shop_id}/listings", state="active", limit=100)),
        "listings_draft": safe("draft", lambda: get(f"/application/shops/{shop_id}/listings", state="draft", limit=100)),
    }
    with open("shop_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    s = snapshot["shop"]
    print(f"Negozio: {s['shop_name']} (id {s['shop_id']})  {s['url']}")
    for k in ["title", "announcement", "sale_message", "digital_sale_message", "policy_additional", "icon_url_fullxfull"]:
        print(f"  {k:22}: {'(vuoto)' if not s.get(k) else str(s[k])[:80]}")
    for k in ["sections", "shipping_profiles", "return_policies", "production_partners",
              "listings_active", "listings_draft"]:
        v = snapshot[k]
        n = v.get("_error") or v.get("count", len(v.get("results", [])))
        print(f"  {k:22}: {n}")
    print("Dettagli completi in shop_snapshot.json")


if __name__ == "__main__":
    main()
