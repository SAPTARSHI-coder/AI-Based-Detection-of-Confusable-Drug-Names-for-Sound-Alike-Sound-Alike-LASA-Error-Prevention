"""
Module 9: FastAPI Web Application
Endpoints:
  POST /analyze  — text input → LASA analysis
  POST /voice    — audio file upload → LASA analysis
  GET  /         — HTML frontend
"""
import sys, os, tempfile, shutil, importlib.util
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
MODULES_DIR = BASE_DIR / "modules"

def _load(filename, alias):
    path = MODULES_DIR / filename
    spec = importlib.util.spec_from_file_location(alias, path)
    m    = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

_utils = _load("modules_utils.py",          "modules_utils")
_nlp   = _load("05_nlp_drug_extractor.py",  "nlp_extractor")
_stt   = _load("06_speech_to_text.py",      "stt")
_ctx   = _load("07_patient_context.py",     "patient_ctx")
_dec   = _load("08_decision_engine.py",     "decision")

import joblib, pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

MODEL_PATH  = BASE_DIR / "models" / "lasa_classifier.pkl"
DRUG_LIST   = BASE_DIR / "data"   / "drug_list.txt"
DRUG_PAIRS  = BASE_DIR / "data"   / "processed" / "drug_pairs.csv"

_artifact   = None
_drugs: list = []
_ismp_pairs = set()

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

def score_drug_local(query: str, top_n: int = 10):
    _load_artifacts()
    if _artifact is None:
        raise RuntimeError("Model not trained yet. Run python run_all.py first.")
    model, feat_cols = _artifact["model"], _artifact["feature_cols"]
    query = query.lower().strip()
    rows, candidates = [], []
    for cand in _drugs:
        if cand == query:
            continue
        rows.append(_utils.compute_features_pair(query, cand))
        candidates.append(cand)
    if not rows:
        return []
    df    = pd.DataFrame(rows, columns=feat_cols)
    probs = model.predict_proba(df.fillna(0))[:, 1]
    
    results = []
    for i, (c, p) in enumerate(zip(candidates, probs)):
        feat_dict = rows[i]
        ismp_flag = (query, c) in _ismp_pairs
        base_score = float(p)
        
        adj_score = base_score
        if ismp_flag: adj_score += 0.15
        
        results.append({
            "candidate": c,
            "lasa_prob": round(base_score, 4),
            "risk_level": "HIGH" if adj_score > 0.75 else ("MEDIUM" if adj_score > 0.45 else "LOW"),
            "known_in_ismp": ismp_flag,
            "features": feat_dict
        })
        
    results.sort(key=lambda x: x["lasa_prob"], reverse=True)
    return results[:top_n]

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="LASA Drug Detector", version="1.0")

static_dir = BASE_DIR / "app" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

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
        return JSONResponse({
            "status": "ok", "transcript": text, "drug": drug,
            "extracted": extracted, "decision": decision, "lasa_hits": hits[:5],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
