# 📄 01_data_preprocessing.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It reads official PDF documents containing known dangerous drug name pairs, cleans them up, generates fake "safe" pairs as counter-examples, and saves everything as two spreadsheets that the AI will later learn from.

---

## Real-Life Analogy Before We Start

Think of this module as a **data librarian**. Before any teaching can happen, someone has to go collect and organize the study materials. This module:

1. Opens up PDF books (ISMP reports)
2. Finds and extracts all the dangerous drug name pairs listed inside
3. Cleans up messy formatting (removes dosage numbers, brackets, etc.)
4. Creates "safe" examples by randomly pairing drugs that are NOT known to be dangerous
5. Saves two organized spreadsheets for the AI to study from

---

## The Full Code, Explained Line by Line

---

### Lines 1–5 — The Docstring (Description Block)

```python
"""
Module 1: Data Preprocessing
Extracts LASA drug pairs from PDFs, normalizes them,
generates negative samples, and saves the training dataset.
"""
```

**What is this?**

This is a **docstring** — a block of text in triple quotes that describes what the file does. Python ignores it when running the code. It's purely for humans to read. Think of it like the title and summary on the cover of a book.

---

### Lines 6–12 — Importing Tools

```python
import os
import re
import csv
import random
import pdfplumber
import pandas as pd
from pathlib import Path
```

**What is "importing"?**

Imagine you're about to cook a meal. Before you start, you lay out all your kitchen tools — knife, bowl, pot, spoon. Importing in programming is the same idea. You're loading pre-built tools (called **libraries**) that someone else already wrote, so you don't have to build them yourself.

| Import | What tool it provides |
|:---|:---|
| `os` | Handles operating system tasks — like creating folders |
| `re` | Short for "regular expressions" — a powerful search tool for finding patterns in text |
| `csv` | Reads and writes spreadsheet-style `.csv` files |
| `random` | Generates random choices (used to create random drug pairs) |
| `pdfplumber` | Opens PDF files and reads the text/tables inside them |
| `pandas as pd` | A tool for organizing data into table format; `pd` is just a shorter nickname |
| `Path` | A smart way to refer to file paths — works on Windows, Mac, and Linux automatically |

---

### Lines 14–17 — Setting Up File Paths

```python
ROOT_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = ROOT_DIR / "data" / "raw"
PROC_DIR   = ROOT_DIR / "data" / "processed"
DRUG_LIST  = ROOT_DIR / "data" / "drug_list.txt"
```

**What is happening here?**

These four lines figure out where different folders and files are located on your computer. Let's break it down:

```python
ROOT_DIR = Path(__file__).resolve().parent.parent
```

