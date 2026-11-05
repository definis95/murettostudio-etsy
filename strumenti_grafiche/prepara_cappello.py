"""Prepara il file di stampa di un cappellino dal disegno di ChatGPT.

Uso:
  python strumenti_grafiche/prepara_cappello.py CARTELLA --area 1500x525 --altezza 0.9 [--fili ffffff,ffcc00,3399ff]

- pulisce aloni e trasparenze (prepara_stampa.pulisci), ritaglia il disegno
- --fili (ricamo): ogni pixel diventa esattamente uno dei colori dei fili, trasparenza netta
- centra il disegno nell'area: altezza = frazione dell'area (larghezza al massimo 92%)
Esce CARTELLA/design_WxH.png (300 DPI) + anteprima su tessuti scuri.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from prepara_stampa import DPI, pulisci  # noqa: E402


def a_fili(im, fili):
    """Ricamo: alpha netto e ogni pixel al colore del filo piu' vicino."""
    pal = [tuple(int(f[i:i + 2], 16) for i in (0, 2, 4)) for f in fili]
    alpha = im.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    flat = Image.new("P", (1, 1))
    flat.putpalette(sum(pal, ()) + (0, 0, 0) * (256 - len(pal)))
    rgb = im.convert("RGB").quantize(palette=flat, dither=Image.Dither.NONE).convert("RGB")
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cartella")
    ap.add_argument("--area", required=True)
    ap.add_argument("--altezza", type=float, default=0.9)
    ap.add_argument("--fili")
    a = ap.parse_args()
    cartella = Path(a.cartella)
    W, H = map(int, a.area.split("x"))
    im = pulisci(Image.open(cartella / "design.png").convert("RGBA"))
    if a.fili:
        im = a_fili(im, a.fili.split(","))
    im = im.crop(im.getchannel("A").getbbox())
    scala = min(H * a.altezza / im.height, W * 0.92 / im.width)
    im = im.resize((round(im.width * scala), round(im.height * scala)), Image.LANCZOS)
    if a.fili:  # dopo il ridimensionamento torna a colori e bordi netti
        im = a_fili(im, a.fili.split(","))
    tela = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tela.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))
    out = cartella / f"design_{W}x{H}.png"
    tela.save(out, dpi=(DPI, DPI))
    fondi = [(20, 20, 22), (31, 42, 68), (150, 30, 35), (75, 83, 50), (70, 72, 75)]
    prova = Image.new("RGB", (W, H * len(fondi)))
    for i, c in enumerate(fondi):
        f = Image.new("RGBA", (W, H), c + (255,))
        f.alpha_composite(tela)
        prova.paste(f.convert("RGB"), (0, i * H))
    prova.save(cartella / f"design_{W}x{H}_anteprima.jpg", quality=90)
    print(out, f"disegno {im.width}x{im.height} px = {im.width / DPI * 2.54:.1f} x {im.height / DPI * 2.54:.1f} cm")


if __name__ == "__main__":
    main()
