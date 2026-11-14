"""Genera index.html (pagina di Dario, sempre lo STESSO artifact) da catalogo.json + schede/<id>.html.

Regole: la pagina cresce sempre, nessun prodotto sparisce (al massimo cambia gruppo o finisce negli scartati).
Ogni modifica a un prodotto si fa sulla sua scheda in schede/, poi:
  python anteprime_printify/pagina/genera.py
e ripubblicare l'artifact BQKt2WeEhQqBteJDQpzgqB (slug UUID 543d20dd-30cf-4ca8-b154-b1a17eb41e1e).
"""
import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
CSS_EXTRA = """
  .indice { display:flex; flex-wrap:wrap; gap:6px; margin:6px 0 4px; }
  .indice a { font-size:.82rem; text-decoration:none; color:var(--ink); background:#fff; border:1px solid var(--line); border-radius:99px; padding:3px 10px; }
  .gruppo { margin:30px 0 10px; padding-top:6px; border-top:2px solid var(--line); }
  .gruppo h1 { font-size:1.3rem; }
  .conta { color:var(--muted); font-weight:400; font-size:1rem; }
  .tag.no { background:#eee; color:#777; }
  .su { display:block; text-align:right; font-size:.8rem; margin:-8px 0 14px; }
  a { color:#8a4b1f; }
  .zona { display:inline-block; font-size:.85rem; font-weight:700; padding:3px 10px; border-radius:8px; margin:0 0 8px; }
  .zona.usa { background:#e5edf9; color:#1f4f8f; }
  .zona.europa { background:#eef4e2; color:#4a6b1d; }
  .zona.usa_europa { background:#efe7f7; color:#5b3b86; }
  .versione { border-top:1px dashed var(--line); margin-top:14px; padding-top:12px; }
  .versione h3 { font-size:1rem; margin:0 0 8px; }
  .versione h3 .zona { margin:0 0 4px; }
  .zona.digitale { background:#f1f1f1; color:#555; }
  .filtro { display:flex; gap:6px; margin:0 0 14px; position:sticky; top:0; background:var(--bg); padding:8px 0; z-index:5; }
  .filtro button { flex:1; font:inherit; font-size:.9rem; padding:7px 4px; border-radius:10px; border:1px solid var(--line); background:#fff; color:var(--ink); }
  .filtro button.on { background:var(--ink); color:#fff; border-color:var(--ink); }
"""
ETICHETTE = {"usa": "🇺🇸 Spedito in USA + Canada", "europa": "🇪🇺 Spedito in Europa + Regno Unito",
             "usa_europa": "🇺🇸🇪🇺 Spedito in USA + Europa", "digitale": "🌍 PDF da scaricare, ovunque"}
FILTRO = """  <div class="filtro"><button class="on" data-f="tutti">Tutti</button><button data-f="usa">🇺🇸 USA</button><button data-f="europa">🇪🇺 Europa</button></div>
"""
FILTRO_JS = """<script>
  document.querySelectorAll('.filtro button').forEach(b => b.addEventListener('click', () => {
    document.querySelectorAll('.filtro button').forEach(x => x.classList.toggle('on', x === b));
    const f = b.dataset.f;
    document.querySelectorAll('.box[data-zona]').forEach(c => {
      const z = c.dataset.zona.split(' ');
      const vedi = f === 'tutti' || z.includes('digitale') || z.includes(f) || z.includes('usa_europa');
      c.style.display = vedi ? '' : 'none';
      const su = c.nextElementSibling; if (su && su.classList.contains('su')) su.style.display = vedi ? '' : 'none';
    });
  }));
</script>
"""


def etsy_id(p):
    ROOT = P.parents[1]
    for f in [ROOT / "inserzioni" / f"{p}.json", *sorted((ROOT / "inserzioni").glob(f"{p}_*.json"))]:
        if f.exists() and not f.stem.endswith("_pdf"):  # le inserzioni PDF (22) stanno nella loro card
            return json.loads(f.read_text(encoding="utf-8")).get("etsy_listing_id")
    return None


def stato_etsy(p, cat):
    """Riga con il link all'inserzione Etsy (dal file inserzione), o 'inattiva' se in catalogo -> inattivi."""
    lid = etsy_id(p)
    if not lid:
        return ""
    url = f"https://www.etsy.com/listing/{lid}"
    if p in cat.get("inattivi", []):
        return f'    <p class="meta"><span class="tag wait">su Etsy ma INATTIVA</span> <a href="{url}">inserzione {lid}</a></p>\n'
    return f'    <p class="meta"><span class="tag ok">in vendita su Etsy</span> <a href="{url}">apri l\'inserzione</a></p>\n'


def zona(p, cat):
    if p in cat.get("zone", {}):
        return cat["zone"][p]
    ROOT = P.parents[1]
    for f in [ROOT / "inserzioni" / f"{p}.json", *sorted((ROOT / "inserzioni").glob(f"{p}_*.json"))]:
        if f.exists():
            return json.loads(f.read_text(encoding="utf-8"))["etsy"]["zona"]
    raise SystemExit(f"zona di spedizione sconosciuta per {p}: aggiungila in catalogo.json -> zone")


