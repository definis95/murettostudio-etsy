"""Controllo delle inserzioni Etsy dopo la pubblicazione (sola lettura: non modifica nulla).

Uso:
  python verifica.py 27a_body 27b_body ...   (nomi in inserzioni/, senza .json)
  python verifica.py --tutti

Per ogni inserzione controlla:
  - stato attivo
  - foto 1 = mockup Printify (regola Etsy: niente foto AI in copertina), poi foto ChatGPT e foto extra in ordine
  - nessun mockup Printify bianco/vuoto (successo con 24u)
  - video presente
  - attributi Etsy compilati come nel file inserzione
  - spedizioni solo nella zona di produzione, USA gratis per i prodotti fatti negli USA
  - testi: dichiarazione AI e nota sulle foto nella descrizione, 13 tag
  - file di stampa su Printify al 100% dell'area a scala 1 (= 300 DPI sul modello Printify)
La copertina MOSTRATA da Etsy non si legge dall'API (bug visto 2 volte): pubblica.py la fissa per ultima,
ma va comunque guardata nella pagina Inserzioni.
"""
import io
import json
import sys
from pathlib import Path

import requests
from PIL import Image, ImageStat

import etsy_client as etsy
import printify_client as printify
from pubblica import TARIFFE_FISSE, ZONE

ROOT = Path(__file__).parent


def mockup_vuoto(img):
    """True se la foto e' quasi tutta bianca e uniforme (mockup Printify senza prodotto)."""
    im = Image.open(io.BytesIO(requests.get(img["url_170x135"], timeout=60).content)).convert("L")
    st = ImageStat.Stat(im)
    return st.mean[0] > 245 and st.stddev[0] < 6


def controlla_foto(lid, ins, problemi):
    cfg = ins["etsy"]
    caricate = ins.get("etsy_immagini") or {}
    mie = set(caricate.values())
    imgs = sorted(etsy.get(f"/application/listings/{lid}/images")["results"], key=lambda i: i["rank"])
    if not imgs:
        problemi.append("nessuna foto")
        return
    if imgs[0]["listing_image_id"] in mie:
        problemi.append("foto 1 e' una foto nostra, non il mockup Printify")
    attese = [caricate.get(p) for p in [cfg.get("foto"), *cfg.get("foto_extra", [])] if p]
    if not cfg.get("foto"):
        problemi.append("manca la foto ambientata ChatGPT (etsy.foto)")
    presenti = [i["listing_image_id"] for i in imgs]
    mancano = [a for a in attese if a not in presenti]
    if mancano:
        problemi.append(f"{len(mancano)} foto nostre non caricate su Etsy")
    elif presenti[1:1 + len(attese)] != attese:
        problemi.append("ordine foto diverso da: mockup, foto ChatGPT, foto extra")
    vuoti = [i["rank"] for i in imgs if i["listing_image_id"] not in mie and mockup_vuoto(i)]
    if vuoti:
        problemi.append(f"mockup Printify bianchi/vuoti in posizione {vuoti}")


def controlla_attributi(shop_id, lid, attributi, problemi):
    if not attributi:
        problemi.append("nessun attributo Etsy nel file inserzione")
        return
    # l'inserzione usa nomi interni ("Material multi"), il file i nomi mostrati ("Materials"): confronto per id
    tid = etsy.get(f"/application/listings/{lid}")["taxonomy_id"]
    per_nome = {p["display_name"]: p["property_id"]
                for p in etsy.get(f"/application/seller-taxonomy/nodes/{tid}/properties")["results"]}
    impostati = {p["property_id"] for p in etsy.get(f"/application/shops/{shop_id}/listings/{lid}/properties")["results"]}
    for nome in attributi:
        if nome not in per_nome:
            problemi.append(f"attributo '{nome}' non esiste per questa categoria")
        elif per_nome[nome] not in impostati:
            problemi.append(f"attributo '{nome}' non impostato")


