# Stato del progetto (aggiornare a ogni cambiamento)

Ultimo aggiornamento: 2026-11-14.

## Online su Etsy (31 inserzioni, id in `inserzioni/*.json` → `etsy_listing_id`)
- 14/11: libri da colorare 21 (Natale) e 21b (pirati), USA, 19,90 € con spedizione USA gratis.
- Prima release 01/11: 04 e 05 magliette (toddler + youth, USA), 06 e 07 body (EU), 12 e 13 tazze (EU),
  14 e 15 tote (EU).
- Serie 2 (04/11): 17a/17c/17d berretti ricamati (USA+EU), 18a-d berretti cotone (USA), 19b-e sciarpe (USA),
  20 calza EU + 20u USA, 24 carta EU + 24u USA, 27a/27b body colorati (USA), 27c/27d body bianchi (EU).
- 05/11: copertine corrette su tutte (bug Etsy), attributi compilati sui berretti, `verifica.py --tutti` = tutto OK.
- 05/11 pulizia cartella: tolti PNG gemelli della carta, mockup scaricati per i video, anteprime sciolte,
  grafiche/_prove, proposta 19, cataloghi di prodotti abbandonati, foto_info.py, demo upscaler. Tenuti originali
  ChatGPT e versioni x4 (servono per rifare le stampe senza quota).

- 13/11 Natale: `natale.py --applica` ha messo le date limite (Printify − 3 giorni) su tutte le 29 descrizioni
  e nell'annuncio. Utilita' di pianificazione di Windows: "MurettoStudio Natale - aggiorna date" ogni mattina
  alle 7:13 fino al 24/12 (`--applica`, copre anche le nuove pubblicazioni) e "MurettoStudio Natale - togli
  date" il 25/12 (`--togli`); partono anche in ritardo se il PC era spento, si cancellano da soli dopo la
  scadenza. Esito in `stampa/natale_log.txt` (da cancellare a gennaio).

