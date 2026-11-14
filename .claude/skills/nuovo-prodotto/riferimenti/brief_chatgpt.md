# Come scrivere i brief per ChatGPT

Strumento: `python strumenti_grafiche/chatgpt_bridge.py --prompt-file brief.txt --out <file> [--formato ...]
[--opaco] [--riferimento img ...] [--bozza]`. In Git Bash aggiungere al PATH
`/c/Users/defin/AppData/Roaming/npm:/c/Program Files/nodejs`. Circa 70-80 s per immagine.

## Grafica di stampa
- Colore del capo, dimensione reale della stampa in cm, palette (hex), stile.
- Testi da scrivere **verbatim** e brevi; controllarli lettera per lettera nel risultato.
- Sfondo trasparente; niente dettagli troppo sottili (in stampa spariscono); niente aloni sfumati.
- Motivi sparsi / fantasie: chiedere un foglio di soggetti separati, staccati tra loro (li dispone lo script).
- Bambini: soggetti piccoli sparsi su tutto il capo, non un solo disegno grande al centro.
- Libri da colorare (stile comune in `libro_colorare.py` → `STILE`, soggetti in `libri_colorare.json`):
  - riempire ~85% della pagina; un soggetto singolo ha sempre un ambiente minimo (terreno/fondale, piante, bolle);
  - conteggi scritti come somma ("4 + 3 = 7 stars", "4 + 4 = 8 tentacles"): ChatGPT sbaglia i numeri;
  - se due correzioni sulle distanze falliscono, **togliere elementi** o dare uno schema fisso (righe, lati) invece
    di ripetere "lascia 1,5 cm";
  - animali di profilo con un solo occhio lontano da corna e contorni; zampe e gambe come forme chiuse.
- **Correggere un difetto, non rifare il disegno** (Dario, 13/11: la pagina 21c/11 riscritta per togliere una
  collina sospesa era uscita piatta e brutta): prima copiare da parte l'originale e la pagina di stampa; poi
  `chatgpt_bridge.py --riferimento <versione approvata>` con un brief "redraw THIS SAME PAGE, keep everything
  identical, fix ONLY: <difetto e correzione>". Riscrivere il soggetto solo se il disegno e' da buttare.
  `--out` deve stare dentro il progetto (fuori, il ponte salva ma poi si ferma con errore).
- Coerenza col marchio (sigillo MurettoStudio) quando c'e' branding.

## Foto ambientate e schede
- Allegare come riferimento il mockup Printify + un ritaglio della stampa al 100%.
- Dare le misure reali (motivo in cm, sciarpa 69x180, berretto con/senza risvolto, stampa vs ricamo, materiale
  vero: le sciarpe sono voile di poliestere, non lino): altrimenti ChatGPT rimpicciolisce o ridisegna i motivi.
- Variare i modelli (eta', capelli) in una serie. Chiedere 2048 px.
- Schede: testi da `strumenti_grafiche/schede_info.json`, stile di riferimento `06_body_scheda.jpg`.

## Quota
- Bozze: modello luna, `--bozza`. Definitivi: astra, massimo 1 nuovo tentativo solo per errori veri.
- Se esce "usage limit": fermarsi e dire a Dario l'orario di ripristino.
