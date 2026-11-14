# Prodotti e stampatori gia' usati

Aggiornare questa tabella quando si aggiunge un tipo di prodotto nuovo. Prezzi in centesimi EUR (come nei file inserzione).
Dati per articolo: `inserzioni/<id>.json`; costi letti: `printify_dati/costi.json`.

| Prodotto | Blueprint / provider | Zona | Prezzo | Note |
|---|---|---|---|---|
| Maglietta bambino toddler | 586 / 99 Printify Choice | usa | 3490 | spedizione USA gratis inclusa; CPSIA; valutare SwiftPOD 39 (etichetta al collo) |
| Maglietta bambino youth | 1702 / 99 Printify Choice | usa | 3690 | come sopra |
| Body neonato Babybugz | 974 / 26 Textildruck DE | europa | 2990 | solo bianco; solo fronte (retro porta il costo da 18.88 a 26.16) |
| Body manica lunga colorato | 31 / 39 SwiftPOD | usa | 3490 | Rabbit Skins 4411 Light Blue/Pink; area cresce con la taglia (1264..2100 px); CPSIA |
| Tazza | 441 / 30 OPT CZ | europa | 1790 / 2190 | stampa su ENTRAMBI i lati (`--tazza entrambi`); il mockup Printify mostra il lato opposto al manico |
| Tote | 731 / 26 Textildruck DE | europa | 2490 | |
| Berretto ricamato | 1691 / 410 Printful | usa_europa | 2990 | fili Printful con `prepara_cappello.py --fili`; personalizzazione nome: max 8 lettere A-Z, controllo ordine per ordine |
| Berretto cotone | 5254 / 217 Fulfill Engine | usa | 2990 | senza risvolto; verso l'Europa costa troppo |
| Sciarpa leggera | 1327 / 99 Printify Choice | usa | 4290 | 69x180 cm, voile poliestere; area ~155 DPI reali (limite Printify) |
| Calza di Natale EU | 850 / 72 | europa | 2990 | fronte disegno, retro solo pattern |
| Calza di Natale USA | 380 / 99 Printify Choice | usa | 3490 | fleece, fronte+retro |
| Carta da regalo EU | 845 / 69 | europa | 1990 / 2990 | JPEG: Printify rifiuta upload ~32 MB (413), 16 MB ok |
| Carta da regalo USA | 1100 / 99 Printify Choice | usa | 2990 / 3990 | area ~200 DPI reali (limite Printify); controllare mockup bianchi |
| Libro da colorare | 2721 | usa | 28 District Photo (stabilimento unico, Beltsville MD: serve per l'etichetta CPSIA) | 6 libri online; 8,16 $ + sped. USA 5,49 $; per l'Europa (e tutto il mondo) i PDF digitali 22 |

## Fatti utili

- Nessuno stampatore europeo su Printify per berretti, libri da colorare, sciarpe, calendari, decorazioni.
- Printify riscala un file (area piu' grande) su tutte le taglie; la taglia la sceglie il cliente su Etsy.
- I profili di spedizione Printify sono condivisi per stampatore: dopo ogni pubblicazione `pubblica.py` li rifila.
- USA: spedizione gratis inclusa nel prezzo (`TARIFFE_FISSE` in `pubblica.py`); magliette: il Canada paga la differenza.
