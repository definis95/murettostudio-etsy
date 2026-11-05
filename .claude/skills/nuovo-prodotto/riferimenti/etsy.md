# Testi e dati dell'inserzione

## Titolo, descrizione, tag (inglese)
- Titolo: soggetto + prodotto + colore + occasione, parole che la gente cerca (vedi `inserzioni/27a_body.json`).
- Descrizione: frase d'apertura, uso/regalo, poi sezioni DETAILS, CARE, PRODUCTION AND SHIPPING (zona e tempi).
- Dichiarazione AI obbligatoria: "Design created by MurettoStudio with the help of AI image tools, then checked
  and prepared for print by me." Mai scrivere "disegno tutto io".
- Nota sulle foto (vedi `foto.md`).
- Tazze: misure prima in ml per gli acquirenti europei (le varianti restano "11oz/15oz").
- 13 tag, massimo 20 caratteri ciascuno.

## Campo `etsy` del file inserzione
```json
"etsy": {
  "sezione": "Baby Bodysuits",            // sezione del negozio (creata se manca)
  "zona": "usa",                           // europa | usa | usa_europa
  "attributi": {"Graphic": "Animal", "Materials": ["Cotton"], "Primary color": "Blue"},
  "foto": "stampa/foto_etsy/27a.jpg",      // ambientata ChatGPT
  "foto_extra": ["stampa/foto_etsy/scheda_body_us.jpg"]
}
```
Gli attributi usano i nomi mostrati da Etsy e i valori della sua lista; `pubblica.py` dice quali non esistono.

## Prezzi
- In centesimi EUR nel file inserzione (`variants`). Prodotti USA: spedizione USA gratis inclusa nel prezzo.
- Prima release: massimo 10 prodotti alla volta, li sceglie Dario.
