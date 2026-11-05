"""Crea e carica su Etsy un breve video (circa 10 s, 1080x1080, senza audio) per ogni inserzione.

Uso:
  python strumenti_grafiche/video_etsy.py 04_toddler ...   (nomi in inserzioni/, senza .json)
  python strumenti_grafiche/video_etsy.py --tutti [--solo-video]   (--solo-video: crea ma non carica)

Sequenza: foto ambientata -> mockup Printify (scaricato dall'inserzione) -> dettaglio stampa (se manca:
secondo mockup Printify, es. altro colore) -> foto ambientata, ognuna con un leggero zoom e dissolvenza.
PRASSI: ogni inserzione ha il suo video. pubblica.py chiama video_inserzione() dopo le foto, quindi i
prodotti nuovi lo ricevono da soli; questo comando serve per rifarli o per le inserzioni vecchie. Serve ffmpeg (winget install Gyan.FFmpeg).
L'id del video caricato viene salvato nel file inserzione ("etsy_video_id") per non caricarlo due volte.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import requests
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import etsy_client as etsy  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FOTO = ROOT / "stampa" / "foto_etsy"
SECONDI, DISSOLVENZA, FPS = 3.0, 0.6, 30


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if not exe:
        trovati = sorted((Path.home() / "AppData/Local/Microsoft/WinGet/Packages").glob("Gyan.FFmpeg*/*/bin/ffmpeg.exe"))
        exe = str(trovati[-1]) if trovati else None
    if not exe:
        raise SystemExit("ffmpeg non trovato: winget install Gyan.FFmpeg")
    return exe


def crea_video(immagini, out):
    cmd = [ffmpeg(), "-y", "-loglevel", "error"]
    for img in immagini:  # una sola immagine per ingresso: zoompan ne ricava d fotogrammi
        cmd += ["-i", str(img)]
    frame = int(SECONDI * FPS)
    filtri = [f"[{k}]scale=2160:2160:force_original_aspect_ratio=decrease,pad=2160:2160:(ow-iw)/2:(oh-ih)/2:white,"
              f"zoompan=z='min(zoom+0.0007,1.07)':d={frame}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
              f":s=1080x1080:fps={FPS},setsar=1[v{k}]" for k in range(len(immagini))]
    ultimo = "v0"
    for k in range(1, len(immagini)):
        offset = k * (SECONDI - DISSOLVENZA)
        filtri.append(f"[{ultimo}][v{k}]xfade=transition=fade:duration={DISSOLVENZA}:offset={offset:.2f}[x{k}]")
        ultimo = f"x{k}"
    cmd += ["-filter_complex", ";".join(filtri), "-map", f"[{ultimo}]", "-c:v", "libx264", "-crf", "21",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out)]
    subprocess.run(cmd, check=True)


def scarica(img, dest):
    """Scarica il mockup e toglie il bianco attorno al prodotto (sciarpe e carta sono strisce piccole su fondo bianco)."""
    dest.write_bytes(requests.get(img["url_fullxfull"], timeout=60).content)
    im = Image.open(dest).convert("RGB")
    bbox = ImageOps.invert(im.convert("L").point(lambda v: 255 if v > 245 else v)).getbbox()
    if bbox:
        l, t, r, b = bbox
        m = round(0.08 * max(r - l, b - t))
        im = im.crop((max(0, l - m), max(0, t - m), min(im.width, r + m), min(im.height, b + m)))
        im.save(dest, quality=94)
    return dest


def video_inserzione(shop_id, nome, ins, solo_video=False):
    """Crea (e carica, se manca) il video dell'inserzione. Aggiorna ins["etsy_video_id"]; ritorna un esito."""
    lid = ins["etsy_listing_id"]
    if not ins["etsy"].get("foto"):
        return "nessun video: manca la foto ambientata"
    if not solo_video and ins.get("etsy_video_id"):
        esistenti = {v["video_id"] for v in etsy.get(f"/application/listings/{lid}/videos")["results"]}
        if ins["etsy_video_id"] in esistenti:
            return "video gia' presente"
    # mockup Printify = foto dell'inserzione che non abbiamo caricato noi (la prima e' in posizione 1)
    mie = set((ins.get("etsy_immagini") or {}).values())
    immagini = sorted(etsy.get(f"/application/listings/{lid}/images")["results"], key=lambda i: i["rank"])
    mockup = [i for i in immagini if i["listing_image_id"] not in mie]
    ambientata = ROOT / ins["etsy"]["foto"]
    sequenza = [ambientata, scarica(mockup[0], FOTO / f"{nome}_printify.jpg")]
    if (FOTO / f"{nome}_stampa.jpg").exists():
        sequenza.append(FOTO / f"{nome}_stampa.jpg")
    elif len(mockup) > 1:
        sequenza.append(scarica(mockup[1], FOTO / f"{nome}_printify2.jpg"))
    sequenza.append(ambientata)
    video = FOTO / f"{nome}_video.mp4"
    crea_video(sequenza, video)
    if solo_video:
        return f"video creato: {video.name} ({len(sequenza)} immagini)"
    with open(video, "rb") as f:
        r = etsy.request("POST", f"/application/shops/{shop_id}/listings/{lid}/videos",
                         files={"video": (video.name, f, "video/mp4")}, data={"name": video.name})
    ins["etsy_video_id"] = r["video_id"]
    return f"video caricato: {r['video_id']} {r.get('video_state')}"


def main():
    nomi = ([p.stem for p in sorted((ROOT / "inserzioni").glob("*.json"))] if "--tutti" in sys.argv
            else [a for a in sys.argv[1:] if not a.startswith("--")])
    shop_id, _ = etsy.get_shop_id()
    for nome in nomi:
        path = ROOT / "inserzioni" / f"{nome}.json"
        ins = json.loads(path.read_text(encoding="utf-8"))
        if not ins.get("etsy_listing_id"):
            print(nome, "non ancora su Etsy")
            continue
        print(nome, video_inserzione(shop_id, nome, ins, "--solo-video" in sys.argv), flush=True)
        path.write_text(json.dumps(ins, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
