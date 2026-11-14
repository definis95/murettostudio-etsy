---
name: nuovo-prodotto
description: Flusso completo MurettoStudio per portare un prodotto dall'idea all'inserzione Etsy online (proposte, scelta prodotto Printify, grafica ChatGPT a 300 DPI, bozza Printify, foto extra, pubblicazione e verifica), piu' le regole del progetto (pulizia, git, chiavi). Usala per nuove idee/prodotti, nuove versioni USA/Europa di un articolo, rifare grafiche o foto, pubblicare su Etsy, controllare inserzioni, modificare gli script del progetto.
---

# Nuovo prodotto MurettoStudio

Negozio Etsy print-on-demand via Printify. Dario e' il titolare: decide lui, non e' esperto, segue spesso dal telefono.
Chat in **italiano**; tutto cio' che va sul negozio (titoli, descrizioni, tag, schede) in **inglese**.

**Questa skill e' la fonte unica** delle regole e dello stato del progetto. All'inizio leggi `riferimenti/stato.md`.

| File | Contenuto |
|---|---|
| `riferimenti/stato.md` | cosa e' online, in lavorazione, in sospeso, conformita' aperta |
| `riferimenti/negozio.md` | negozio, marchio, come lavorare con Dario |
| `riferimenti/prodotti.md` | prodotti/stampatori usati, prezzi, limiti |
| `riferimenti/conformita.md` | bambini, CPSIA, GPSR, zone, fisco |
| `riferimenti/brief_chatgpt.md` | come scrivere i brief, quota |
| `riferimenti/strumenti.md` | ponte ChatGPT, upscaler, script di composizione, Printify, Etsy |
| `riferimenti/foto.md` | ordine foto, bug copertina, ingrandimento, video |
| `riferimenti/etsy.md` | titoli, descrizioni, tag, campo `etsy`, prezzi |
| `riferimenti/pagina.md` | pagina di revisione per Dario |
| `riferimenti/pulizia.md` | cosa cancellare e cosa tenere |
| `riferimenti/git.md` | repository GitHub, revisione, commit e push |
| `CHIAVI_API.md` (radice progetto) | dove stanno le chiavi, come vederle/rifarle sui siti |

## Regole fisse

**Prodotto e grafica**
1. **Immagini create solo da ChatGPT** (`strumenti_grafiche/chatgpt_bridge.py`): disegni di stampa, foto ambientate,
   schede informative. Il codice fa tutto cio' che e' lavoro da script sulle immagini di ChatGPT: adattare
   all'area, pulire, ingrandire, convertire, comporre/disporre i motivi (`compone_*.py`), montare il video.
   Mai disegnare con Pillow/HTML/SVG la grafica di un prodotto.
2. **Stampa sempre a 300 DPI**: ogni file copre il 100% dell'area Printify a scala 1. Se lo stampatore definisce
   l'area a risoluzione piu' bassa (es. sciarpe 1327/99 ~155 DPI, carta USA 1100/99 ~200 DPI), dirlo a Dario
   PRIMA di scegliere il prodotto.
