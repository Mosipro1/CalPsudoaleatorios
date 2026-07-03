import struct
import wave
import io
import subprocess
import os
import math
import threading


class SoundManager:
    def __init__(self):
        self._player = self._detect_player()
        self._enabled = True

    def _detect_player(self):
        for cmd in [["paplay"], ["aplay"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]]:
            try:
                subprocess.run(cmd + ["--version"] if cmd[0] != "ffplay" else cmd[:1] + ["-version"],
                               capture_output=True, timeout=1)
                return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return None

    def _generate_wav(self, freq, duration, volume=0.3, wave_type="sine"):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        data = []
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == "sine":
                sample = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square":
                sample = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            elif wave_type == "sawtooth":
                sample = 2.0 * (freq * t - math.floor(freq * t + 0.5))
            elif wave_type == "noise":
                import random
                sample = random.uniform(-1, 1)
            else:
                sample = math.sin(2 * math.pi * freq * t)
            sample *= volume * max(0, 1 - t / duration)
            data.append(int(sample * 32767))
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            for s in data:
                wf.writeframes(struct.pack("<h", s))
        return buf.getvalue()

    def _play_wav(self, wav_data):
        if not self._player or not self._enabled:
            return
        try:
            subprocess.run(self._player + ["-"], input=wav_data,
                           capture_output=True, timeout=2)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def play(self, freq, duration, wave_type="sine", volume=0.3):
        wav = self._generate_wav(freq, duration, volume, wave_type)
        threading.Thread(target=self._play_wav, args=(wav,), daemon=True).start()

    def click(self):
        self.play(900, 0.06, "square", 0.08)

    def chip(self):
        self.play(600, 0.05, "sine", 0.06)
        threading.Timer(0.04, lambda: self.play(800, 0.04, "sine", 0.04)).start()

    def spin(self):
        for i in range(20):
            threading.Timer(i * 0.04, lambda f=150+i*12: self.play(f, 0.08, "sawtooth", 0.04)).start()

    def tick(self):
        self.play(1200, 0.02, "square", 0.03)

    def win(self):
        self.play(523, 0.12, "sine", 0.12)
        threading.Timer(0.12, lambda: self.play(659, 0.12, "sine", 0.12)).start()
        threading.Timer(0.24, lambda: self.play(784, 0.25, "sine", 0.12)).start()

    def lose(self):
        self.play(250, 0.25, "sawtooth", 0.1)
        threading.Timer(0.25, lambda: self.play(180, 0.35, "sawtooth", 0.1)).start()

    def set_enabled(self, enabled):
        self._enabled = enabled


sounds = SoundManager()
