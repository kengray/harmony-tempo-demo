#!/bin/sh
# Makes the pre-rendered slow versions with Rubber Band (through ffmpeg) and 128 kbps mp3s.
# Speeds: 100 (as made), 80, 65 per cent. Pitch is kept; only the tempo changes.
# Run from this folder after gen_audio.py: sh prerender.sh
set -e
for v in guitar lead tenor baritone; do
  ffmpeg -y -loglevel error -i audio/$v-100.wav -b:a 128k audio/$v-100.mp3
  for s in 80 65; do
    t=$(python3 -c "print($s/100)")
    ffmpeg -y -loglevel error -i audio/$v-100.wav -af "rubberband=tempo=$t" -b:a 128k audio/$v-$s.mp3
  done
done
rm -f audio/*.wav
ls -l audio
