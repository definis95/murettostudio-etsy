"""Compone il file di stampa di una carta regalo (motivo continuo) a partire dal disegno di ChatGPT.

Uso:
  python strumenti_grafiche/compone_carta.py DISEGNO.png --area 8268x11811 [--area 8268x23622] [--seme 7]
         [--scala 0.4] [--unisci 15]   (sciarpe: motivi ritagliati interi dal disegno grande, poi rimpiccioliti)

Il disegno di ChatGPT e' un riquadro con fondo pieno e motivi sparsi (renne, agrifoglio, stelle).
Ripeterlo cosi' com'e' lascerebbe giunture e motivi tagliati, quindi lo script:
  1. ritaglia ogni motivo intero (quelli tagliati dal bordo del riquadro vengono scartati)
  2. li ridistribuisce su tutta l'area: motivi grandi su una griglia sfalsata con piccoli spostamenti
     casuali (alternando i tipi), poi i motivi piccoli negli spazi liberi
  3. compone a 1/4 della risoluzione e ingrandisce x4 con Real-ESRGAN (dettagli netti, 300 DPI)
Esce DISEGNO_front_WxH.png per ogni area + anteprima jpg.
"""
import argparse
import random
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat

UPSCALER = Path(__file__).parent / "upscaler" / "realesrgan-ncnn-vulkan.exe"
DPI = 300
Image.MAX_IMAGE_PIXELS = None  # i rotoli di carta superano il limite di sicurezza di PIL


def colore_base(im):
    piccolo = im.convert("RGB").resize((200, 200)).quantize(8)
    indice = max(piccolo.getcolors(), key=lambda c: c[0])[1]
    return tuple(piccolo.getpalette()[indice * 3:indice * 3 + 3])


def estrai_motivi(im, base, unisci=5):
    """Lista di (sprite RGBA, area in pixel) dei motivi interi."""
    rgb = im.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", im.size, base)).convert("L")
    pieno = diff.point(lambda v: 255 if v > 30 else 0)
    unito = pieno.filter(ImageFilter.MaxFilter(unisci))  # unisce bracci delle stelle, foglie e bacche
    alpha = diff.point(lambda v: min(255, v * 4))  # bordo morbido del motivo
    motivi = []
    w, h = im.size
    while True:
        bbox = unito.point(lambda v: 255 if v == 255 else 0).getbbox()
        if not bbox:
            break
        riga = unito.crop((bbox[0], bbox[1], bbox[2], bbox[1] + 1)).tobytes()
        seme = (bbox[0] + next(i for i, v in enumerate(riga) if v == 255), bbox[1])
        ImageDraw.floodfill(unito, seme, 128)
        questo = unito.point(lambda v: 255 if v == 128 else 0)
        b = questo.getbbox()
        unito = ImageChops.subtract(unito, questo.point(lambda v: 128 if v else 0))  # 128 -> 0
        if b[0] <= 1 or b[1] <= 1 or b[2] >= w - 1 or b[3] >= h - 1:
            continue  # tagliato dal bordo
        area = sum(1 for v in questo.crop(b).tobytes() if v)
        if area < 30:
            continue  # puntino/rumore
        sprite = rgb.crop(b).convert("RGBA")
        sprite.putalpha(ImageChops.multiply(alpha.crop(b), questo.crop(b).filter(ImageFilter.MaxFilter(3))))
        motivi.append((sprite, area))
    return motivi


