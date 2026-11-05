"""Motivo "a disegnini sparsi" per capi (body, tutine): soggetti piccoli distribuiti su tutta l'area.

Uso:
  python strumenti_grafiche/compone_sparsi.py CARTELLA --area 2100x2400 [--altezza 1.1] [--seme 3]

CARTELLA/design.png (+ design_x4.png se c'e') e' il disegno trasparente di ChatGPT con piu' soggetti
(es. orsetti, nuvole, stelle). Lo script:
  1. separa i soggetti (forme staccate tra loro)
  2. li rimpicciolisce tutti dello stesso fattore: il soggetto piu' alto diventa --altezza pollici
  3. li distribuisce su una griglia sfalsata (file alterne: soggetti grandi / medi), con piccole
     rotazioni, poi riempie gli spazi con i soggetti piccoli (stelle, cuori...)
  4. tiene tutto DENTRO l'area: nessun soggetto tagliato dal bordo della stampa
Esce CARTELLA/sparsi_WxH.png (trasparente, 300 DPI) + anteprima su bianco.
"""
import argparse
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).parent))
from prepara_stampa import DPI, pulisci  # noqa: E402


def soggetti(cartella, a_unisci=3):
    """Ritaglia ogni forma staccata; le cerca sulla versione 1x (veloce), ritaglia dalla x4 (nitida)."""
    piccola = pulisci(Image.open(cartella / "design.png"))
    x4p = cartella / "design_x4.png"
    grande = pulisci(Image.open(x4p)) if x4p.exists() else piccola
    k = grande.width / piccola.width
    # unisce le parti vicine (fiore + gambo + foglie) in un solo soggetto
    comp = piccola.getchannel("A").point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.MaxFilter(a_unisci))
    out = []
    while True:
        bbox = comp.point(lambda v: 255 if v == 255 else 0).getbbox()
        if not bbox:
            break
        riga = comp.crop((bbox[0], bbox[1], bbox[2], bbox[1] + 1)).tobytes()
        ImageDraw.floodfill(comp, (bbox[0] + next(i for i, v in enumerate(riga) if v == 255), bbox[1]), 100)
        parte = comp.point(lambda v: 255 if v == 100 else 0)
        comp = ImageChops.subtract(comp, parte.point(lambda v: 50 if v else 0))
        b = parte.getbbox()
        area = sum(1 for v in parte.crop(b).tobytes() if v)
        if area < 40:
            continue
        B = tuple(round(v * k) for v in b)
        m = parte.crop(b).filter(ImageFilter.MaxFilter(3)).resize((B[2] - B[0], B[3] - B[1]))
        s = grande.crop(B)
        s.putalpha(ImageChops.multiply(s.getchannel("A"), m))
        out.append((s, area))
    return out


