"""
One-shot runner: copies PDFs, runs the entire ML pipeline, outputs artefacts.
Usage:  python run_all.py
Requires: pip install pdfplumber pandas rapidfuzz jellyfish scikit-learn xgboost joblib matplotlib seaborn
"""
import sys, os, shutil, random
from pathlib import Path

ROOT     = Path(__file__).resolve().parent
MOD_DIR  = ROOT / "modules"
sys.path.insert(0, str(MOD_DIR))

# ── 1. Copy PDFs if needed ─────────────────────────────────────────────────
src = ROOT.parent
for pdf in ["2368.pdf", "confuseddrugnames(02.2015).pdf"]:
    s = src / pdf
    d = ROOT / "data" / "raw" / pdf
    if s.exists() and not d.exists():
        shutil.copy(s, d)
        print(f"Copied {pdf}")

# ── 2. Data preprocessing ──────────────────────────────────────────────────
print("\n===== Step 1: Data Preprocessing =====")
import importlib.util, types

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

preproc = load_module(MOD_DIR / "01_data_preprocessing.py", "preproc")
preproc.main()

# ── 3. Feature engineering ─────────────────────────────────────────────────
print("\n===== Step 2: Feature Engineering =====")
feateng = load_module(MOD_DIR / "02_feature_engineering.py", "feateng")
feateng.main()

# ── 4. Model training ──────────────────────────────────────────────────────
print("\n===== Step 3: Model Training =====")
trainer = load_module(MOD_DIR / "03_model_training.py", "trainer")
trainer.main()

print("\n\n✅  Full pipeline completed successfully!")
print("    ► Start the web app:  python -m uvicorn app.app:app --port 8000")
