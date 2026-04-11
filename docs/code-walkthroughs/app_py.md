# 📄 app/app.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It runs a web server that listens for requests from a browser, coordinates all the other modules, and sends back a complete LASA risk analysis as a response — either for typed text or for an uploaded audio file.

---

## Real-Life Analogy

Think of this file as the **hospital reception desk**.

All the specialists (each module) are ready in their rooms. When a patient (user) arrives:
1. The receptionist (app.py) greets them
2. Takes their information (text or audio)
3. Sends them to the right specialists (NLP extractor, LASA engine, context validator, decision engine)
4. Collects all the specialist reports
5. Hands the combined report back to the patient

The receptionist doesn't do any of the medical analysis themselves — they coordinate everyone else.

---

## Key Concept: What is a Web Server?

A **web server** is a program that runs continuously on a computer, waiting for requests from a browser. When you open a webpage, your browser sends a "request" to the server. The server processes it and sends back a "response" (HTML, data, etc.).

Your web server is built with **FastAPI** — a Python framework designed for building fast, modern web APIs (Application Programming Interfaces). APIs are channels through which different software talks to each other.

---

## Two Types of HTTP Requests Used in This File

| Type | What it does | When used |
|:---|:---|:---|
| `GET` | Fetch something — no data sent | Opening the webpage in a browser |
| `POST` | Send data to be processed | Submitting a drug name / uploading audio |

---

## The Full Code, Explained Line by Line

---

### Lines 1–7 — Docstring

```python
"""
Module 9: FastAPI Web Application
Endpoints:
  POST /analyze  — text input → LASA analysis
  POST /voice    — audio file upload → LASA analysis
  GET  /         — HTML frontend
"""
```

Lists the three **endpoints** (URLs) this web server handles. Think of an endpoint like a specific counter at a post office — each one handles a different type of request.

---

### Lines 8–9 — Imports (Standard Library)

```python
import sys, os, tempfile, shutil, importlib.util
from pathlib import Path
```

