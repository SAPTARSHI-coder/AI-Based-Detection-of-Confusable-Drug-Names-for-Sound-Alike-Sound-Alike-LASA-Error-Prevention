# 📄 02_feature_engineering.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It takes every drug pair from the training spreadsheet and calculates 9 numbers that describe how similar the two drug names are — turning words into numbers that an AI model can understand.

---

## Real-Life Analogy Before We Start

Imagine you're a linguistics expert asked to compare two names.

Instead of just saying *"they sound similar,"* you measure them precisely:
- How many letters are different?
- Do they rhyme?
- Do they share syllable chunks?
- Are they the same length?

That's exactly what this module does. It converts two drug name strings into 9 measurable numbers — a process called **feature engineering**.

> **Why "feature engineering"?** In machine learning, a "feature" is a measurable property of something. Engineering them means carefully designing and computing the right measurements.

---

## The Full Code, Explained Line by Line

---

### Lines 1–4 — Docstring

```python
"""
Module 2: Feature Engineering
Computes string-similarity features for each drug pair in the training dataset.
"""
```
Plain description of what this file does. The AI ignores this — it's just for humans.

---

### Lines 5–10 — Imports

```python
import pandas as pd
import numpy as np
from pathlib import Path
from rapidfuzz import distance as rfd, fuzz
import jellyfish
from sklearn.feature_extraction.text import CountVectorizer
```

| Import | What it's used for |
|:---|:---|
| `pandas as pd` | Read CSV files and build tables/spreadsheets |
| `numpy as np` | Numerical math operations |
| `Path` | Smart cross-platform file path handling |
| `rapidfuzz` (as `rfd` and `fuzz`) | Fast string similarity calculations — Levenshtein, WRatio, Token Sort |
| `jellyfish` | Phonetic encoding — Soundex and Metaphone |
| `CountVectorizer` | (Imported here but the custom n-gram functions are used instead) |

---

### Lines 12–16 — File Path Setup

```python
ROOT_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT_DIR / "data" / "processed"

INPUT_CSV  = PROC_DIR / "training_dataset.csv"
OUTPUT_CSV = PROC_DIR / "feature_matrix.csv"
```

- `ROOT_DIR` = the project's root folder (`lasa_detection/`)
- `INPUT_CSV` = the training spreadsheet produced by Module 01
- `OUTPUT_CSV` = where this module will save its results (the 9 feature numbers)

---

### Lines 19–23 — The `metaphone_match()` Function

```python
def metaphone_match(a: str, b: str) -> int:
    try:
        return int(jellyfish.metaphone(a) == jellyfish.metaphone(b))
    except Exception:
        return 0
```

**What does Metaphone do?**

Metaphone converts a word into a phonetic code based on how it sounds in English. Think of it like a "sounds like" fingerprint.

- `jellyfish.metaphone("hydroxyzine")` → `"HTRKSN"`
- `jellyfish.metaphone("hydralazine")` → `"HTRLSN"`

If the two codes are the same → the drugs sound the same → result is `1` (True)
If the codes are different → result is `0` (False)

`int(...)` converts the Python True/False into 1 or 0 (numbers).

`try/except` — this is a safety net. If `jellyfish.metaphone()` crashes for some unusual input, the function returns `0` instead of crashing the entire program.

---

### Lines 25–29 — The `soundex_match()` Function

```python
def soundex_match(a: str, b: str) -> int:
    try:
        return int(jellyfish.soundex(a) == jellyfish.soundex(b))
    except Exception:
        return 0
```

Exactly the same structure as `metaphone_match()` but using **Soundex** instead.

**What is Soundex?**

Soundex is an older, simpler phonetic encoding system. It produces a 4-character code: one letter followed by 3 digits.

- `jellyfish.soundex("dopamine")` → `"D155"`
- `jellyfish.soundex("dobutamine")` → `"D153"`

These are very close (only the last digit differs), which correctly reflects that the names sound similar.

---

### Lines 31–32 — The `prefix_match()` Function

```python
def prefix_match(a: str, b: str, n: int = 5) -> int:
    return int(a[:n] == b[:n])
```

**What does `a[:5]` mean?**

In Python, `a[:5]` means *"take the first 5 characters of string `a`."*

- `"vincristine"[:5]` = `"vinci"`
- `"vinblastine"[:5]` = `"vinbl"`

They're different → `0`

Why 5 characters? Because the first 5 characters of a drug name is often the most recognizable and memorable part — and if two drugs share those 5 characters, a handwriting misread or quick glance could easily confuse them.

---

### Lines 34–41 — The `ngram_overlap()` Function

```python
def ngram_overlap(a: str, b: str, n: int = 2) -> float:
    """Character n-gram Jaccard overlap."""
    def ngrams(s):
        return set(s[i:i+n] for i in range(len(s) - n + 1))
    g1, g2 = ngrams(a), ngrams(b)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)
```

**What is an n-gram?**

An n-gram is every consecutive group of `n` characters in a word.

For `n=2` (bigrams):
```
"dopamine" → {"do", "op", "pa", "am", "mi", "in", "ne"}
```

For `n=3` (trigrams):
```
"dopamine" → {"dop", "opa", "pam", "ami", "min", "ine"}
```

**Inner function `ngrams(s)`:**
```python
return set(s[i:i+n] for i in range(len(s) - n + 1))
```
This loops through every position `i` in the string and takes a slice of `n` characters starting at position `i`. The result is a **set** (no duplicates).

