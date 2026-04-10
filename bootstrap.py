"""
Bootstrap script: creates directories, installs deps, and runs the full ML pipeline.
Run with: python bootstrap.py
"""
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).parent

dirs = [
    "data/raw", "data/processed", "models",
    "app/templates", "app/static", "notebooks"
]
for d in dirs:
    (ROOT / d).mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {d}")

# Copy PDFs if they exist one level up
src_dir = ROOT.parent
for pdf in ["2368.pdf", "confuseddrugnames(02.2015).pdf"]:
    src = src_dir / pdf
    dst = ROOT / "data" / "raw" / pdf
    if src.exists() and not dst.exists():
        import shutil
        shutil.copy(src, dst)
        print(f"  ✓ Copied {pdf} → data/raw/")
    elif dst.exists():
        print(f"  ✓ {pdf} already in data/raw/")
    else:
        print(f"  ⚠ {pdf} not found at {src}")

print("\n[2/5] Installing dependencies...")
pkgs = [
    "pdfplumber", "pandas", "numpy", "rapidfuzz", "jellyfish",
    "scikit-learn", "xgboost", "joblib", "fastapi", "uvicorn[standard]",
    "python-multipart", "jinja2", "matplotlib", "seaborn", "tqdm"
]
subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + pkgs)
print("  ✓ Dependencies installed")

print("\n[3/5] Data preprocessing...")
subprocess.check_call([sys.executable, "modules/01_data_preprocessing.py"])

print("\n[4/5] Feature engineering...")
subprocess.check_call([sys.executable, "modules/02_feature_engineering.py"])

print("\n[5/5] Model training...")
subprocess.check_call([sys.executable, "modules/03_model_training.py"])

print("\n✅ Pipeline complete!")
print("   Start with: python -m uvicorn app.app:app --host 0.0.0.0 --port 8000")
