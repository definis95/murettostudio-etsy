"""Ponte Claude -> ChatGPT: fa disegnare un'immagine a ChatGPT tramite Codex CLI.

Codex CLI e' collegato all'abbonamento ChatGPT (codex login): la generazione usa la quota
del piano, non crediti API, e non serve nessuna chiave OpenAI.

Uso:
  python strumenti_grafiche/chatgpt_bridge.py --prompt-file brief.txt --out grafiche/xx/nome.png
  opzioni: --formato verticale|orizzontale|quadrato   (default verticale)
           --opaco                                     (sfondo pieno invece che trasparente)
           --riferimento file.png                      (immagine da usare come riferimento, ripetibile)
           --modello gpt-6-astra --impegno medium      (modello che guida e controlla il disegno)
           --bozza                                     (una sola generazione, senza controllo: per le proposte)

Il brief (scritto da Claude) descrive soggetto, stile, colori e vincoli di stampa.
Il modello (Astra) non disegna: guida il generatore di immagini di ChatGPT, controlla il
risultato contro il brief e lo rifa' (max 1 volta) solo per errori veri (testo, tagli, sfondo).
Il file prodotto e' l'immagine originale di ChatGPT (circa 1024x1536): per la stampa va poi
passato a prepara_stampa.py.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMATI = {"verticale": "portrait (2:3)", "orizzontale": "landscape (3:2)", "quadrato": "square (1:1)"}

ISTRUZIONI = """You are the art director driving the built-in image_gen tool. Follow exactly:
1. Use only the built-in image_gen tool (never the CLI fallback, never an API key, never draw with code).
2. Format: {formato}. Background: {sfondo}.
3. Do not add anything that is not in the brief. Any text in the brief must be spelled exactly.
{riferimenti}{controllo}5. Copy the chosen PNG into the current directory as {nome}. Do not create or modify any other file.
6. Reply with one line: the final path, then a short note of any remaining defect (or "ok").

BRIEF:
{brief}
"""
RIFERIMENTI = ("   The attached image(s) are references: {uso}\n")
CONTROLLO = """4. Look at the result with view_image. Regenerate (at most 1 retry) ONLY for real blockers:
   a misspelled or missing word, an element cut off at the edges, wrong subject, a background that
   should be transparent but is not, extra text or watermark. Do NOT regenerate for minor shading,
   grain, slight palette shifts or edge noise: those are fixed later in print preparation.
"""
BOZZA = "4. This is a quick draft: generate ONCE, do not review or regenerate.\n"


CODEX_HOME = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def pulisci_codex(output_json):
    """Codex tiene una copia di ogni immagine in ~/.codex/generated_images/<id sessione>/:
    l'immagine utile e' gia' nel progetto, quindi cancella la cartella di QUESTA sessione
    (comprese le versioni scartate). Lo storico non viene salvato (--ephemeral)."""
    for riga in output_json.splitlines():
        try:
            evento = json.loads(riga)
        except ValueError:
            continue
        if evento.get("type") == "thread.started" and evento.get("thread_id"):
            cartella = CODEX_HOME / "generated_images" / evento["thread_id"]
            shutil.rmtree(cartella, ignore_errors=True)
            return


def codex_exe():
    exe = shutil.which("codex") or shutil.which("codex.cmd")
    if not exe:
        npm = Path(os.environ.get("APPDATA", "")) / "npm" / "codex.cmd"
        exe = str(npm) if npm.exists() else None
    if not exe:
        raise SystemExit("Codex CLI non trovato: installalo con  npm install -g @openai/codex")
    return exe


def genera(brief, out, formato="verticale", trasparente=True, riferimenti=(), uso_riferimenti="",
           modello="gpt-6-astra", impegno="medium", controllo=True, timeout=900):
    out = Path(out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    sfondo = ("fully TRANSPARENT (real alpha channel), no backdrop, no shadow, no frame"
              if trasparente else "as described in the brief")
    rif = RIFERIMENTI.format(uso=uso_riferimenti or "follow them as described in the brief") if riferimenti else ""
    with tempfile.TemporaryDirectory() as tmp:
        nome = "immagine.png"
        risposta = Path(tmp) / "risposta.txt"
        prompt = ISTRUZIONI.format(formato=FORMATI[formato], sfondo=sfondo, nome=nome, riferimenti=rif,
                                   controllo=CONTROLLO if controllo else BOZZA, brief=brief.strip())
        cmd = [codex_exe(), "exec", "--skip-git-repo-check", "--ephemeral", "--json", "-s", "workspace-write",
               "-m", modello, "-c", f'model_reasoning_effort="{impegno}"',
               "-C", tmp, "-o", str(risposta)]
        for r in riferimenti:
            cmd += ["-i", str(Path(r).resolve())]
        cmd.append("-")
        t0 = time.time()
        r = subprocess.run(cmd, input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=timeout)
        pulisci_codex(r.stdout)
        risultato = Path(tmp) / nome
        if not risultato.exists():
            coda = (r.stdout + r.stderr)[-1500:]
            raise SystemExit(f"ChatGPT non ha prodotto l'immagine (exit {r.returncode}).\n{coda}")
        nota = risposta.read_text(encoding="utf-8").strip().splitlines()[-1] if risposta.exists() else ""
        nota = nota.split(" — ", 1)[-1].replace(str(risultato), "").strip()  # via il percorso temporaneo
        shutil.move(risultato, out)
    print(f"Immagine generata da ChatGPT ({modello}) in {time.time() - t0:.0f}s -> {out.relative_to(ROOT)}"
          f"  [{nota}]")
    return out, nota


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--formato", choices=FORMATI, default="verticale")
    ap.add_argument("--opaco", action="store_true")
    ap.add_argument("--riferimento", action="append", default=[])
    ap.add_argument("--modello", default="gpt-6-astra")
    ap.add_argument("--impegno", default="medium")
    ap.add_argument("--bozza", action="store_true")
    a = ap.parse_args()
    brief = Path(a.prompt_file).read_text(encoding="utf-8")
    genera(brief, a.out, a.formato, trasparente=not a.opaco, riferimenti=a.riferimento,
           modello=a.modello, impegno=a.impegno, controllo=not a.bozza)


if __name__ == "__main__":
    main()
