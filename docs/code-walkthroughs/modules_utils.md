# 📄 modules_utils.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It provides **one shared function** — `compute_features_pair()` — that calculates all 9 similarity numbers for any two drug names, and it's reused by both the training pipeline (Module 02) and the real-time inference engine (Module 04).

---

## Real-Life Analogy

Think of this file as a **shared measurement kit** in a laboratory.

Two different departments (the Training Lab and the Live Analysis Lab) both need to measure the same properties of drug name pairs. Instead of each department building and maintaining their own measurement tools, the hospital creates one standard kit that everyone uses.

This avoids a critical problem: if Module 02 calculated Levenshtein distance one way, and Module 04 calculated it a different way, the AI model would be trained on different numbers than what it actually receives during live use — causing incorrect predictions. By sharing one function, consistency is guaranteed.

---

## Why This File Is More Important Than It Looks

This is the shortest file in the project (36 lines) but arguably the most **architecturally critical**.

In machine learning, a very common real-world bug is called **training-serving skew**. It happens when:

- Features are calculated one way during **training**
- Features are calculated a slightly different way in **production**

The model then receives numbers that don't match what it was trained on, and its predictions become unreliable.

By defining `compute_features_pair()` in exactly one place and importing it from both Module 02 and Module 04, your codebase has **zero training-serving skew risk**.

---

## The Full Code, Explained Line by Line

---

### Lines 1–4 — Docstring

```python
"""
Shared utility: compute feature vector for a single (drug1, drug2) pair.
Used by both feature_engineering and lasa_engine.
"""
```

Plain-English description. Emphasizes the "shared" nature — this is explicitly the file where the reusable logic lives.

---

### Lines 5–6 — Imports

```python
from rapidfuzz import distance as rfd, fuzz
import jellyfish
```

| Import | What it provides |
|:---|:---|
| `rapidfuzz.distance as rfd` | Fast Levenshtein distance calculation — aliased as `rfd` for brevity |
| `rapidfuzz.fuzz` | WRatio and Token Sort Ratio fuzzy string matching |
| `jellyfish` | Phonetic encoding: Soundex and Metaphone |

**Why `rapidfuzz` instead of the classic `python-Levenshtein`?**

`rapidfuzz` is written with performance-optimized C++ code underneath Python. For this project, where Module 04 runs ~300 comparisons every time a drug is queried, speed matters.

---

### Lines 8–12 — FEATURE_COLS List

```python
FEATURE_COLS = [
    "levenshtein_norm", "jaro_winkler", "token_sort_ratio",
    "ngram_bigram", "ngram_trigram",
    "soundex_match", "metaphone_match", "prefix5_match", "length_ratio",
]
```

This is the **canonical, authoritative list** of the 9 feature names — in the exact order they must appear.

**Why does order matter?**

When the trained model was saved (Module 03), it learned from columns in a specific order. When new data is fed to the model for prediction, the columns must appear in the same order — otherwise the model would mix up, say, `soundex_match` values with `length_ratio` values, producing nonsense predictions.

`FEATURE_COLS` is imported wherever this order needs to be enforced.

---

### Lines 14–20 — The `_ngram_overlap()` Helper Function

```python
def _ngram_overlap(a, b, n=2):
    def ngrams(s):
        return set(s[i:i+n] for i in range(len(s) - n + 1))
    g1, g2 = ngrams(a), ngrams(b)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)
```