def main():
    cat = json.loads((P / "catalogo.json").read_text(encoding="utf-8"))
    head = (P / "_head.html").read_text(encoding="utf-8")
    head = re.sub(r"<title>.*?</title>", "<title>MurettoStudio – tutti i prodotti</title>", head)
    head = head.replace("</style>", CSS_EXTRA + "</style>")
    coda = (P / "_script.html").read_text(encoding="utf-8")
    usati = set()
    out = [head, "<body>\n<main id=\"top\">\n",
           "  <h1>MurettoStudio – tutti i prodotti</h1>\n",
           f"  <p class=\"sub\">Aggiornato: {cat['aggiornato']}. Il link di questa pagina non cambia mai: si aggiorna. "
           "Tocca una foto per ingrandirla.</p>\n"]
    out.append("  <div class=\"box\">\n    <h2>Novità di questo aggiornamento</h2>\n    <ul class=\"check\">\n"
               + "".join(f"      <li>{x}</li>\n" for x in cat["novita"]) + "    </ul>\n"
               "    <h2 style=\"margin-top:12px\">Cosa devi fare</h2>\n    <ul class=\"check\">\n"
               + "".join(f"      <li>{x}</li>\n" for x in cat["da_fare"]) + "    </ul>\n  </div>\n")
    out.append(FILTRO)
    # riepilogo con salti ai gruppi e ai prodotti
    out.append("  <div class=\"box\">\n    <h2>Riepilogo</h2>\n")
    for g in cat["gruppi"]:
        out.append(f"    <p style=\"margin:10px 0 0\"><a href=\"#g-{g['id']}\"><b>{g['titolo']}</b></a> "
                   f"<span class=\"conta\">({len(g['prodotti'])})</span></p>\n    <div class=\"indice\">"
                   + "".join(f"<a href=\"#p-{p.split('+')[0]}\">{p.replace('+', ' + ')}</a>" for p in g["prodotti"]) + "</div>\n")
    out.append(f"    <p style=\"margin:10px 0 0\"><a href=\"#g-scartati\"><b>Scartati</b></a> "
               f"<span class=\"conta\">({len(cat['scartati'])})</span></p>\n  </div>\n")
    for g in cat["gruppi"]:
        out.append(f"\n  <div class=\"gruppo\" id=\"g-{g['id']}\"><h1>{g['titolo']} "
                   f"<span class=\"conta\">({len(g['prodotti'])})</span></h1>\n")
        if g.get("sotto"):
            out.append(f"  <p class=\"sub\">{g['sotto']}</p>\n")
        out.append("  </div>\n")
        for voce in g["prodotti"]:
            ids = voce.split("+")
            for p in ids:
                if p in usati:
                    raise SystemExit(f"{p} compare in due gruppi")
                usati.add(p)
            if len(ids) == 1:
                p = ids[0]
                scheda = (P / "schede" / f"{p}.html").read_text(encoding="utf-8")
                z = zona(p, cat)
                scheda = scheda.replace('<div class="box">', f'<div class="box" id="p-{p}" data-zona="{z}">', 1)
                etichetta = f'</h2>\n    <span class="zona {z}">{ETICHETTE[z]}</span>\n'
                scheda = scheda.replace("</h2>\n", etichetta + stato_etsy(p, cat), 1)
            else:  # stesso articolo in versione USA ed Europa: UNA scheda con le due versioni dentro
                zone = [zona(p, cat) for p in ids]
                scheda = (f'  <div class="box" id="p-{ids[0]}" data-zona="{" ".join(zone)}">\n'
                          f'    <h2>{" + ".join(ids)} · {cat["unite"][voce]}</h2>\n'
                          + "".join(f'    <span class="zona {z}">{ETICHETTE[z]}</span>\n' for z in zone))
                for p, z in zip(ids, zone):
                    interno = (P / "schede" / f"{p}.html").read_text(encoding="utf-8").strip()
                    interno = interno[len('<div class="box">'):-len("</div>")]
                    titolo = re.search(r"<h2>(.*?)</h2>", interno).group(1)
                    interno = re.sub(r"\s*<h2>.*?</h2>", "", interno, count=1)
                    scheda += (f'    <div class="versione"><h3><span class="zona {z}">{ETICHETTE[z]}</span>'
                               f'<br>{titolo}</h3>\n{stato_etsy(p, cat)}{interno}\n    </div>\n')
                scheda += "  </div>\n"
            out.append(scheda + "  <a class=\"su\" href=\"#top\">↑ torna su</a>\n")
    out.append("\n  <div class=\"gruppo\" id=\"g-scartati\"><h1>Scartati</h1></div>\n  <div class=\"box\">\n    <ul class=\"check\">\n"
               + "".join(f"      <li>{x}</li>\n" for x in cat["scartati"]) + "    </ul>\n  </div>\n")
    out.append("  <p class=\"nota\">* Indicativo: prezzo meno costo Printify, meno le commissioni Etsy (circa 6,5% di vendita, "
               "circa 4% + 0,30 € di pagamento, 0,18 € di inserzione). Dove la spedizione è gratis, il suo costo è già tolto; "
               "altrimenti la paga il cliente a parte.</p>\n</main>\n")
    out.append(coda + "\n</body>\n</html>\n")
    mancanti = sorted({f.stem for f in (P / "schede").glob("*.html")} - usati)
    if mancanti:
        raise SystemExit(f"schede senza gruppo (nessun prodotto deve sparire): {mancanti}")
    html = "".join(out).replace("<img ", "<img loading=\"lazy\" ")
    (P / "index.html").write_text(html, encoding="utf-8")
    immagini = set(re.findall(r'src="([^"]+)"', html))
    assenti = [i for i in immagini if not (P / i).exists()]
    print(f"index.html: {len(usati)} prodotti, {len(immagini)} immagini" + (f", MANCANO {assenti}" if assenti else ""))


if __name__ == "__main__":
    main()