| Import | Purpose |
|:---|:---|
| `sys` | Access system paths (Python's module search path) |
| `os` | File system operations (e.g., deleting temporary files) |
| `tempfile` | Create temporary files for uploaded audio |
| `shutil` | Copy file contents (used to save uploaded audio to temporary location) |
| `importlib.util` | Dynamically load Python files by their path — used here to load the modules |
| `Path` | Smart cross-platform file path handling |

---

### Lines 11–19 — The Dynamic Module Loader (`_load`)

```python
BASE_DIR    = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"

def _load(filename, alias):
    path = MODULES_DIR / filename
    spec = importlib.util.spec_from_file_location(alias, path)
    m    = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
```

**Why is this needed?**

Normally Python imports modules using `import module_name`. But this only works if the module is in a standard location. Your module files have names starting with numbers (`01_data_preprocessing.py`) — Python's standard `import` statement can't handle filenames starting with numbers.

The solution: use `importlib` to load them **directly from their file path**, bypassing the naming restriction.

**Line by line:**

```python
BASE_DIR    = Path(__file__).resolve().parent.parent
```
Go two levels up from `app.py` (which lives in `app/`) to reach the project root (`lasa_detection/`).

```python
MODULES_DIR = BASE_DIR / "modules"
```
Build the path to the `modules/` folder.

```python
def _load(filename, alias):
    path = MODULES_DIR / filename
```
Build the full path to the module file (e.g., `lasa_detection/modules/05_nlp_drug_extractor.py`).

```python
    spec = importlib.util.spec_from_file_location(alias, path)
```
Create a **module specification** — a description of where the module is and what name to register it as. `alias` is the internal name you want to use (e.g., `"nlp_extractor"`).

```python
    m = importlib.util.module_from_spec(spec)
```
Create an empty module object based on the spec.

```python
    spec.loader.exec_module(m)
```
**Execute the module's code** — this is where the Python file actually runs. All functions, classes, and variables defined inside it become available on the module object `m`.

```python
    return m
```
Return the loaded module so it can be used.

---

### Lines 21–25 — Loading All Modules

```python
_utils = _load("modules_utils.py",          "modules_utils")
_nlp   = _load("05_nlp_drug_extractor.py",  "nlp_extractor")
_stt   = _load("06_speech_to_text.py",      "stt")
_ctx   = _load("07_patient_context.py",     "patient_ctx")
_dec   = _load("08_decision_engine.py",     "decision")
```

Load all 5 modules needed for inference. Each module is loaded once at startup and stored in a variable:

| Variable | Module Loaded | What it provides |
|:---|:---|:---|
| `_utils` | `modules_utils.py` | `compute_features_pair()` function |
| `_nlp` | `05_nlp_drug_extractor.py` | `extract()` function |
| `_stt` | `06_speech_to_text.py` | `transcribe()` function |
| `_ctx` | `07_patient_context.py` | `validate()` function |
| `_dec` | `08_decision_engine.py` | `decide()` function |

Note that Modules 01, 02, and 03 are NOT loaded here — they are training-only modules. Once training is done, they're not needed during live use.

---

### Lines 27–31 — FastAPI Library Imports

```python
import joblib, pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
```

| Import | Purpose |
|:---|:---|
| `joblib` | Load the saved trained model (`.pkl` file) |
| `pandas as pd` | Build DataFrames for model prediction |
| `FastAPI` | The main web framework class |
| `UploadFile, File` | Handle file uploads (audio files) |
| `Form` | Handle form data from browser submissions |
| `Request` | Represents an incoming HTTP request |
| `HTTPException` | Return error responses with HTTP status codes |
| `HTMLResponse` | Send back an HTML page |
| `JSONResponse` | Send back structured JSON data |
| `StaticFiles` | Serve CSS/JS files from the `static/` folder |
| `Jinja2Templates` | Render HTML template files with dynamic data |

---

### Lines 33–39 — Global State Variables

```python
MODEL_PATH  = BASE_DIR / "models" / "lasa_classifier.pkl"
DRUG_LIST   = BASE_DIR / "data"   / "drug_list.txt"
DRUG_PAIRS  = BASE_DIR / "data"   / "processed" / "drug_pairs.csv"

_artifact   = None
_drugs: list = []
_ismp_pairs = set()
```

Three **module-level variables** that store loaded data:
- `_artifact = None` → Will hold the loaded model once loaded
- `_drugs = []` → Will hold the master drug list
- `_ismp_pairs = set()` → Will hold all known ISMP danger pairs as a set for fast lookup

They start empty. The `_load_artifacts()` function populates them on first use.

---

### Lines 41–53 — The `_load_artifacts()` Function

```python
def _load_artifacts():
    global _artifact, _drugs, _ismp_pairs
    if _artifact is None and MODEL_PATH.exists():
        _artifact = joblib.load(MODEL_PATH)
    if not _drugs and DRUG_LIST.exists():
        with open(DRUG_LIST, encoding="utf-8") as f:
            _drugs = [l.strip() for l in f if l.strip()]
    if not _ismp_pairs and DRUG_PAIRS.exists():
        df_pairs = pd.read_csv(DRUG_PAIRS)
        for _, row in df_pairs.iterrows():
            d1, d2 = str(row["drug1"]).lower(), str(row["drug2"]).lower()
            _ismp_pairs.add((d1, d2))
            _ismp_pairs.add((d2, d1))
```

This function loads the three data resources if they haven't been loaded yet (**lazy loading** — only do expensive file reading when first needed).

```python
global _artifact, _drugs, _ismp_pairs
```
Declare that we're modifying the global variables (not creating local copies).

```python
if _artifact is None and MODEL_PATH.exists():
    _artifact = joblib.load(MODEL_PATH)
```
Load the trained model only once. If it's already loaded (`_artifact is not None`), skip.

```python
if not _drugs and DRUG_LIST.exists():
    with open(DRUG_LIST, encoding="utf-8") as f:
        _drugs = [l.strip() for l in f if l.strip()]
```
Load the drug list — one drug name per line — into a Python list.

```python
if not _ismp_pairs and DRUG_PAIRS.exists():
    df_pairs = pd.read_csv(DRUG_PAIRS)
    for _, row in df_pairs.iterrows():
        d1, d2 = str(row["drug1"]).lower(), str(row["drug2"]).lower()
        _ismp_pairs.add((d1, d2))
        _ismp_pairs.add((d2, d1))
```

Load the ISMP confirmed drug pairs file. Store each pair in **both directions**:
- `(d1, d2)` → if querying `d1`, checking if `d2` is a known pair
- `(d2, d1)` → if querying `d2`, checking if `d1` is a known pair

Using a `set` makes the lookup `O(1)` — instant checking regardless of how many pairs are stored.

---

### Lines 55–90 — The `score_drug_local()` Function

This is the app's own version of the LASA scoring function — slightly more capable than Module 04's version because it also adds the ISMP flag directly to each result.

```python
def score_drug_local(query: str, top_n: int = 10):
    _load_artifacts()
    if _artifact is None:
        raise RuntimeError("Model not trained yet. Run python run_all.py first.")
```

First, ensure artifacts are loaded. If the model file doesn't exist yet (training hasn't been run), raise an error with a clear message explaining what to do.

