# 📄 04_lasa_engine.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

Given a drug name as input, it loads the saved AI model, compares that drug against every drug in the master list using 9 similarity features, and returns the top 10 most dangerous confusable matches with their risk probabilities.

---

## Real-Life Analogy

Think of this module as the **airport security scanner**.

You put a bag through the scanner (your drug name goes in). The scanner compares it against a database of thousands of known threat patterns (all 300+ drug names). It returns a ranked list: *"These 10 items in the bag are the most suspicious, here's the confidence level for each."*

This module is the bridge between the trained AI model and real-time use. It takes one new drug name and uses everything the model learned to answer: *"Which other drugs could this be confused with?"*

---

## The Full Code, Explained Line by Line

---

### Lines 1–5 — Docstring

```python
"""
Module 4: LASA Detection Engine
Given a query drug name, scores it against all known drugs and
returns top-N most confusable drugs with risk probabilities.
"""
```
Plain description. Python ignores this at runtime.

---

### Lines 6–9 — Imports

```python
import joblib
import pandas as pd
from pathlib import Path
from typing import List, Dict
```

| Import | Purpose |
|:---|:---|
| `joblib` | Load the saved trained model from the `.pkl` file |
| `pandas as pd` | Build a DataFrame (table) from the feature rows |
| `Path` | File path handling |
| `List, Dict` | Type hints — they tell Python-aware editors what kind of data functions expect and return. `List` means a list, `Dict` means a dictionary. |

---

### Lines 11–14 — Loading the Shared Feature Calculator

```python
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from modules_utils import compute_features_pair
```

**Why is this needed?**

`compute_features_pair` is a function that lives in a separate file — `modules_utils.py`. To use it here, we need to:
1. Tell Python where to look for it: `sys.path.insert(0, ...)` adds the `modules/` folder to Python's search list
2. Import it: `from modules_utils import compute_features_pair`

This is called **code reuse**. The same feature calculation function is used in both training (Module 02) and real-time inference here (Module 04). Defining it once in `modules_utils.py` prevents duplication and ensures consistency — the exact same 9 features are always computed the same way.

---

### Lines 16–18 — File Path Setup

```python
ROOT_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "lasa_classifier.pkl"
DRUG_LIST  = ROOT_DIR / "data" / "drug_list.txt"
```

- `MODEL_PATH` — Points to the saved trained model (`.pkl` file)
- `DRUG_LIST` — Points to the master drug name list (`drug_list.txt`)

---

### Lines 21–27 — The `load_engine()` Function

```python
def load_engine():
    artifact   = joblib.load(MODEL_PATH)
    model      = artifact["model"]
    feat_cols  = artifact["feature_cols"]
    with open(DRUG_LIST, encoding="utf-8") as f:
        drugs = [line.strip() for line in f if line.strip()]
    return model, feat_cols, drugs
```

This function loads everything the engine needs before scoring can begin.

```python
artifact = joblib.load(MODEL_PATH)
```
Load the `.pkl` file from disk. Remember, this file is a dictionary containing the model, feature column names, model name, and AUC score — all saved by Module 03.

```python
model     = artifact["model"]
feat_cols = artifact["feature_cols"]
```
Extract just the model object and the feature column names from the dictionary.

```python
with open(DRUG_LIST, encoding="utf-8") as f:
    drugs = [line.strip() for line in f if line.strip()]
```
Read the drug list file line by line:
- `for line in f` → Read each line
- `line.strip()` → Remove whitespace/newline from each line
- `if line.strip()` → Skip any blank lines
- The result is a Python **list** of drug names: `["aspirin", "dopamine", "fentanyl", ...]`

```python
return model, feat_cols, drugs
```
Return all three items as a tuple — they'll be used immediately in `score_drug()`.

---

### Lines 30–61 — The `score_drug()` Function

This is the **main function** of this module — the function that does all the real work.

```python
def score_drug(query: str, top_n: int = 10) -> List[Dict]:
```
- `query: str` — The drug name to check (e.g., `"hydralazine"`)
- `top_n: int = 10` — How many top matches to return (default is 10)
- `-> List[Dict]` — Returns a list of dictionaries (each dict = one match result)

```python
    model, feat_cols, drugs = load_engine()
    query = query.lower().strip()
```
- Load everything (model + drug list)
- Clean the query: convert to lowercase, remove surrounding spaces

This ensures consistency — if the user types `"Hydralazine"` or `"HYDRALAZINE"`, they all become `"hydralazine"`.

---

```python
    rows = []
    for candidate in drugs:
        if candidate == query:
            continue
        feat = compute_features_pair(query, candidate)
        rows.append(feat)
```

