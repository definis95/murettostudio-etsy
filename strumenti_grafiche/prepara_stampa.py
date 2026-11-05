"""Adatta un'immagine di ChatGPT all'area di stampa reale di un prodotto Printify.

Uso:
  python strumenti_grafiche/prepara_stampa.py IMMAGINE --blueprint 12 --provider 29 [--posizione front]
         [--allinea alto|centro] [--margine 0.9] [--colori 000000,ffffff,1e2d50] [--ai-upscale]

Cosa fa:
  1. legge da Printify l'area di stampa della taglia piu' grande (Printify riscala sulle altre;
     --tutte-le-taglie per un file per ogni area diversa)
  2. pulisce la trasparenza (niente aloni semi-trasparenti che in stampa diventano sbiaditi)
  3. ritaglia lo spazio vuoto e ingrandisce il disegno fino a riempire l'area
  4. salva un PNG per ogni dimensione d'area + un'anteprima del disegno sui colori del capo
  5. segnala la risoluzione effettiva: la regola e' 300 DPI, sotto avvisa di passare dall'upscaler

--tazza sinistra|destra|entrambi : tazze avvolgenti, disegno su un lato o su tutti e due (sfondo bianco),
                         un file per formato (11oz/15oz); il lato giusto si verifica sui mockup Printify.
--ai-upscale usa Real-ESRGAN (strumenti_grafiche/upscaler) invece del semplice ricampionamento.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from printify_client import get  # noqa: E402

DPI = 300
UPSCALER = ROOT / "strumenti_grafiche" / "upscaler" / "realesrgan-ncnn-vulkan.exe"


def aree_stampa(blueprint, provider, posizione):
    """{(larghezza, altezza): [taglie]} per la posizione richiesta."""
    varianti = get(f"/catalog/blueprints/{blueprint}/print_providers/{provider}/variants.json")["variants"]
    aree = {}
    for v in varianti:
        for ph in v["placeholders"]:
            if ph["position"] == posizione:
                aree.setdefault((ph["width"], ph["height"]), set()).add(v["options"].get("size", v["title"]))
    if not aree:
        posizioni = sorted({ph["position"] for v in varianti for ph in v["placeholders"]})
        raise SystemExit(f"Posizione '{posizione}' inesistente. Disponibili: {', '.join(posizioni)}")
    return aree


def pulisci(im):
    """Alpha netto: quasi trasparente -> 0, quasi pieno -> 255; bordi antialias intatti.
    Toglie anche gli aloni sfumati di ChatGPT: resta semitrasparente solo la fascia di pochi pixel
    attorno alle forme piene (l'antialias), il resto dell'alone va a 0."""
    im = im.convert("RGBA")
    a = im.getchannel("A")
    pieno = a.point(lambda x: 255 if x >= 128 else 0)
    raggio = max(2, round(max(im.size) / 400))  # ~4 px su 1536, ~15 px sulle versioni x4
    vicino = pieno.filter(ImageFilter.MaxFilter(2 * raggio + 1))
    a = ImageChops.multiply(a, vicino)
    a = a.point(lambda x: 0 if x <= 8 else 255 if x >= 245 else x)
    im.putalpha(a)
    bbox = a.getbbox()
    if not bbox:
        raise SystemExit("L'immagine e' completamente trasparente.")
    return im.crop(bbox)


def ingrandisci(im, fattore, ai):
    if ai and fattore > 1.2:
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "in.png", Path(tmp) / "out.png"
            im.save(src)
            subprocess.run([str(UPSCALER), "-i", str(src), "-o", str(dst), "-n", "realesrgan-x4plus-anime"],
                           check=True, capture_output=True)
            im = Image.open(dst).convert("RGBA")
    return im


def adatta(im, area, allinea, margine, ai):
    w, h = area
    scala = min(w * margine / im.width, h * margine / im.height)
    nuovo = (round(im.width * scala), round(im.height * scala))
    grande = ingrandisci(im, scala, ai).resize(nuovo, Image.LANCZOS)
    tela = Image.new("RGBA", area, (0, 0, 0, 0))
    x = (w - nuovo[0]) // 2
    y = round(h * 0.04) if allinea == "alto" else (h - nuovo[1]) // 2  # in alto: poco sotto il bordo
    tela.alpha_composite(grande, (x, y))
    dpi_effettivi = im.width / (nuovo[0] / DPI)
    return tela, dpi_effettivi


def adatta_tazza(im, area, lato, ai):
    """Tazza a stampa avvolgente: il disegno occupa un solo lato (centrato al 25% o al 75% della
    larghezza), largo al massimo il 42% dell'area per restare tutto visibile da quel lato."""
    w, h = area
    rgb = im.convert("RGB")
    sfondo = Image.new("RGB", rgb.size, (255, 255, 255))
    bbox = ImageChops.difference(rgb, sfondo).point(lambda x: 255 if x > 18 else 0).convert("L").getbbox()
    rgb = rgb.crop(bbox)
    larghezza = 0.38 if lato == "entrambi" else 0.42  # sui due lati: resta spazio libero attorno al manico
    scala = min(w * larghezza / rgb.width, h * 0.86 / rgb.height)
    nuovo = (round(rgb.width * scala), round(rgb.height * scala))
    grande = ingrandisci(rgb.convert("RGBA"), scala, ai).convert("RGB").resize(nuovo, Image.LANCZOS)
    tela = Image.new("RGB", area, (255, 255, 255))
    centri = {"sinistra": [0.25], "destra": [0.75], "entrambi": [0.25, 0.75]}[lato]
    for c in centri:
        tela.paste(grande, (round(w * c - nuovo[0] / 2), (h - nuovo[1]) // 2))
    return tela, rgb.width / (nuovo[0] / DPI)


def anteprima(tela, colori, out):
    lato = 700
    pannelli = []
    for c in colori:
        fondo = Image.new("RGBA", tela.size, tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
        fondo.alpha_composite(tela)
        fondo = fondo.convert("RGB")
        fondo.thumbnail((lato, lato))
        pannelli.append(fondo)
    foglio = Image.new("RGB", (sum(p.width for p in pannelli), max(p.height for p in pannelli)), "white")
    x = 0
    for p in pannelli:
        foglio.paste(p, (x, 0))
        x += p.width
    foglio.save(out, quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("immagine")
    ap.add_argument("--blueprint", type=int, required=True)
    ap.add_argument("--provider", type=int, required=True)
    ap.add_argument("--posizione", default="front")
    ap.add_argument("--allinea", choices=["alto", "centro"], default="alto")
    ap.add_argument("--margine", type=float, default=0.92)
    ap.add_argument("--colori", default="ffffff,000000,1e2d50")
    ap.add_argument("--ai-upscale", action="store_true")
    ap.add_argument("--tutte-le-taglie", action="store_true", help="un file per ogni area di stampa diversa")
    ap.add_argument("--tazza", choices=["sinistra", "destra", "entrambi"],
                    help="tazza avvolgente: lato su cui mettere il disegno (entrambi = stampa sui due lati)")
    a = ap.parse_args()

    src = Path(a.immagine)
    x4 = src.with_name(src.stem + "_x4.png")  # versione ingrandita da upscaler/ingrandisci_tutto.bat
    im = Image.open(x4 if x4.exists() else src)
    print(f"Sorgente: {(x4 if x4.exists() else src).name} {im.size[0]}x{im.size[1]}")
    aree = aree_stampa(a.blueprint, a.provider, a.posizione)
    if a.tazza:  # un file per ogni formato (11oz, 15oz): le aree hanno proporzioni diverse
        for (w, h), varianti in sorted(aree.items()):
            tela, dpi = adatta_tazza(im, (w, h), a.tazza, a.ai_upscale)
            out = src.with_name(f"{src.stem}_tazza_{w}x{h}.png")
            tela.save(out, dpi=(DPI, DPI))
            print(f"{out.name}  area {w}x{h}  ({', '.join(sorted(varianti))})  lato {a.tazza}  {dpi:.0f} DPI"
                  + ("" if dpi >= 294 else "  SOTTO 300 DPI: prima ingrandisci con l'upscaler"))
        return
    if im.mode != "RGBA":
        print("ATTENZIONE: l'immagine non ha trasparenza, su capi colorati si vedra' il riquadro di sfondo.")
    im = pulisci(im)
    if not a.tutte_le_taglie:  # Printify riscala da solo la grafica sulle taglie piu' piccole
        piu_grande = max(aree, key=lambda wh: wh[0] * wh[1])
        aree = {piu_grande: {t for ts in aree.values() for t in ts}}
    for (w, h), taglie in sorted(aree.items()):
        suffisso = f"_{a.posizione}_{w}x{h}"
        tela, dpi = adatta(im, (w, h), a.allinea, a.margine, a.ai_upscale)
        out = src.with_name(src.stem + suffisso + ".png")
        tela.save(out, dpi=(DPI, DPI))
        anteprima(tela, a.colori.split(","), src.with_name(src.stem + suffisso + "_anteprima.jpg"))
        # regola di Dario: stampa sempre a 300 DPI (tolleranza 2% per arrotondamenti)
        giudizio = ("OK (300 DPI)" if dpi >= 294 else
                    "SOTTO 300 DPI: prima ingrandisci con l'upscaler (design_x4.png) e rilancia")
        print(f"{out.name}  area {w}x{h}  taglie: {', '.join(sorted(taglie))}")
        print(f"  risoluzione effettiva {dpi:.0f} DPI -> {giudizio}")


if __name__ == "__main__":
    main()
