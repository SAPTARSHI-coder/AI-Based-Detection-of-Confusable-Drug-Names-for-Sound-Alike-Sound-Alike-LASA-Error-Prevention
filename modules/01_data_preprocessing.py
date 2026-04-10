"""
Module 1: Data Preprocessing
Extracts LASA drug pairs from PDFs, normalizes them,
generates negative samples, and saves the training dataset.
"""
import os
import re
import csv
import random
import pdfplumber
import pandas as pd
from pathlib import Path

ROOT_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = ROOT_DIR / "data" / "raw"
PROC_DIR   = ROOT_DIR / "data" / "processed"
DRUG_LIST  = ROOT_DIR / "data" / "drug_list.txt"

PDF_FILES  = ["2368.pdf", "confuseddrugnames(02.2015).pdf"]
NEG_RATIO  = 3         # negatives per positive

# ── helpers ───────────────────────────────────────────────────────────────────
STOP_WORDS = {
    "drug", "name", "drug name", "confused with", "confused", "generic",
    "brand", "similar", "look-alike", "sound-alike", "lasa", "example",
    "class", "medication", "the", "and", "or", "of", "for", "to", "in",
    "a", "an", "with", "type", "table", "drug class",
}

def clean(text: str) -> str:
    """Normalise a raw drug name candidate."""
    text = re.sub(r'\([^)]*\)', '', text)       # drop parenthetical dosage
    text = re.sub(r'\[[^\]]*\]', '', text)       # drop bracket content
    text = re.sub(r'\b\d+(\.\d+)?\s*(mg|mcg|g|ml|units|%)\b', '',
                  text, flags=re.IGNORECASE)
    text = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', text)
    return text.lower().strip()

def valid(name: str) -> bool:
    if len(name) < 3 or len(name) > 35:
        return False
    if not re.search(r'[a-z]', name):          # must contain a letter
        return False
    if name in STOP_WORDS:
        return False
    if re.match(r'^\d+$', name):               # purely numeric → skip
        return False
    return True

# ── extraction ────────────────────────────────────────────────────────────────
def extract_from_pdf(pdf_path: Path) -> set:
    """Extract positive LASA pairs from a PDF via tables and regex."""
    pairs = set()
    print(f"  Reading: {pdf_path.name}")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # 1. structured tables
            for table in page.extract_tables() or []:
                for row in table:
                    row = [c for c in row if c]          # drop None cells
                    if len(row) >= 2:
                        d1, d2 = clean(str(row[0])), clean(str(row[1]))
                        if valid(d1) and valid(d2) and d1 != d2:
                            pairs.add(tuple(sorted([d1, d2])))

            # 2. plain text — look for "X / Y", "X and Y", "X vs Y"
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

    return pairs

# ── negative sampling ─────────────────────────────────────────────────────────
def generate_negatives(positives: set, all_drugs: list, ratio: int = NEG_RATIO) -> set:
    """
    Random pairing strategy: pick two random drugs ensuring the pair
    is not already a known positive.
    """
    target   = len(positives) * ratio
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

# ── built-in seed pairs ───────────────────────────────────────────────────────
SEED_PAIRS = [
    ("dopamine",    "dobutamine"),
    ("celebrex",    "celexa"),
    ("alprazolam",  "lorazepam"),
    ("vincristine", "vinblastine"),
    ("hydroxyzine", "hydralazine"),
    ("clonidine",   "clonazepam"),
    ("metformin",   "metronidazole"),
    ("lamictal",    "lamisil"),
    ("zyprexa",     "zyrtec"),
    ("paxil",       "taxol"),
    ("fentanyl",    "sufentanil"),
    ("carboplatin", "cisplatin"),
    ("prednisone",  "prednisolone"),
    ("glipizide",   "glyburide"),
    ("morphine",    "hydromorphone"),
    ("amiodarone",  "amiodipine"),
    ("nimodipine",  "nifedipine"),
    ("adalimumab",  "infliximab"),
    ("warfarin",    "heparin"),
    ("epinephrine", "norepinephrine"),
]

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(PROC_DIR, exist_ok=True)

    positives = set(tuple(sorted(p)) for p in SEED_PAIRS)

    for fname in PDF_FILES:
        path = RAW_DIR / fname
        if path.exists():
            found = extract_from_pdf(path)
            print(f"    -> {len(found)} pairs extracted from {fname}")
            positives.update(found)
        else:
            print(f"  Warning: {fname} not found in {RAW_DIR}")

    print(f"\n> Total positive LASA pairs: {len(positives)}")

    # collect master drug list
    drug_set = set()
    for d1, d2 in positives:
        drug_set.update([d1, d2])

    # save master drug list
    DRUG_LIST.parent.mkdir(parents=True, exist_ok=True)
    with open(DRUG_LIST, "w", encoding="utf-8") as f:
        for d in sorted(drug_set):
            f.write(d + "\n")
    print(f"> Master drug list saved ({len(drug_set)} drugs)")

    # save positive pairs
    pairs_path = PROC_DIR / "drug_pairs.csv"
    pd.DataFrame(list(positives), columns=["drug1", "drug2"]).to_csv(
        pairs_path, index=False
    )
    print(f"> Positive pairs saved -> {pairs_path.name}")

    # generate negatives
    negatives = generate_negatives(positives, list(drug_set))
    print(f"> Negative samples generated: {len(negatives)}")

    # build training dataset
    rows = [(d1, d2, 1) for d1, d2 in positives]
    rows += [(d1, d2, 0) for d1, d2 in negatives]
    random.shuffle(rows)

    ds_path = PROC_DIR / "training_dataset.csv"
    pd.DataFrame(rows, columns=["drug1", "drug2", "label"]).to_csv(
        ds_path, index=False
    )
    print(f"> Training dataset saved -> {ds_path.name}  (total rows: {len(rows)})\n")

if __name__ == "__main__":
    main()
