"""Mette nella scheda di ogni libro da colorare (21-21f) copertina e pagine pronte (stampa/<id>_2721).
Uso: python anteprime_printify/pagina/libri_in_pagina.py 21 21b ...   poi genera.py e ripubblicare l'artifact."""
import re
import sys
from pathlib import Path

from PIL import Image

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
nuovi = []
for lib in sys.argv[1:]:
    d = ROOT / "stampa" / f"{lib}_2721"
    fig = []
    cop = d / "copertina_5175x3375.png"
    if cop.exists():
        c = Image.open(cop).convert("RGB")
        c.thumbnail((1600, 1600))
        c.save(P / f"{lib}_copertina.jpg", quality=85)
        nuovi.append(f"{lib}_copertina.jpg")
        fig.append(f'      <figure><img src="{lib}_copertina.jpg" alt="Copertina e retro"><figcaption>Copertina (a destra) e retro (a sinistra)</figcaption></figure>\n')
    if (P / f"{lib}_bozza.jpg").exists():
        fig.append(f'      <figure><img src="{lib}_bozza.jpg" alt="Bozza approvata"><figcaption>Bozza approvata all\'inizio</figcaption></figure>\n')
    pagine = sorted((d / "pagine").glob("pagina_*.png"))
    for f in pagine:
        n = f.stem[-2:]
        im = Image.open(f).convert("RGB")
        im.thumbnail((700, 900))
        im.save(P / f"{lib}_p{n}.jpg", quality=80)
        nuovi.append(f"{lib}_p{n}.jpg")
        fig.append(f'      <figure><img class="alto" src="{lib}_p{n}.jpg" alt="Pagina {int(n)}"><figcaption>Pagina {int(n)}</figcaption></figure>\n')
    s = (P / "schede" / f"{lib}.html").read_text(encoding="utf-8")
    i = s.index('<div class="gal">')
    j = s.index("    </div>", i) + len("    </div>")
    s = s[:i] + '<div class="gal">\n' + "".join(fig) + "    </div>" + s[j:]
    stato = (f'<li id="stato{lib}">Pagine pronte: {len(pagine)} su 24 (disegnate da ChatGPT). '
             + ("Copertina e retro pronti." if cop.exists() else "Copertina e retro: da fare (li disegna ChatGPT).") + "</li>")
    if f'id="stato{lib}"' in s:
        s = re.sub(rf'<li id="stato{lib}">.*?</li>', stato, s)
    else:
        s = s.replace('<ul class="check">', '<ul class="check">\n      ' + stato, 1)
    s = s.replace('<span class="tag wait">da fare</span>', '<span class="tag wait">in lavorazione</span>')
    (P / "schede" / f"{lib}.html").write_text(s, encoding="utf-8")
(P / "_nuovi.txt").write_text("\n".join(nuovi), encoding="utf-8")
print(len(nuovi), "immagini")
