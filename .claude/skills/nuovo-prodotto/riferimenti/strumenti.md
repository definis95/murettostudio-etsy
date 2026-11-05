# Strumenti tecnici

## Ponte ChatGPT (`strumenti_grafiche/chatgpt_bridge.py`)
- Usa Codex CLI (`@openai/codex`, Node.js LTS) collegato all'abbonamento ChatGPT di Dario (`codex login status` =
  "Logged in using ChatGPT"). Disegna lo strumento `image_gen` con la quota del piano: niente crediti API, niente
  OPENAI_API_KEY. Non usare wrapper di terze parti che chiamano endpoint non documentati (rischio ToS).
- Modelli sull'account: gpt-6-astra (il migliore, guida e controlla), gpt-6.1-sol (predefinito), gpt-6-luna
  (rapido, per le bozze). Il modello dirige soltanto: disegna sempre image_gen.
- Default: astra/medium con autocontrollo (max 1 nuovo tentativo, solo per errori veri: testo, tagli, sfondo).
  `--bozza` = un solo tentativo senza controllo.
- Uscita: circa 1024x1536 / 1536x1024 / ~1254 quadrato; lo sfondo trasparente funziona (alpha 253-254 → 255 in
  prepara_stampa).
- Pulizia: gira con `--ephemeral --json`, legge `thread.started` e cancella `~/.codex/generated_images/<thread_id>/`
  dopo aver copiato l'immagine nel progetto. Le ALTRE cartelle in generated_images sono di Dario: non toccarle.
- Quota: il 01/11 circa 20 bozze luna + 25 immagini astra l'hanno esaurita; il 03/11 dopo ~16 astra in una sera
  (ripristino dopo ~50 min). Pianificare i giri di immagini.

## Upscaler (Real-ESRGAN)
- `strumenti_grafiche/upscaler/realesrgan-ncnn-vulkan.exe`, modello `realesrgan-x4plus-anime` (RTX 3070, pochi
  secondi). Dario ha autorizzato `./realesrgan-ncnn-vulkan.exe` lanciato da quella cartella.
- `stampa/<id>_<blueprint>/design.png` → `design_x4.png`; `prepara_stampa.py` usa da solo `design_x4.png` se c'e'.
- Solo grafica piatta, file di stampa e schede di testo: MAI su foto (vedi `foto.md`).

## Adattamento all'area di stampa
- `prepara_stampa.py`: legge da Printify le aree reali; un file sull'area piu' grande (Printify riscala sulle
  altre taglie) o `--tutte-le-taglie`; pulisce gli aloni di ChatGPT; anteprime sui colori del capo.
- Margini usati: magliette 0.85-0.88, body 0.92, tote 0.85, tazze `--tazza entrambi` (ogni copia max 38% della
  fascia, manico a destra visto dal lato stampato).
- `compone_sparsi.py CARTELLA --area WxH [--altezza 1.1] [--unisci 13] [--distanza 1.15] [--ovale]
  [--max-proporzione] [--no-file] [--seme N]`: soggetti piccoli sparsi dentro l'area, nessuno tagliato dal bordo;
  `--no-file` evita file regolari di soggetti grandi/medi; log PIAZZATI per cercare il seme migliore.
  Per aree piccole: comporre all'area reale e poi Real-ESRGAN fino a 2100x2400.
- `compone_carta.py`: fantasia continua dai motivi ChatGPT (compone a 1/4 e ingrandisce x4).
- `compone_sciarpa.py` (preset per id: motivi da un foglio ChatGPT x4, griglia sfalsata, riga trasversale al
  collo, meta' ruotata di 180° perche' entrambe le estremita' si leggano dritte) e `compone_piastrelle.py`.
- `compone_calza.py` (fronte disegno, retro pattern), `prepara_cappello.py [--fili]` (ricamo: colori agganciati ai
  fili Printful: bianco, oro FFCC00, aqua 3399FF, kiwi 7BA35A, grigio 96A1A8, flamingo CC3366; l'old gold A67843
  viene fangoso).
- Stampe DTG su cotone: solo rettangoli fronte/retro (niente maniche, nessun body 100% cotone all-over su
  Printify), quindi "tutto il capo" = area fronte+retro piena.

## Printify
- `printify_client.py` usa il token personale PRINTIFY_TOKEN dentro `.env` (mai leggerlo).
- `printify_create.py inserzioni/<id>.json [--dry-run] [--solo-stampa]`: crea/aggiorna la bozza, non pubblica.
- `printify_costs.py`: il catalogo non ha prezzi, crea una bozza, legge i costi e la cancella → `printify_dati/costi.json`.
- Le inserzioni POD vanno create tramite l'integrazione Printify → Etsy (non con l'API Etsy diretta), altrimenti
  gli ordini non arrivano in produzione.
- L'API Printify non puo' allegare mockup personalizzati: le foto extra si caricano solo su Etsy.

## Etsy
- `etsy_client.py` (Seller App "dario-shop-tools" approvata, OAuth; token in un file locale da non stampare).
- `inspect_shop.py` (stato del negozio → `shop_snapshot.json`), `setup_shop.py [--dry-run]` (testi negozio da
  `shop_content_en.json`), `pubblica.py`, `verifica.py`.
- Video: ffmpeg (`winget install Gyan.FFmpeg`).
