"""
Module 2: Feature Engineering
Computes string-similarity features for each drug pair in the training dataset.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from rapidfuzz import distance as rfd, fuzz
import jellyfish
from sklearn.feature_extraction.text import CountVectorizer

ROOT_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT_DIR / "data" / "processed"

INPUT_CSV  = PROC_DIR / "training_dataset.csv"
OUTPUT_CSV = PROC_DIR / "feature_matrix.csv"

# ── helpers ───────────────────────────────────────────────────────────────────
def metaphone_match(a: str, b: str) -> int:
    try:
        return int(jellyfish.metaphone(a) == jellyfish.metaphone(b))
    except Exception:
        return 0

def soundex_match(a: str, b: str) -> int:
    try:
        return int(jellyfish.soundex(a) == jellyfish.soundex(b))
    except Exception:
        return 0

def prefix_match(a: str, b: str, n: int = 5) -> int:
    return int(a[:n] == b[:n])

def ngram_overlap(a: str, b: str, n: int = 2) -> float:
    """Character n-gram Jaccard overlap."""
    def ngrams(s):
        return set(s[i:i+n] for i in range(len(s) - n + 1))
    g1, g2 = ngrams(a), ngrams(b)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)

def length_ratio(a: str, b: str) -> float:
    if max(len(a), len(b)) == 0:
        return 1.0
    return min(len(a), len(b)) / max(len(a), len(b))

# ── feature function ──────────────────────────────────────────────────────────
def compute_features(row: pd.Series) -> dict:
    a, b = str(row["drug1"]), str(row["drug2"])
    lev_dist  = rfd.Levenshtein.distance(a, b)
    max_len   = max(len(a), len(b)) or 1
    lev_norm  = 1 - lev_dist / max_len          # higher = more similar

    return {
        "levenshtein_norm":   lev_norm,
        "jaro_winkler":       fuzz.WRatio(a, b) / 100.0,
        "token_sort_ratio":   fuzz.token_sort_ratio(a, b) / 100.0,
        "ngram_bigram":       ngram_overlap(a, b, 2),
        "ngram_trigram":      ngram_overlap(a, b, 3),
        "soundex_match":      soundex_match(a, b),
        "metaphone_match":    metaphone_match(a, b),
        "prefix5_match":      prefix_match(a, b, 5),
        "length_ratio":       length_ratio(a, b),
    }

# ── main ──────────────────────────────────────────────────────────────────────
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    features = df.apply(compute_features, axis=1, result_type="expand")
    if "label" in df.columns:
        features["label"] = df["label"].values
    return features

def main():
    print("Loading training dataset ...")
    df = pd.read_csv(INPUT_CSV)
    print(f"  Rows loaded: {len(df)}")

    print("Computing features …")
    feat_df = build_features(df)

    feat_df.to_csv(OUTPUT_CSV, index=False)
    print(f"> Feature matrix saved -> {OUTPUT_CSV.name}")
    print(f"  Shape: {feat_df.shape}")
    print(feat_df.head(3))

if __name__ == "__main__":
    main()
