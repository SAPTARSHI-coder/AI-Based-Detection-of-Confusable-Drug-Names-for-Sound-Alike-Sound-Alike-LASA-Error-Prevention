"""
Module 3: Model Training
Trains a Random Forest and Gradient Boosting classifier on the feature matrix,
evaluates performance, and saves the best model.
"""
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, ConfusionMatrixDisplay
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = ROOT_DIR / "data" / "processed"
MODEL_DIR  = ROOT_DIR / "models"
FEAT_CSV   = PROC_DIR / "feature_matrix.csv"
MODEL_PATH = MODEL_DIR / "lasa_classifier.pkl"

FEATURE_COLS = [
    "levenshtein_norm", "jaro_winkler", "token_sort_ratio",
    "ngram_bigram", "ngram_trigram",
    "soundex_match", "metaphone_match", "prefix5_match", "length_ratio",
]

# ── helpers ───────────────────────────────────────────────────────────────────
def evaluate(name, model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc    = roc_auc_score(y_test, y_prob)
    print(f"\n-- {name} ----------------------")
    print(classification_report(y_test, y_pred, target_names=["Non-LASA", "LASA"]))
    print(f"  AUC-ROC: {auc:.4f}")
    return auc, y_pred

def evaluate_baseline(X_test, y_test):
    jw_scores = X_test["jaro_winkler"].fillna(0)
    y_pred    = (jw_scores > 0.85).astype(int)
    auc       = roc_auc_score(y_test, jw_scores)
    
    print("\n-- Fuzzy Matching Baseline (Jaro-Winkler > 0.85) --")
    print(classification_report(y_test, y_pred, target_names=["Non-LASA", "LASA"]))
    print(f"  AUC-ROC: {auc:.4f}")
    return auc, y_pred

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    MODEL_DIR.mkdir(exist_ok=True)

    print("Loading feature matrix ...")
    df = pd.read_csv(FEAT_CSV)
    print(f"  Shape: {df.shape}")

    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)}  |  Test: {len(X_test)}")
    
    evaluate_baseline(X_test, y_test)

    # ── models ────────────────────────────────────────────────────────────────
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=200, class_weight="balanced",
            max_depth=10, random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05,
            max_depth=5, random_state=42
        ),
    }

    best_auc   = -1
    best_model = None
    best_name  = ""

    for name, clf in models.items():
        clf.fit(X_train, y_train)
        auc, _ = evaluate(name, clf, X_test, y_test)
        if auc > best_auc:
            best_auc, best_model, best_name = auc, clf, name

    print(f"\n> Best model: {best_name}  (AUC = {best_auc:.4f})")

    # ── save ──────────────────────────────────────────────────────────────────
    artifact = {
        "model":        best_model,
        "feature_cols": FEATURE_COLS,
        "model_name":   best_name,
        "auc":          best_auc,
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"> Model saved -> {MODEL_PATH}")

    # ── confusion matrix plot ─────────────────────────────────────────────────
    y_pred_best = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(cm, display_labels=["Non-LASA", "LASA"])
    disp.plot(ax=ax, colorbar=False)
    ax.set_title(f"{best_name} – Confusion Matrix")
    plot_path = MODEL_DIR / "confusion_matrix.png"
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"> Confusion matrix plot saved -> {plot_path}")

if __name__ == "__main__":
    main()