def controlla_spedizioni(shop_id, profile_id, zona, problemi):
    prof = etsy.get(f"/application/shops/{shop_id}/shipping-profiles/{profile_id}")
    fuori = [d.get("destination_country_iso") or "resto del mondo" for d in prof["shipping_profile_destinations"]
             if d.get("destination_country_iso") not in ZONE[zona]]
    if fuori:
        problemi.append(f"profilo '{prof['title']}' spedisce fuori zona {zona}: {fuori}")
    for paese, (primo, _) in TARIFFE_FISSE.get(zona, {}).items():
        for d in prof["shipping_profile_destinations"]:
            if d.get("destination_country_iso") == paese and d["primary_cost"]["amount"] != primo:
                problemi.append(f"spedizione {paese} non gratuita ({d['primary_cost']['amount'] / 100:.2f})")


def controlla_testi(l, problemi):
    desc = l.get("description", "")
    if "help of AI" not in desc:
        problemi.append("descrizione senza dichiarazione AI")
    if "Photos:" not in desc:
        problemi.append("descrizione senza nota sulle foto (Photos: ...)")
    if "\\n" in desc or "<br" in desc:
        problemi.append("descrizione con \\n o <br> scritti nel testo invece di veri a capo")
    if len(l.get("tags", [])) < 13:
        problemi.append(f"solo {len(l.get('tags', []))} tag su 13")


def controlla_stampa(pf_shop, pid, problemi, cache):
    prod = printify.get(f"/shops/{pf_shop}/products/{pid}.json")
    chiave = (prod["blueprint_id"], prod["print_provider_id"])
    if chiave not in cache:
        cache[chiave] = {v["id"]: v for v in printify.get(
            f"/catalog/blueprints/{chiave[0]}/print_providers/{chiave[1]}/variants.json")["variants"]}
    abilitati = {v["id"] for v in prod["variants"] if v["is_enabled"]}
    for pa in prod["print_areas"]:
        vids = [v for v in pa["variant_ids"] if v in abilitati]
        for ph in pa["placeholders"]:
            aree = [(q["width"], q["height"]) for v in vids for q in cache[chiave][v]["placeholders"]
                    if q["position"] == ph["position"]]
            if not aree:
                continue
            W = max(w for w, _ in aree)
            for im in ph["images"]:
                if im.get("type", "").startswith("text"):
                    continue
                dpi = 300 * im["width"] / (im["scale"] * W)
                if dpi < 294:
                    problemi.append(f"stampa {ph['position']} {im.get('name', '')}: {dpi:.0f} DPI sull'area Printify")


def main():
    # i PDF digitali (*_pdf.json) non hanno prodotto Printify ne' spedizioni da controllare
    nomi = ([p.stem for p in sorted((ROOT / "inserzioni").glob("*.json")) if not p.stem.endswith("_pdf")]
            if "--tutti" in sys.argv
            else [a for a in sys.argv[1:] if not a.startswith("--")])
    shop_id, _ = etsy.get_shop_id()
    pf_shop = printify.get_shop()["id"]
    cache, ok, ko = {}, 0, 0
    for nome in nomi:
        ins = json.loads((ROOT / "inserzioni" / f"{nome}.json").read_text(encoding="utf-8"))
        lid = ins.get("etsy_listing_id")
        if not lid:
            print(f"{nome}: non ancora su Etsy")
            continue
        problemi = []
        l = etsy.get(f"/application/listings/{lid}")
        if l["state"] != "active":
            problemi.append(f"stato {l['state']}")
        controlla_foto(lid, ins, problemi)
        video = {v["video_id"] for v in etsy.get(f"/application/listings/{lid}/videos")["results"]}
        if not video:
            problemi.append("nessun video")
        controlla_attributi(shop_id, lid, ins["etsy"].get("attributi"), problemi)
        controlla_spedizioni(shop_id, l["shipping_profile_id"], ins["etsy"]["zona"], problemi)
        controlla_testi(l, problemi)
        controlla_stampa(pf_shop, ins["printify_product_id"], problemi, cache)
        if problemi:
            ko += 1
            print(f"{nome} ({lid}): " + "; ".join(problemi))
        else:
            ok += 1
            print(f"{nome}: OK")
    print(f"\n{ok} OK, {ko} con problemi. Ricorda: la copertina mostrata da Etsy va guardata nella pagina Inserzioni.")


if __name__ == "__main__":
    main()
