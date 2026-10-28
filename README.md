# Harmony tempo demo (proof of concept)

Shows one way to give a harmony practice player a speed control: **make slower copies of each part once, offline, and let the page switch files.** Dummy audio only (generated tones, not anyone's songs).

## Versions
- v1: first standalone tempo demo (as the slow-down demo).
- v2: renamed Harmony tempo demo, desktop-only note, master volume stage (the four parts clipped at default faders), no overlapping parts after quick clicks. The version shows next to the heading.
- v3: a real tune instead of near-constant tones, so "Loop bars 3 and 4" is audible (the old loop section held almost one pitch). Harmony parts a third above and below the lead, each bar different.

## Run it
The page loads audio with fetch, so it needs a web server, not a double-click:

    python3 -m http.server 8000
    # then open http://localhost:8000/

**Desktop only so far.** The tempo control has been built and checked in a desktop browser. It has not been tried on phones or tablets.

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
- **How it sounds on real voices.** Tones are easy to stretch. Real harmony vocals can pick up artefacts, so listen to a real song before choosing the stretch settings.
- Phones and Safari: only checked in desktop Chromium, not by ear and not on an iPhone.
- How the key slider behaves together with a slow copy (the demo has no key control).

## Making the files
    python3 gen_audio.py     # the four 100% parts and melody.json
    sh prerender.sh          # Rubber Band (via ffmpeg) slow copies at 80% and 65%, mp3 128 kbps

Needs ffmpeg built with the rubberband filter, numpy and scipy.
