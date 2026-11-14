# Foto e video dell'inserzione Etsy

## Ordine delle foto (regole Etsy sulle immagini, 22/10/2026)
1. Mockup Printify (foto reale o mockup autorizzato del produttore: le foto AI NON possono essere la prima).
2. Foto ambientata ChatGPT (`etsy.foto`, es. `stampa/foto_etsy/<idea>.jpg`).
3. Foto extra (`etsy.foto_extra`): dettaglio stampa, taglie, scheda informativa.
4. Altri mockup Printify (altri colori).

La descrizione deve dire: "Photos: the first photo is the product mockup from our print partner; the lifestyle
photos are digital mockups created for illustration."

## Bug copertina Etsy (visto 2 volte)
L'API da' l'ordine giusto ma Etsy mostra come copertina l'ultima foto caricata/spostata. `pubblica.py` chiama
`fissa_copertina()` per ultima. L'API non mostra la copertina: farla guardare a Dario in Shop Manager.

## Ingrandimento
- **Foto** (ambientate): MAI Real-ESRGAN (pelle cerosa, ricami di plastica). Pillow LANCZOS a 2000 px +
  UnsharpMask(1.2, 50, 3), JPEG qualita' 94, subsampling 0.
- **Grafica piatta, file di stampa, schede di testo**: Real-ESRGAN va bene.

## Video (sempre, su ogni inserzione)
`pubblica.py` lo fa da solo con `strumenti_grafiche/video_etsy.py` (ffmpeg): ambientata → mockup Printify →
dettaglio stampa → ambientata, circa 10 s. Controllare un foglio di fotogrammi prima di caricarlo.

## Controlli
- Foto con matite/pastelli (libri da colorare, 14/11): ChatGPT sbaglia spesso il colore della punta rispetto al
  corpo, anche se il brief lo chiede; il libro sottile va chiesto esplicitamente ("thin 24-page saddle-stitched
  booklet, about 3 mm"). Ritocco locale: cambiare solo la tinta conservando la luminosita' originale, maschera
  sfumata, pixel neri protetti (niente schiarimenti: sporcano le righe nere).
- Mockup Printify bianchi/vuoti (successo con 24u): `verifica.py` li segnala, si tolgono a mano.
- Gli id delle foto caricate stanno in `etsy_immagini`: Etsy cancella il testo alternativo quando si riordina,
  quindi non usarlo per riconoscere le foto.
- Le foto extra vanno SOLO su Etsy (non su Printify, non sulla pagina di revisione).
