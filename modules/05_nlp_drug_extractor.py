"""
Module 5: NLP Drug Extractor
Extracts drug names, dosage, and route from free-text clinical sentences.
Phase 1: regex + dictionary lookup (interpretable, no heavy model needed).
"""
import re
from pathlib import Path
from typing import Optional, Dict

ROOT_DIR  = Path(__file__).resolve().parent.parent
DRUG_LIST = ROOT_DIR / "data" / "drug_list.txt"

DOSAGE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units?|u|%)',
    re.IGNORECASE
)
ROUTE_KEYWORDS = {
    "oral", "po", "iv", "intravenous", "im", "intramuscular",
    "subcutaneous", "sc", "topical", "inhaled", "sublingual",
    "rectal", "nasal", "ophthalmic", "transdermal",
}

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

def extract(sentence: str) -> Dict:
    """
    Extract drug name, dosage, and route from a clinical sentence.

    Returns
    -------
    dict: {drug, dosage, route, raw}
    """
    drugs     = _load_drugs()
    sentence  = sentence.strip()
    lower     = sentence.lower()

    # dosage
    dosage_match = DOSAGE_PATTERN.search(sentence)
    dosage = dosage_match.group(0) if dosage_match else None

    # route
    route = None
    for kw in ROUTE_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', lower):
            route = kw
            break

    # drug — longest match from dictionary
    found_drug = None
    best_len   = 0
    for drug in drugs:
        if re.search(r'\b' + re.escape(drug) + r'\b', lower):
            if len(drug) > best_len:
                found_drug, best_len = drug, len(drug)

    return {"drug": found_drug, "dosage": dosage, "route": route, "raw": sentence}


# ── CLI demo ───────────────────────────────────────────────────────────────────
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