This is the **comparison loop** — the heart of the engine.

For every drug in the master list:
- Skip the drug if it's the same as what we're searching (you can't confuse a drug with itself)
- Calculate the 9 similarity features between `query` and `candidate`
- Store the feature dictionary in `rows`

At the end, `rows` is a list of ~300 dictionaries, one per drug comparison.

**Example of one entry in `rows`:**
```python
{
    "levenshtein_norm": 0.83,
    "jaro_winkler": 0.96,
    "token_sort_ratio": 0.96,
    "ngram_bigram": 0.75,
    "ngram_trigram": 0.54,
    "soundex_match": 1,
    "metaphone_match": 0,
    "prefix5_match": 0,
    "length_ratio": 0.92
}
```

---

```python
    if not rows:
        return []
```
Safety check: if somehow the drug list is empty, return an empty list instead of crashing.

---

```python
    df    = pd.DataFrame(rows, columns=feat_cols)
    probs = model.predict_proba(df.fillna(0))[:, 1]
```

```python
df = pd.DataFrame(rows, columns=feat_cols)
```
Convert the list of ~300 feature dictionaries into a proper DataFrame (table). Each row is one drug comparison; each column is one of the 9 features.

```python
probs = model.predict_proba(df.fillna(0))[:, 1]
```
- `df.fillna(0)` → Replace any missing values with 0
- `model.predict_proba(...)` → Ask the model to predict probabilities for all ~300 rows at once
- This returns a table with 2 columns: `[P(not LASA), P(LASA)]`
- `[:, 1]` → Keep only column 1 (the LASA probability)

Now `probs` is an array of ~300 numbers, each between 0 and 1.

---

```python
    results = []
    for i, candidate in enumerate([d for d in drugs if d != query]):
        p = float(probs[i])
        risk = "HIGH" if p > 0.75 else ("MEDIUM" if p > 0.45 else "LOW")
        results.append({"candidate": candidate, "lasa_prob": round(p, 4), "risk_level": risk})
```

Now build the result list:

- `enumerate(...)` → Loop with both an index `i` and the candidate drug name
- `p = float(probs[i])` → Get the LASA probability for this candidate (as a plain Python float)
- Risk assignment:
  - > 0.75 → HIGH
  - > 0.45 → MEDIUM
  - Otherwise → LOW

> **Note:** In the web app (`app.py`), additional scores are added for ISMP-known pairs and context mismatch. This module gives the raw base probability only.

```python
results.sort(key=lambda x: x["lasa_prob"], reverse=True)
return results[:top_n]
```
- Sort the results by `lasa_prob` from highest to lowest (most dangerous first)
- Return only the top `top_n` matches (default 10)

**`lambda x: x["lasa_prob"]`** — A lambda is a tiny, one-line anonymous function. This one says: *"When sorting, use the `lasa_prob` value from each result dictionary as the sort key."*

---

### Lines 63–69 — CLI Demo

```python
if __name__ == "__main__":
    query = input("Enter drug name to check: ").strip()
    hits  = score_drug(query)
    print(f"\nTop LASA matches for '{query}':")
    for h in hits:
        print(f"  {h['candidate']:<25} prob={h['lasa_prob']:.3f}  [{h['risk_level']}]")
```

This section only runs when you execute this file directly in a terminal (not when it's imported by the web app).

- `input(...)` → Pause and wait for the user to type a drug name in the terminal
- Call `score_drug()` with the user's input
- Print each result formatted neatly:
  - `{h['candidate']:<25}` → Print the drug name, left-aligned in a 25-character column
  - `{h['lasa_prob']:.3f}` → Print the probability with 3 decimal places
  - `[{h['risk_level']}]` → Print the risk level in brackets

**If you ran this file directly:**
```
Enter drug name to check: hydralazine

Top LASA matches for 'hydralazine':
  hydroxyzine               prob=0.974  [HIGH]
  hydralazine hcl           prob=0.891  [HIGH]
  clonidine                 prob=0.412  [LOW]
  ...
```

---

## Summary: What This File Does at Runtime

```
Input:   "hydralazine"  (query drug name)
             ↓
Load:    models/lasa_classifier.pkl  +  data/drug_list.txt
             ↓
Compare: "hydralazine" vs every drug in the list (~300 comparisons)
         Each comparison → 9 feature numbers → fed to model
             ↓
Score:   Model outputs a LASA probability for each comparison
             ↓
Output:  Top 10 most similar/dangerous drugs, sorted by probability
         [{"candidate": "hydroxyzine", "lasa_prob": 0.97, "risk_level": "HIGH"}, ...]
```
