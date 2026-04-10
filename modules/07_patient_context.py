"""
Module 7: Patient Context Validator
Flags potential drug-diagnosis mismatches using a simple
diagnosis → expected drug class mapping.
"""
from typing import Dict, Optional, List

# ── drug class taxonomy ────────────────────────────────────────────────────────
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
    # pain / opioid
    "morphine":      "opioid",
    "fentanyl":      "opioid",
    "hydromorphone": "opioid",
    "sufentanil":    "opioid",
    # antibiotics / antimicrobial
    "metronidazole": "antibiotic",
    "vancomycin":    "antibiotic",
    # psychiatry / neuro
    "alprazolam":    "benzodiazepine",
    "lorazepam":     "benzodiazepine",
    "clonazepam":    "benzodiazepine",
    "clonidine":     "antihypertensive",
    "hydroxyzine":   "antihistamine",
    "hydralazine":   "antihypertensive",
    # oncology
    "vincristine":   "vinca_alkaloid",
    "vinblastine":   "vinca_alkaloid",
    "carboplatin":   "platinum_agent",
    "cisplatin":     "platinum_agent",
    # misc
    "prednisone":    "corticosteroid",
    "prednisolone":  "corticosteroid",
    # heart failure
    "digoxin":       "inotropic",
    "milrinone":     "inotropic",
    "furosemide":    "diuretic",
    "lasix":         "diuretic",
}

# ── diagnosis → expected drug classes ─────────────────────────────────────────
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

# ── public API ─────────────────────────────────────────────────────────────────
def validate(drug: str, diagnosis: Optional[str]) -> Dict:
    """
    Check if 'drug' is an expected treatment for 'diagnosis'.

    Returns
    -------
    dict: {mismatch, drug_class, expected_classes, note}
    """
    drug = (drug or "").lower().strip()
    drug_class = DRUG_CLASS_MAP.get(drug)

    if not diagnosis:
        return {"mismatch": False, "drug_class": drug_class,
                "expected_classes": [], "note": "No diagnosis provided."}

    diagnosis = diagnosis.lower().replace(" ", "_")
    expected  = DIAGNOSIS_CLASS_MAP.get(diagnosis, [])

    mismatch = bool(drug_class and expected and drug_class not in expected)

    note = ""
    if not drug_class:
        note = f"Drug class for '{drug}' not found in taxonomy."
    elif mismatch:
        note = (f"'{drug}' ({drug_class}) may not be indicated for "
                f"'{diagnosis}' (expected classes: {expected}).")
    else:
        note = f"'{drug}' appears consistent with diagnosis '{diagnosis}'."

    return {
        "mismatch":        mismatch,
        "drug_class":      drug_class,
        "expected_classes": expected,
        "note":            note,
    }


# ── CLI demo ───────────────────────────────────────────────────────────────────
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
        flag = "⚠ MISMATCH" if r["mismatch"] else "✓ OK"
        print(f"{flag}  drug={drug}  diag={diag}  → {r['note']}")
