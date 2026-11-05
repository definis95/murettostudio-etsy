"""Crea UNA VOLTA le schede (schede/<id>.html) dei prodotti che non ne hanno ancora una.
Le schede esistenti non vengono mai sovrascritte: dopo la creazione si modificano a mano."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "anteprime_printify" / "pagina"
S = P / "schede"
ALTO = ' class="alto"'


def img(src, dst, lato=900):
    im = Image.open(ROOT / src).convert("RGB")
    im.thumbnail((lato, lato))
    im.save(P / dst, quality=85)
    return dst


def fig(f, c, alto=False):
    cl = ALTO if alto else ""
    return f'      <figure><img{cl} src="{f}" alt="{c}"><figcaption>{c}</figcaption></figure>\n'


def box(id_, titolo, meta, figs, righe=None, nota=None):
    h = f'  <div class="box">\n    <h2>{id_} · {titolo}</h2>\n    <p class="meta">{meta}</p>\n'
    if figs:
        h += '    <div class="gal">\n' + "".join(figs) + '    </div>\n'
    if righe:
        h += '    <ul class="check">\n' + "".join(f"      <li>{r}</li>\n" for r in righe) + '    </ul>\n'
    if nota:
        h += f'    <p class="nota">{nota}</p>\n'
    return h + '  </div>\n'


def scrivi(nome, testo):
    f = S / f"{nome}.html"
    if f.exists():
        return
    f.write_text(testo, encoding="utf-8")
    print("creata", f.name)


def euro(c):
    return f"{c / 100:.2f} €".replace(".", ",")


COL = {"Red": "rosso", "Navy": "blu navy", "Black": "nero", "White": "bianco", "Pink": "rosa", "Natural": "naturale",
       "Classic Red": "rosso", "French Navy": "blu navy", "Light Blue": "celeste"}
VENDUTI = {
    "04_toddler": ("Santa's Little Helper – maglietta bimbo 2-6 anni", "04", "Printify Choice (USA) · USA + Canada, spedizione gratis USA"),
    "04_youth": ("Santa's Little Helper – maglietta ragazzo 6-16 anni", "04", "Printify Choice (USA) · USA + Canada, spedizione gratis USA"),
    "05_toddler": ("Most Likely To Eat Santa's Cookies – maglietta bimbo 2-6 anni", "05", "Printify Choice (USA) · USA + Canada, spedizione gratis USA"),
    "05_youth": ("Most Likely To Eat Santa's Cookies – maglietta ragazzo 6-16 anni", "05", "Printify Choice (USA) · USA + Canada, spedizione gratis USA"),
    "06_body": ("Dear Santa, I Can Explain – body neonato", "06", "Textildruck (Germania) · Europa + Regno Unito"),
    "07_body": ("Little But Fierce – body neonato", "07", "Textildruck (Germania) · Europa + Regno Unito"),
    "12_mug": ("Dear Santa, Define 'Good' – tazza", "12", "Repubblica Ceca · Europa + Regno Unito"),
    "13_mug": ("Christmas Movie Watching Club – tazza", "13", "Repubblica Ceca · Europa + Regno Unito"),
    "14_tote": ("North Pole Postal Service – borsa", "14", "Textildruck (Germania) · Europa + Regno Unito"),
    "15_tote": ("Merry & Bright – borsa", "15", "Textildruck (Germania) · Europa + Regno Unito"),
}
ATTESA = {"08": "Promoted to Big Sister 2027 – maglietta bimba", "09": "Promoted to Big Brother 2027 – maglietta bimbo",
          "10": "Little Meatball – body neonato", "16": "Buon Natale (moka e panettone) – borsa"}


def main():
    S.mkdir(exist_ok=True)
    for n, (t, idea, dove) in VENDUTI.items():
        d = json.load(open(ROOT / f"inserzioni/{n}.json", encoding="utf-8"))
        prezzi = " / ".join(euro(p) if k == "*" else f"{k} {euro(p)}" for k, p in d["variants"].items())
        col = ", ".join(COL.get(c, c) for c in d.get("colori") or [])
        figs = [fig(img(f"stampa/foto_etsy/{n}_printify.jpg", f"{n}_printify.jpg"), "Prima foto su Etsy (Printify)"),
                fig(img(f"stampa/foto_etsy/{idea}.jpg", f"{idea}_ambientata.jpg"), "Foto ambientata (ChatGPT)")]
        link = f'<a href="https://www.etsy.com/listing/{d["etsy_listing_id"]}">Apri l\'inserzione su Etsy</a>'
        righe = [f"<b>Prezzo:</b> {prezzi}"] + ([f"<b>Colori:</b> {col}"] if col else []) + [f"<b>Dove:</b> {dove}", link]
        if idea in ("04", "05"):
            righe.append("CPSIA (USA): in attesa dei documenti sull'inchiostro (SwiftPOD / Printify).")
        scrivi(n, box(n, t, '<span class="tag ok">in vendita su Etsy dal 1° novembre</span>', figs, righe))
    pr = {i["id"]: i for i in json.load(open(ROOT / "proposte/2026-11_natale_bambini/proposte.json", encoding="utf-8"))["idee"]}
    for k, t in ATTESA.items():
        i = pr[k]
        col = ", ".join(COL.get(c, c) for c in i.get("colori") or [])
        figs = [fig(img(f"proposte/2026-11_natale_bambini/{k}/mockup.png", f"{k}_mockup.jpg"), "Foto di prova (ChatGPT)"),
                fig(img(f"proposte/2026-11_natale_bambini/{k}/design.png", f"{k}_disegno.jpg"), "Disegno")]
        scrivi(k, box(k, t, '<span class="tag wait">in attesa di una tua decisione</span>', figs,
                      [f"<b>Prodotto:</b> {i['prodotto']}", f"<b>Colori:</b> {col}",
                       "Disegno pronto dal 1° novembre, non ancora su Printify: l'avevi messo in attesa. Dimmi se lo vuoi in vendita."]))
    p2 = {i["id"]: i for i in json.load(open(ROOT / "proposte/2026-11_natale_2/proposte.json", encoding="utf-8"))["idee"]}
    for k in ["19b", "19c", "19d", "19e"]:
        i = p2[k]
        figs = [fig(img(f"proposte/2026-11_natale_2/{k}/bozza.png", f"{k}_bozza.jpg"), "Bozza approvata come idea"),
                fig(img(f"stampa/{k}_1327/design.png", f"{k}_disegno.jpg"), "Disegno definitivo di ChatGPT"),
                fig(img(f"stampa/{k}_1327/dettaglio_100.jpg", f"{k}_dettaglio.jpg"), "Dettaglio a grandezza reale (30 × 19 cm)"),
                fig(img(f"stampa/{k}_1327/anteprima.jpg", f"{k}_file.jpg", 1400), "File di stampa intero (180 × 69 cm)", True)]
        scrivi(k, box(k, i["titolo"], 'Printify Choice (USA) · solo USA + Canada · <span class="tag wait">in lavorazione</span>', figs,
                      ["Sciarpa leggera 100% poliestere, 69 × 180 cm, stampata su un lato.",
                       "Prezzo proposto 42,90 € con spedizione gratis negli USA (costo 24,34 $ + spedizione 6,39 $): ti resta circa 7 €.",
                       "I motivi sono orientati per stare dritti quando la sciarpa pende dal collo."]))
    for k in ["21", "21b", "21c", "21d", "21e", "21f", "22"]:
        i = p2[k]
        righe = [f"<b>Prodotto:</b> {i['prodotto']}"]
        if k != "22":
            righe.append("Solo USA + Canada: in Europa la spedizione costerebbe 17,49 $. Per l'Europa c'è il PDF 22.")
        righe.append("Si fa dopo che avrai pubblicato i prodotti in bozza, come mi hai chiesto.")
        scrivi(k, box(k, i["titolo"], '<span class="tag ok">approvato</span> <span class="tag wait">da fare</span>',
                      [fig(img(f"proposte/2026-11_natale_2/{k}/bozza.png", f"{k}_bozza.jpg"), "Bozza approvata")], righe))


if __name__ == "__main__":
    main()