## In lavorazione / in attesa
- Libri da colorare 21-21f (bp 2721/99, USA, prezzo proposto 19,90 € con spedizione USA gratis, costo 8,13 $
  + 6,19 $ spedizione) e 22 PDF per l'Europa. Al 13/11:
  - 21 Natale: pagine e copertina approvate, bozza Printify 6aec6ade902ad8910b041a25 (`inserzioni/21_book.json`)
    → attende l'ok di Dario su bozza e prezzo; poi foto ambientate, scheda e video.
  - 21b pirati: pagine e copertina approvate, bozza Printify 6aeca90e45ea31e28f041b03 (`inserzioni/21b_book.json`)
    → attende l'ok di Dario come il 21.
  - 13/11 sera: Dario ha trovato una collina sospesa (21c/11) passata dall'art director → nuova revisione pagina
    per pagina di TUTTI i libri con la sezione "Scene logic" di `art-director.md`: 42 pagine da correggere,
    copertine tutte PASS. Correzioni con ChatGPT sulla pagina stessa (`libro_colorare.py correggi`, difetti in
    `strumenti_grafiche/correzioni_libri.json`) → prove `pagine/_NN_prova.png` riviste per intero dall'art
    director → `accetta`. 14/11: tutte le 144 pagine approvate, `correzioni_libri.json` vuoto, file di stampa
    2625x3375 a 300 DPI. Bozze Printify di 21 e 21b aggiornate (`--solo-stampa`).
  - Ritocchi a mano rimasti sui file di stampa (si perdono rifacendo `prepara` di quella pagina): 21/04, 21b/23
    (tolta la sesta stella), 21d/07 (Giove all'88%), 21d/13, 21e/20, 21e/22 (colonne laterali di pesci ±100 px),
    21f/04. Su 21f/12 chiuso a mano un anello della catena direttamente su 12_chatgpt.png (resta anche rifacendo
    `prepara`). 21/09, 21/23, 21c/18 e 21e/06 rifatte da ChatGPT. Originali sostituiti in pagine/_vecchie/.
  - 14/11: Dario ha trovato ancora 21c/11 sbagliata due volte (paesaggio sospeso, poi collina che finisce dietro
    il triceratopo) → in `art-director.md` aggiunti "Anchored ground" e il "Method" di continuità (seguire ogni
    linea che tocca un personaggio e dire dove esce). Ricontrollo linea per linea di tutte le 144 pagine: 26
    pagine corrette e approvate. Alla sera tutti e 6 i libri passano; bozze Printify di 21 e 21b aggiornate.
  - 14/11 sera (ok di Dario "vai"): titoli/descrizioni/tag di tutti i libri "Ages 4-8" (tolto "toddlers": i
    libri per bambini di 3 anni o meno escono dall'esenzione CPSIA "ordinary book") e produzione "up to about 10
    business days" (prima diceva 2-5). Bozze Printify create anche per 21c 6af89e364643b0e30508f187, 21d
    6af89e7dedd1928e090c485c, 21e 6af89ec3ca5d307abc00f010, 21f 6af89f0e948a470d52066962. Foto ambientate
    ChatGPT di 21 e 21b (`stampa/<id>_2721/foto/brief_foto.txt`, libretto sottile; punte delle matite
    ricolorate a mano) e scheda `scheda_libro_us.jpg` (voce `libro_us` in schede_info.json, vale per tutti e 6):
    art director PASS. Pagina di revisione aggiornata (6 libri nel gruppo "pronti").
  - CPSIA libri: bozza in `documenti_conformita/CPSIA/LIBRI.md` (certificato, testo etichetta per il retro della
    copertina, domanda a Printify su rilegatura/inchiostri/stabilimento/date di Natale). Da Dario: citta' e
    indirizzo per etichetta e certificato, scelta stampatore (99 Printify Choice, rete; oppure 28 District Photo,
    Beltsville MD, stabilimento unico, 8,16 $), invio della domanda a Printify.
  - Foto ambientate fatte e PASS anche per 21c-21f (21e e 21f con punte di pastelli/matite ricolorate a mano);
    `etsy.foto` e `foto_extra` compilati su tutti e 6 i libri. Originali prima dei ritocchi: nessuno da tenere.
  - 14/11 sera (ok di Dario): stampatore District Photo (provider 28, Beltsville MD, costo 8,16 $ + sped. USA
    5,49 $): bozze rifatte su 28 e cancellate quelle su 99. Etichetta CPSIA sul retro delle 6 copertine
    (`libro_colorare.py` -> `etichetta`, rifatta da `copertina <id> unisci`), art director PASS. Attributi Etsy:
    Book format=Paperback (+ Holiday=Christmas sul 21). `natale.py`: date prudenti per il provider 28 (US 5/12).
  - **21 e 21b pubblicati su Etsy il 14/11**: 21 inserzione 4617461552, 21b 4617463598, sezione nuova
    "Coloring Books", verifica OK. Printify aveva passato i <br> come "\n" scritti: corretto su Etsy, ora
    `pubblica.py` li sistema da solo e `verifica.py` li segnala.
  - Prossimo: pubblicare 21c-21f quando lo dice Dario; poi PDF 22 per l'Europa (nessuno stampatore europeo di libri).
  - Da decidere con Dario: sfondo castello+collina ripetuto in 21f (p02, 05, 13, 22, 24); stesso pesce in 21e
    p10, 16, 22; segni decorativi isolati (onde, ciuffi, puntini) accettati per ora.
- 17d nome personalizzato: verificare il flusso di personalizzazione Printify (max 8 lettere A-Z, controllo di
  ogni ordine) — Dario vuole garanzie sul testo del cliente.
- Idee 08, 09, 10, 16 in sospeso (decide Dario). Scartate: 17b, 19 pan di zenzero, 23, 25, 26, berretti/sciarpe
  solo natalizi, "CIAO".
- Ritocco facoltativo segnalato dall'art director su 19c (qualche papavero senza stelo).

## Conformita' aperta
- CPSIA bimbi USA (04/05 magliette, 27a/27b body): registro in `documenti_conformita/CPSIA/REGISTRO.md`.
  Printify ha mandato CPC LAT 3302 (ok) e quello sbagliato B+C heather; manca il CPC 3501Y 100% cotone.
  Test inchiostro (16 CFR 1303) a carico del venditore; Dario ha scelto inchiostro Kornit; scritto a SwiftPOD
  il 03/11 per sapere quale inchiostro usano. Kornit: report SGS SL12600270037601TX (NeoPigment, piombo e ftalati
  ND, senza test 1303 sul rivestimento); contatto sergio.brandriss@kornit.com. Printify suggerisce SwiftPOD 39
  con etichetta al collo per le magliette bimbi.
- GPSR: Dario lo aggiunge in Printify prima di ogni pubblicazione verso l'Europa.
- Fisco: Dario non ha Partita IVA, sta chiedendo alla commercialista (forfettario, ATECO 47.91.10, INPS
  commercianti, DAC7): chiedere la risposta prima di consigliare altro.
