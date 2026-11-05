"""Pubblica su Etsy (tramite Printify) i prodotti in inserzioni/*.json e sistema l'inserzione Etsy.

Uso:
  python pubblica.py 04_toddler 07_body ...   (nomi dei file in inserzioni/, senza .json)
  python pubblica.py --tutti

Per ogni prodotto:
  1. pubblica da Printify (se non e' gia' su Etsy) e aspetta l'id dell'inserzione Etsy
  2. su Etsy: sezione del negozio, partner di produzione, rinnovo automatico
  3. carica la foto di ChatGPT (stampa/foto_etsy/<idea>.jpg) come SECONDA foto: la prima resta il mockup
     Printify, perché le regole Etsy sulle immagini (22/10/2026) non accettano foto AI come principale
  4. compila gli attributi Etsy (campo "attributi": occasione, materiale, colore...) usati nei filtri di ricerca
  5. limita il profilo di spedizione alla zona di produzione (Europa+UK, USA+Canada o entrambe per "usa_europa")
     e mette la spedizione USA gratis per i prodotti fatti negli USA
  6. video dell'inserzione (prassi: ogni inserzione ne ha uno), da strumenti_grafiche/video_etsy.py
I dati di pubblicazione stanno nel campo "etsy" del file inserzione (sezione, zona, foto).
"""
import json
import sys
import time
from pathlib import Path

import etsy_client as etsy
import printify_client as printify
sys.path.insert(0, str(Path(__file__).parent / "strumenti_grafiche"))
from video_etsy import video_inserzione  # noqa: E402

ROOT = Path(__file__).parent
PARTNER = {"europa": ["Print-on-demand partner in Europe"], "usa": ["Print-on-demand partner in the USA"],
           "usa_europa": ["Print-on-demand partner in the USA", "Print-on-demand partner in Europe"]}
EUROPA = set("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE "
             "GB CH NO IS LI AD MC SM VA GI IM JE GG AL BA ME MK RS KV MD UA FO AX".split())
ZONE = {"europa": EUROPA, "usa": {"US", "CA"}, "usa_europa": EUROPA | {"US", "CA"}}
# Spedizione gratuita negli USA (Etsy la premia nella ricerca americana): il costo e' incluso nel prezzo di
# tutti i prodotti fatti negli USA. Valori fissi in centesimi: (primo articolo, articoli successivi).
TARIFFE_FISSE = {"usa": {"US": (0, 0)}, "usa_europa": {"US": (0, 0)}}
# tariffe fisse in piu' per profilo (parola nel titolo del profilo Etsy): t-shirt, il Canada paga la differenza
TARIFFE_PROFILO = {"T-Shirt": {"CA": (474, 439)}}


def pubblica_printify(shop_id, pid):
    p = printify.get(f"/shops/{shop_id}/products/{pid}.json")
    if (p.get("external") or {}).get("id"):
        return p["external"]["id"]
    printify.request("POST", f"/shops/{shop_id}/products/{pid}/publish.json", json={
        "title": True, "description": True, "images": True, "variants": True, "tags": True,
        "keyFeatures": True, "shipping_template": True})
    for _ in range(36):  # fino a 6 minuti
        time.sleep(10)
        ext = printify.get(f"/shops/{shop_id}/products/{pid}.json").get("external") or {}
        if ext.get("id"):
            return ext["id"]
    raise SystemExit(f"Printify non ha ancora creato l'inserzione Etsy per {pid}")


def sistema_inserzione(shop_id, listing_id, cfg, sezioni, partner):
    etsy.request("PATCH", f"/application/shops/{shop_id}/listings/{listing_id}", data=[
        ("shop_section_id", sezioni[cfg["sezione"]]),
        ("should_auto_renew", "true"),
    ] + [("production_partner_ids", partner[n]) for n in PARTNER[cfg["zona"]]])


