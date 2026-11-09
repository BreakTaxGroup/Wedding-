#!/usr/bin/env bash
# Prepara la apertura a partir del video de Higgsfield (9:16, 1080x1920).
# Uso: tools/prep_apertura.sh VIDEO_HIGGSFIELD SAVE_THE_DATE.mp4 invitacion/media
set -euo pipefail
V="$1"; STD="$2"; OUT="$3"
ffmpeg -v error -y -ss 1.6 -i "$V" -c:v libx264 -preset slow -crf 21 -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -af "afade=t=in:st=0:d=0.15,volume=1.6" -c:a aac -b:a 160k "$OUT/apertura.mp4"
ffmpeg -v error -y -ss 0.25 -t 1.35 -i "$V" -filter_complex "[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0,scale=720:-2" \
  -an -c:v libx264 -preset slow -crf 25 -pix_fmt yuv420p -movflags +faststart "$OUT/espera.mp4"
ffmpeg -v error -y -ss 1.6 -i "$V" -frames:v 1 -q:v 2 "$OUT/apertura-poster.jpg"
ffmpeg -v error -y -sseof -0.05 -i "$V" -frames:v 1 -vf "crop=940:1410:70:150" -q:v 3 "$OUT/tarjeta.jpg"
ffmpeg -v error -y -ss 7.6 -i "$STD" -vn -af "afade=t=in:st=0:d=1.2,afade=t=out:st=37.5:d=1.8,loudnorm=I=-20:TP=-2:LRA=11" \
  -c:a libmp3lame -b:a 128k "$OUT/musica.mp3"
ls -la "$OUT"
