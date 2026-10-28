# Makes four dummy stems (guitar, lead, tenor, baritone) at 100 bpm, 8 bars, 44.1 kHz mono WAV,
# plus melody.json with the lead's note per beat (so the page can show expected vs heard pitch).
# Run from this folder: python3 gen_audio.py
import json, os
import numpy as np
from scipy.io import wavfile
sr = 44100
bpm = 100
beat = 60 / bpm
bars = 8
beats = bars * 4
n = int(sr * beat * beats)
t = np.arange(n) / sr
# A short tune in G major, one note per beat, with the harmony parts a third above (tenor) and a third below (baritone)
# so the parts move together and each bar sounds different. Bars 3 and 4 (the loop) climb and turn, so a loop is easy to hear.
STEP = [0, 2, 4, 5, 7, 9, 11]                       # major scale in semitones
def hz(d): return 392.00 * 2 ** (((d // 7) * 12 + STEP[d % 7]) / 12)   # degree 0 = G4
tune = [0, 1, 2, 4,   4, 2, 1, 0,   3, 4, 5, 4,   3, 5, 4, 2,   4, 5, 6, 7,   7, 6, 4, 2,   4, 2, 1, 0,   0, 1, 0, 0]
roots = [98.00, 98.00, 130.81, 146.83, 146.83, 130.81, 146.83, 98.00]    # G G C D D C D G, one per bar
def voice(freqs_per_beat, vib=True):
    out = np.zeros(n)
    for b in range(beats):
        s, e = int(b * beat * sr), int((b + 1) * beat * sr)
        f = freqs_per_beat[b]
        tt = np.arange(e - s) / sr
        v = 1 + (0.004 * np.sin(2 * np.pi * 5.5 * tt) if vib else 0)
        ph = 2 * np.pi * np.cumsum(f * v) / sr
        w = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
        env = np.minimum(1, tt / 0.02) * np.minimum(1, np.maximum(0, (beat * 0.82 - tt)) / 0.06)   # a short gap between notes
        out[s:e] = w * env
    return out
lead_notes = [round(hz(d), 2) for d in tune]
tenor = [hz(d + 2) for d in tune]
bari = [hz(d - 2) for d in tune]
# guitar: a pluck on every beat (root, then octave), so the tempo is easy to hear
guitar = np.zeros(n)
for b in range(beats):
    s = int(b * beat * sr)
    f = roots[b // 4] * (2 if b % 4 in (1, 3) else 1)
    tt = np.arange(int(0.45 * sr)) / sr
    p = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(4 * np.pi * f * tt) + 0.3 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7)
    guitar[s:s + len(p)] += p
stems = {'guitar': guitar, 'lead': voice(lead_notes), 'tenor': voice(tenor), 'baritone': voice(bari)}
os.makedirs('audio', exist_ok=True)
for name, x in stems.items():
    x = x / np.max(np.abs(x)) * 0.6
    wavfile.write(f'audio/{name}-100.wav', sr, (x * 32767).astype(np.int16))
json.dump({'bpm': bpm, 'beat': beat, 'beats': beats, 'duration': beat * beats, 'lead': lead_notes}, open('melody.json', 'w'))
print('done', beat * beats, 's')
