"""Schede informative degli annunci (foto extra Etsy) disegnate da ChatGPT, testi in schede_info.json.

Uso:
  python strumenti_grafiche/schede_chatgpt.py            # fa le schede che mancano (si ferma se finisce la quota)
  python strumenti_grafiche/schede_chatgpt.py sciarpa    # rifà solo quella scheda

Output: stampa/foto_etsy/scheda_<nome>_chatgpt.png (originale) e scheda_<nome>.jpg (2000 px, da caricare su Etsy).
Ogni scheda va controllata dall'art director lettera per lettera prima di caricarla.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from chatgpt_bridge import genera as chatgpt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCHEDE = json.loads((Path(__file__).parent / "schede_info.json").read_text(encoding="utf-8"))
STILE = ROOT / "stampa" / "foto_etsy" / "06_body_scheda.jpg"  # stile delle schede gia' online
BRIEF = """Use case: product information card (an extra photo of an Etsy listing), flat graphic, NOT a photo.
Copy the attached reference card EXACTLY: same layout, same fonts, same sizes, same colours, same margins; ONLY the text changes.
- Background: flat warm cream #F8F1E7, no texture, no frame.
- Title: light elegant serif (like Cormorant Garamond), dark brown, top left; under it the subtitle in small light-grey sans-serif (like Jost).
- Bullets: small round terracotta dots, body text in a clean dark-brown sans-serif (like Jost), same size as the reference, left-aligned, generous line spacing, NO divider lines.
- Margins: at least 9% empty space on the left AND on the right; no text closer to the edges; wrap long lines onto two lines.
- Bottom: the brand name MURETTOSTUDIO in widely spaced terracotta capitals, centred near the bottom, exactly like the reference.
- No product picture, no icons, no logo other than the brand name, no watermark.
Text (verbatim, exact spelling, letter by letter; parts between ** must be rendered in bold, without the asterisks; everything else regular weight, including commas):
Title: {titolo}
Subtitle: Everything you need to know
Bullets, in this order:
{punti}
Bottom: MURETTOSTUDIO
No other text anywhere."""


def main():
    solo = sys.argv[1:]
    for nome, s in SCHEDE.items():
        if solo and nome not in solo:
            continue
        png = ROOT / "stampa" / "foto_etsy" / f"scheda_{nome}_chatgpt.png"
        if png.exists() and not solo:
            continue
        brief = BRIEF.format(titolo=s["titolo"], punti="\n".join(f"- {p}" for p in s["punti"]))
        try:
            chatgpt(brief, png, "quadrato", trasparente=False, riferimenti=[STILE],
                    uso_riferimenti="the style reference: copy its layout, colours and fonts, NOT its text")
        except SystemExit as e:
            print(f"{nome}: {str(e)[-300:]}", flush=True)
            if "usage limit" in str(e).lower():
                print("quota ChatGPT finita", flush=True)
                sys.exit(3)
            continue
        # niente upscaler IA: scurisce il testo sottile (sottotitolo grigio). LANCZOS a 2000 px come le schede online
        im = Image.open(png).convert("RGB").resize((2000, 2000), Image.LANCZOS).filter(
            ImageFilter.UnsharpMask(radius=1.0, percent=40, threshold=2))
        im.save(png.with_name(f"scheda_{nome}.jpg"), quality=94, subsampling=0)
        print(f"{nome}: fatta", flush=True)


if __name__ == "__main__":
    main()
