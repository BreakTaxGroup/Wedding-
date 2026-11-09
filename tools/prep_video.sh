#!/usr/bin/env bash
# Prepara el video de los novios: lo endereza (venía girado 90°), quita el marco oscuro redondeado
# y genera el fondo en loop (sin texto ni audio) y el save the date completo (con audio).
# Uso: tools/prep_video.sh VIDEO_ORIGINAL invitacion/media
set -euo pipefail
SRC="$1"; OUT="$2"
VF="transpose=1,crop=1216:684:32:18,scale=1280:720:flags=lanczos,setsar=1"
# Fondo: tramo limpio 9.0 s – 42.0 s, sin audio, ligero para el celular
ffmpeg -v error -y -ss 9.0 -to 42.0 -i "$SRC" -vf "$VF,fps=30" -an \
  -c:v libx264 -preset slow -crf 27 -pix_fmt yuv420p -profile:v high -movflags +faststart "$OUT/novios-fondo.mp4"
ffmpeg -v error -y -ss 18.5 -i "$SRC" -frames:v 1 -vf "$VF" -q:v 3 "$OUT/novios-poster.jpg"
# Save the date completo: desde que aparece el texto (3.4 s) hasta el final, con su audio
ffmpeg -v error -y -ss 3.4 -i "$SRC" -vf "$VF,fps=30" \
  -c:v libx264 -preset slow -crf 24 -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 128k "$OUT/save-the-date.mp4"
ffmpeg -v error -y -ss 46.5 -i "$SRC" -frames:v 1 -vf "$VF" -q:v 3 "$OUT/save-the-date-poster.jpg"
ls -la "$OUT"
