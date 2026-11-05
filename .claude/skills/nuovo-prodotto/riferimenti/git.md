# Repository GitHub, revisione, commit e push

- Repository **privato** `definis95/murettostudio-etsy` su GitHub, creato il 05/11/2026. Contiene tutto il
  progetto, immagini comprese: fa anche da backup di grafiche e originali ChatGPT.
- Accesso: GitHub CLI `gh` collegato all'account definis95 (`gh auth status`). Protocollo https.
- Esclusi da `.gitignore`: `.env*` (tranne `.env.example`), file `*_tokens.json`, `.venv/`, `__pycache__/`.
- Limite GitHub: 100 MB per file. Prima di aggiungere file grandi (es. stampe di carta/sciarpe) controlla le
  dimensioni; sopra i 50 MB GitHub avvisa, sopra i 100 MB rifiuta il push.

## Flusso di lavoro (regola 8)

1. Lavora e prova le modifiche (script lanciati, `verifica.py` dove serve).
2. Mostra a Dario cosa e' cambiato: `git status` + `git diff --stat`, e a parole le modifiche al codice
   (file, cosa fa di diverso, esito delle prove). Per i file di immagini basta l'elenco.
3. 🛑 **Aspetta l'ok di Dario.** Senza ok non si fa ne' commit ne' push.
4. Dopo l'ok: `git add` dei file mostrati (mai `git add` di file non visti), controlla che `.env` e i token non
   compaiano in `git status`, commit, `git push`.
5. Se Dario chiede modifiche: correggi e torna al punto 2.

## Messaggi di commit
- In italiano, prima riga breve con cosa cambia (es. "pubblica.py: fissa la copertina come ultima operazione"),
  poi eventuali dettagli.
- Ultima riga: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Un commit per argomento quando possibile (codice, skill, nuove immagini di un prodotto).

## Cose da non fare
- Niente `push --force`, riscritture della storia o cancellazione di rami senza richiesta esplicita di Dario.
- Se una chiave finisce in un commit: fermarsi, avvisare Dario, rigenerarla (vedi `CHIAVI_API.md`).