def classifica(motivi):
    """grandi (renne, agrifoglio...) e piccoli (stelle), i grandi divisi per colore medio."""
    aree = sorted(a for _, a in motivi)
    soglia = aree[len(aree) // 2] * 3 if aree else 0
    grandi = [s for s, a in motivi if a >= soglia]
    piccoli = [s for s, a in motivi if a < soglia]
    if not grandi:  # motivi tutti simili (rametti, mazzolini): grandi = dalla mediana/2 in su
        mediana = aree[len(aree) // 2] if aree else 0
        grandi = [s for s, a in motivi if a >= mediana / 2]
        piccoli = [s for s, a in motivi if a < mediana / 2]
    gruppi = {}
    for s in grandi:
        pieno = s.getchannel("A").point(lambda v: 255 if v > 128 else 0)
        r, g, b = ImageStat.Stat(s.convert("RGB"), mask=pieno).mean  # colore medio del solo motivo
        gruppi.setdefault("chiaro" if r + g + b > 450 else "scuro", []).append(s)
    return list(gruppi.values()), piccoli


def libero(occupato, sprite, pos, margine):
    m = sprite.getchannel("A").point(lambda v: 255 if v > 20 else 0)
    box = (pos[0] - margine, pos[1] - margine, pos[0] + sprite.width + margine, pos[1] + sprite.height + margine)
    vicino = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0)
    vicino.paste(m, (margine, margine))
    vicino = vicino.filter(ImageFilter.MaxFilter(margine * 2 + 1))
    return not ImageChops.multiply(vicino, occupato.crop(box)).getbbox()


def segna(occupato, sprite, pos):
    occupato.paste(255, pos, sprite.getchannel("A").point(lambda v: 255 if v > 20 else 0))
    return occupato


def componi(gruppi, piccoli, base, size, passo, rnd):
    w, h = size
    tela = Image.new("RGBA", size, base + (255,))
    occupato = Image.new("L", size, 0)
    # file alterne per tipo (renne, agrifoglio, ...); ogni tipo forma una griglia sfalsata a sé,
    # la fila dell'altro tipo cade negli spazi in mezzo. Densità come nel disegno originale.
    dx, dy = passo * 1.25, passo / 1.25
    n = len(gruppi)
    righe = int(h / dy) + 2
    colonne = int(w / dx) + 2
    for r in range(-1, righe):
        tipo = r % n
        sfasa = (r * dx / (2 * n)) % dx  # ogni fila sfalsata: lo stesso tipo non si allinea in colonna
        for c in range(-1, colonne):
            s = rnd.choice(gruppi[tipo])
            if rnd.random() < 0.5:
                s = s.transpose(Image.FLIP_LEFT_RIGHT)  # motivi in entrambe le direzioni
            cx = c * dx + sfasa + rnd.uniform(-0.06, 0.06) * passo
            cy = r * dy + rnd.uniform(-0.06, 0.06) * passo
            pos = (round(cx - s.width / 2), round(cy - s.height / 2))
            tela.paste(s, pos, s)
            occupato = segna(occupato, s, pos)
    falliti, messi = 0, 0
    while piccoli and falliti < 400:
        s = rnd.choice(piccoli)
        pos = (rnd.randrange(-s.width // 2, w - s.width // 2), rnd.randrange(-s.height // 2, h - s.height // 2))
        if libero(occupato, s, pos, round(passo * 0.06)):
            tela.paste(s, pos, s)
            occupato = segna(occupato, s, pos)
            messi, falliti = messi + 1, 0
        else:
            falliti += 1
    return tela, messi


def ingrandisci_x4(im):
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.png", Path(tmp) / "out.png"
        im.convert("RGB").save(src)
        subprocess.run([str(UPSCALER), "-i", str(src), "-o", str(dst), "-n", "realesrgan-x4plus-anime"],
                       check=True, capture_output=True, cwd=UPSCALER.parent)
        return Image.open(dst).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("disegno")
    ap.add_argument("--area", action="append", required=True)
    ap.add_argument("--seme", type=int, default=7)
    ap.add_argument("--scala", type=float, default=1.0, help="rimpicciolisce i motivi DOPO averli ritagliati")
    ap.add_argument("--unisci", type=int, default=5, help="distanza (px, dispari) entro cui i pezzi formano un motivo")
    a = ap.parse_args()
    src = Path(a.disegno)
    im = Image.open(src).convert("RGB")
    base = colore_base(im)
    motivi = estrai_motivi(im, base, a.unisci)
    if a.scala != 1:
        motivi = [(s.resize((max(1, round(s.width * a.scala)), max(1, round(s.height * a.scala))), Image.LANCZOS),
                   ar * a.scala ** 2) for s, ar in motivi]
    gruppi, piccoli = classifica(motivi)
    print(flush=True)
    print(f"fondo {base}, motivi interi: {len(motivi)} (grandi {[len(g) for g in gruppi]}, piccoli {len(piccoli)})")
    # passo della griglia = distanza media tra i motivi grandi nel disegno originale
    n_grandi = sum(len(g) for g in gruppi)
    passo = (im.width * im.height / max(n_grandi, 1)) ** 0.5 * a.scala
    for area in a.area:
        W, H = map(int, area.split("x"))
        piccola = (round(W / 4), round(H / 4))
        tela, messi = componi(gruppi, piccoli, base, piccola, passo, random.Random(a.seme))
        print(f"{area}: griglia passo {passo:.0f}px, {messi} stelle aggiunte; ingrandisco x4...")
        finale = ingrandisci_x4(tela).resize((W, H), Image.LANCZOS)
        out = src.with_name(f"{src.stem}_front_{W}x{H}.png")
        finale.save(out, dpi=(DPI, DPI))
        anteprima = finale.copy()
        anteprima.thumbnail((900, 1400))
        anteprima.save(src.with_name(f"{src.stem}_front_{W}x{H}_anteprima.jpg"), quality=90)
        print(out)


if __name__ == "__main__":
    main()
