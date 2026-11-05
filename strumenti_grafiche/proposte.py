"""Proposte di prodotto da far validare a Dario prima di realizzarle.

Due fasi:
  1. genera   -> per ogni idea UNA bozza veloce (bozza.png: il prodotto con il disegno sopra),
                 modello rapido, nessun controllo; tutte raccolte in index.html per Dario.
  2. realizza -> solo per le idee APPROVATE: grafica di stampa definitiva (design.png, trasparente,
                 guidata e controllata da Astra) e foto prodotto per Etsy (mockup.png).

Uso:
  python strumenti_grafiche/proposte.py genera   proposte/<cartella>/proposte.json [--solo 01,03] [--paralleli 4]
  python strumenti_grafiche/proposte.py approva  proposte/<cartella>/proposte.json 01 03
  python strumenti_grafiche/proposte.py scarta   proposte/<cartella>/proposte.json 02
  python strumenti_grafiche/proposte.py realizza proposte/<cartella>/proposte.json [--paralleli 2]
  python strumenti_grafiche/proposte.py pagina   proposte/<cartella>/proposte.json
"""
import argparse
import html
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chatgpt_bridge import genera  # noqa: E402

REGOLE = {
    "capo": """PRINT RULES (direct-to-garment print on a cotton garment):
- Single compact composition, centred, nothing touching the image edges, generous empty margin.
- Clean bold shapes and lettering; no line or detail thinner than 2 mm at about 20 cm print width.
- Flat colours with minimal soft shading; no photo effects, glitter, glow, drop shadows or textures.
- No background, no ground shadow, no sticker border or white outline around the design.
- Maximum 6 colours. No extra text, no watermark, no signature.""",
    "ornamento": """PRINT RULES (sublimation print on a round 7.5 cm ceramic Christmas ornament):
- The image is square but will be cut to a CIRCLE: keep all text and key elements inside the central
  circle, at least 10% away from it; the background colour must fill the whole square edge to edge.
- Text large and bold enough to read at 7.5 cm; no hairline details.
- No border ring, no hole or ribbon drawn, no extra text, no watermark, no signature.""",
    "tazza": """PRINT RULES (sublimation print on a white ceramic mug, wrap area about 20 x 8.5 cm):
- Wide landscape composition on a WHITE background (white = unprinted mug), main design centred so it
  shows on the side facing a right-handed drinker; nothing important at the far left/right edges
  (they meet under the handle).
- Bold readable shapes and lettering; no hairlines. No extra text, no watermark, no signature.""",
    "borsa": """PRINT RULES (direct-to-garment print on a DARK organic cotton tote bag: black, red or navy):
- Use ONLY light colours (cream, white, gold, light green, light pink); no black, no dark navy, no red
  lines, so it reads on all three bag colours.
- Single compact composition, centred, nothing touching the edges; no line thinner than 2 mm at 30 cm.
- No background, no shadow, no sticker border. No extra text, no watermark, no signature.""",
    "berretto": """EMBROIDERY RULES (machine embroidery on the cuff of a knit beanie, area about 12 x 4 cm):
- Flat artwork for digitising: solid flat colour areas only, maximum 4 thread colours, no gradients, no
  shading, no texture, no thread effect drawn in.
- Every shape and line at least 1.5 mm wide at final size; letters at least 6 mm tall; no tiny gaps.
- Single compact composition, centred, wide landscape; no background, no outline border around it.
- Readable on dark AND light beanies. No extra text, no watermark, no signature.""",
    "berretto_stampa": """PRINT RULES (DTF print on the front of a dark cotton beanie: black, navy, graphite; about 9 x 5.5 cm):
- Use ONLY light colours that read on dark fabric; no black, no dark navy.
- Clean flat shapes; no line thinner than 1 mm at 9 cm width (thicken stems, rays and outlines).
- Single compact composition, centred; no background, no shadow, no border. No extra text, no watermark.""",
    "calza": """PRINT RULES (sublimation print on the front of a Christmas stocking, tall boot shape):
- The background colour must fill the WHOLE image edge to edge (the stocking shape is cut from it).
- Keep text and the main subject in the upper-central part (the leg of the stocking), at least 12% away
  from every edge; the lower part and the sides only carry background and small decorations.
- Bold readable lettering; no hairlines. No extra text, no watermark, no signature.""",
    "carta": """PRINT RULES (pattern tile for gift wrapping paper, repeated side by side many times):
- Solid flat background colour filling the whole image edge to edge.
- Motifs evenly scattered, every motif fully inside the image and at least 4% away from all edges
  (nothing cut by the edges), so the tile repeats with no visible seam.
- Flat illustration, crisp edges. No text, no watermark, no signature.""",
    "libro": """PRINT RULES (front cover of a US letter children's coloring book, portrait):
- The background illustration fills the WHOLE image edge to edge.
- Title large and readable, in the upper third, at least 6% away from every edge; no other text.
- Bright, friendly, thick outlines. No barcode, no author name, no watermark, no signature.""",
}
POSIZIONI = {
    "capo": "front print, centred on the chest, following the fabric folds",
    "ornamento": "printed on the round face, covering it edge to edge",
    "tazza": "printed on the side of the mug facing the camera, wrapping with the curve",
    "borsa": "front print, centred on the bag, following the canvas texture",
    "berretto": "small flat embroidered patch-style design on the front of the folded cuff, with visible thread texture",
    "berretto_stampa": "small flat print on the front of the beanie, following the knit texture",
    "sciarpa": "all-over printed pattern on the lightweight scarf fabric",
    "calza": "all-over printed design on the front of the faux suede stocking",
    "libro": "printed on the soft cover, with a couple of open interior coloring pages visible",
    "digitale": "shown as printed sheets of paper, the way the buyer prints them at home",
    "carta": "all-over repeating pattern printed on the wrapping paper",
    "adesivi": "printed on a sticker sheet with several die-cut stickers",
}

