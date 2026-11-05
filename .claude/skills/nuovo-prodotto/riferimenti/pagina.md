# Pagina di revisione "MurettoStudio – tutti i prodotti"

Dario rivede tutto dal telefono con UN solo link: dargli sempre il link dell'artifact, non file locali.

- Artifact: https://claude.ai/artifact/BQKt2WeEhQqBteJDQpzgqB (slug 543d20dd-30cf-4ca8-b154-b1a17eb41e1e).
- Sorgente: `anteprime_printify/pagina/`
  - `schede/<id>.html`: una card per prodotto. Ogni modifica va sulla card dello stesso prodotto.
  - `catalogo.json`: `aggiornato`, `novita`, `da_fare`, gruppi per stato (vendita / pronti / lavorazione /
    dafare / attesa), `scartati`, `unite` (stesso articolo USA+Europa in UNA card, es. "20+20u", con etichetta
    di spedizione per versione).
- Rigenera: `python anteprime_printify/pagina/genera.py` (si rifiuta se una card non ha gruppo: niente sparisce).
- Pubblica: `publish_files` in modalita' patch sullo stesso slug, con `index.html` + immagini nuove/cambiate.
- Aggiornare ogni volta `aggiornato` e `novita`.
- La pagina CRESCE: non togliere mai prodotti quando si aggiunge una serie nuova.
