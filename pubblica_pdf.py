"""PDF stampabili dei libri da colorare (idea 22): prodotti digitali Etsy, venduti in tutto il mondo.

I file digitali non passano da Printify: l'inserzione si crea direttamente su Etsy (tipo "download").

Uso:
  python pubblica_pdf.py anteprime 22_21 22_tutti ...   # foto dell'inserzione composte da copertine e pagine vere
  python pubblica_pdf.py bozza 22_21 ...                # crea la bozza Etsy (o la aggiorna): testi, foto, file PDF
  python pubblica_pdf.py attiva 22_21 ...               # pubblica la bozza (solo dopo l'ok di Dario)

Dati in inserzioni/<nome>_pdf.json: titolo, descrizione, tag, prezzo, libri, file, foto, sezione.
I PDF si fanno con: python strumenti_grafiche/libro_colorare.py pdf tutti 21 21b 21c 21d 21e 21f
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import etsy_client as etsy

ROOT = Path(__file__).parent
FONDO = (246, 241, 233)  # calce chiaro, come le schede
LATO = 2000


def leggi(nome):
    path = ROOT / "inserzioni" / f"{nome}_pdf.json"
    return path, json.loads(path.read_text(encoding="utf-8"))


def salva(path, ins):
    path.write_text(json.dumps(ins, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fronte(libro):
    cop = Image.open(ROOT / "stampa" / f"{libro}_2721" / "copertina_5175x3375.png").convert("RGB")
    meta = (cop.width + 1) // 2
    return cop.crop((cop.width - meta + 38, 38, cop.width - 38, cop.height - 38))  # senza abbondanza


def pagina(libro, n):
    p = Image.open(ROOT / "stampa" / f"{libro}_2721" / "pagine" / f"pagina_{n:02d}.png").convert("RGB")
    l, t = (p.width - 2550) // 2, (p.height - 3300) // 2
    return p.crop((l, t, l + 2550, t + 3300))  # foglio Letter, come nel PDF


def con_ombra(tela, im, xy, raggio=18):
    """Incolla im su tela con un'ombra morbida (impaginazione, nessun disegno)."""
    x, y = xy
    ombra = Image.new("L", (im.width + 4 * raggio, im.height + 4 * raggio), 0)
    ImageDraw.Draw(ombra).rectangle((2 * raggio, 2 * raggio, 2 * raggio + im.width, 2 * raggio + im.height), fill=90)
    ombra = ombra.filter(ImageFilter.GaussianBlur(raggio))
    tela.paste((60, 50, 40), (x - 2 * raggio + 10, y - 2 * raggio + 14), ombra)
    tela.paste(im, (x, y))