- `__file__` → This is the current file itself (`01_data_preprocessing.py`)
- `.resolve()` → Get the full, absolute path (like `D:\DESKTOP\lasa_detection\modules\01_data_preprocessing.py`)
- `.parent` → Go one folder up (now you're in `modules/`)
- `.parent` again → Go one more folder up (now you're in `lasa_detection/`)

So `ROOT_DIR` = the root of the whole project.

```python
RAW_DIR  = ROOT_DIR / "data" / "raw"
```

This builds the path: `lasa_detection/data/raw/` — where the PDF files are stored.

The `/` symbol here is not division — it's the `Path` library's way of joining folder names. Very readable.

---

### Lines 19–20 — Naming the PDF Files and Ratio Setting

```python
PDF_FILES  = ["2368.pdf", "confuseddrugnames(02.2015).pdf"]
NEG_RATIO  = 3
```

- `PDF_FILES` — A list of the two ISMP PDF files this module will try to read.
- `NEG_RATIO = 3` — For every 1 real dangerous pair (positive), the system will create 3 fake safe pairs (negatives). This keeps the training data balanced.

> **Why 3 negatives for every 1 positive?** In real life, most drug name pairs are NOT dangerous. If you only trained on dangerous pairs, the AI would think everything is dangerous. You need to show it lots of "normal" examples too.

---

### Lines 23–28 — Stop Words List

```python
STOP_WORDS = {
    "drug", "name", "drug name", "confused with", "confused", "generic",
    "brand", "similar", "look-alike", "sound-alike", "lasa", "example",
    "class", "medication", "the", "and", "or", "of", "for", "to", "in",
    "a", "an", "with", "type", "table", "drug class",
}
```

**What is a stop word?**

When you extract text from a PDF table, you sometimes get cells that say things like "Drug Name" or "Class" — these are column headers, not actual drug names. Stop words is a list of such words to **ignore**. If anything extracted from the PDF matches one of these words, it gets thrown away.

It's like telling someone: *"Read this document and write down every drug name you see — but don't write down words like 'the' or 'and'."*

---

### Lines 30–37 — The `clean()` Function

```python
def clean(text: str) -> str:
    """Normalise a raw drug name candidate."""
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\b\d+(\.\d+)?\s*(mg|mcg|g|ml|units|%)\b', '',
                  text, flags=re.IGNORECASE)
    text = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text)
    return text.lower().strip()
```

**What is a function?**

A **function** is a named, reusable block of steps. Instead of writing the same 5 steps over and over, you write them once, give them a name (`clean`), and call that name whenever you need those steps.

`def clean(text: str) -> str:` means:
- `def` = define a function
- `clean` = name of the function
- `text: str` = the function receives one input: a piece of text (string)
- `-> str` = the function will return a string (cleaned text)

**Line by line inside `clean()`:**

```python
text = re.sub(r'\([^)]*\)', '', text)
```
Remove everything inside parentheses. Example: `"dopamine (HCl)"` → `"dopamine "`. The `r'\([^)]*\)'` is a pattern — read it as "match: open bracket, then anything, then close bracket". Replace all that with nothing (`''`).

```python
text = re.sub(r'\[[^\]]*\]', '', text)
```
Same idea — remove everything inside square brackets. Example: `"warfarin [brand]"` → `"warfarin "`.

```python
text = re.sub(r'\b\d+(\.\d+)?\s*(mg|mcg|g|ml|units|%)\b', '', text, flags=re.IGNORECASE)
```
Remove dosage information. Example: `"metformin 500mg"` → `"metformin "`. The pattern matches: a number, optional decimal, then a dose unit like mg or ml.

```python
text = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text)
```
Replace any character that is NOT a letter, number, space, or hyphen with a space. This removes stray punctuation like commas, slashes.

```python
return text.lower().strip()
```
- `.lower()` → Convert to all lowercase (`"Dopamine"` → `"dopamine"`)
- `.strip()` → Remove any spaces from the beginning and end

---

### Lines 39–48 — The `valid()` Function

```python
def valid(name: str) -> bool:
    if len(name) < 3 or len(name) > 35:
        return False
    if not re.search(r'[a-z]', name):
        return False
    if name in STOP_WORDS:
        return False
    if re.match(r'^\d+$', name):
        return False
    return True
```

This function acts as a **quality control gate**. It checks if a cleaned name is actually a valid drug name. It returns `True` (valid) or `False` (reject this one).

| Check | What it filters out |
|:---|:---|
| `len(name) < 3` | Names that are too short (like "IV" alone) |
| `len(name) > 35` | Names that are too long (probably a phrase, not a drug name) |
| `not re.search(r'[a-z]', name)` | Names with no letters (just numbers or symbols) |
| `name in STOP_WORDS` | Common English words, headers like "Drug Name" |
| `re.match(r'^\d+$', name)` | Purely numeric strings like "500" |

---

### Lines 51–80 — The `extract_from_pdf()` Function

```python
def extract_from_pdf(pdf_path: Path) -> set:
    pairs = set()
    print(f"  Reading: {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
```

- `set()` → A collection that automatically removes duplicates. We use a set because the same pair might appear multiple times across pages.
- `pdfplumber.open(pdf_path)` → Opens the PDF file safely (the `with` keyword ensures it's properly closed after we're done reading it).
- `for page in pdf.pages:` → Goes through the PDF one page at a time.

```python
            for table in page.extract_tables() or []:
                for row in table:
                    row = [c for c in row if c]
                    if len(row) >= 2:
                        d1, d2 = clean(str(row[0])), clean(str(row[1]))
                        if valid(d1) and valid(d2) and d1 != d2:
                            pairs.add(tuple(sorted([d1, d2])))
```

**Strategy 1 — Reading structured tables inside the PDF:**

- `page.extract_tables()` → Reads all tables on that page (like an HTML table in a PDF)
- `for row in table:` → Reads each row of the table
- `row = [c for c in row if c]` → Removes empty/None cells from the row
- `if len(row) >= 2:` → A valid pair needs at least 2 cells (drug A and drug B)
- `d1, d2 = clean(str(row[0])), clean(str(row[1]))` → Clean the first and second column
- `if valid(d1) and valid(d2) and d1 != d2:` → Both names must be valid, and they can't be the same word
- `pairs.add(tuple(sorted([d1, d2])))` → Add the pair to the set. `sorted()` ensures `(dopamine, dobutamine)` and `(dobutamine, dopamine)` are stored the same way.

```python
            text = page.extract_text() or ""
            for line in text.splitlines():
                line = line.strip()
                m = re.search(
                    r'^(.+?)\s*(?:/|vs\.?| and | or )\s*(.+)$',
                    line, re.IGNORECASE
                )
                if m:
                    d1, d2 = clean(m.group(1)), clean(m.group(2))
                    if valid(d1) and valid(d2) and d1 != d2:
                        pairs.add(tuple(sorted([d1, d2])))
```

**Strategy 2 — Reading plain text lines:**

Some ISMP PDFs don't use tables — they just write:
`"dopamine / dobutamine"` or `"vincristine vs vinblastine"` as plain text.

This block:
- Reads all text on the page
- Splits it into individual lines
- Searches each line for the pattern: `something / something` or `something vs something` or `something and something`
- If found, extracts the two parts, cleans them, validates them, and adds to the pairs set

---

### Lines 83–100 — The `generate_negatives()` Function

```python
def generate_negatives(positives: set, all_drugs: list, ratio: int = NEG_RATIO) -> set:
    target    = len(positives) * ratio
    negatives = set()
    drugs     = list(all_drugs)
    attempts  = 0

    while len(negatives) < target and attempts < target * 20:
        d1, d2 = random.sample(drugs, 2)
        pair   = tuple(sorted([d1, d2]))
        if pair not in positives and pair not in negatives:
            negatives.add(pair)
        attempts += 1

    return negatives
```

This function creates **negative samples** — randomly paired drug names that are NOT known LASA pairs.

- `target = len(positives) * ratio` → If there are 100 positive pairs, we want 300 negatives (ratio = 3)
- `while len(negatives) < target and attempts < target * 20:` → Keep trying until we've collected enough pairs (or until we've tried too many times, to prevent an infinite loop)
- `random.sample(drugs, 2)` → Pick 2 random drugs from the list
- `if pair not in positives and pair not in negatives:` → Only add this pair if it's not already a known LASA pair and not already in our negatives list
- `attempts += 1` → Count each attempt so we don't loop forever

---

### Lines 103–124 — Hardcoded Seed Pairs

```python
SEED_PAIRS = [
    ("dopamine",    "dobutamine"),
    ("celebrex",    "celexa"),
    ...
    ("epinephrine", "norepinephrine"),
]
```

These are 20 well-known dangerous LASA pairs that are **hardcoded directly into the code**. Even if the PDF files are unavailable, the system will still have these pairs to train from. Think of it as the minimum guaranteed knowledge the system will always have.

---

### Lines 127–175 — The `main()` Function

This is the master function that runs everything in sequence.

```python
def main():
    os.makedirs(PROC_DIR, exist_ok=True)
```
Create the `data/processed/` folder if it doesn't exist yet. `exist_ok=True` means: don't crash if it already exists.

```python
    positives = set(tuple(sorted(p)) for p in SEED_PAIRS)
```
Start the positives set pre-loaded with the 20 hardcoded SEED_PAIRS.

```python
    for fname in PDF_FILES:
        path = RAW_DIR / fname
        if path.exists():
            found = extract_from_pdf(path)
            positives.update(found)
        else:
            print(f"  Warning: {fname} not found in {RAW_DIR}")
```
Try to read each PDF. If found, extract pairs and add them to `positives`. If not found, print a warning but don't crash.

```python
    drug_set = set()
    for d1, d2 in positives:
        drug_set.update([d1, d2])
```
Collect every individual drug name mentioned in any pair. This becomes the **master drug list**.

```python
    with open(DRUG_LIST, "w", encoding="utf-8") as f:
        for d in sorted(drug_set):
            f.write(d + "\n")
```
Save the master drug list to `data/drug_list.txt` — one drug per line, alphabetically sorted.

```python
    rows = [(d1, d2, 1) for d1, d2 in positives]
    rows += [(d1, d2, 0) for d1, d2 in negatives]
    random.shuffle(rows)
    pd.DataFrame(rows, columns=["drug1", "drug2", "label"]).to_csv(ds_path, index=False)
```
- Build a list of rows: positive pairs get label `1`, negative pairs get label `0`
- Shuffle them randomly so the dataset is not ordered
- Save as `training_dataset.csv` using pandas

---

### Lines 177–178 — Entry Point

```python
if __name__ == "__main__":
    main()
```

This means: *"Only run `main()` if someone runs THIS file directly."* If another module imports this file, `main()` won't run automatically.

---

## Summary: What This File Produces

| Output File | What's In It |
|:---|:---|
| `data/drug_list.txt` | Every unique drug name (one per line) |
| `data/processed/drug_pairs.csv` | All confirmed LASA pairs (drug1, drug2) — label 1 |
| `data/processed/training_dataset.csv` | Balanced dataset: positive pairs (label=1) + negative pairs (label=0), shuffled |
