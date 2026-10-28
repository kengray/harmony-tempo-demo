# Harmony tempo demo (proof of concept)

Shows one way to give a harmony practice player a speed control: **make slower copies of each part once, offline, and let the page switch files.** Dummy audio only (generated tones, not anyone's songs).

## Versions
- v1: first standalone tempo demo (as the slow-down demo).
- v2: renamed Harmony tempo demo, desktop-only note, master volume stage (the four parts clipped at default faders), no overlapping parts after quick clicks. The version shows next to the heading.
- v3: a real tune instead of near-constant tones, so "Loop bars 3 and 4" is audible (the old loop section held almost one pitch). Harmony parts a third above and below the lead, each bar different.
- v4: audio and melody requests carry the version number, so a browser cannot show old audio after an update.
- v5: slower files made with a shorter Rubber Band window (`window=short`), which removes most of the reverb-like tail on the slowed plucked notes.
- v6: the dummy parts no longer have vibrato. Stretching slows a vibrato with the song (5.5 Hz becomes 4.4 Hz at 80% and 3.6 Hz at 65%), which was heard as a warble on every note.
- v7: slower files made with Rubber Band in offline mode (R3 "finer" engine) through `prerender.py`. The ffmpeg filter used before works in real-time mode and left a wobble on steady notes at 65%. Measured on the lead: level wobble 1.0 dB to 0.15 dB, pitch swing 29 cents to 0.4 cents; reverb-like tail on plucks 0.044 to 0.003.
- v8: iPad and iPhone fix. The audio is now created and resumed straight from the tap (Safari ignores it otherwise), the page asks for the "playback" audio session so the mute switch does not silence it, and it says so on the page if the device still blocks audio. Same fix the offline demo already had.
- v9: 20 ms fade out of the old parts and fade in of the new ones when switching speed, pausing or looping the start, to remove the click.
- v10: the device note on the page and in this README now says what was checked (desktop, Android phone, iPad).

## Run it
The page loads audio with fetch, so it needs a web server, not a double-click:

    python3 -m http.server 8000
    # then open http://localhost:8000/

**Checked on:** a desktop browser, an Android phone and an iPad (by ear, by Ken). Not yet tried on an iPhone.

This demo is separate from the offline demo (offline-harmony-demo). Suggested repository name: `harmony-tempo-demo`.

## What it does
- Four parts (guitar, lead, tenor, baritone), 100 bpm, 8 bars, at 100%, 80% and 65%.
- Switching speed while playing keeps your place in the song and restarts all four parts at the same instant.
- "Loop bars 3 and 4" keeps working at every speed.
- A "Method" switch lets you compare with the simple approach (just slow the playback), where the pitch drops. The page measures the lead part's pitch and shows expected against heard.

## What the checks showed (headless Chromium, `python3 tests/run.py`)
- Place kept when switching speed: pass (moves forward, no jump back).
- Four parts start together: pass.
- Pre-rendered 80%: lead pitch within about 1 cent of expected.
- Plain slow-down at 80%: pitch drops by 386 cents (about four semitones), as the arithmetic says.
- Loop stays inside bars 3 and 4 at 65%: pass.
- File sizes: constant 128 kbps, so size follows duration: the 80% files are 1.25 times the size of the 100% files, the 65% files 1.54 times.

## What this does not show
- **Vibrato on real voices.** Time-stretching slows a singer's vibrato by the same factor as the song, so a slowed vocal wobbles more slowly than the singer would. The dummy parts have no vibrato so this cannot be heard here.
- **How it sounds on real voices.** Tones are easy to stretch. Real harmony vocals can pick up artefacts, so listen to a real song before choosing the stretch settings.
- iPhone: not tried. Android and iPad were checked by ear.
- How the key slider behaves together with a slow copy (the demo has no key control).

## Making the files
    python3 gen_audio.py     # the four 100% parts and melody.json
    python3 prerender.py     # Rubber Band (offline, R3 engine) slow copies at 80% and 65%, mp3 128 kbps

Needs ffmpeg, numpy and scipy. `prerender.py` calls the Rubber Band library (librubberband, version 3 or later) directly through `rubberband_offline.py`, because ffmpeg's rubberband filter cannot use the offline mode or the finer engine. On Debian or Ubuntu: `apt install librubberband2`.
