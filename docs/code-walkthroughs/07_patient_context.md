# 📄 07_patient_context.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It checks whether a prescribed drug makes clinical sense for the patient's diagnosis — using two lookup tables that map drugs to their drug class, and diagnoses to their expected drug classes.

---

## Real-Life Analogy

Imagine a very experienced pharmacist who has memorized:
1. What category every drug belongs to (e.g., metformin → diabetes drug)
2. What categories of drugs are typically prescribed for each disease (e.g., diabetes → diabetes drugs / insulin)

When they see a prescription, they instantly cross-reference: *"Is the drug's category on the list of expected categories for this diagnosis?"* If not, they raise a flag.

This module is that pharmacist's memory, encoded as Python dictionaries.

---

## The Full Code, Explained Line by Line

---

### Lines 1–5 — Docstring

```python
"""
Module 7: Patient Context Validator
Flags potential drug-diagnosis mismatches using a simple
diagnosis → expected drug class mapping.
"""
```
Plain English description of the file's purpose.

---

### Lines 6 — Imports

```python
from typing import Dict, Optional, List
```

Type hints only — no actual functional libraries needed. This file is entirely built from custom dictionaries and logic.

| Type Hint | Meaning |
|:---|:---|
| `Dict` | A Python dictionary (key → value pairs) |
| `Optional` | A value that could be `None` |
| `List` | A Python list (ordered collection) |

---

### Lines 9–55 — DRUG_CLASS_MAP Dictionary

```python
DRUG_CLASS_MAP: Dict[str, str] = {
    # cardiac / BP
    "dopamine":      "vasopressor",
    "dobutamine":    "vasopressor",
    "norepinephrine":"vasopressor",
    "epinephrine":   "vasopressor",
    "amiodarone":    "antiarrhythmic",
    "warfarin":      "anticoagulant",
    "heparin":       "anticoagulant",
    "metoprolol":    "beta_blocker",
    "lopressor":     "beta_blocker",
    "nimodipine":    "calcium_channel_blocker",
    "nifedipine":    "calcium_channel_blocker",
    # diabetes
    "metformin":     "antidiabetic",
    "glipizide":     "antidiabetic",
    "glyburide":     "antidiabetic",
    "insulin":       "antidiabetic",
    ...
}
```

`Dict[str, str]` means: a dictionary where both keys and values are strings.

**Structure:**
```
drug name (string) → drug class (string)
```

**What is a "drug class"?**

A drug class is a **category** of drugs that share the same mechanism of action or therapeutic purpose. This allows grouping:

| Drug Class | What it does |
|:---|:---|
| `vasopressor` | Raises blood pressure — used in emergencies |
| `antiarrhythmic` | Controls abnormal heart rhythms |
| `anticoagulant` | Thins the blood — prevents clotting |
| `beta_blocker` | Slows the heart rate, lowers BP |
| `calcium_channel_blocker` | Relaxes blood vessels |
| `antidiabetic` | Controls blood sugar |
| `opioid` | Pain relief (morphine-like drugs) |
| `antibiotic` | Kills bacteria |
| `benzodiazepine` | Calms nerves / reduces anxiety |
| `antihypertensive` | Lowers blood pressure |
| `antihistamine` | Reduces allergic reactions |
| `vinca_alkaloid` | Chemotherapy — disrupts cell division |
| `platinum_agent` | Chemotherapy — damages cancer cell DNA |
| `corticosteroid` | Reduces inflammation |
| `inotropic` | Strengthens the heart's contractions |
| `diuretic` | Removes excess fluid from the body |

**Why use classes instead of individual drugs?**

Because it would be impractical to list every possible drug-diagnosis pair. By grouping drugs into classes, you can define rules at a higher level: *"For anxiety, give a benzodiazepine or antihistamine"* — covering dozens of individual drug choices without listing them all.

---

### Lines 58–71 — DIAGNOSIS_CLASS_MAP Dictionary

