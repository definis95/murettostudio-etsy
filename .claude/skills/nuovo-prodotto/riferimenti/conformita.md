# Conformita' e regole di prodotto

## Bambini
- Solo **100% cotone**: escludere le varianti heather/melange (sono misti).
- **USA (CPSIA)**: servono CPC del capo (versione 100% cotone, non heather) e test dell'inchiostro (piombo
  16 CFR 1303, laboratorio accettato CPSC) + etichetta di tracciabilita'. Stato e documenti in
  `documenti_conformita/CPSIA/REGISTRO.md`: tenerlo aggiornato. Non pubblicare articoli per bambini USA
  senza documenti a posto (decide Dario).
- Indirizzo SwiftPOD: usare quello dell'API Printify (etichetta "San Jose, CA, USA").

## Europa (GPSR)
- Printify non ha un campo API: Dario aggiunge le info sicurezza prodotto dall'interfaccia Printify
  (selezione → More actions → Edit description → Add product safety information).
- Viene aggiunto in fondo alla descrizione: `printify_create.py` non sovrascrive una descrizione che contiene
  "safety". Senza GPSR non si pubblica un prodotto spedito in Europa.

## Zone di spedizione
- Ogni prodotto spedisce solo nella sua zona di produzione: Europa+UK oppure USA+Canada (dazi USA dal 2025,
  USA→Europa lento). `usa_europa` = stesso articolo prodotto in entrambe.
- Dario vuole ogni articolo vendibile sia in USA sia in Europa: se una zona non e' fattibile, dirlo.

## Fisco
- Dario non ha ancora Partita IVA e ne sta parlando con la commercialista: non dare consigli fiscali nuovi
  senza chiedere prima la sua risposta.
