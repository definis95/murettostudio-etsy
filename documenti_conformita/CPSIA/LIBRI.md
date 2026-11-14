# CPSIA – libri da colorare USA (21, 21b, 21c, 21d, 21e, 21f)

Prodotto: Printify blueprint 2721 "Coloring Book" 8.5 x 11 in, copertina morbida lucida, 24 pagine carta 60 lb
(Soporset Opaque Smooth Text), stampa digitale. Stampatore scelto da Dario il 14/11: **District Photo**
(Printify provider 28), 10501 Rhode Island Ave, Beltsville MD 20705, USA (un solo stabilimento, dato dell'API
Printify). Fascia d'eta': 4-8 anni.

## Cosa dice la CPSC (letto il 14/11/2026)
- Il libro da colorare per bambini e' un prodotto per bambini (12 anni o meno): serve un certificato (CPC)
  emesso da chi lo mette in vendita col proprio marchio (MurettoStudio = private labeler).
- "Ordinary book" (carta o cartone, inchiostri o toner, rilegatura normale, "intended to be read or has
  educational value"): niente test di laboratorio sul piombo; nel CPC, sezione 6, si cita PL 112-28.
  Escluse: libri per bambini di 3 anni o meno e libri "with inherent play value". I libri da colorare non sono
  citati: caso dubbio (https://cpsc.gov/FAQ/Childrens-Books).
- In ogni caso la carta e gli inchiostri CMYK da stampa su carta non richiedono test di laboratorio per il
  piombo (determinazioni 16 CFR 1500.91, https://www.cpsc.gov/FAQ/Total-Lead-Content).
- Etichetta di tracciabilita' (CPSIA sez. 14(a)(5)): segni permanenti sul prodotto con chi lo vende, dove e
  quando e' stato prodotto, lotto.

## Etichetta (stampata sul retro della copertina dal 14/11, `libro_colorare.py` -> `etichetta`)
```
MurettoStudio · Polignano a Mare, Italy
Printed on demand in the USA by District Photo, Beltsville, MD
Batch MS-<id>-2611 · Date of production: see the order date on the packing slip
Children's product for ages 4-8 · Conforms to CPSIA
```
Il lotto (2611 = novembre 2026) cambia quando si ristampano pagine o copertina (`LOTTO` nello script).
Sul libro non va l'indirizzo completo: sta nel certificato.

## Certificato (CPC) – uno per libro, cambia solo la riga 1
1. Prodotto: "<titolo Etsy> – children's coloring book, 8.5 x 11 in, 24 pages, soft cover", lotto MS-<id>-2611.
2. Regole: CPSIA sez. 101 (piombo nel substrato) e 16 CFR 1303 (piombo nelle vernici di superficie).
3. Chi certifica (private labeler): Dario De Finis, MurettoStudio, Traversa di Via Vivarini 6, 70044 Polignano a
   Mare (BA), Italia, definis95@yahoo.it.
4. Chi conserva i documenti dei test: lo stesso.
5. Data e luogo di produzione: stampa su ordine dal novembre 2026 presso District Photo, 10501 Rhode Island Ave,
   Beltsville MD 20705, USA.
6. Base della conformita': prodotto di carta stampato con inchiostri/toner per carta, esente dal test di terza
   parte per il piombo (PL 112-28, "ordinary book / ordinary paper-based printed material"; 16 CFR 1500.91).
7. Laboratorio: nessuno (esenzione).

## Domande ancora aperte (non bloccano la pubblicazione)
Printify non ha un'API per i messaggi all'assistenza: le domande si fanno dalla chat di Printify.
- Rilegatura (punti metallici o colla) e copertina (plastificata o verniciata): l'esenzione vale per entrambe
  le rilegature normali; da confermare che non ci siano parti in plastica.
- Date di Natale 2026 di District Photo per gli USA: la tabella di Printify
  (printify.com/network-fulfillment-status) si legge solo nel browser. In `natale.py` messe date prudenti
  (ordini USA entro il 2/12, Canada entro il 28/11).

## Cronologia
**14 nov 2026** – Titoli e descrizioni dei 6 libri portati a "ages 4-8" (tolto "toddlers") per restare fuori
dall'esclusione dei libri per bambini di 3 anni o meno; corretto il tempo di produzione (circa 10 giorni).
Dario sceglie District Photo; etichetta aggiunta sul retro delle 6 copertine.
