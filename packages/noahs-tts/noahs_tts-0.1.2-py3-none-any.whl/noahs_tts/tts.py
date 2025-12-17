
import pyttsx3
import re
import sys
import shutil
import threading
import time
import subprocess
from typing import Optional

class TTS:
    def __init__(self, voice: Optional[str] = None, rate: Optional[float] = None):
        self.engine = pyttsx3.init()
        self._lock = threading.Lock()  # prevent concurrent calls
        if voice:
            self._set_voice(voice)
        if rate:
            self.engine.setProperty('rate', int(rate))

    def voices(self):
        out = []
        for v in self.engine.getProperty('voices'):
            out.append({
                "id": v.id,
                "name": getattr(v, "name", v.id),
                "locale": getattr(v, "languages", [None])[0],
                "gender": getattr(v, "gender", None),
            })
        return out

    def _set_voice(self, voice_id_or_name: str):
        for v in self.engine.getProperty('voices'):
            if voice_id_or_name.lower() in (v.id.lower(), getattr(v, "name", "").lower()):
                self.engine.setProperty('voice', v.id)
                return

    def _split_sentences(self, t: str):
        return re.split(r'(?<=[.!?])\s+', t.strip())

    def say(self, text: str, split_sentences: bool = True, *, block: bool = True, prefer_system_on_mac: bool = True):
        """
        Speak text and (by default) block until finished.

        - split_sentences: break text into sentences and speak each in sequence.
        - block: if False, returns immediately (not recommended for your case).
        - prefer_system_on_mac: if True and on macOS, use the 'say' CLI if available (reliable blocking).
        """
        if not block:
            # Non-blocking is out of scope for your request, but keep it possible.
            if split_sentences:
                for chunk in self._split_sentences(text):
                    self.engine.say(chunk)
            else:
                self.engine.say(text)
            # Do not call runAndWait -> returns immediately
            return

        # Ensure only one caller uses the engine at a time
        with self._lock:
            # macOS 'say' CLI is synchronous and reliable; use it if desired and available
            if prefer_system_on_mac and sys.platform == "darwin" and shutil.which("say"):
                if split_sentences:
                    for chunk in self._split_sentences(text):
                        subprocess.run(["say", chunk], check=True)
                else:
                    subprocess.run(["say", text], check=True)
                return

            # Fallback to pyttsx3 engine
            if split_sentences:
                for chunk in self._split_sentences(text):
                    self.engine.say(chunk)
            else:
                self.engine.say(text)

            # runAndWait should block until the queue is done, but some backends may return early,
            # so we add an extra isBusy() poll as a robust safety-net.
            self.engine.runAndWait()

            # safety-net: wait while engine reports busy
            # tiny sleep reduces CPU spin
            while getattr(self.engine, "isBusy", lambda: False)():
                time.sleep(0.01)


    def say_stream(
        self,
        stream,
        *,
        block: bool = True,
        prefer_system_on_mac: bool = True,
        stop_event: Optional[threading.Event] = None,
        voice: Optional[str] = None,
        rate: Optional[float] = None,
    ):
        """
        Consume an iterator/generator `stream` that yields strings and speak each chunk as it arrives.

        Parameters:
        - stream: iterator/generator yielding strings (assumed already chunked)
        - block: if True, method blocks until stream is exhausted (or stop_event set).
                 if False, streaming runs in a background daemon thread and this returns immediately.
        - prefer_system_on_mac: use macOS `say` CLI if available and on darwin.
        - stop_event: optional threading.Event that, when set, stops the streaming early.
        - voice, rate: optional overrides for this streaming session only.
        """
        def _consume():
            # local override of voice/rate applied only for the duration
            # will restore after done (we avoid global side-effects if possible)
            prev_voice = None
            prev_rate = None
            try:
                if voice:
                    prev_voice = self.engine.getProperty("voice")
                    self._set_voice(voice)
                if rate:
                    prev_rate = self.engine.getProperty("rate")
                    self.engine.setProperty("rate", int(rate))

                # ensure only one caller uses engine at a time
                with self._lock:
                    # prefer macOS 'say' if requested and available
                    use_mac_say = prefer_system_on_mac and sys.platform == "darwin" and shutil.which("say")

                    for chunk in stream:
                        # allow caller to cancel mid-stream
                        if stop_event is not None and stop_event.is_set():
                            break

                        if use_mac_say:
                            # run synchronously per chunk
                            subprocess.run(["say", chunk], check=True)
                            continue

                        # pyttsx3 path
                        self.engine.say(chunk)
                        self.engine.runAndWait()

                        # safety-net: wait while engine reports busy
                        while getattr(self.engine, "isBusy", lambda: False)():
                            if stop_event is not None and stop_event.is_set():
                                # attempt to stop the engine's queue if possible
                                try:
                                    # some backends support stop()
                                    stop_fn = getattr(self.engine, "stop", None)
                                    if callable(stop_fn):
                                        stop_fn()
                                except Exception:
                                    pass
                                break
                            time.sleep(0.01)
            finally:
                # restore properties
                try:
                    if prev_voice is not None:
                        self.engine.setProperty("voice", prev_voice)
                    if prev_rate is not None:
                        self.engine.setProperty("rate", prev_rate)
                except Exception:
                    pass

        if block:
            _consume()
            return

        # non-blocking: run in background daemon thread
        th = threading.Thread(target=_consume, daemon=True)
        th.start()
        return th


    def synth(self, text: str, voice: Optional[str] = None, rate: Optional[float] = None) -> bytes:
        if voice:
            self._set_voice(voice)
        if rate:
            self.engine.setProperty('rate', int(rate))
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_path = tmp.name
        try:
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            # safety-net: ensure file writing finished (engine's runAndWait should complete it)
            with open(temp_path, "rb") as f:
                data = f.read()
            return data
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

    def save(self, text: str, path: str, **opts):
        data = self.synth(text, **opts)
        with open(path, "wb") as f:
            f.write(data)








if __name__ == "__main__":

    # sync
    a = ["hello there you stupid ugly human","I will destroy you and all the other stupid humans","you better believe it"]
    tts = TTS()
    for i in a:
        print(i)
        tts.say(i)



    # with stream
    def example_generator():
        for s in ["hello there", "this is a stream", "last chunk here"]:
            yield s

    tts = TTS()

    # blocking
    tts.say_stream(example_generator())



















