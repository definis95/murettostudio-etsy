# Pulizia della cartella

Si fa nella "Chiusura di ogni lavoro" (SKILL.md) e quando Dario la chiede.
Flusso: inventario → lista con spazio liberato e motivo → **ok di Dario** → cancella → controlla che nulla si
sia rotto → annota in `stato.md` → la cancellazione entra nel commit (dopo revisione, `git.md`).
I file gia' committati restano recuperabili dalla storia git; quelli mai committati e i file esclusi
(`.env`, token) no.

Prima di cancellare, cerca riferimenti: `inserzioni/*.json`, script, `anteprime_printify/pagina/`, la skill.
Un file citato da un'inserzione non si tocca.

## Si cancella
- Grafiche, bozze e cartelle di idee **scartate** (prima `proposte.py scarta <file> <id>`, poi la cartella,
  poi `proposte.py pagina` per non lasciare immagini rotte).
- PNG gemelli di file di stampa caricati su Printify in JPEG (es. carta da regalo).
- Mockup Printify scaricati solo per montare i video (`stampa/foto_etsy/*_printify*.jpg`): `video_etsy.py` li
  riscarica.
- Anteprime sciolte in `anteprime_printify/` fuori da `pagina/` (la pagina ha le sue copie).
- Prove (`grafiche/_prove` e simili), cataloghi Printify di prodotti abbandonati (`printify_dati/catalogo_*`).
- Script superati da un nuovo metodo (dopo aver controllato che nessuno li importi).
- File residui fuori dal progetto (es. cartelle temporanee, `~/.codex/generated_images/<thread>` del ponte;
  MAI le altre cartelle di generated_images, che sono di Dario).

## Si tiene
- Originali ChatGPT (`design.png`, `*_chatgpt.png`, pagine dei libri) e versioni `*_x4.png`: servono per
  rifare le stampe senza spendere quota.
- Tutto cio' che e' citato dalle inserzioni, i video, `documenti_conformita/`, `grafiche/00_brand/`.
- Lavori in corso (es. libri da colorare non ancora pubblicati), brief e log (pesano pochissimo).
- `.env`, `.etsy_tokens.json` (segreti: mai leggerli, mai cancellarli).