```python
DIAGNOSIS_CLASS_MAP: Dict[str, List[str]] = {
    "cardiac_arrest":       ["vasopressor", "antiarrhythmic"],
    "hypertension":         ["beta_blocker", "calcium_channel_blocker", "antihypertensive"],
    "atrial_fibrillation":  ["antiarrhythmic", "anticoagulant", "beta_blocker"],
    "diabetes":             ["antidiabetic"],
    "pain":                 ["opioid", "nsaid"],
    "infection":            ["antibiotic"],
    "anxiety":              ["benzodiazepine", "antihistamine"],
    "cancer":               ["vinca_alkaloid", "platinum_agent", "corticosteroid"],
    "septic_shock":         ["vasopressor", "antibiotic"],
    "seizure":              ["anticonvulsant", "benzodiazepine"],
    "inflammation":         ["corticosteroid", "nsaid"],
    "heart_failure":        ["vasopressor", "inotropic", "beta_blocker", "diuretic", "antihypertensive"],
}
```

`Dict[str, List[str]]` means: a dictionary where keys are strings (diagnosis names) and values are **lists** of strings (allowed drug classes).

**Structure:**
```
diagnosis name (string) → list of accepted drug class names
```

**Examples:**

| Diagnosis | Why these drug classes? |
|:---|:---|
| `cardiac_arrest` | Need vasopressors to restore blood pressure, antiarrhythmics to fix heart rhythm |
| `diabetes` | Only antidiabetic drugs (metformin, insulin, etc.) |
| `anxiety` | Benzodiazepines (lorazepam) or antihistamines (hydroxyzine) |
| `cancer` | Chemotherapy: vinca alkaloids (vincristine), platinum agents (carboplatin) |

**Why does `heart_failure` have 5 expected classes?**

Heart failure is complex — different aspects of it are treated simultaneously:
- `vasopressor` → support blood pressure if it drops
- `inotropic` → strengthen heart contractions (digoxin)
- `beta_blocker` → reduce heart workload
- `diuretic` → remove fluid buildup in lungs
- `antihypertensive` → control blood pressure long-term

A drug from any of these 5 classes is appropriate. The validator accepts any of them.

---

### Lines 74–108 — The `validate()` Function

This is the **main function** — the one that actually does the checking.

```python
def validate(drug: str, diagnosis: Optional[str]) -> Dict:
```
- `drug: str` — The drug name to check (e.g., `"hydralazine"`)
- `diagnosis: Optional[str]` — The patient's diagnosis (or `None` if not provided)
- Returns a dictionary with the validation result

---

```python
    drug = (drug or "").lower().strip()
    drug_class = DRUG_CLASS_MAP.get(drug)
```

```python
drug = (drug or "").lower().strip()
```
Safety cleanup: if `drug` is `None`, convert to an empty string first (`or ""`). Then lowercase and strip whitespace.

```python
drug_class = DRUG_CLASS_MAP.get(drug)
```
Look up the drug's class in the `DRUG_CLASS_MAP` dictionary.
- If `drug = "metformin"` → `drug_class = "antidiabetic"`
- If `drug = "aspirin"` → `drug_class = None` (not in the map, unknown class)

`.get()` is safer than direct access (`map[key]`) because it returns `None` if the key doesn't exist, instead of crashing.

---

```python
    if not diagnosis:
        return {"mismatch": False, "drug_class": drug_class,
                "expected_classes": [], "note": "No diagnosis provided."}
```

If no diagnosis was given, there's nothing to check — return a "no mismatch" result with a note. This handles the case where a user submits a drug query without a diagnosis.

---

```python
    diagnosis = diagnosis.lower().replace(" ", "_")
    expected  = DIAGNOSIS_CLASS_MAP.get(diagnosis, [])
```

```python
diagnosis = diagnosis.lower().replace(" ", "_")
```
Normalize the diagnosis: lowercase and replace spaces with underscores. This means `"Cardiac Arrest"`, `"cardiac arrest"`, and `"cardiac_arrest"` all work.

```python
expected = DIAGNOSIS_CLASS_MAP.get(diagnosis, [])
```
Look up what drug classes are expected for this diagnosis. The second argument `[]` is the default — if the diagnosis isn't in the map, return an empty list (unknown diagnosis).

