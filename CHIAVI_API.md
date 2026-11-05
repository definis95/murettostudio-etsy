# Chiavi API: dove sono, come vederle, come rifarle

Le chiavi stanno SOLO nel file `.env`, in questa cartella. Quel file non va mai condiviso e non deve finire
nel repository git (è escluso da `.gitignore`). Nel repository c'è invece `.env.example`, con i soli nomi
delle variabili e senza valori.

## Cosa deve contenere `.env`

```
ETSY_KEYSTRING=...        chiave dell'app Etsy (keystring)
ETSY_SHARED_SECRET=...    segreto dell'app Etsy (shared secret)
PRINTIFY_TOKEN=...        token personale Printify
```
Gli script accettano anche i nomi brevi `keystring` e `shared_secret`, maiuscoli o minuscoli.

Per ricrearlo da zero: copia `.env.example`, rinominalo `.env` e incolla i valori presi dai siti
(istruzioni sotto).

---

## 1. Etsy: keystring e shared secret

**Dove vederli**
1. Accedi a Etsy con l'account del negozio.
2. Apri **https://www.etsy.com/developers/your-apps** (pagina "Your Apps" / "Manage your apps").
3. Accanto all'app **dario-shop-tools** apri **"See API Key Details"** (il "+" accanto all'app).
4. Lì trovi **Keystring** e **Shared secret**, e lo **stato** dell'app (approvata).

**Se il shared secret è stato esposto (o va cambiato)**
1. Dalla stessa pagina apri l'app → **Rotate shared secret** → **Generate a new secret**.
2. Copia il nuovo segreto in `.env` (`ETSY_SHARED_SECRET`).
3. Controlla che funzioni: `python inspect_shop.py`.
4. Torna su Etsy → **I've completed the rotation** e conferma: il vecchio segreto viene cancellato.
   Finché non confermi, funzionano tutti e due. Etsy chiude la rotazione da sola dopo un periodo indicato nella
   pagina e manda una mail 2 giorni prima.

**Indirizzo di ritorno del login (redirect URI)**
Si modifica dalla stessa pagina "Your Apps" → modifica app. Deve essere identico a quello usato da
`etsy_auth.py`: `http://localhost:3003/oauth/redirect` (Etsy controlla maiuscole, barre finali, tutto).

## 2. Etsy: token di accesso (file `.etsy_tokens.json`)

Non è una chiave che si copia da un sito: lo crea il login.
- Si crea con `python etsy_auth.py`: si apre il browser, clicchi **Allow access**, e lo script salva i token
  in `.etsy_tokens.json`.
- Valgono 1 ora e si rinnovano da soli per 90 giorni. Se uno script dice "rifai il login", rilancia
  `python etsy_auth.py`.
- Anche questo file è segreto ed è escluso da git.

## 3. Printify: token personale (`PRINTIFY_TOKEN`)

**Dove vederlo / crearlo**
1. Accedi a Printify.
2. Menu account → **My Profile** → **Connections** (oppure direttamente
   **https://printify.com/app/account/api**).
3. Nella sezione dei **Personal Access Tokens** vedi i token esistenti (nome, scadenza) e puoi revocarli o
   generarne uno nuovo, scegliendo i permessi (scopes).

**Attenzione**
- Printify mostra il valore del token **una sola volta**, quando lo generi. Dopo non si può più rileggerlo
  dal sito: se lo perdi, ne generi uno nuovo, lo metti in `.env` e revochi il vecchio.
- Il token **scade dopo 1 anno**. Il nostro è stato creato il 30/10/2026, quindi va rifatto entro fine ottobre
  2027.
- Prova: `python printify_catalog.py --check`.

## 4. ChatGPT (Codex)

Nessuna chiave nel progetto: Codex usa il login all'abbonamento ChatGPT, salvato nel profilo utente di Windows
(cartella `.codex`), fuori dal progetto.
- Controllo: `codex login status` → deve dire "Logged in using ChatGPT".
- Nuovo login: `codex login`.

---

## Prima del primo commit git

1. Controlla che i file segreti siano esclusi:
   `git check-ignore -v .env .etsy_tokens.json` → deve stampare una riga per ciascuno.
2. Dopo `git add .`, `git status` NON deve mostrare `.env` né `.etsy_tokens.json`.
3. Se una chiave finisce per errore in un commit (o online), cancellarla dal repository non basta:
   **rigenerala subito** (rotazione Etsy, nuovo token Printify) e aggiorna `.env`.
