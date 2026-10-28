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
# G, C, D, G progression, two bars each pair. Frequencies in Hz.
G = dict(root=98.00, bar=196.00, baritone=196.00, lead=392.00, tenor=493.88)
C = dict(root=130.81, bar=261.63, baritone=261.63, lead=523.25, tenor=659.26)
D = dict(root=146.83, bar=293.66, baritone=293.66, lead=587.33, tenor=739.99)
chords = [G, G, C, C, D, D, G, G]  # one per bar
def voice(freqs_per_beat, vib=True):
    out = np.zeros(n)
    for b in range(beats):
        s, e = int(b * beat * sr), int((b + 1) * beat * sr)
        f = freqs_per_beat[b]
        tt = np.arange(e - s) / sr
        v = 1 + (0.004 * np.sin(2 * np.pi * 5.5 * tt) if vib else 0)
        ph = 2 * np.pi * np.cumsum(f * v) / sr
        w = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
        env = np.minimum(1, tt / 0.03) * np.minimum(1, (beat - tt) / 0.05)
        out[s:e] = w * env
    return out
lead_notes = []
for bar, ch in enumerate(chords):
    for k in range(4):
        # a simple pattern: lead goes up a whole tone on beat 3 of each bar so the pitch is not constant
        f = ch['lead'] * (1.122462 if k == 2 else 1.0)
        lead_notes.append(round(f, 2))
tenor = [chords[b // 4]['tenor'] for b in range(beats)]
bari = [chords[b // 4]['baritone'] for b in range(beats)]
# guitar: a pluck on every beat (root), so the tempo is easy to hear
guitar = np.zeros(n)
for b in range(beats):
    s = int(b * beat * sr)
    f = chords[b // 4]['root'] * (2 if b % 4 in (1, 3) else 1)
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
