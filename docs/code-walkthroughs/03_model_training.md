# 📄 03_model_training.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It reads the 9-feature spreadsheet, trains two AI models (Random Forest and Gradient Boosting), compares them, keeps the better one, and saves it to a file — along with a confusion matrix image.

---

## Real-Life Analogy

Think of this as the **exam day** for two different students (the two AI models). Both studied the same material (feature matrix). Today we test them, compare their scores, and hire the better one permanently.

---

## The Full Code, Explained Line by Line

---

### Lines 1–5 — Docstring

```python
"""
Module 3: Model Training
Trains a Random Forest and Gradient Boosting classifier on the feature matrix,
evaluates performance, and saves the best model.
"""
```
A human-readable description of this file. Python ignores this at runtime.

---

### Lines 6–19 — Imports

```python
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
```

| Import | What it provides |
|:---|:---|
| `joblib` | Saves and loads Python objects to/from files (used to save the trained model) |
| `numpy as np` | Numerical computation — arrays, math operations |
| `pandas as pd` | Reading CSVs and handling tabular data |
| `matplotlib.pyplot as plt` | Drawing charts and plots |
| `seaborn as sns` | Higher-level chart plotting (used for heatmaps in notebooks) |
| `Path` | File path handling |
| `RandomForestClassifier` | The first AI model to train |
| `GradientBoostingClassifier` | The second AI model to train |
| `train_test_split` | Splits data into training set and test set |
| `StratifiedKFold` | (Imported, available for advanced cross-validation if needed) |
| `cross_val_score` | (Imported, available for cross-validation evaluation if needed) |
| `classification_report` | A detailed report showing precision, recall, F1-score |
| `confusion_matrix` | A table showing correct/incorrect predictions |
| `roc_auc_score` | Calculates the AUC-ROC score (model quality measure) |
| `ConfusionMatrixDisplay` | Draws the confusion matrix as a visual plot |
| `Pipeline` | (Imported, available for building model pipelines if needed) |
| `StandardScaler` | (Imported, available to normalize features if needed) |

---

### Lines 21–31 — Paths and Feature Column Names

```python
ROOT_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = ROOT_DIR / "data" / "processed"
MODEL_DIR  = ROOT_DIR / "models"
FEAT_CSV   = PROC_DIR / "feature_matrix.csv"
MODEL_PATH = MODEL_DIR / "lasa_classifier.pkl"
```

Standard path setup:
- `FEAT_CSV` = the input (spreadsheet from Module 02)
- `MODEL_PATH` = where the trained model will be saved

```python
FEATURE_COLS = [
    "levenshtein_norm", "jaro_winkler", "token_sort_ratio",
    "ngram_bigram", "ngram_trigram",
    "soundex_match", "metaphone_match", "prefix5_match", "length_ratio",
]
```

This is the **list of the 9 feature column names**. These are the exact column names in the CSV. When loading data, we'll only use these 9 columns as inputs to the model (not the `label` column, which is the answer).

---

### Lines 34–41 — The `evaluate()` Helper Function

```python
def evaluate(name, model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc    = roc_auc_score(y_test, y_prob)
    print(f"\n-- {name} ----------------------")
    print(classification_report(y_test, y_pred, target_names=["Non-LASA", "LASA"]))
    print(f"  AUC-ROC: {auc:.4f}")
    return auc, y_pred
```

This helper function tests a trained model and reports how well it did.

**Parameter by parameter:**
- `name` — Just the model's name (e.g., "RandomForest"), used for printing
- `model` — The trained AI model object
- `X_test` — The test input data (9 feature columns, 20% of the total data)
- `y_test` — The correct answers for the test data (actual labels: 0 or 1)

```python
y_pred = model.predict(X_test)
```
Ask the model to **predict** the label (0 or 1) for every row in the test set.

```python
y_prob = model.predict_proba(X_test)[:, 1]
```
Ask the model to give a **probability** for each prediction.

- `predict_proba()` returns a table with 2 columns: `[P(label=0), P(label=1)]`
- `[:, 1]` means "take column 1" → the probability that the label is 1 (LASA pair)

```python
auc = roc_auc_score(y_test, y_prob)
```
Compare the probabilities against the real labels to compute the **AUC-ROC** score (0.5 = random guessing, 1.0 = perfect).

```python
print(classification_report(y_test, y_pred, target_names=["Non-LASA", "LASA"]))
```
Print a detailed breakdown of model performance with **precision**, **recall**, and **F1-score** for each class.

**What are these terms?**

| Term | Plain English |
|:---|:---|
| Precision | Of all the pairs I said were LASA, what % were actually LASA? |
| Recall | Of all the actual LASA pairs, what % did I catch? |
| F1-Score | A balanced average of Precision and Recall |

---

### Lines 43–51 — The `evaluate_baseline()` Function

```python
def evaluate_baseline(X_test, y_test):
    jw_scores = X_test["jaro_winkler"].fillna(0)
    y_pred    = (jw_scores > 0.85).astype(int)
    auc       = roc_auc_score(y_test, jw_scores)
    print("-- Fuzzy Matching Baseline (Jaro-Winkler > 0.85) --")
    print(classification_report(y_test, y_pred, target_names=["Non-LASA", "LASA"]))
    print(f"  AUC-ROC: {auc:.4f}")
    return auc, y_pred
```

This tests a **simple baseline** — to see how well a naive approach (just using one score with a fixed threshold) performs, so we can compare it to our full ML model.

