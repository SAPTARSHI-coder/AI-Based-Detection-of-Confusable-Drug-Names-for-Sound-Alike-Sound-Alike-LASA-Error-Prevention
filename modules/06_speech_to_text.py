"""
Module 6: Speech-to-Text (Whisper Wrapper)
Transcribes audio files or microphone input using OpenAI Whisper.
Falls back to a mock implementation if whisper is not installed.
"""
import os
from pathlib import Path
from typing import Dict

# ── Whisper loading (optional dependency) ─────────────────────────────────────
try:
    import whisper as _whisper
    _MODEL = None

    def _load_model(size: str = "base"):
        global _MODEL
        if _MODEL is None:
            print(f"  Loading Whisper model ({size}) …")
            _MODEL = _whisper.load_model(size)
        return _MODEL

    def transcribe_file(audio_path: str, model_size: str = "base") -> Dict:
        model  = _load_model(model_size)
        result = model.transcribe(audio_path)
        return {
            "text":       result["text"].strip(),
            "language":   result.get("language", "en"),
            "confidence": None,   # Whisper doesn't expose per-utterance confidence
        }

    WHISPER_AVAILABLE = True

except ImportError:
    WHISPER_AVAILABLE = False

    def transcribe_file(audio_path: str, model_size: str = "base") -> Dict:
        """Mock STT: echoes file name as placeholder transcript."""
        filename = Path(audio_path).stem.replace("_", " ")
        return {
            "text":       f"[Mock transcript for '{filename}']",
            "language":   "en",
            "confidence": None,
        }

# ── public API ─────────────────────────────────────────────────────────────────
def transcribe(audio_path: str, model_size: str = "base") -> Dict:
    """
    Transcribe an audio file.

    Returns
    -------
    dict: {text, language, confidence}
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    return transcribe_file(audio_path, model_size)


# ── CLI demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 06_speech_to_text.py <audio_file>")
        sys.exit(1)
    result = transcribe(sys.argv[1])
    print("Transcript:", result["text"])
    print("Language: ", result["language"])
