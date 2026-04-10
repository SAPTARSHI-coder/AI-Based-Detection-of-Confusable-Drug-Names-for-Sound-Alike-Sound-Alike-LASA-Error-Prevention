"""
Module 4: LASA Detection Engine
Given a query drug name, scores it against all known drugs and
returns top-N most confusable drugs with risk probabilities.
"""
import joblib
import pandas as pd
from pathlib import Path
from typing import List, Dict

# sibling modules
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from modules_utils import compute_features_pair   # shared helper

ROOT_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "lasa_classifier.pkl"
DRUG_LIST  = ROOT_DIR / "data" / "drug_list.txt"

# ── load artifacts ─────────────────────────────────────────────────────────────
def load_engine():
    artifact   = joblib.load(MODEL_PATH)
    model      = artifact["model"]
    feat_cols  = artifact["feature_cols"]
    with open(DRUG_LIST, encoding="utf-8") as f:
        drugs = [line.strip() for line in f if line.strip()]
    return model, feat_cols, drugs

# ── scoring ────────────────────────────────────────────────────────────────────
def score_drug(query: str, top_n: int = 10) -> List[Dict]:
    """
    Return top-N most confusable drugs for the query.

    Returns
    -------
    list of dicts with keys: candidate, lasa_prob, risk_level
    """
    model, feat_cols, drugs = load_engine()
    query = query.lower().strip()

    rows = []
    for candidate in drugs:
        if candidate == query:
            continue
        feat = compute_features_pair(query, candidate)
        rows.append(feat)

    if not rows:
        return []

    df   = pd.DataFrame(rows, columns=feat_cols)
    probs = model.predict_proba(df.fillna(0))[:, 1]

    results = []
    for i, candidate in enumerate([d for d in drugs if d != query]):
        p = float(probs[i])
        risk = "HIGH" if p > 0.75 else ("MEDIUM" if p > 0.45 else "LOW")
        results.append({"candidate": candidate, "lasa_prob": round(p, 4), "risk_level": risk})

    results.sort(key=lambda x: x["lasa_prob"], reverse=True)
    return results[:top_n]

# ── CLI demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    query = input("Enter drug name to check: ").strip()
    hits  = score_drug(query)
    print(f"\nTop LASA matches for '{query}':")
    for h in hits:
        print(f"  {h['candidate']:<25} prob={h['lasa_prob']:.3f}  [{h['risk_level']}]")
