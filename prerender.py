# Makes the pre-rendered slow versions with Rubber Band in offline mode (the "finer" R3 engine) and 128 kbps mp3s.
# Pitch is kept; only the tempo changes. Needs librubberband (Linux: apt install librubberband2) and numpy/scipy.
# Offline mode matters: ffmpeg's rubberband filter works in real-time mode and left a 1 dB / 25 cent wobble on steady notes at 65%;
# offline R3 leaves about 0.2 dB / 1 cent.
# Run from this folder after gen_audio.py:  python3 prerender.py
import os, subprocess, sys, numpy as np
from scipy.io import wavfile
import rubberband_offline as rb
OPTS = rb.ENGINE_FINER | rb.WINDOW_SHORT
for v in ['guitar', 'lead', 'tenor', 'baritone']:
    sr, x = wavfile.read(f'audio/{v}-100.wav'); x = x.astype(np.float32) / 32768
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'audio/{v}-100.wav', '-b:a', '128k', f'audio/{v}-100.mp3'], check=True)
    for s in (80, 65):
        y = rb.stretch(x, sr, s / 100, OPTS)
        wavfile.write(f'audio/{v}-{s}.wav', sr, (np.clip(y, -1, 1) * 32767).astype(np.int16))
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'audio/{v}-{s}.wav', '-b:a', '128k', f'audio/{v}-{s}.mp3'], check=True)
for f in os.listdir('audio'):
    if f.endswith('.wav'): os.remove('audio/' + f)
print(sorted(os.listdir('audio')))