def libero(occupato, s, pos, margine):
    m = s.getchannel("A").point(lambda v: 255 if v > 20 else 0)
    box = (pos[0] - margine, pos[1] - margine, pos[0] + s.width + margine, pos[1] + s.height + margine)
    vicino = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0)
    vicino.paste(m, (margine, margine))
    # dilata di "margine" px: su una copia ridotta 1/4 con MaxFilter (veloce e vede anche le punte
    # sottili, es. orecchie; il BoxBlur le perdeva e lasciava soggetti quasi attaccati)
    k = 4
    rid = vicino.resize((vicino.width // k + 1, vicino.height // k + 1), Image.BOX).point(lambda v: 255 if v else 0)
    rid = rid.filter(ImageFilter.MaxFilter(2 * (margine // k) + 1))
    vicino = rid.resize((rid.width * k, rid.height * k), Image.NEAREST).crop((0, 0, vicino.width, vicino.height))
    return not ImageChops.multiply(vicino, occupato.crop(box)).getbbox()


def dentro(s, pos, size, bordo):
    return (pos[0] >= bordo and pos[1] >= bordo and pos[0] + s.width <= size[0] - bordo
            and pos[1] + s.height <= size[1] - bordo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cartella")
    ap.add_argument("--area", default="2100x2400")
    ap.add_argument("--altezza", type=float, default=1.1, help="pollici del soggetto piu' alto")
    ap.add_argument("--seme", type=int, default=3)
    ap.add_argument("--nome", default="sparsi")
    ap.add_argument("--distanza", type=float, default=0.75, help="piu alto = meno riempitivi (stelle, cuori)")
    ap.add_argument("--unisci", type=int, default=3, help="px (dispari): parti piu vicine di cosi = un soggetto")
    ap.add_argument("--max-proporzione", type=float, default=0,
                    help="scarta soggetti piu' alti di N volte la larghezza (es. 1.7: due animali uniti per sbaglio)")
    ap.add_argument("--no-file", action="store_true",
                    help="regola anti-allineamento anche per soggetti grandi e medi (niente file e colonne)")
    ap.add_argument("--ovale", action="store_true",
                    help="sagoma ovale vera: ogni soggetto sta tutto dentro un'ellisse rientrata del 4%%")
    a = ap.parse_args()
    cartella = Path(a.cartella)
    W, H = map(int, a.area.split("x"))
    rnd = random.Random(a.seme)

    tutti = soggetti(cartella, a.unisci)
    if a.max_proporzione:
        tutti = [(s, ar) for s, ar in tutti if s.height <= a.max_proporzione * s.width]
    alto = max(s.height for s, _ in tutti)
    f = a.altezza * DPI / alto
    tutti = [(s.resize((max(1, round(s.width * f)), max(1, round(s.height * f))), Image.LANCZOS), ar) for s, ar in tutti]
    massimo = max(ar for _, ar in tutti)
    grandi = [s for s, ar in tutti if ar >= 0.35 * massimo]
    medi = [s for s, ar in tutti if 0.08 * massimo <= ar < 0.35 * massimo]
    piccoli = [s for s, ar in tutti if ar < 0.08 * massimo]
    print(f"soggetti: {len(grandi)} grandi, {len(medi)} medi, {len(piccoli)} piccoli; scala {f:.3f}")
    gruppi = [g for g in (grandi, medi) if g]

    # dettagli troppo piccoli per il DTG (sotto ~4 mm sulla taglia piu' grande): via
    minimo = round(0.15 * DPI)
    piccoli = [s for s in piccoli if max(s.size) >= minimo]

    tela = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    occupato = Image.new("L", (W, H), 0)
    bordo = round(0.12 * DPI)  # 3 mm dal bordo dell'area

    def peso(cx, cy):
        """0 al centro, 1 sul bordo di una superellisse: angoli vuoti, sagoma morbida, non un rettangolo."""
        return (abs(cx - W / 2) / (W / 2)) ** 2.6 + (abs(cy - H / 2) / (H / 2)) ** 2.6

    def in_ovale(cx, cy, s):
        """Con --ovale: gli angoli del soggetto (rientrati del 20%, le forme sono tonde) dentro l'ellisse."""
        if not a.ovale:
            return True
        rx, ry = W / 2 * 0.96, H / 2 * 0.96
        return all(((cx + sx * s.width * 0.4 - W / 2) / rx) ** 2 + ((cy + sy * s.height * 0.4 - H / 2) / ry) ** 2 <= 1
                   for sx in (-1, 1) for sy in (-1, 1))

    piazzati = []  # (gruppo, forma, cx, cy): stampato a fine lavoro per controlli automatici
    forma_di = lambda x: "largo" if x.width > 1.15 * x.height else "alto"
    centri_piccoli = []  # per evitare file orizzontali/verticali di riempitivi (si nota l'algoritmo)

    def allineato(cx, cy, centri=None, tolleranza=0.14 * DPI, campo=1.2 * DPI):
        return any((abs(cy - y) < tolleranza and abs(cx - x) < campo)
                   or (abs(cx - x) < tolleranza and abs(cy - y) < campo)
                   for x, y in (centri_piccoli if centri is None else centri))

    alt_px = a.altezza * DPI
    regole_file = {"grandi": (0.35 * alt_px, 4 * alt_px), "medi": (0.25 * alt_px, 3 * alt_px)}
    fasce = {"grandi": 0.5 * alt_px, "medi": 0.35 * alt_px}  # striscia = 2*valore: 1 orso / 0.7 orso  # max 2 per fascia/colonna su TUTTA l'area

    def in_fila(cx, cy, centri, mezza):
        """Vero se il nuovo centro forma con altri due un trio in una striscia (riga o colonna) larga 2*mezza."""
        def trio(v, valori):
            vicini = sorted(w for w in valori if abs(w - v) < 2 * mezza)
            return any(max(w1, w2, v) - min(w1, w2, v) < 2 * mezza
                       for i, w1 in enumerate(vicini) for w2 in vicini[i + 1:])
        return trio(cy, [y for _, y in centri]) or trio(cx, [x for x, _ in centri])

    def semina(gruppo, distanza, accetta, rotazione, tentativi=400, quanti=10 ** 6, riempitivo=False, nome_gruppo=""):
        """Posizioni casuali con distanza minima (niente griglia); sceglie il soggetto meno usato."""
        usati, messi, falliti = {}, 0, 0
        centri = []
        regola = regole_file.get(nome_gruppo) if a.no_file else None
        per_tipo = {}  # con --no-file: copie dello stesso soggetto lontane tra loro (sparse su tutta l'area)
        lontano = 0.33 * min(W, H)
        # "tipo" = forma: soggetti larghi (es. orsetti che dormono) e alti (seduti) si spargono a parte
        forma = lambda x: "largo" if x.width > 1.15 * x.height else "alto"
        # solo la forma piu' rara tra i soggetti grandi (le altre restano libere, se no il motivo si svuota)
        forme = [forma(x) for x in gruppo]
        rara = min(set(forme), key=forme.count) if nome_gruppo == "grandi" and len(set(forme)) > 1 else None
        while falliti < tentativi and messi < quanti and gruppo:
            s = min(gruppo, key=lambda x: (usati.get(id(x), 0), rnd.random()))
            s2 = s.rotate(rnd.uniform(-rotazione, rotazione), resample=Image.BICUBIC, expand=True)
            cx, cy = rnd.uniform(0, W), rnd.uniform(0, H)
            pos = (round(cx - s2.width / 2), round(cy - s2.height / 2))
            if (accetta(cx, cy) and dentro(s2, pos, (W, H), bordo) and in_ovale(cx, cy, s2)
                    and not (riempitivo and allineato(cx, cy))
                    and not (regola and allineato(cx, cy, centri, *regola))
                    and not (regola and in_fila(cx, cy, centri, fasce[nome_gruppo]))
                    and not (regola and forma(s2) == rara and any((cx - x) ** 2 + (cy - y) ** 2 < lontano ** 2
                                                                  for x, y in per_tipo.get(rara, [])))
                    and libero(occupato, s2, pos, distanza)):
                if riempitivo:
                    centri_piccoli.append((cx, cy))
                centri.append((cx, cy))
                piazzati.append((nome_gruppo or ("riempitivi" if riempitivo else ""), forma_di(s2), round(cx), round(cy)))
                per_tipo.setdefault(forma(s2), []).append((cx, cy))
                tela.alpha_composite(s2, pos)
                occupato.paste(255, pos, s2.getchannel("A").point(lambda v: 255 if v > 20 else 0))
                usati[id(s)] = usati.get(id(s), 0) + 1
                messi, falliti = messi + 1, 0
            else:
                falliti += 1
        return messi

    collo = lambda cy: cy > 0.06 * H or rnd.random() < 0.3  # sotto il collo piu' rado
    n_grandi = semina(grandi, round(0.3 * a.altezza * DPI), lambda x, y: peso(x, y) <= 0.75 and collo(y), 12,
                     nome_gruppo="grandi")
    n_medi = semina(medi, round(0.22 * a.altezza * DPI),
                    lambda x, y: peso(x, y) <= 0.9 and collo(y) and rnd.random() < min(1, (1 - peso(x, y)) / 0.3), 15,
                    quanti=round(n_grandi * 1.3), nome_gruppo="medi") if piccoli else 0
    riempitivi = piccoli or medi
    massimo_piccoli = round(W * H / (a.altezza * DPI * a.distanza) ** 2)  # densita' leggera, non un cielo pieno
    messi = semina(riempitivi, round(0.2 * DPI),
                   lambda x, y: peso(x, y) <= 1 and collo(y) and rnd.random() < min(1, (1 - peso(x, y)) / 0.3), 20,
                   tentativi=300, quanti=massimo_piccoli, riempitivo=True)
    print(f"messi: {n_grandi} grandi, {n_medi} medi")
    print("PIAZZATI " + json.dumps(piazzati))
    origine = tela.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()[:2]
    tela = pulisci(tela)  # niente pixel quasi trasparenti dopo rotazioni/ridimensionamenti
    tela.putalpha(tela.getchannel("A").point(lambda v: 0 if v < 16 else v))
    # pulisci ritaglia al contenuto: lo rimette nella stessa posizione dell'area
    contenuto = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    contenuto.alpha_composite(tela, origine)  # stessa posizione di prima (pulisci ritaglia)
    out = cartella / f"{a.nome}_{W}x{H}.png"
    contenuto.save(out, dpi=(DPI, DPI))
    prev = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    prev.alpha_composite(contenuto)
    prev = prev.convert("RGB")
    prev.thumbnail((700, 800))
    prev.save(cartella / f"{a.nome}_{W}x{H}_anteprima.jpg", quality=90)
    print(f"{out}  + {messi} piccoli negli spazi")


if __name__ == "__main__":
    main()