BOZZA = """Quick concept draft for a product idea (it only needs to convey the idea; it is not the final art).
Simple product photo: {mockup}
On the product ({posizione}) show this artwork:
{design}"""

MODELLO_BOZZA = ("gpt-6-luna", "low")

MOCKUP = """Use case: product-mockup. Asset: Etsy listing photo to show the finished product.
Photorealistic product photo: {mockup}
The attached image is the exact artwork. Reproduce it faithfully as a real print on the product
({posizione}), with correct proportions; do not redraw, restyle or translate it, keep every word identical.
Do not add any other text, logo or watermark. Soft natural daylight, sharp focus on the print, square format."""


def carica(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def salva(path, dati):
    Path(path).write_text(json.dumps(dati, indent=2, ensure_ascii=False), encoding="utf-8")


def posizione(idea):
    return POSIZIONI[idea["tipo"]]


def bozza_idea(cartella, idea):
    """Una sola immagine veloce: il prodotto con il disegno sopra."""
    out = cartella / idea["id"] / "bozza.png"
    if out.exists():
        return {}
    brief = BOZZA.format(mockup=idea["mockup"].strip(), posizione=posizione(idea), design=idea["brief_design"].strip())
    modello, impegno = MODELLO_BOZZA
    genera(brief, out, "quadrato", trasparente=False, modello=modello, impegno=impegno, controllo=False)
    return {}


def realizza_idea(cartella, idea):
    """Lavoro completo (solo idee approvate): grafica di stampa controllata da Astra + foto prodotto."""
    note = {}
    base = cartella / idea["id"]
    design = base / "design.png"
    if not design.exists():
        brief = idea["brief_design"].strip() + "\n\n" + REGOLE[idea["tipo"]]
        rif = [base / "bozza.png"] if (base / "bozza.png").exists() else []
        _, note["design"] = genera(brief, design, idea.get("formato", "quadrato"),
                                   trasparente=idea["tipo"] in ("capo", "borsa", "berretto", "berretto_stampa"),
                                   riferimenti=rif,
                                   uso_riferimenti="the approved concept draft: keep its idea, character and "
                                                   "layout, but produce clean final print artwork only "
                                                   "(no garment, no photo)")
    mockup = base / "mockup.png"
    if not mockup.exists():
        brief = MOCKUP.format(mockup=idea["mockup"].strip(), posizione=posizione(idea))
        rif = riferimento_mockup(design, idea)
        try:
            _, note["mockup"] = genera(brief, mockup, "quadrato", trasparente=False, riferimenti=[rif],
                                       uso_riferimenti="it is the artwork to print on the product; the flat "
                                                       "colour around it is the product colour, not part of the print")
        finally:
            if rif != design:
                rif.unlink(missing_ok=True)
    return note


# colore del capo su cui appoggiare il disegno trasparente quando lo si passa a ChatGPT per la foto
COLORI_CAPO = {"white": "FFFFFF", "natural": "F3EBDD", "black": "111111", "navy": "1E2D50", "red": "B3202A",
               "light blue": "A8C8E6", "pink": "EBA9BB", "olive": "5B5E3A", "graphite": "4A4A4D",
               "heather grey": "B5B5B5", "dark grey": "4A4A4D"}


def riferimento_mockup(design, idea):
    """I PNG trasparenti di ChatGPT hanno colori sfumati nascosti sotto i pixel trasparenti: chi ignora
    la trasparenza li vede come un riquadro sfocato. Per la foto si passa il disegno pulito (come in
    prepara_stampa) appoggiato sul colore del capo."""
    from PIL import Image
    im = Image.open(design)
    if im.mode != "RGBA":
        return design
    a = im.getchannel("A").point(lambda x: 0 if x <= 8 else 255 if x >= 245 else x)
    im.putalpha(a)
    colore = COLORI_CAPO.get(idea["colori"][0].lower(), "FFFFFF")
    fondo = Image.new("RGBA", im.size, tuple(int(colore[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    fondo.alpha_composite(im)
    out = design.with_name("riferimento_mockup.png")
    fondo.convert("RGB").save(out)
    return out


def esegui(path, funzione, filtro, paralleli, nuovo_stato=None):
    dati = carica(path)
    cartella = Path(path).parent
    idee = [i for i in dati["idee"] if filtro(i)]
    print(f"{len(idee)} idee da lavorare ({paralleli} in parallelo)...")
    with ThreadPoolExecutor(paralleli) as ex:
        futuri = {ex.submit(funzione, cartella, i): i for i in idee}
        for f in as_completed(futuri):
            idea = futuri[f]
            try:
                idea.setdefault("note_qualita", {}).update(f.result())
                idea.pop("errore", None)
                if nuovo_stato:
                    idea["stato"] = nuovo_stato
                print(f"  {idea['id']} {idea['titolo']}: pronto")
            except BaseException as e:  # un'idea fallita non blocca le altre
                idea["errore"] = str(e)[:300]
                print(f"  {idea['id']} {idea['titolo']}: ERRORE {str(e)[:200]}")
    # rilegge il file (puo' essere stato modificato nel frattempo) e aggiorna solo i campi toccati qui
    attuale = carica(path)
    lavorate = {i["id"]: i for i in idee}
    for i in attuale["idee"]:
        if i["id"] in lavorate:
            nuova = lavorate[i["id"]]
            i["note_qualita"] = nuova.get("note_qualita", {})
            i.pop("errore", None)
            if nuova.get("errore"):
                i["errore"] = nuova["errore"]
            if nuovo_stato and not nuova.get("errore"):
                i["stato"] = nuovo_stato
    salva(path, attuale)
    cmd_pagina(path)


def cmd_stato(path, ids, stato):
    dati = carica(path)
    for i in dati["idee"]:
        if i["id"] in ids:
            i["stato"] = stato
    salva(path, dati)
    cmd_pagina(path)


ETICHETTE = {"proposta": ("Da valutare", "#8a6d1f"), "approvata": ("Approvata", "#2e7d4f"),
             "scartata": ("Scartata", "#9a3b3b"), "realizzata": ("Realizzata", "#2b5d8a")}


def cmd_pagina(path):
    dati = carica(path)
    cartella = Path(path).parent
    schede = []
    for i in dati["idee"]:
        e = html.escape
        etichetta, colore = ETICHETTE[i["stato"]]
        mock = next((f"{i['id']}/{n}" for n in ("mockup.png", "bozza.png") if (cartella / i["id"] / n).exists()), "")
        des = f"{i['id']}/design.png" if (cartella / i["id"] / "design.png").exists() else ""
        img = f'<img class="mock" src="{mock}">' if mock else '<div class="vuoto">immagine non ancora generata</div>'
        mini = f'<img class="design" src="{des}" title="grafica di stampa">' if des else ""
        errore = f'<p class="err">Errore: {e(i["errore"])}</p>' if i.get("errore") else ""
        schede.append(f"""
<article>
  {img}
  <div class="testo">
    <div class="riga"><span class="num">{e(i['id'])}</span><span class="stato" style="background:{colore}">{etichetta}</span>
      <span class="coll">{e(i['collezione'])}</span></div>
    <h2>{e(i['titolo'])}</h2>
    <p class="prod">{e(i['prodotto'])}<br><span>Colori: {e(', '.join(i['colori']))}</span></p>
    <p>{e(i['perche'])}</p>
    {mini}{errore}
  </div>
</article>""")
    pagina = f"""<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">
<title>{html.escape(dati['titolo'])}</title>
<style>
body{{font-family:system-ui,Segoe UI,sans-serif;background:#f4f1ec;color:#222;margin:0;padding:32px}}
h1{{margin:0 0 6px}} .sotto{{color:#666;margin:0 0 28px}}
.griglia{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:24px}}
article{{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 2px 10px #0001}}
.mock{{width:100%;display:block;aspect-ratio:1;object-fit:cover}}
.vuoto{{aspect-ratio:1;display:grid;place-items:center;color:#999;background:#eee}}
.testo{{padding:16px 18px 20px;position:relative}}
.riga{{display:flex;gap:8px;align-items:center;font-size:13px}}
.num{{font-weight:700;font-size:18px}} .stato{{color:#fff;border-radius:20px;padding:2px 10px}}
.coll{{color:#777}} h2{{font-size:19px;margin:10px 0 6px}}
.prod{{font-size:14px;color:#444}} .prod span{{color:#777}} p{{font-size:14px;line-height:1.45}}
.design{{width:90px;height:90px;object-fit:contain;background:repeating-conic-gradient(#ddd 0 25%,#fff 0 50%) 0 0/16px 16px;border-radius:8px;border:1px solid #ddd}}
.err{{color:#9a3b3b}}
</style></head><body>
<h1>{html.escape(dati['titolo'])}</h1>
<p class="sotto">{html.escape(dati.get('sottotitolo', ''))}</p>
<div class="griglia">{''.join(schede)}</div>
</body></html>"""
    out = cartella / "index.html"
    out.write_text(pagina, encoding="utf-8")
    print(f"Pagina aggiornata: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("comando", choices=["genera", "approva", "scarta", "realizza", "pagina"])
    ap.add_argument("file")
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--solo", default="")
    ap.add_argument("--paralleli", type=int, default=0)
    a = ap.parse_args()
    solo = {s for s in a.solo.split(",") if s}
    if a.comando == "genera":
        esegui(a.file, bozza_idea, lambda i: i["stato"] == "proposta" and (not solo or i["id"] in solo),
               a.paralleli or 4)
    elif a.comando == "realizza":
        esegui(a.file, realizza_idea, lambda i: i["stato"] == "approvata" and (not solo or i["id"] in solo),
               a.paralleli or 2, nuovo_stato="realizzata")
    elif a.comando == "pagina":
        cmd_pagina(a.file)
    else:
        cmd_stato(a.file, set(a.ids), "approvata" if a.comando == "approva" else "scartata")


if __name__ == "__main__":
    main()
