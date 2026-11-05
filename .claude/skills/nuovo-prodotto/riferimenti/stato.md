# Stato del progetto (aggiornare a ogni cambiamento)

Ultimo aggiornamento: 2026-11-05.

## Online su Etsy (29 inserzioni, id in `inserzioni/*.json` → `etsy_listing_id`)
- Prima release 01/11: 04 e 05 magliette (toddler + youth, USA), 06 e 07 body (EU), 12 e 13 tazze (EU),
  14 e 15 tote (EU).
- Serie 2 (04/11): 17a/17c/17d berretti ricamati (USA+EU), 18a-d berretti cotone (USA), 19b-e sciarpe (USA),
  20 calza EU + 20u USA, 24 carta EU + 24u USA, 27a/27b body colorati (USA), 27c/27d body bianchi (EU).
- 05/11: copertine corrette su tutte (bug Etsy), attributi compilati sui berretti, `verifica.py --tutti` = tutto OK.
- 05/11 pulizia cartella: tolti PNG gemelli della carta, mockup scaricati per i video, anteprime sciolte,
  grafiche/_prove, proposta 19, cataloghi di prodotti abbandonati, foto_info.py, demo upscaler. Tenuti originali
  ChatGPT e versioni x4 (servono per rifare le stampe senza quota).

## In lavorazione / in attesa
- 21-21f libri da colorare (bp 2721, USA) e 22 PDF per l'Europa: dopo le foto mancanti degli articoli online
  (priorita' di Dario 04/11: prima le foto degli articoli online, poi i prodotti nuovi). Anche loro col video.
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