def carica_foto(shop_id, listing_id, foto, extra, caricate):
    """caricate = {file: listing_image_id} salvato nel file inserzione: cosi' non si ricarica mai due volte
    (Etsy azzera il testo alternativo quando si riordina, quindi non si puo' usare quello)."""
    url = f"/application/shops/{shop_id}/listings/{listing_id}/images"
    immagini = etsy.get(f"/application/listings/{listing_id}/images")["results"]
    esistenti = {i["listing_image_id"] for i in immagini}
    for percorso in [foto, *extra]:
        if caricate.get(percorso) not in esistenti:
            with open(ROOT / percorso, "rb") as f:
                r = etsy.request("POST", url, files={"image": (Path(percorso).name, f, "image/jpeg")})
            caricate[percorso] = r["listing_image_id"]
    # Regole Etsy sulle immagini (22/10/2026): la foto principale deve essere reale o il mockup autorizzato
    # del produttore. Ordine: 1 = primo mockup Printify, 2 = foto ChatGPT, poi dettaglio stampa / taglie /
    # scheda prodotto, infine gli altri mockup Printify (altri colori).
    immagini = sorted(etsy.get(f"/application/listings/{listing_id}/images")["results"], key=lambda i: i["rank"])
    per_id = {i["listing_image_id"]: i for i in immagini}
    mie = [per_id[caricate[p]] for p in [foto, *extra] if caricate.get(p) in per_id]
    printify_img = [i for i in immagini if i["listing_image_id"] not in set(caricate.values())]
    ordine = printify_img[:1] + mie + printify_img[1:]
    for rank, img in enumerate(ordine, start=1):
        if img["rank"] != rank:
            etsy.request("POST", url, data={"listing_image_id": img["listing_image_id"], "rank": rank})
    return f"{len(mie)} nostre foto dopo il mockup Printify"


def fissa_copertina(shop_id, listing_id):
    """Bug Etsy (visto 2 volte, 04/11/2026): dopo caricamenti e riordini l'API da' l'ordine giusto ma la copertina
    mostrata (Shop Manager, ricerca) resta l'ultima foto caricata/spostata, es. la scheda info. Rimettere la foto 1
    in posizione 1 come ULTIMA operazione sull'inserzione aggiorna la copertina."""
    prima = min(etsy.get(f"/application/listings/{listing_id}/images")["results"], key=lambda i: i["rank"])
    etsy.request("POST", f"/application/shops/{shop_id}/listings/{listing_id}/images",
                 data={"listing_image_id": prima["listing_image_id"], "rank": 1})
    return prima["listing_image_id"]


def applica_attributi(shop_id, listing_id, attributi):
    """Attributi Etsy (filtri di ricerca): {"Holiday": "Christmas", "Materials": ["Cotton"], ...}.
    I nomi sono quelli mostrati da Etsy (display_name) e i valori quelli della sua lista."""
    if not attributi:
        return []
    tid = etsy.get(f"/application/listings/{listing_id}")["taxonomy_id"]
    props = {p["display_name"]: p for p in etsy.get(f"/application/seller-taxonomy/nodes/{tid}/properties")["results"]}
    esiti = []
    for nome, valori in attributi.items():
        valori = valori if isinstance(valori, list) else [valori]
        p = props.get(nome)
        possibili = {v["name"]: v["value_id"] for v in (p or {}).get("possible_values", [])}
        if not p or any(v not in possibili for v in valori):
            esiti.append(f"{nome}: non disponibile")
            continue
        dati = [("value_ids", possibili[v]) for v in valori] + [("values", v) for v in valori]
        try:
            etsy.request("PUT", f"/application/shops/{shop_id}/listings/{listing_id}/properties/{p['property_id']}",
                         data=dati)
            esiti.append(f"{nome}={'/'.join(valori)}")
        except RuntimeError as e:  # es. attributo gia' usato dalle varianti
            esiti.append(f"{nome}: rifiutato ({str(e)[-80:]})")
    return esiti


