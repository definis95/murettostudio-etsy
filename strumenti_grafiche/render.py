"""Renderizza un file HTML/SVG in PNG alla risoluzione esatta, usando Microsoft Edge (Playwright).

Uso:
  .venv\\Scripts\\python strumenti_grafiche\\render.py <input.html|svg> <output.png> --size 4800x7200
      [--design 1000]       larghezza in px con cui è scritto l'HTML (default: uguale a --size)
      [--transparent]       sfondo trasparente (il body non deve avere background)
      [--preview 900]       salva anche un'anteprima JPG larga N px accanto all'output

L'HTML va scritto per un foglio di  design x (design*H/W)  px; il render lo scala alla
dimensione finale con device_scale_factor, così testo e vettori restano nitidi.
"""
import argparse
import asyncio
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

Image.MAX_IMAGE_PIXELS = None


async def render(src, out, W, H, design, transparent):
    scale = W / design
    vw, vh = design, round(design * H / W)
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge")
        page = await browser.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=scale)
        await page.goto(Path(src).resolve().as_uri())
        await page.evaluate("document.fonts.ready")
        # le pagine che si costruiscono in modo asincrono impostano window.__ready = false ... true
        await page.wait_for_function("window.__ready !== false", timeout=60000)
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(out), omit_background=transparent, full_page=False)
        await browser.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--size", required=True)
    ap.add_argument("--design", type=int)
    ap.add_argument("--transparent", action="store_true")
    ap.add_argument("--preview", type=int)
    a = ap.parse_args()
    W, H = map(int, a.size.lower().split("x"))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(render(a.src, out, W, H, a.design or W, a.transparent))
    img = Image.open(out)
    if img.size != (W, H):  # arrotondamenti del browser: riporta alla misura esatta
        img = img.resize((W, H), Image.LANCZOS)
    img.save(out, dpi=(300, 300), optimize=True)
    print(f"ok {out} {img.size}")
    if a.preview:
        pv = img.copy()
        pv.thumbnail((a.preview, a.preview * 4))
        bg = Image.new("RGB", pv.size, (200, 196, 188))
        bg.paste(pv, mask=pv.split()[-1] if pv.mode == "RGBA" else None)
        bg.save(out.with_name(out.stem + "_preview.jpg"), quality=90)


if __name__ == "__main__":
    main()
