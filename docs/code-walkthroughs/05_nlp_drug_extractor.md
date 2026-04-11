# 📄 05_nlp_drug_extractor.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It reads a clinical sentence (like a doctor's order) and pulls out three pieces of information: the **drug name**, the **dose** (e.g., 500mg), and the **route** (e.g., oral, IV).

---

## Real-Life Analogy

Think of a pharmacist's assistant whose only job is to read prescriptions and highlight three things with a yellow marker:

1. 🟡 **Drug name** — What is being prescribed?
2. 🟡 **Dose** — How much?
3. 🟡 **Route** — How is it being given?

They ignore everything else in the sentence (the patient's name, the date, the instructions). They just need those three things to pass to the next step in the workflow.

This module is that assistant.

---

## The Full Code, Explained Line by Line

---

### Lines 1–5 — Docstring

```python
"""
Module 5: NLP Drug Extractor
Extracts drug names, dosage, and route from free-text clinical sentences.
Phase 1: regex + dictionary lookup (interpretable, no heavy model needed).
"""
```
Describes the file's purpose. The comment *"Phase 1"* indicates this uses a simpler rule-based approach — future improvements could swap it for a deep learning NER (Named Entity Recognition) model.

---

### Lines 6–8 — Imports

```python
import re
from pathlib import Path
from typing import Optional, Dict
```

| Import | Purpose |
|:---|:---|
| `re` | Regular expressions — a powerful pattern matching tool for searching text |
| `Path` | Smart file path handling |
| `Optional` | A type hint meaning a value that could be `None` (no value) |
| `Dict` | A type hint for dictionary return types |

---

### Lines 10–11 — File Path Setup

```python
ROOT_DIR  = Path(__file__).resolve().parent.parent
DRUG_LIST = ROOT_DIR / "data" / "drug_list.txt"
```
Points to the master drug dictionary file (`drug_list.txt`). This file was created by Module 01 and contains one drug name per line.

---

### Lines 13–16 — The Dosage Pattern

```python
DOSAGE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units?|u|%)',
    re.IGNORECASE
)
```

This is a **regular expression** (regex) — a pattern that searches for text matching a specific format.

**What does this pattern mean in plain English?**

> *"Find: one or more digits, optionally followed by a decimal point and more digits, then optional spaces, then a unit like mg, mcg, g, ml, units, u, or %."*

Breaking down the pattern character by character:

| Part | Meaning |
|:---|:---|
| `\d+` | One or more digit characters (0–9) |
| `(?:\.\d+)?` | Optionally, a decimal point followed by more digits (for doses like 2.5mg) |
| `\s*` | Zero or more spaces between the number and the unit |
| `(mg\|mcg\|g\|ml\|units?\|u\|%)` | The unit — one of these options. The `?` after `units` makes the `s` optional (so both "unit" and "units" match) |
| `re.IGNORECASE` | Match regardless of uppercase/lowercase — "MG", "mg", "Mg" all match |

```python
re.compile(...)
```
This **compiles** the pattern once and stores it in `DOSAGE_PATTERN`. Compiling it once upfront is more efficient than recompiling it every time it's needed.

**Example matches:**
- `"500mg"` → matches → `"500mg"`
- `"2.5 mcg"` → matches → `"2.5 mcg"`
- `"10 units"` → matches → `"10 units"`

---

### Lines 17–21 — The Route Keywords Set

```python
ROUTE_KEYWORDS = {
    "oral", "po", "iv", "intravenous", "im", "intramuscular",
    "subcutaneous", "sc", "topical", "inhaled", "sublingual",
    "rectal", "nasal", "ophthalmic", "transdermal",
}
```

This is a **set** (like a list but with no duplicates and faster lookup) of all recognized routes of drug administration.

| Abbreviation | Full Form |
|:---|:---|
| `po` | Per os (by mouth) — oral |
| `iv` | Intravenous (into a vein) |
| `im` | Intramuscular (into a muscle) |
| `sc` | Subcutaneous (under the skin) |
| `sublingual` | Under the tongue |

When scanning the sentence, the extractor checks whether any word from this set appears.

---

### Lines 23–33 — The Drug List Loader

```python
_drug_set: Optional[set] = None

def _load_drugs() -> set:
    global _drug_set
    if _drug_set is None:
        if DRUG_LIST.exists():
            with open(DRUG_LIST, encoding="utf-8") as f:
                _drug_set = {l.strip().lower() for l in f if l.strip()}
        else:
            _drug_set = set()
    return _drug_set
```

**Why the underscore prefix `_drug_set` and `_load_drugs`?**

In Python, names starting with `_` are conventionally "private" — meaning they're internal implementation details, not meant to be used directly by other modules.

**Why `global _drug_set`?**

`_drug_set` is defined outside any function (at module level), which makes it a **global variable**. The line `global _drug_set` inside the function tells Python: *"When I write `_drug_set = ...` below, I'm modifying the global variable, not creating a new local one."*

**The lazy loading pattern (caching):**

```python
if _drug_set is None:
    # ... load the file
```

The `if _drug_set is None:` check means: *"Only load the file once. After the first time, it's already in memory — just return it."* This is called **lazy loading** or **caching** — don't do expensive work (reading a file from disk) more than necessary.

**The set comprehension:**

```python
_drug_set = {l.strip().lower() for l in f if l.strip()}
```

This reads every line in the file and creates a set of cleaned drug names:
- `for l in f` → read each line
- `if l.strip()` → skip blank lines
- `l.strip().lower()` → remove whitespace and convert to lowercase

---

### Lines 35–66 — The `extract()` Function

This is the **main function** — the one other modules call.

```python
def extract(sentence: str) -> Dict:
```
Takes one input: a clinical sentence (string). Returns a dictionary with drug, dosage, route, and the original sentence.

```python
    drugs    = _load_drugs()
    sentence = sentence.strip()
    lower    = sentence.lower()
```
- Load (or retrieve from cache) the drug dictionary
- Clean the sentence: remove leading/trailing whitespace
- Create a lowercase version (`lower`) — used for case-insensitive searching without modifying the original

---

**Step 1: Extract the Dose**

```python
    dosage_match = DOSAGE_PATTERN.search(sentence)
    dosage = dosage_match.group(0) if dosage_match else None
```

- `DOSAGE_PATTERN.search(sentence)` → Search the sentence for a dosage pattern
- `.search()` returns a **match object** if found, or `None` if not found
- `.group(0)` → Extract the entire matched text (the full dosage string)
- If nothing found → `dosage = None`

**Example:**
```
sentence = "Give dopamine 5mg IV"
DOSAGE_PATTERN.search(sentence) → matches "5mg"
dosage = "5mg"
```

---

**Step 2: Extract the Route**

```python
    route = None
    for kw in ROUTE_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', lower):
            route = kw
            break
```

Loop through every route keyword. Check if that keyword appears as a **whole word** in the sentence.

`r'\b' + kw + r'\b'` builds a pattern like `\biv\b` — the `\b` means "word boundary" (the edge of a word). This prevents partial matches — `"intravenous"` wouldn't accidentally match a word that just happens to contain "iv" as letters.

As soon as a match is found, save it to `route` and stop (`break`) — no need to keep checking.

---

**Step 3: Extract the Drug Name**

```python
    found_drug = None
    best_len   = 0
    for drug in drugs:
        if re.search(r'\b' + re.escape(drug) + r'\b', lower):
            if len(drug) > best_len:
                found_drug, best_len = drug, len(drug)
```

This is the **longest match strategy**.

Loop through every drug in the dictionary. For each:
- `re.escape(drug)` → Makes any special characters in the drug name safe for regex (e.g., periods in drug names)
- `r'\b' + ... + r'\b'` → Match as a whole word only
- If the drug name appears in the sentence AND it's longer than any previous match → save it

**Why longest match?**

Consider a sentence with `"hydromorphone"`. Both `"morphine"` and `"hydromorphone"` might be in the dictionary. We want `"hydromorphone"` — the more specific, longer match — not just `"morphine"` (which is a substring of hydromorphone). The longest match wins.

---

```python
    return {"drug": found_drug, "dosage": dosage, "route": route, "raw": sentence}
```

Return the results as a dictionary:
- `drug` → The identified drug name (or `None` if not found)
- `dosage` → The dose string (or `None`)
- `route` → The administration route (or `None`)
- `raw` → The original unmodified sentence (for reference)

---

### Lines 70–79 — CLI Demo

```python
if __name__ == "__main__":
    samples = [
        "Please administer dopamine 5mg IV immediately.",
        "Patient was given clonazepam 1mg oral for anxiety.",
        "Give the patient fentanyl 50mcg sublingual.",
        "Administer lopressor 25 mg twice a day.",
    ]
    for s in samples:
        result = extract(s)
        print(result)
```

When run directly in the terminal, this tests the extractor on 4 sample sentences and prints the results.

**Expected output:**
```python
{'drug': 'dopamine',   'dosage': '5mg',   'route': 'iv',         'raw': 'Please administer dopamine 5mg IV immediately.'}
{'drug': 'clonazepam', 'dosage': '1mg',   'route': 'oral',       'raw': 'Patient was given clonazepam 1mg oral for anxiety.'}
{'drug': 'fentanyl',   'dosage': '50mcg', 'route': 'sublingual', 'raw': 'Give the patient fentanyl 50mcg sublingual.'}
{'drug': 'lopressor',  'dosage': '25 mg', 'route': None,         'raw': 'Administer lopressor 25 mg twice a day.'}
```

Note: `lopressor`'s route is `None` because none of the route keywords appear in that sentence.

---

## Summary: What This Function Does

```
Input:   "Administer 25mg hydralazine IV for hypertensive patient."
             ↓
Find:    Dosage → "25mg"
         Route  → "iv"
         Drug   → "hydralazine" (matched against drug_list.txt)
             ↓
Output:  {
           "drug": "hydralazine",
           "dosage": "25mg",
           "route": "iv",
           "raw": "Administer 25mg hydralazine IV for hypertensive patient."
         }
```