```python
    model, feat_cols = _artifact["model"], _artifact["feature_cols"]
    query = query.lower().strip()
```
Extract model and feature column names from the artifact dictionary. Normalize the query (lowercase, no whitespace).

```python
    rows, candidates = [], []
    for cand in _drugs:
        if cand == query:
            continue
        rows.append(_utils.compute_features_pair(query, cand))
        candidates.append(cand)
```

Loop through the drug list and:
- Skip the drug itself (can't be confused with itself)
- Calculate 9 similarity features between query and each candidate
- Store features (`rows`) and candidate names (`candidates`) in parallel lists — same index `i` in both lists corresponds to the same comparison

```python
    df    = pd.DataFrame(rows, columns=feat_cols)
    probs = model.predict_proba(df.fillna(0))[:, 1]
```

Convert all feature rows to a DataFrame → get probabilities for all ~300 comparisons at once (batch prediction is much faster than predicting one by one).

```python
    results = []
    for i, (c, p) in enumerate(zip(candidates, probs)):
        feat_dict = rows[i]
        ismp_flag = (query, c) in _ismp_pairs
        base_score = float(p)
        
        adj_score = base_score
        if ismp_flag: adj_score += 0.15
        
        results.append({
            "candidate":    c,
            "lasa_prob":    round(base_score, 4),
            "risk_level":   "HIGH" if adj_score > 0.75 else ("MEDIUM" if adj_score > 0.45 else "LOW"),
            "known_in_ismp": ismp_flag,
            "features":     feat_dict
        })
```

For each candidate:

- `zip(candidates, probs)` → Pair each candidate name with its probability (same index)
- `feat_dict = rows[i]` → Retrieve the feature dictionary for this comparison
- `ismp_flag = (query, c) in _ismp_pairs` → Is this an officially documented LASA pair?
- `adj_score = base_score + 0.15 (if ISMP)` → Boost the score for known danger pairs
- Build the result dictionary with all fields including `features` (for the decision engine's explanation) and `known_in_ismp` (for the decision engine's ISMP boost logic)

```python
    results.sort(key=lambda x: x["lasa_prob"], reverse=True)
    return results[:top_n]
```
Sort by base probability (highest first) and return top `top_n` results (default 10).

---

### Lines 93–98 — Creating the FastAPI App

```python
app = FastAPI(title="LASA Drug Detector", version="1.0")

static_dir = BASE_DIR / "app" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
```

```python
app = FastAPI(title="LASA Drug Detector", version="1.0")
```
Create the FastAPI application object. This is the core server — all routes (URL handlers) will be registered onto this object.

```python
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
```
Tell the web server: *"Any request for `/static/something.css` → serve it from the `app/static/` folder."* This is how CSS, JavaScript, and image files get served to the browser.

```python
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
```
Set up the template engine. **Jinja2** is a templating system — it takes HTML files with placeholder variables and fills them in with real data before sending to the browser.

---

### Lines 100–102 — The `GET /` Endpoint (Homepage)

```python
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")
```

**`@app.get("/")`** — This is a **decorator**. It tells FastAPI: *"Register the function below as the handler for GET requests to the `/` URL (the homepage)."*

**`async def index(...)`** — `async` means asynchronous — the function can handle multiple requests efficiently without blocking.

**`templates.TemplateResponse(request, "index.html")`** — Render the `index.html` template and return it as an HTML response. This is what sends the webpage to the browser when you visit `http://localhost:8000`.

---

### Lines 104–118 — The `POST /analyze` Endpoint (Text Input)

```python
@app.post("/analyze")
async def analyze(text: str = Form(...), diagnosis: str = Form("")):
    try:
        _load_artifacts()
        extracted = _nlp.extract(text)
        drug      = extracted.get("drug") or text.lower().strip()
        hits      = score_drug_local(drug)
        ctx       = _ctx.validate(drug, diagnosis or None)
        decision  = _dec.decide(hits, ctx)
        return JSONResponse({
            "status": "ok", "drug": drug,
            "extracted": extracted, "decision": decision, "lasa_hits": hits[:5],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**`@app.post("/analyze")`** — Register as the handler for POST requests to `/analyze`.

**`text: str = Form(...)`** — Receive form data called `text`. The `...` means it's required.
**`diagnosis: str = Form("")`** — Receive form data called `diagnosis`. `""` = default empty string if not provided.

**Inside the `try` block:**

```python
_load_artifacts()
```
Ensure model and drug lists are loaded.

```python
extracted = _nlp.extract(text)
```
Call Module 05 to extract the drug name, dose, and route from the clinical sentence.

```python
drug = extracted.get("drug") or text.lower().strip()
```
Use the extracted drug name. If extraction failed (returned `None`), fall back to treating the entire input text as the drug name.

```python
hits = score_drug_local(drug)
```
Run the LASA scoring against all known drugs. Returns top 10 matches.

```python
ctx = _ctx.validate(drug, diagnosis or None)
```
Run patient context check. If `diagnosis` is an empty string (`""`), convert to `None` (signal: no diagnosis provided).

```python
decision = _dec.decide(hits, ctx)
```
Run the decision engine with no voice confidence (`stt_confidence=None` by default since this is text input).

```python
return JSONResponse({...})
```
Return the complete analysis as a **JSON response** — a structured data format that the browser's JavaScript can read and display.

**`try/except Exception as e:`** — If anything goes wrong anywhere in the pipeline, catch the error and return an HTTP 500 error with the error message, rather than crashing the server.

---

### Lines 120–141 — The `POST /voice` Endpoint (Audio Input)

```python
@app.post("/voice")
async def voice(file: UploadFile = File(...), diagnosis: str = Form("")):
    try:
        _load_artifacts()
        suffix = Path(file.filename).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        transcript = _stt.transcribe(tmp_path)
        os.unlink(tmp_path)
        text      = transcript["text"]
        extracted = _nlp.extract(text)
        drug      = extracted.get("drug") or text.lower().strip()
        hits      = score_drug_local(drug)
        ctx       = _ctx.validate(drug, diagnosis or None)
        decision  = _dec.decide(hits, ctx, stt_confidence=transcript.get("confidence"))
        return JSONResponse({...})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**`file: UploadFile = File(...)`** — Accept an uploaded file (the audio recording). Required.

```python
suffix = Path(file.filename).suffix or ".wav"
```
Extract the file extension (e.g., `.wav`, `.mp3`). Default to `.wav` if none found.

```python
with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
    shutil.copyfileobj(file.file, tmp)
    tmp_path = tmp.name
```
**This is how file uploads are handled:**

1. Create a temporary file on disk (with the correct extension)
2. `shutil.copyfileobj(file.file, tmp)` → Copy the uploaded audio bytes into the temp file
3. Store the temp file's path in `tmp_path`
4. The `with` block closes the file when done

`delete=False` — Don't auto-delete when closing, because Whisper needs to access it by path.

```python
transcript = _stt.transcribe(tmp_path)
os.unlink(tmp_path)
```
Transcribe the audio file. Then **immediately delete** the temporary file (`os.unlink()`) — clean up after use. Leaving temp files is a resource leak.

```python
decision = _dec.decide(hits, ctx, stt_confidence=transcript.get("confidence"))
```
Pass the voice confidence score to the decision engine. If Whisper was uncertain (low confidence), the decision engine adds +0.05 to the risk score.

The rest is identical to the `/analyze` endpoint — extract drug, score, validate context, decide.

---

### Lines 143–145 — Running the Server

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

```python
import uvicorn
```
Load `uvicorn` — the high-performance ASGI (Asynchronous Server Gateway Interface) server that runs FastAPI applications.

```python
uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```
- `"app:app"` → Find the `app` variable in the file named `app.py`
- `host="0.0.0.0"` → Accept connections from any network interface (not just localhost)
- `port=8000` → Listen on port 8000 (so browser visits `http://localhost:8000`)
- `reload=True` → Automatically restart the server when code changes (development mode)

---

## Summary: The Complete Request Flow

```
Browser visits http://localhost:8000
  → GET  /  → index() → serves index.html
  
User types "hydralazine 25mg IV" and submits:
  → POST /analyze
  → _nlp.extract()         → drug = "hydralazine"
  → score_drug_local()     → 300 comparisons → top 10 LASA hits
  → _ctx.validate()        → mismatch? True (if diagnosis = anxiety)
  → _dec.decide()          → risk = HIGH, reasons = [...], message = "⚠ Caution..."
  → JSONResponse(...)      → browser receives JSON, displays result

User uploads voice.wav:
  → POST /voice
  → save to temp file
  → _stt.transcribe()      → "Administer hydralazine IV"
  → delete temp file
  → [same 4 steps as above]
  → JSONResponse(...)      → browser receives JSON, displays result with transcript
```
