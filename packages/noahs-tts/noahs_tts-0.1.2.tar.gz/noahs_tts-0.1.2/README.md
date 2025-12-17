## Usage: `noahs_tts`

### Getting Started

First, install the library:

```bash
pip install noahs_tts
```

## Quick start

```python
from noahs_tts import TTS  # if you saved the class in tts.py

tts = TTS()
tts.say("Hello world!")  # blocks until finished
```

Speak sentence-by-sentence (default) for snappier responsiveness:

```python
tts.say("First sentence. Second sentence! Third sentence?")
```

Speak the whole string as one chunk:

```python
tts.say("This will be spoken as a single utterance.", split_sentences=False)
```

Speak the contents of a stream generator:

```python
def example_generator():
    for s in ["hello there", "this is a stream", "last chunk here"]:
        yield s

tts.say_stream(example_generator())
```

---

## Voice management

List available voices (id, name, locale, gender when available):

```python
voices = tts.voices()
for v in voices:
    print(v["id"], v["name"], v["locale"], v["gender"])
```

Pick a voice by **name** or **id** (partial match allowed):

```python
tts = TTS(voice="Zira")          # Windows example
tts = TTS(voice="Samantha")      # macOS example
tts = TTS(voice="english-us")    # Linux/eSpeak example
```

---

## Control rate

Rate is engine-specific “words per minute” style. This wrapper casts to `int`.

```python
tts = TTS(rate=180)      # set default on init
tts.say("Speaking at 180 wpm (approx).")

tts.say("Speed this one up.", split_sentences=False)
```

You can also override per-call when saving/synthesizing:

```python
data = tts.synth("Faster line.", rate=220)
```

---

## Save audio

Get WAV bytes:

```python
wav_bytes = tts.synth("Save me to a file later.")
with open("out.wav", "wb") as f:
    f.write(wav_bytes)
```

Or save directly:

```python
tts.save("Write this straight to disk.", "speech.wav", voice="Samantha", rate=170)
```

---


### Check out Source Code

`https://github.com/jonesnoah45010/noahs_tts`