**The Jaccard Formula:**
```python
return len(g1 & g2) / len(g1 | g2)
```
- `g1 & g2` → items that appear in BOTH sets (shared n-grams)
- `g1 | g2` → items that appear in EITHER set (all unique n-grams combined)
- Dividing gives a score: 0 (nothing shared) to 1 (identical)

**Example:**
```
"dopamine"  bigrams: {do, op, pa, am, mi, in, ne}  — 7 items
"dobutamine" bigrams: {do, ob, bu, ut, ta, am, mi, in, ne} — 9 items

Shared (& ): {do, am, mi, in, ne} — 5 items
Union  (| ): {do, op, pa, am, mi, in, ne, ob, bu, ut, ta} — 11 items

Score = 5 / 11 = 0.45
```

---

### Lines 43–46 — The `length_ratio()` Function

```python
def length_ratio(a: str, b: str) -> float:
    if max(len(a), len(b)) == 0:
        return 1.0
    return min(len(a), len(b)) / max(len(a), len(b))
```

Divides the shorter word's length by the longer word's length.

- If both words are 9 letters long: `9/9 = 1.0` (identical length)
- If one is 5 letters and the other is 10: `5/10 = 0.5` (very different lengths)

The `if max(...) == 0: return 1.0` is a safety check for the unlikely case of two empty strings — to avoid dividing by zero (which would crash Python).

---

### Lines 49–65 — The `compute_features()` Function

```python
def compute_features(row: pd.Series) -> dict:
    a, b = str(row["drug1"]), str(row["drug2"])
    lev_dist  = rfd.Levenshtein.distance(a, b)
    max_len   = max(len(a), len(b)) or 1
    lev_norm  = 1 - lev_dist / max_len

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
```

This is the **core function** of the entire file. For each row in the training data (each drug pair), it calculates all 9 features and returns them as a dictionary.

**Breaking down each line:**

```python
a, b = str(row["drug1"]), str(row["drug2"])
```
Extract the two drug names from the current row. `str()` converts them to text in case they're stored in a different format.

```python
lev_dist = rfd.Levenshtein.distance(a, b)
```
Calculate the raw **Levenshtein distance** — the number of single-character edits needed to turn `a` into `b`.

```python
max_len = max(len(a), len(b)) or 1
```
Find the length of the longer word. `or 1` prevents a division-by-zero if both words are somehow empty (very unlikely but safe to handle).

```python
lev_norm = 1 - lev_dist / max_len
```
Normalize the Levenshtein distance to a 0–1 scale. Subtracting from 1 flips it so that:
- 1 = identical (0 edits needed)
- 0 = completely different

```python
"jaro_winkler": fuzz.WRatio(a, b) / 100.0,
```
`fuzz.WRatio()` returns a score from 0 to 100. Dividing by 100 converts it to 0–1 range.

```python
"token_sort_ratio": fuzz.token_sort_ratio(a, b) / 100.0,
```
Another fuzzy string comparison from `rapidfuzz`, also divided by 100.

```python
"ngram_bigram":  ngram_overlap(a, b, 2),
"ngram_trigram": ngram_overlap(a, b, 3),
```
Calls the `ngram_overlap()` function defined earlier, with `n=2` and `n=3`.

```python
"soundex_match":   soundex_match(a, b),
"metaphone_match": metaphone_match(a, b),
"prefix5_match":   prefix_match(a, b, 5),
"length_ratio":    length_ratio(a, b),
```
Calls the helper functions defined earlier.

---

### Lines 68–72 — The `build_features()` Function

```python
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    features = df.apply(compute_features, axis=1, result_type="expand")
    if "label" in df.columns:
        features["label"] = df["label"].values
    return features
```

```python
features = df.apply(compute_features, axis=1, result_type="expand")
```
- `df.apply()` → Run a function on every row of the dataframe
- `compute_features` → The function to run on each row
- `axis=1` → Apply row by row (not column by column)
- `result_type="expand"` → Expand the dictionary result into separate columns

```python
if "label" in df.columns:
    features["label"] = df["label"].values
```
If the source data has a `label` column (1 or 0), copy it into the features table. This label tells the AI whether the pair is LASA or not.

---

### Lines 74–85 — The `main()` Function

```python
def main():
    print("Loading training dataset ...")
    df = pd.read_csv(INPUT_CSV)
    print(f"  Rows loaded: {len(df)}")
```
Load the `training_dataset.csv` file created by Module 01.

```python
    print("Computing features …")
    feat_df = build_features(df)
```
Call `build_features()` on the entire dataframe. This runs `compute_features()` on every row.

```python
    feat_df.to_csv(OUTPUT_CSV, index=False)
    print(f"> Feature matrix saved -> {OUTPUT_CSV.name}")
    print(f"  Shape: {feat_df.shape}")
    print(feat_df.head(3))
```
- `.to_csv()` → Save the resulting table as a CSV file (`feature_matrix.csv`)
- `index=False` → Don't include the row numbers in the saved file
- `feat_df.shape` → Print how many rows and columns the table has
- `feat_df.head(3)` → Print the first 3 rows as a preview

---

## Summary: What This File Produces

| Output File | Contents |
|:---|:---|
| `data/processed/feature_matrix.csv` | One row per drug pair, 9 feature columns + `label` column |

**Example of what one row looks like:**

| drug1 | drug2 | lev | jw | tok | bi | tri | sx | mt | pf | len | label |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| dopamine | dobutamine | 0.70 | 0.89 | 0.89 | 0.45 | 0.27 | 1 | 0 | 0 | 0.80 | 1 |
| aspirin | ibuprofen | 0.22 | 0.40 | 0.40 | 0.10 | 0.05 | 0 | 0 | 0 | 0.78 | 0 |