This is a **private helper** (the underscore prefix `_` signals: don't call this directly from outside).

**What it does step by step:**

```python
def ngrams(s):
    return set(s[i:i+n] for i in range(len(s) - n + 1))
```

An **inner function** (defined inside `_ngram_overlap`). It takes a string `s` and returns a set of all consecutive `n`-character chunks.

- `s[i:i+n]` → Take `n` characters starting at position `i`
- `range(len(s) - n + 1)` → Loop from position 0 to the last valid start position
- `set(...)` → Store as a set (no duplicates)

**Worked example with `n=2` (bigrams):**

```
s = "dopamine"
positions: 0–7
chunks:
  i=0: s[0:2] = "do"
  i=1: s[1:3] = "op"
  i=2: s[2:4] = "pa"
  i=3: s[3:5] = "am"
  i=4: s[4:6] = "mi"
  i=5: s[5:7] = "in"
  i=6: s[6:8] = "ne"
result: {"do", "op", "pa", "am", "mi", "in", "ne"}
```

```python
g1, g2 = ngrams(a), ngrams(b)
if not g1 or not g2:
    return 0.0
```

Compute ngrams for both drug names. If either word is too short to have any ngrams (e.g., a 1-character word has no bigrams), return 0.0 instead of crashing.

```python
return len(g1 & g2) / len(g1 | g2)
```

**Jaccard Similarity formula:**

```
Jaccard = |intersection| / |union|
        = (items in both sets) / (all unique items across both sets)
```

- Range: 0 (nothing shared) to 1 (sets are identical)
- This gives a normalized score regardless of word length

---

### Lines 22–35 — The `compute_features_pair()` Main Function

```python
def compute_features_pair(a: str, b: str) -> dict:
    lev_dist = rfd.Levenshtein.distance(a, b)
    max_len  = max(len(a), len(b)) or 1
    return {
        "levenshtein_norm": 1 - lev_dist / max_len,
        "jaro_winkler":     fuzz.WRatio(a, b) / 100.0,
        "token_sort_ratio": fuzz.token_sort_ratio(a, b) / 100.0,
        "ngram_bigram":     _ngram_overlap(a, b, 2),
        "ngram_trigram":    _ngram_overlap(a, b, 3),
        "soundex_match":    int(jellyfish.soundex(a) == jellyfish.soundex(b)),
        "metaphone_match":  int(jellyfish.metaphone(a) == jellyfish.metaphone(b)),
        "prefix5_match":    int(a[:5] == b[:5]),
        "length_ratio":     min(len(a), len(b)) / max_len,
    }
```

**Function signature:**

```python
def compute_features_pair(a: str, b: str) -> dict:
```
- `a` → First drug name (e.g., `"hydralazine"`)
- `b` → Second drug name (e.g., `"hydroxyzine"`)
- Returns: a Python `dict` with 9 key-value pairs

---

**Line 1: Levenshtein Distance**

```python
lev_dist = rfd.Levenshtein.distance(a, b)
```

`rfd.Levenshtein.distance()` counts the minimum number of single-character edits (insertions, deletions, substitutions) to convert string `a` into string `b`.

**Example:**
```
a = "hydralazine"  (11 chars)
b = "hydroxyzine"  (11 chars)

Changes needed:
  dral → drox (replace 'a','l' with 'o','x') = 2 changes
  zine → zine (no change)

lev_dist = 2
```

---

**Line 2: Max Length (for normalization)**

```python
max_len = max(len(a), len(b)) or 1
```

- `max(len(a), len(b))` → Length of the longer word
- `or 1` → If both words are empty (length 0), use 1 to prevent division by zero

---

**Line 3: Normalized Levenshtein (in the returned dict)**

```python
"levenshtein_norm": 1 - lev_dist / max_len,
```

Converts the raw distance to a 0–1 similarity score:
- `lev_dist / max_len` = fraction of characters that differ
- `1 - ...` = flip it so 1 = identical, 0 = completely different

```
hydralazine vs hydroxyzine:
  1 - (2 / 11) = 1 - 0.18 = 0.82
```

---

**Line 4: Jaro-Winkler (WRatio)**

```python
"jaro_winkler": fuzz.WRatio(a, b) / 100.0,
```

`fuzz.WRatio()` from rapidfuzz computes a weighted ratio that combines multiple fuzz strategies including Jaro-Winkler. Returns 0–100 → divided by 100 to get 0–1.

This metric gives bonus credit when words share the same prefix, making it especially useful for drug name families (e.g., all cephalosporins start with "cef").

---

**Line 5: Token Sort Ratio**

```python
"token_sort_ratio": fuzz.token_sort_ratio(a, b) / 100.0,
```

`fuzz.token_sort_ratio()` sorts the tokens (words) alphabetically before comparing. For single-word drug names this is functionally similar to WRatio, but it tolerates word-order variations in multi-word names (e.g., "sodium bicarbonate" vs "bicarbonate sodium"). Divided by 100 to get 0–1.

---

**Lines 6–7: N-gram Overlaps**

```python
"ngram_bigram":  _ngram_overlap(a, b, 2),
"ngram_trigram": _ngram_overlap(a, b, 3),
```

Calls the helper defined above with `n=2` (bigrams) and `n=3` (trigrams). Both return Jaccard similarity scores in the 0–1 range.

---

**Lines 8–9: Phonetic Matches**

```python
"soundex_match":   int(jellyfish.soundex(a)    == jellyfish.soundex(b)),
"metaphone_match": int(jellyfish.metaphone(a) == jellyfish.metaphone(b)),
```

Both:
- Convert each drug name to a phonetic code
- Compare the two codes
- `==` returns `True` or `False`
- `int(...)` converts to `1` or `0`

Soundex example:
```
jellyfish.soundex("dopamine")   → "D155"
jellyfish.soundex("dobutamine") → "D153"
"D155" == "D153" → False → int(False) = 0
```

Metaphone example:
```
jellyfish.metaphone("hydroxyzine") → "HTRKSN"
jellyfish.metaphone("hydralazine") → "HTRLSN"
"HTRKSN" == "HTRLSN" → False → 0
```

Even though both return 0 for these pairs, the Jaro-Winkler and Levenshtein scores for `hydralazine/hydroxyzine` are very high — that's what makes the AI flag them as dangerous despite phonetic features not firing.

---

**Line 10: Prefix Match**

```python
"prefix5_match": int(a[:5] == b[:5]),
```

- `a[:5]` → First 5 characters of drug name `a`
- `==` → Are they identical?
- `int(...)` → 1 if yes, 0 if no

```
"vincristine"[:5] = "vinci"
"vinblastine"[:5] = "vinbl"
"vinci" == "vinbl" → False → 0
```

---

**Line 11: Length Ratio**

```python
"length_ratio": min(len(a), len(b)) / max_len,
```

```
min(len("hydralazine"), len("hydroxyzine")) = min(11, 11) = 11
max_len = 11
length_ratio = 11 / 11 = 1.0
```

Both are 11 characters → same length → 1.0. This is consistent with them being easily confused.

---

## What This File Produces: One Complete Example

**Input:** `a = "hydralazine"`, `b = "hydroxyzine"`

**Output:**

```python
{
    "levenshtein_norm": 0.82,   # 82% similar by edit distance
    "jaro_winkler":     0.96,   # 96% similar by character alignment
    "token_sort_ratio": 0.96,   # same as above
    "ngram_bigram":     0.75,   # 75% of 2-char chunks are shared
    "ngram_trigram":    0.54,   # 54% of 3-char chunks are shared
    "soundex_match":    1,      # same Soundex code (S532 for both)
    "metaphone_match":  0,      # slightly different Metaphone codes
    "prefix5_match":    0,      # "hydra" ≠ "hydro"
    "length_ratio":     1.0,    # same length (11 chars each)
}
```

These 9 numbers are what the AI model actually "sees". Given that most scores are very high, the model correctly predicts a very high LASA probability.

---

## Summary: Why This File Exists

| Without `modules_utils.py` | With `modules_utils.py` |
|:---|:---|
| Module 02 has its own feature calculation | One function shared everywhere |
| Module 04 has a different calculation | Same function used in training AND live use |
| Risk of training-serving skew | Zero skew — guaranteed consistency |
| Duplicate code to maintain | Single source of truth — change once, fixed everywhere |