```python
jw_scores = X_test["jaro_winkler"].fillna(0)
```
Just take the Jaro-Winkler column from the test data. `.fillna(0)` replaces any missing values with 0.

```python
y_pred = (jw_scores > 0.85).astype(int)
```
Simple rule: *"If the Jaro-Winkler score is above 0.85, say it's a LASA pair."*
`(jw_scores > 0.85)` gives True/False → `.astype(int)` converts to 1/0.

This is the "dumb" approach — and comparing our AI's AUC to this baseline proves the AI is genuinely smarter than a single threshold rule.

---

### Lines 54–103 — The `main()` Function

```python
def main():
    MODEL_DIR.mkdir(exist_ok=True)
```
Create the `models/` folder if it doesn't exist yet.

```python
    df = pd.read_csv(FEAT_CSV)
    X = df[FEATURE_COLS].fillna(0)
    y = df["label"]
```
- Load the feature matrix CSV
- `X` = the input features (the 9 columns) — this is what the model learns FROM
- `y` = the labels (column: "label") — this is what the model learns TO PREDICT
- `.fillna(0)` — Replace any missing values with 0 (safe default)

```python
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
```

**This is one of the most important lines in machine learning.**

It splits the data into:
- **80% Training set** (`X_train`, `y_train`) — what the model will learn from
- **20% Test set** (`X_test`, `y_test`) — kept aside, the model NEVER sees this during training

Think of it like: studying from 80% of past exam papers, then testing yourself on the remaining 20% papers that you've never seen before.

- `test_size=0.2` → 20% goes to the test set
- `random_state=42` → Sets a fixed random seed so the split is always the same (reproducible)
- `stratify=y` → Ensures the 80/20 split is balanced: if 30% of all rows are LASA pairs, then 30% of training rows AND 30% of test rows will be LASA pairs. This is critical for fairness.

---

### Lines 72–81 — Defining the Two Models

```python
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
```

This creates a dictionary containing both AI models. Let's break down each setting:

**RandomForestClassifier settings:**

| Setting | Value | What it means |
|:---|:---|:---|
| `n_estimators` | 200 | Build 200 independent decision trees (the "forest") |
| `class_weight` | "balanced" | Pay more attention to LASA pairs since they're rarer — don't let the model cheat by always saying "not dangerous" |
| `max_depth` | 10 | Each decision tree can be at most 10 levels deep (prevents overfitting) |
| `random_state` | 42 | Fixed randomness for reproducibility |
| `n_jobs` | -1 | Use all available CPU cores to train in parallel (faster) |

**GradientBoostingClassifier settings:**

| Setting | Value | What it means |
|:---|:---|:---|
| `n_estimators` | 200 | Train 200 sequential corrective trees |
| `learning_rate` | 0.05 | How much each new tree corrects the previous — 0.05 is cautious (more stable) |
| `max_depth` | 5 | Each tree is smaller (5 levels) — GBM trees are usually shallower |
| `random_state` | 42 | Fixed randomness |

---

### Lines 83–91 — Training Loop

```python
    best_auc   = -1
    best_model = None
    best_name  = ""

    for name, clf in models.items():
        clf.fit(X_train, y_train)
        auc, _ = evaluate(name, clf, X_test, y_test)
        if auc > best_auc:
            best_auc, best_model, best_name = auc, clf, name
```

- Start with `best_auc = -1` so even a bad model will be selected first
- `for name, clf in models.items():` → Loop through both models
- `clf.fit(X_train, y_train)` → **TRAIN** the model. This is where the learning actually happens. The model sees all 800+ rows of training data and finds patterns.
- `evaluate(name, clf, X_test, y_test)` → Test it on the held-out test set
- `if auc > best_auc:` → If this model outperformed the previous best, update the best

---

### Lines 95–103 — Saving the Best Model

```python
    artifact = {
        "model":        best_model,
        "feature_cols": FEATURE_COLS,
        "model_name":   best_name,
        "auc":          best_auc,
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"> Model saved -> {MODEL_PATH}")
```

Instead of just saving the model object, we save a **dictionary** containing:
- The trained model itself
- The list of feature column names (so future code knows exactly what order the 9 features must be in)
- The model's name as a string
- The model's AUC score (for reference)

`joblib.dump()` serializes this dictionary to a `.pkl` file. This is like converting a complex object into a saveable format (like saving a Word document to a `.docx` file).

---

### Lines 105–116 — Confusion Matrix Plot

```python
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
```

This creates and saves a **confusion matrix image**.

A confusion matrix is a 2x2 grid showing:

```
                Predicted Non-LASA | Predicted LASA
Actual Non-LASA      TN (correct)  |   FP (false alarm)
Actual LASA          FN (missed!)  |   TP (correct catch)
```

- `confusion_matrix(y_test, y_pred_best)` → Compute the 2x2 table
- `plt.subplots(figsize=(5, 4))` → Create a 5x4 inch canvas to draw on
- `ConfusionMatrixDisplay(...)` → Set up the display object
- `disp.plot(ax=ax, colorbar=False)` → Draw the matrix on the canvas
- `plt.savefig(plot_path)` → Save as a PNG image
- `plt.close()` → Close the plot to free memory

---

## Summary: What This File Produces

| Output File | What's In It |
|:---|:---|
| `models/lasa_classifier.pkl` | The trained AI model (dict with model, feature columns, name, AUC) |
| `models/confusion_matrix.png` | A visual showing correct vs incorrect predictions |
