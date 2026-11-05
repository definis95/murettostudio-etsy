# genera le pagine mancanti dei libri 21-21f; se finisce la quota ChatGPT aspetta 30 minuti e riprova (max 60 giri = 30 ore). Avanzamento in stampa/libri_ciclo_log.txt
cd "/c/Users/defin/Downloads/market place etsy"
export PATH="/c/Users/defin/AppData/Roaming/npm:/c/Program Files/nodejs:$PATH"
for giro in $(seq 1 60); do
  mancano=0
  for b in 21 21b 21c 21d 21e 21f; do
    n=$(ls stampa/${b}_2721/pagine/*_chatgpt.png 2>/dev/null | wc -l)
    if [ "$n" -lt 24 ]; then
      mancano=1
      .venv/Scripts/python strumenti_grafiche/libro_colorare.py genera $b >> stampa/${b}_2721/log_genera.txt 2>&1
      n=$(ls stampa/${b}_2721/pagine/*_chatgpt.png 2>/dev/null | wc -l)
      echo "$(date "+%d/%m %H:%M") $b: $n/24" >> stampa/libri_ciclo_log.txt 
      [ "$n" -lt 24 ] && break
    fi
  done
  [ "$mancano" = 0 ] && break
  n=$(ls stampa/21f_2721/pagine/*_chatgpt.png 2>/dev/null | wc -l); [ "$n" -ge 24 ] && break
  sleep 1800
done
for b in 21b 21c 21d 21e 21f; do mkdir -p stampa/${b}_2721; echo "$b $(ls stampa/${b}_2721/pagine/*_chatgpt.png 2>/dev/null | wc -l)/24"; done
