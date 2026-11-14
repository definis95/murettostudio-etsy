"""Date limite di Natale sulle inserzioni Etsy online e nell'annuncio del negozio.

Uso:
  python natale.py              anteprima: mostra il blocco che andrebbe in cima a ogni descrizione
  python natale.py --applica    scrive i blocchi su Etsy e aggiorna l'annuncio del negozio
  python natale.py --togli      dopo Natale: toglie i blocchi e rimette l'annuncio normale

Le date sono quelle di Printify (pagina "Network fulfillment status", cut-off per consegna entro il 24/12),
anticipate di MARGINE giorni perche' a dicembre i corrieri ritardano. Quando una data e' passata, rilanciando
lo script con --applica quella riga diventa "orders placed now may arrive after Christmas".
Il blocco va in cima alla descrizione e comincia sempre con INIZIO: rilanciare lo script lo sostituisce.
"""
import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import etsy_client as etsy

ROOT = Path(__file__).parent
MARGINE = 3
INIZIO = "CHRISTMAS DELIVERY"
# Printify, aggiornamento del 10/11/2026: data limite per stampatore e destinazione (USA = spedizione Standard)
D = lambda m, g: date(2026, m, g)  # noqa: E731
CUTOFF = {
    99: {"US": D(12, 9), "CA": D(12, 3), "EU": D(12, 8), "UK": D(12, 10)},    # Printify Choice
    39: {"US": D(12, 9), "CA": D(12, 3), "EU": D(11, 27), "UK": D(11, 27)},   # SwiftPOD
    410: {"US": D(12, 9), "CA": D(12, 8), "EU": D(12, 4), "UK": D(12, 9)},    # Printful
    217: {"US": D(12, 9), "CA": D(11, 27), "EU": D(11, 20), "UK": D(11, 20)}, # Fulfill Engine
    26: {"US": D(11, 25), "CA": D(11, 25), "EU": D(12, 9), "UK": D(12, 2)},   # Textildruck Europa
    30: {"US": D(11, 20), "CA": D(11, 20), "EU": D(12, 7), "UK": D(11, 27)},  # OPT OnDemand
    72: {"US": D(11, 18), "CA": D(11, 23), "EU": D(11, 27), "UK": D(12, 14)}, # Print Clever (UK Standard)
    69: {"US": D(12, 8), "CA": D(11, 27), "EU": D(12, 4), "UK": D(12, 9)},    # Prodigi
    # District Photo (libri da colorare): la tabella 2026 di Printify non era leggibile (14/11); date prudenti
    # stimate da 10 giorni di produzione + spedizione. Da verificare in Printify -> holiday order deadlines.
    28: {"US": D(12, 5), "CA": D(12, 1), "EU": D(11, 25), "UK": D(11, 25)},
}
DESTINAZIONI = {"usa": ["US", "CA"], "europa": ["EU", "UK"], "usa_europa": ["US", "CA", "EU", "UK"]}
NOMI = {"US": "US", "CA": "Canada", "EU": "Europe", "UK": "UK"}
# annuncio del negozio: l'ultimo paragrafo normale, sostituito a Natale da un paragrafo che comincia con INIZIO
ANNUNCIO_NORMALE = "Please check the estimated delivery date at checkout and order early for the holidays."


MESI = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]  # in chiaro: %B dipende dalla lingua del sistema


def giorno(d):
    return f"{MESI[d.month - 1]} {d.day}"


def limite_cliente(provider, dest):
    return CUTOFF[provider][dest] - timedelta(days=MARGINE)


def annuncio_natale(limiti, oggi):
    prossimi = sorted(d for d in limiti if d >= oggi)
    testo = f"{INIZIO}: every listing shows the last day to order for delivery by December 24."
    if prossimi:
        return f"{testo} The next one is {giorno(prossimi[0])}, so please order early!"
    return f"{testo} Orders placed now may arrive after Christmas."


def blocco(provider, zona, oggi):
    righe = [f"{INIZIO} - order by these dates to receive your order by December 24:"]
    for dest in DESTINAZIONI[zona]:
        limite = limite_cliente(provider, dest)
        quando = (giorno(limite) if oggi <= limite
                  else "orders placed now may arrive after Christmas")
        righe.append(f"- {NOMI[dest]}: {quando}")
    return "\n".join(righe)


def senza_blocco(desc):
    """Toglie il blocco di Natale in cima (fino alla prima riga vuota), se c'e'."""
    if desc.startswith(INIZIO):
        return re.split(r"\n\s*\n", desc, maxsplit=1)[1] if re.search(r"\n\s*\n", desc) else ""
    return desc


def main():
    applica, togli = "--applica" in sys.argv, "--togli" in sys.argv
    oggi = date.today()
    print(f"=== {oggi}")
    shop_id, shop = etsy.get_shop_id()
    limiti = []
    for path in sorted((ROOT / "inserzioni").glob("*.json")):
        ins = json.loads(path.read_text(encoding="utf-8"))
        lid = ins.get("etsy_listing_id")
        if not lid:
            continue
        if ins["print_provider_id"] not in CUTOFF:  # stampatore nuovo: aggiungere le sue date in CUTOFF
            print(f"ATTENZIONE: {path.stem} saltata, stampatore {ins['print_provider_id']} senza date in CUTOFF")
            continue
        limiti += [limite_cliente(ins["print_provider_id"], d) for d in DESTINAZIONI[ins["etsy"]["zona"]]]
        # Etsy restituisce la descrizione con le entita' HTML (&quot; &#39;): vanno tolte prima di riscriverla
        attuale = html.unescape(etsy.get(f"/application/listings/{lid}")["description"])
        base = senza_blocco(attuale)
        nuovo = blocco(ins["print_provider_id"], ins["etsy"]["zona"], oggi)
        desc = base if togli else f"{nuovo}\n\n{base}"
        if not applica and not togli:
            print(f"--- {path.stem} ({lid})\n{nuovo}\n")
            continue
        if desc != attuale:
            etsy.request("PATCH", f"/application/shops/{shop_id}/listings/{lid}", data={"description": desc})
            print(f"{path.stem}: {'blocco tolto' if togli else 'aggiornata'}")
    if applica or togli:
        annuncio = html.unescape(shop.get("announcement") or "")
        nuovo = ANNUNCIO_NORMALE if togli else annuncio_natale(limiti, oggi)
        paragrafo = re.compile(re.escape(INIZIO) + r":[^\n]*|" + re.escape(ANNUNCIO_NORMALE))
        if not paragrafo.search(annuncio):
            print("ATTENZIONE: annuncio diverso dal previsto, non toccato:\n" + annuncio)
        elif paragrafo.sub(nuovo, annuncio, count=1) != annuncio:
            etsy.request("PUT", f"/application/shops/{shop_id}",
                         data={"announcement": paragrafo.sub(nuovo, annuncio, count=1)})
            print(f"annuncio del negozio: {nuovo}")


if __name__ == "__main__":
    main()
