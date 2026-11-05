# Negozio, marchio e modo di lavorare con Dario

## Negozio
- **MurettoStudio** su Etsy, aperto il 30/10/2026; print-on-demand con **Printify** collegato a Etsy.
- Dal 01/11/2026 si vende qualsiasi articolo facile da vendere (magliette divertenti, abbigliamento bimbi,
  articoli regalo), non solo a tema Puglia.
- Testi del negozio (policy, About, FAQ) dichiarano l'uso dell'AI: "created with the help of AI image tools,
  checked and prepared by me".
- Testi caricati via API: `shop_content_en.json` (`setup_shop.py`). Testi che l'API non gestisce (About, ecc.),
  da incollare a mano da Dario: `negozio/testi_da_incollare_su_etsy.md` — aggiornarlo quando cambiano.

## Marchio
- Sigillo rotondo inciso: sole, scogliera di Polignano, ramo d'ulivo, muretto a secco, "MURETTO STUDIO" sul bordo.
  E' l'icona e il banner del negozio; file in `grafiche/00_brand/`. Il branding dei prodotti resta coerente.
- L'agente `printify-designer` (pipeline HTML/SVG) si usa solo per materiale di marchio, non per la grafica dei
  prodotti.

## Lavorare con Dario
- Risposte in italiano, prima i passi concreti da fare, spiegazioni brevi.
- Non e' esperto: spiegare i concetti (es. OAuth, collegamento POD ↔ Etsy) prima di agire.
- Preferisce che Claude lavori in autonomia tramite API invece di fargli fare passaggi a mano in Printify.
- Segue spesso dal telefono: dare link dell'artifact, non file locali.
- Vuole prima bozze veloci e lavoro completo solo sulle idee approvate (era stato troppo lento fare tutto per ogni
  idea).
- Vuole tutti i file utili nel progetto e nessun file residuo sul PC.
- Le grafiche scartate si cancellano.
- Credenziali: mai leggere, aprire o stampare `.env` o i file token (vale anche per grep/cat). Gli script le
  caricano a runtime senza mostrarle.
