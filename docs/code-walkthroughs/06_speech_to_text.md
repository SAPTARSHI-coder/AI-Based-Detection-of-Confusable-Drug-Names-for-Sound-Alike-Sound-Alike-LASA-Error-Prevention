# 📄 06_speech_to_text.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It converts an audio recording (like a doctor speaking a prescription) into written text — and gracefully falls back to a placeholder mode if the voice recognition library is not installed.

---

## Real-Life Analogy

Think of a **court stenographer** — the person who types out everything said during a legal proceeding in real time. Your file is a digital version of that. Give it an audio file, and it produces a text transcript.

If the stenographer is unavailable (the library isn't installed), a backup system stamps the recording file's name on the transcript instead of crashing the courtroom.

---

## Key Concept Before We Start: Optional Dependencies and Graceful Fallback

This module introduces an important software design pattern: **graceful degradation**.

Your system has an optional feature — voice input using Whisper. If Whisper is not installed on a machine, most software would crash immediately with an error. But yours doesn't. It uses Python's `try/except` block to say:

*"Try to use Whisper. If it's not available, define a different, simpler version of the function that still works."*

This is professional-grade resilience.

---

## The Full Code, Explained Line by Line

---

### Lines 1–5 — Docstring

```python
"""
Module 6: Speech-to-Text (Whisper Wrapper)
Transcribes audio files or microphone input using OpenAI Whisper.
Falls back to a mock implementation if whisper is not installed.
"""
```
Plain-English description of the file. The key phrase here is *"Falls back to a mock implementation"* — the fallback design is a deliberate, documented choice.

---

### Lines 6–8 — Imports

```python
import os
from pathlib import Path
from typing import Dict
```

| Import | Purpose |
|:---|:---|
| `os` | Used to check if a file path exists on disk (`os.path.exists()`) |
| `Path` | Smart file path handling |
| `Dict` | Type hint for dictionary return types |

---

### Lines 11–43 — The Core Try/Except Block

This is the most important and most interesting part of this module.

```python
try:
    import whisper as _whisper
    _MODEL = None
```

**What is `try`?**

`try` starts a block of code that Python will *attempt* to execute. If any error occurs inside, Python jumps to the `except` block instead of crashing.

```python
import whisper as _whisper
```
Try to import the `whisper` library. If Whisper is installed → this succeeds. If not → Python raises an `ImportError` and jumps to the `except` block at line 33.

The underscore prefix `_whisper` is a convention meaning "this is a private/internal reference — don't import or use this directly from outside the module."

```python
_MODEL = None
```
Initialize a global variable `_MODEL` to `None`. This will hold the Whisper model object once it's loaded (lazy loading — load it only when first needed).

---

### Lines 15–20 — The `_load_model()` Function (inside the `try` block)

```python
def _load_model(size: str = "base"):
    global _MODEL
    if _MODEL is None:
        print(f"  Loading Whisper model ({size}) ...")
        _MODEL = _whisper.load_model(size)
    return _MODEL
```

**Why is loading done lazily?**

Loading the Whisper AI model from disk takes time (a few seconds). If you loaded it every time someone called `transcribe()`, it would feel very slow. Instead:

1. The first time `_load_model()` is called → load the model → store in `_MODEL`
2. Every subsequent call → `_MODEL is not None` → simply return the already-loaded model

This is the **singleton pattern** — only one copy of the model exists in memory, no matter how many times it's requested.

**Whisper model sizes:**

| Size | Speed | Accuracy |
|:---|:---|:---|
| `tiny` | Very fast | Lower |
| `base` | Fast | Good |
| `small` | Moderate | Better |
| `medium` | Slow | High |
| `large` | Very slow | Best |

Default is `"base"` — a balanced choice for most clinical audio.

---

### Lines 22–29 — The Real `transcribe_file()` Function (inside `try`)

```python
def transcribe_file(audio_path: str, model_size: str = "base") -> Dict:
    model  = _load_model(model_size)
    result = model.transcribe(audio_path)
    return {
        "text":       result["text"].strip(),
        "language":   result.get("language", "en"),
        "confidence": None,
    }
```

```python
model = _load_model(model_size)
```
Get the Whisper model (loading it if it hasn't been loaded yet).

```python
result = model.transcribe(audio_path)
```
**This is where the actual voice recognition happens.**

`model.transcribe()` is Whisper's core function. It:
1. Reads the audio file at `audio_path`
2. Converts it to a mel spectrogram (a mathematical representation of sound)
3. Runs it through a neural network (a type of deep learning AI)
4. Produces a text transcript

The returned `result` is a dictionary containing:
- `result["text"]` — The full transcript
- `result.get("language", "en")` — The detected language (`"en"` = English)

```python
return {
    "text":       result["text"].strip(),
    "language":   result.get("language", "en"),
    "confidence": None,
}
```

The function returns a clean dictionary:
- `text` — The transcript with leading/trailing whitespace removed
- `language` — What language was detected
- `confidence` — `None` because Whisper doesn't provide a single confidence score per utterance (it provides word-level timestamps but no overall confidence number)

```python
WHISPER_AVAILABLE = True
```
Set a flag so other parts of the system can check whether real Whisper is available.

---

### Lines 33–43 — The `except ImportError:` Block (Fallback)

```python
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
```

If `import whisper` fails (because it's not installed), Python jumps here.

```python
WHISPER_AVAILABLE = False
```
Set the flag to `False` so the rest of the system knows Whisper is unavailable.

**The mock `transcribe_file()`** — a completely different version of the same function is defined here:

```python
filename = Path(audio_path).stem.replace("_", " ")
```
- `Path(audio_path).stem` → Get the filename without the extension.  
  E.g.: `"recordings/patient_order.wav"` → `"patient_order"`
- `.replace("_", " ")` → Replace underscores with spaces → `"patient order"`

```python
return {
    "text": f"[Mock transcript for '{filename}']",
    ...
}
```
Return a fake transcript that at least shows which file was provided. This is useful for testing the rest of the pipeline without actually running voice recognition.

**Why define `transcribe_file` twice?**

Both versions of the function have the **same name** and the **same interface** (same inputs, same output structure). Python will use whichever one was actually successfully defined. The calling code doesn't need to know which version is active — it always calls `transcribe_file()` the same way. This is a classic software pattern called **polymorphism**.

---

### Lines 46–56 — The Public `transcribe()` Function

```python
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
```

This is the **public interface** — the function that other modules import and call.

```python
if not os.path.exists(audio_path):
    raise FileNotFoundError(f"Audio file not found: {audio_path}")
```
Before doing anything, check if the audio file actually exists on disk. If not, raise a `FileNotFoundError` with a helpful message. This is called **input validation** — always check your inputs before processing them.

```python
return transcribe_file(audio_path, model_size)
```
Call the appropriate version of `transcribe_file()` (either the real Whisper one or the mock one, depending on which was defined in the try/except block).

**Why have both `transcribe()` and `transcribe_file()`?**

`transcribe()` is the *public* function (validates input, checked by others), and `transcribe_file()` is the *implementation* (the actual work). This separation keeps responsibilities clean and makes the code easier to test and extend.

---

### Lines 60–67 — CLI Demo

```python
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python 06_speech_to_text.py <audio_file>")
        sys.exit(1)
    result = transcribe(sys.argv[1])
    print("Transcript:", result["text"])
    print("Language: ", result["language"])
```

If you run this file directly in the terminal:

```bash
python 06_speech_to_text.py my_recording.wav
```

- `sys.argv` → The list of command-line arguments. `sys.argv[0]` = the script name, `sys.argv[1]` = the first argument you typed (the audio file path)
- `len(sys.argv) < 2` → If no audio file was provided, print usage instructions and exit
- `sys.exit(1)` → Exit with code 1 (convention: non-zero exit = error occurred)

---

## Summary: What This File Does

```
Input:   Audio file path (e.g., "recordings/patient_order.wav")
             ↓
Check:   Does the file exist? → If not, raise an error
             ↓
Is Whisper available?
    YES → Load Whisper model (cache it) → Transcribe the audio → return real text
    NO  → Return mock placeholder text based on filename
             ↓
Output:  {
           "text": "Administer 25mg hydralazine intravenously.",
           "language": "en",
           "confidence": None
         }
```