def limita_spedizioni(shop_id, profile_id, zona):
    prof = etsy.get(f"/application/shops/{shop_id}/shipping-profiles/{profile_id}")
    tolte = []
    for d in prof["shipping_profile_destinations"]:
        paese = d.get("destination_country_iso")
        if paese not in ZONE[zona]:  # anche "resto del mondo" (paese vuoto)
            etsy.request("DELETE", f"/application/shops/{shop_id}/shipping-profiles/{profile_id}"
                                   f"/destinations/{d['shipping_profile_destination_id']}")
            tolte.append(paese or "resto del mondo")
        else:
            fisse = dict(TARIFFE_FISSE.get(zona, {}))
            for parola, t in TARIFFE_PROFILO.items():
                if parola in prof["title"]:
                    fisse.update(t)
            if paese not in fisse:
                continue
            primo, altri = fisse[paese]
            if (d["primary_cost"]["amount"], d["secondary_cost"]["amount"]) != (primo, altri):
                etsy.request("PUT", f"/application/shops/{shop_id}/shipping-profiles/{profile_id}"
                                    f"/destinations/{d['shipping_profile_destination_id']}",
                             data={"primary_cost": primo / 100, "secondary_cost": altri / 100,
                                   "destination_country_iso": paese})
    return prof["title"], tolte


def main():
    nomi = ([p.stem for p in sorted((ROOT / "inserzioni").glob("*.json"))] if "--tutti" in sys.argv
            else [a for a in sys.argv[1:] if not a.startswith("--")])
    pf_shop = printify.get_shop()["id"]
    shop_id, _ = etsy.get_shop_id()
    sezioni = {s["title"]: s["shop_section_id"] for s in etsy.get(f"/application/shops/{shop_id}/sections")["results"]}
    for nome in nomi:  # sezioni del negozio che mancano (es. "Scarves"): create al primo prodotto
        titolo = json.loads((ROOT / "inserzioni" / f"{nome}.json").read_text(encoding="utf-8"))["etsy"]["sezione"]
        if titolo not in sezioni:
            r = etsy.request("POST", f"/application/shops/{shop_id}/sections", data={"title": titolo})
            sezioni[titolo] = r["shop_section_id"]
            print(f"creata la sezione {titolo}")
    partner = {p["partner_name"]: p["production_partner_id"]
               for p in etsy.get(f"/application/shops/{shop_id}/production-partners")["results"]}
    profili = {}
    for nome in nomi:
        path = ROOT / "inserzioni" / f"{nome}.json"
        ins = json.loads(path.read_text(encoding="utf-8"))
        cfg = ins["etsy"]
        listing_id = pubblica_printify(pf_shop, ins["printify_product_id"])
        ins["etsy_listing_id"] = int(listing_id)
        sistema_inserzione(shop_id, listing_id, cfg, sezioni, partner)
        caricate = ins.setdefault("etsy_immagini", {})
        try:
            esito_foto = (carica_foto(shop_id, listing_id, cfg["foto"], cfg.get("foto_extra", []), caricate)
                          if cfg.get("foto") else "nessuna foto nostra (ancora da fare)")
        finally:  # salva subito gli id delle foto caricate, anche se qualcosa dopo va storto
            path.write_text(json.dumps(ins, indent=2, ensure_ascii=False), encoding="utf-8")
        esito_video = video_inserzione(shop_id, nome, ins)
        path.write_text(json.dumps(ins, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {esito_video}")
        attr = applica_attributi(shop_id, listing_id, cfg.get("attributi"))
        if attr:
            print(f"  attributi: {', '.join(attr)}")
        fissa_copertina(shop_id, listing_id)  # sempre per ultima, dopo foto e video
        l = etsy.get(f"/application/listings/{listing_id}")
        profili[l["shipping_profile_id"]] = cfg["zona"]
        print(f"{nome}: inserzione {listing_id} ({l['state']}) sezione {cfg['sezione']}, "
              f"partner {cfg['zona']}, foto {esito_foto}")
    for profile_id, zona in profili.items():
        titolo, tolte = limita_spedizioni(shop_id, profile_id, zona)
        print(f"Spedizioni '{titolo}': solo {zona}; tolte {len(tolte)} destinazioni {tolte}")


if __name__ == "__main__":
    main()