3. **Art director** (agente `art-director`) su ogni grafica, foto e scheda prima di usarla **e prima di mostrarla
   a Dario**, anche dopo ogni correzione (si ricontrolla l'immagine intera, non solo il punto corretto); testi e
   numeri controllati lettera per lettera. Dario non deve trovare difetti che il controllo poteva vedere.
4. **Quota ChatGPT limitata**: bozze col modello rapido (luna), al massimo 1 nuovo tentativo e solo per errori
   veri; se compare "usage limit" fermarsi e dire a Dario l'orario di ripristino.

**Decisioni di Dario**
5. **Niente di definitivo senza il suo ok**: scelta delle idee, approvazione bozza, scelta di cosa pubblicare
   (stop 🛑 nelle fasi), cancellazioni, commit e push.
6. **Pagina di revisione che cresce**: una sola pagina (artifact), i prodotti non spariscono mai, le modifiche
   vanno sulla card dello stesso prodotto (`riferimenti/pagina.md`).

**Progetto**
7. **Segreti**: mai leggere, aprire o stampare `.env` e `.etsy_tokens.json`; mai nel repository (esclusi da
   `.gitignore`, nomi delle variabili in `.env.example`). Guida: `CHIAVI_API.md`.
8. **Codice su git solo dopo revisione**: ogni modifica a script, skill o file del progetto si mostra a Dario;
   commit e push solo dopo il suo ok (`riferimenti/git.md`).
9. **Progetto pulito**: niente file inutili nel progetto ne' residui fuori (`riferimenti/pulizia.md`).

## Fase 1 - Idee 🛑

1. Scrivi le idee in `proposte/<AAAA-MM_tema>/proposte.json` (prodotto, perche' si vende, zona).
2. `python strumenti_grafiche/proposte.py genera proposte/<cartella>/proposte.json [--solo 01,03] [--paralleli 4]`
   → una bozza veloce per idea (luna, ~50 s ciascuna, nessun controllo).
3. Aggiungi le card alla pagina di revisione (gruppo "da fare") e dai a Dario il link.
4. 🛑 **Dario sceglie i numeri.** Poi `proposte.py approva ...` / `scarta ...`. Lavoro completo solo sulle
   approvate; le cartelle delle scartate si cancellano (`riferimenti/pulizia.md`).

## Fase 2 - Prodotto e stampatore

Vedi `riferimenti/prodotti.md` e `riferimenti/conformita.md`.
1. `python printify_catalog.py <ricerca> [--eu]` e `--blueprint <id>`: prodotto, stampatori, aree di stampa.
2. `python printify_costs.py <bp>:<provider> [--solo front]` → costo reale.
3. Zona: ogni articolo si vende sia in USA sia in Europa se possibile, ognuno prodotto nella sua zona
   (`europa`, `usa`, `usa_europa`). Se una zona non e' possibile, dirlo a Dario.
4. Bambini: motivi piccoli sparsi su tutto il capo, solo 100% cotone (niente heather/melange);
   USA → CPSIA, Europa → GPSR.
5. Controlla la risoluzione dell'area (regola 2).

## Fase 3 - Grafica

1. Brief per ChatGPT secondo `riferimenti/brief_chatgpt.md` → `chatgpt_bridge.py --prompt-file ... --out ...`.
2. Grafica piatta: upscaler Real-ESRGAN → `design_x4.png` (`riferimenti/strumenti.md`).
3. Adatta all'area:
   - stampa singola: `prepara_stampa.py IMMAGINE --blueprint B --provider P [--margine ...] [--tazza entrambi]`
     → deve dire "OK (300 DPI)";
   - motivi sparsi (body): `compone_sparsi.py`; carta: `compone_carta.py`; sciarpe: `compone_sciarpa.py` /
     `compone_piastrelle.py`; calze: `compone_calza.py`; berretti: `prepara_cappello.py [--fili]`.
4. Guarda le anteprime al 100%, poi art director → PASS.

## Fase 4 - Bozza Printify 🛑

1. File `inserzioni/<id>.json`: titolo, descrizione (inglese, dichiarazione AI, sezione "Photos:"), 13 tag
   (max 20 caratteri), prezzi, colori, file di stampa, campo `etsy` (sezione, zona, attributi, foto, foto_extra).
   Modello: un file esistente dello stesso tipo. Regole in `riferimenti/etsy.md`.
2. `python printify_create.py inserzioni/<id>.json` (bozza NON pubblicata; `--solo-stampa` aggiorna solo i file
   mantenendo testi/GPSR/prezzi).
3. Scarica i mockup Printify in `anteprime_printify/`, aggiorna la card sulla pagina, dai il link.
4. 🛑 **Dario approva la bozza** (oppure chiede modifiche: sulla stessa card).

## Fase 5 - Foto, pubblicazione, verifica 🛑

1. Foto extra **da ChatGPT**: 1-2 foto ambientate + scheda informativa (`strumenti_grafiche/schede_chatgpt.py`,
   testi in `schede_info.json`). Regole in `riferimenti/foto.md`. Art director su tutte.
2. 🛑 **Dario sceglie cosa pubblicare.** Europa: GPSR aggiunto da Dario in Printify. Bambini USA: CPSIA a posto.
3. `python pubblica.py <id> ...`: pubblica da Printify, sezione, partner, rinnovo, foto (1 = mockup Printify,
   2 = ChatGPT, poi extra), video, attributi, spedizioni nella zona, copertina fissata per ultima.
4. `python verifica.py <id> ...` → deve dare OK. Poi chiedi a Dario di guardare le copertine nella pagina
   Inserzioni di Etsy (l'API non le mostra).
5. Sposta la card nel gruppo "in vendita" e aggiorna la pagina.

## Chiusura di ogni lavoro

Vale per ogni blocco di lavoro (pubblicazione, nuovi script, correzioni), non solo per la fase 5:
1. Aggiorna `riferimenti/stato.md` e, se e' cambiata una regola, il file della skill giusto (vedi sotto).
2. Pulizia: proponi la lista secondo `riferimenti/pulizia.md`, cancella dopo l'ok.
3. Revisione: mostra a Dario cosa e' cambiato (`riferimenti/git.md`); dopo il suo ok, commit e push.

## Modifiche al codice

- Gli script restano dove sono: la skill e gli altri script li chiamano con questi percorsi.
- Docstring e messaggi in italiano, come negli script esistenti; credenziali sempre da `.env` a runtime.
- Qualsiasi script che carica o riordina foto su Etsy deve chiamare alla fine `pubblica.fissa_copertina()`:
  Etsy mostra come copertina l'ultima foto caricata/spostata anche se l'ordine nell'API e' giusto.
- Prima di proporre il commit: lancia lo script modificato (o `verifica.py`) e riporta l'esito.

## Manutenzione della skill

Quando si aggiunge qualcosa non si accoda una regola in fondo: si rilegge la parte interessata e si mantiene la
struttura pulita e coerente.
- Ogni informazione sta in UN posto: regola generale → "Regole fisse"; passo del flusso → la sua fase o
  "Chiusura"; dettaglio → il file `riferimenti/` del tema (nuovo file solo per un tema nuovo, e in tabella).
- Se una regola nuova cambia o supera una vecchia, si riscrive o si toglie la vecchia; niente doppioni ne'
  contraddizioni tra SKILL.md, riferimenti e memoria.
- SKILL.md resta breve (flusso e regole); esempi, comandi lunghi e storia vanno nei riferimenti.
- Dopo la modifica rileggi SKILL.md da cima a fondo: numerazione, rimandi ai file e tabella devono tornare.