---

```python
    mismatch = bool(drug_class and expected and drug_class not in expected)
```

**This is the actual mismatch detection — one line!**

Let's break it down step by step:

| Part | Meaning |
|:---|:---|
| `drug_class` | Truthy if the drug class was found (not None) |
| `expected` | Truthy if expected classes list is not empty |
| `drug_class not in expected` | True if the drug's class is NOT in the expected list |
| All three connected with `and` | ALL three must be true for mismatch to be True |
| `bool(...)` | Convert the final True/False to a proper boolean |

**Examples:**

| Drug | Diagnosis | drug_class | expected | drug_class not in expected | mismatch |
|:---|:---|:---|:---|:---|:---|
| metformin | diabetes | antidiabetic | [antidiabetic] | False | **False** (correct!) |
| hydralazine | anxiety | antihypertensive | [benzodiazepine, antihistamine] | True | **True** (mismatch!) |
| aspirin | infection | None | [antibiotic] | — | **False** (unknown drug class, can't judge) |

Note: If `drug_class` is `None` (drug not in our taxonomy), `mismatch` will be `False` because the condition `drug_class` itself is falsy. The system doesn't falsely accuse a drug it doesn't know about.

---

```python
    note = ""
    if not drug_class:
        note = f"Drug class for '{drug}' not found in taxonomy."
    elif mismatch:
        note = (f"'{drug}' ({drug_class}) may not be indicated for "
                f"'{diagnosis}' (expected classes: {expected}).")
    else:
        note = f"'{drug}' appears consistent with diagnosis '{diagnosis}'."
```

Generates a **human-readable explanation** of the result. Three branches:
1. Drug class not in our dictionary → neutral note (can't judge)
2. Mismatch detected → warning message with details
3. Everything is fine → reassuring message

---

```python
    return {
        "mismatch":        mismatch,
        "drug_class":      drug_class,
        "expected_classes": expected,
        "note":            note,
    }
```

Returns all result data in a dictionary with four keys.

---

### Lines 111–123 — CLI Demo

```python
if __name__ == "__main__":
    tests = [
        ("dopamine",    "cardiac_arrest"),
        ("metformin",   "atrial_fibrillation"),
        ("warfarin",    "diabetes"),
        ("fentanyl",    "pain"),
        ("vincristine", "cancer"),
    ]
    for drug, diag in tests:
        r = validate(drug, diag)
        flag = "! MISMATCH" if r["mismatch"] else "> OK"
        print(f"{flag}  drug={drug}  diag={diag}  -> {r['note']}")
```

Tests the function with 5 example pairs. Expected output:

```
> OK         drug=dopamine     diag=cardiac_arrest  -> 'dopamine' appears consistent with diagnosis 'cardiac_arrest'.
! MISMATCH   drug=metformin    diag=atrial_fibrillation -> 'metformin' (antidiabetic) may not be indicated for 'atrial_fibrillation'...
! MISMATCH   drug=warfarin     diag=diabetes        -> 'warfarin' (anticoagulant) may not be indicated for 'diabetes'...
> OK         drug=fentanyl     diag=pain            -> 'fentanyl' appears consistent with diagnosis 'pain'.
> OK         drug=vincristine  diag=cancer          -> 'vincristine' appears consistent with diagnosis 'cancer'.
```

---

## Summary: What This File Does

```
Input:   drug = "hydralazine", diagnosis = "anxiety"
             ↓
Lookup:  drug_class for "hydralazine" → "antihypertensive"
         expected for "anxiety"       → ["benzodiazepine", "antihistamine"]
             ↓
Check:   "antihypertensive" not in ["benzodiazepine", "antihistamine"] → mismatch = True
             ↓
Output:  {
           "mismatch": True,
           "drug_class": "antihypertensive",
           "expected_classes": ["benzodiazepine", "antihistamine"],
           "note": "'hydralazine' (antihypertensive) may not be indicated for 'anxiety'..."
         }
```