def scala_h(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


FASCIA = 190  # altezza della fascia di testo in alto nella foto principale
INCHIOSTRO = (43, 37, 35)  # antracite delle schede


def fascia(tela, testo):
    """Riga di testo in alto (composta dal codice, come l'etichetta dei libri): dice subito che e' un PDF."""
    from PIL import ImageFont
    dr = ImageDraw.Draw(tela)
    for corpo in range(66, 40, -2):  # la riga deve stare in 1800 px (margini di 100 px)
        f = ImageFont.truetype(str(ROOT / "fonts" / "Jost_wght.ttf"), corpo)
        f.set_variation_by_axes([560])
        if dr.textlength(testo, font=f) <= LATO - 200:
            break
    dr.text((LATO / 2, FASCIA / 2 + 20), testo, font=f, fill=INCHIOSTRO, anchor="mm")


def griglia(immagini, colonne, margine=40, spazio=24, bordo=True, tela=None, alto=0):
    tela = tela or Image.new("RGB", (LATO, LATO), FONDO)
    alt = LATO - alto  # altezza disponibile sotto l'eventuale fascia
    righe = (len(immagini) + colonne - 1) // colonne
    w = (LATO - 2 * margine - (colonne - 1) * spazio) // colonne
    h = round(w * immagini[0].height / immagini[0].width)
    if righe * h + (righe - 1) * spazio > alt - 2 * margine:
        h = (alt - 2 * margine - (righe - 1) * spazio) // righe
        w = round(h * immagini[0].width / immagini[0].height)
    tot_w, tot_h = colonne * w + (colonne - 1) * spazio, righe * h + (righe - 1) * spazio
    x0, y0 = (LATO - tot_w) // 2, alto + (alt - tot_h) // 2
    for i, im in enumerate(immagini):
        x, y = x0 + (i % colonne) * (w + spazio), y0 + (i // colonne) * (h + spazio)
        im = im.resize((w, h), Image.LANCZOS)
        if bordo:
            ImageDraw.Draw(im).rectangle((0, 0, w - 1, h - 1), outline=(200, 192, 182), width=2)
        con_ombra(tela, im, (x, y), raggio=8)
    return tela


def anteprime(nome):
    path, ins = leggi(nome)
    out = ROOT / "stampa" / "22_pdf" / "foto"
    out.mkdir(parents=True, exist_ok=True)
    libri = ins["libri"]
    foto = []
    if len(libri) == 1:
        libro = libri[0]
        tela = Image.new("RGB", (LATO, LATO), FONDO)
        # fascia di testo in alto; sotto: copertina a sinistra, due pagine intere una sopra l'altra a destra,
        # gruppo centrato con margini uguali
        fascia(tela, "PRINTABLE PDF  ·  24 PAGES  ·  INSTANT DOWNLOAD")
        cop = scala_h(fronte(libro), 1480)
        a, b = (scala_h(pagina(libro, n), 770) for n in ins["pagine_vetrina"])  # 2 x 770 + 80 di spazio
        spazio = 70
        x = (LATO - (cop.width + spazio + a.width)) // 2
        y = FASCIA + (LATO - FASCIA - cop.height) // 2
        con_ombra(tela, cop, (x, y))
        xp = x + cop.width + spazio
        con_ombra(tela, a, (xp, y - 70))
        con_ombra(tela, b, (xp, y + cop.height + 70 - b.height))
        f1 = out / f"{nome}_1.jpg"
        tela.save(f1, quality=94, subsampling=0)
        f2 = out / f"{nome}_2.jpg"
        griglia([pagina(libro, n) for n in range(1, 25)], 6).save(f2, quality=94, subsampling=0)
        foto = [f1, f2]
    else:
        f1 = out / f"{nome}_1.jpg"
        tela = Image.new("RGB", (LATO, LATO), FONDO)
        fascia(tela, f"{len(libri)} PRINTABLE PDF BOOKS  ·  {24 * len(libri)} PAGES  ·  INSTANT DOWNLOAD")
        griglia([fronte(l) for l in libri], 3, margine=60, spazio=50, bordo=False, tela=tela, alto=FASCIA - 20
                ).save(f1, quality=94, subsampling=0)
        f2 = out / f"{nome}_2.jpg"
        griglia([pagina(l, n) for l in libri for n in (2, 6, 11, 18)], 6).save(f2, quality=94, subsampling=0)
        foto = [f1, f2]
    ins["foto"] = [str(f.relative_to(ROOT)).replace("\\", "/") for f in foto] + ins.get("foto_extra", [])
    salva(path, ins)
    print(f"{nome}: anteprime {[f.name for f in foto]}")


def bozza(nome, shop_id, sezioni):
    path, ins = leggi(nome)
    dati = {"title": ins["titolo"], "description": ins["descrizione"], "price": ins["prezzo"],
            "quantity": 999, "who_made": "i_did", "when_made": "made_to_order", "taxonomy_id": 339,
            "type": "download", "is_supply": "false", "should_auto_renew": "true",
            "shop_section_id": sezioni[ins["sezione"]]}
    tag = [("tags", ",".join(ins["tag"]))]  # ripetendo "tags" Etsy tiene solo l'ultima
    lid = ins.get("etsy_listing_id")
    if lid:
        etsy.request("PATCH", f"/application/shops/{shop_id}/listings/{lid}",
                     data=[(k, v) for k, v in dati.items() if k not in ("quantity", "type", "price")] + tag)
        # su un'inserzione esistente il prezzo si cambia solo dall'inventario (il PATCH lo ignora)
        inv = etsy.get(f"/application/listings/{lid}/inventory")
        prodotti = [{"sku": p.get("sku") or "", "property_values": p.get("property_values", []),
                     "offerings": [{"price": ins["prezzo"], "quantity": o["quantity"], "is_enabled": o["is_enabled"]}
                                   for o in p["offerings"]]} for p in inv["products"]]
        etsy.request("PUT", f"/application/listings/{lid}/inventory", json={"products": prodotti})
    else:
        r = etsy.request("POST", f"/application/shops/{shop_id}/listings", data=list(dati.items()) + tag)
        lid = ins["etsy_listing_id"] = r["listing_id"]
        salva(path, ins)
    # foto: nell'ordine del file, ognuna una volta sola (id salvati come per le altre inserzioni)
    caricate = ins.setdefault("etsy_immagini", {})
    esistenti = {i["listing_image_id"] for i in etsy.get(f"/application/listings/{lid}/images")["results"]}
    for rank, f in enumerate(ins["foto"], start=1):
        if caricate.get(f) not in esistenti:
            with open(ROOT / f, "rb") as fh:
                r = etsy.request("POST", f"/application/shops/{shop_id}/listings/{lid}/images",
                                 files={"image": (Path(f).name, fh, "image/jpeg")}, data={"rank": rank})
            caricate[f] = r["listing_image_id"]
            salva(path, ins)
    # file digitali
    caricati = ins.setdefault("etsy_file", {})
    presenti = {f["listing_file_id"] for f in etsy.get(f"/application/shops/{shop_id}/listings/{lid}/files")["results"]}
    for rank, f in enumerate(ins["file"], start=1):
        if caricati.get(f) not in presenti:
            with open(ROOT / f, "rb") as fh:
                r = etsy.request("POST", f"/application/shops/{shop_id}/listings/{lid}/files",
                                 files={"file": (Path(f).name, fh, "application/pdf")},
                                 data={"name": Path(f).name, "rank": rank})
            caricati[f] = r["listing_file_id"]
            salva(path, ins)
    # copertina: rimette la prima foto in posizione 1 per ultima (bug Etsy, vedi pubblica.fissa_copertina)
    etsy.request("POST", f"/application/shops/{shop_id}/listings/{lid}/images",
                 data={"listing_image_id": caricate[ins["foto"][0]], "rank": 1})
    l = etsy.get(f"/application/listings/{lid}")
    print(f"{nome}: bozza {lid} ({l['state']}), {len(ins['foto'])} foto, {len(ins['file'])} file, "
          f"prezzo {l['price']['amount'] / l['price']['divisor']:.2f} {l['price']['currency_code']}")


def attiva(nome, shop_id):
    path, ins = leggi(nome)
    lid = ins["etsy_listing_id"]
    etsy.request("PATCH", f"/application/shops/{shop_id}/listings/{lid}", data={"state": "active"})
    print(f"{nome}: {etsy.get(f'/application/listings/{lid}')['state']} https://www.etsy.com/listing/{lid}")


def main():
    cmd, *nomi = sys.argv[1:]
    if cmd == "anteprime":
        for n in nomi:
            anteprime(n)
        return
    shop_id, _ = etsy.get_shop_id()
    if cmd == "bozza":
        sezioni = {s["title"]: s["shop_section_id"]
                   for s in etsy.get(f"/application/shops/{shop_id}/sections")["results"]}
        for n in nomi:
            titolo = leggi(n)[1]["sezione"]
            if titolo not in sezioni:
                sezioni[titolo] = etsy.request("POST", f"/application/shops/{shop_id}/sections",
                                               data={"title": titolo})["shop_section_id"]
                print(f"creata la sezione {titolo}")
            bozza(n, shop_id, sezioni)
    elif cmd == "attiva":
        for n in nomi:
            attiva(n, shop_id)


if __name__ == "__main__":
    main()
