"""
Module 8: Decision Engine
Combines LASA probability, STT confidence, and patient context flag
into a final risk level (LOW / MEDIUM / HIGH) with a warning message.
"""
from typing import Dict, List, Optional


def decide(
    lasa_hits:       List[Dict],        # from 04_lasa_engine.score_drug()
    context_result:  Dict,              # from 07_patient_context.validate()
    stt_confidence:  Optional[float] = None,  # 0–1 or None
) -> Dict:
    """
    Combine all signals into a single risk decision.

    Parameters
    ----------
    lasa_hits      : ranked list of LASA candidates (top result used)
    context_result : patient-context validation dict
    stt_confidence : optional confidence score from STT (lower = less certain)

    Returns
    -------
    dict: {risk_level, lasa_prob, top_match, mismatch, message, details}
    """
    # unpack inputs
    top       = lasa_hits[0] if lasa_hits else None
    lasa_prob = top["lasa_prob"] if top else 0.0
    top_match = top["candidate"] if top else "N/A"
    mismatch  = context_result.get("mismatch", False)
    
    known_ismp = top.get("known_in_ismp", False) if top else False
    feat       = top.get("features", {}) if top else {}

    # Weighting adjustments
    base_score = lasa_prob
    if known_ismp:
        base_score += 0.15
    if mismatch:
        base_score += 0.10
    if stt_confidence is not None and stt_confidence < 0.6:
        base_score += 0.05

    base_score = min(1.0, base_score)

    risk = "LOW"
    if mismatch:
        if base_score > 0.75:
            risk = "HIGH"
        elif base_score > 0.45:
            risk = "MEDIUM"
    else:
        # If no mismatch, only warn Medium if it's a known dangerous ISMP pair or STT is low
        if (known_ismp or (stt_confidence and stt_confidence < 0.8)) and base_score > 0.8:
            risk = "MEDIUM"
        else:
            risk = "LOW"

    # Explainability formulation
    reasons = []
    if top:
        sim_pct = feat.get("jaro_winkler", 0) * 100
        phonetic = bool(feat.get("metaphone_match") or feat.get("soundex_match"))
        if phonetic:
            reasons.append("High phonetic similarity matches found.")
        if sim_pct > 80:
            reasons.append(f"{sim_pct:.0f}% high string similarity index.")
        if known_ismp:
            reasons.append("! Known historical LASA pair in ISMP dataset (High Risk).")
        reasons.append(f"Base model probability calculated at {lasa_prob:.0%}.")

    if mismatch:
        reasons.append(f"Context Mismatch: {context_result.get('note', '')}")

    if not reasons and not mismatch:
        reasons.append("No significant similarity or context mismatch detected.")

    if top and risk != "LOW":
        message = f"⚠ Caution: Potential LASA confusion with '{top_match}' (Similarity score: {base_score:.0%})."
    else:
        message = "✅ Safe to administer. No significant LASA risk or context mismatch detected."


    return {
        "risk_level": risk,
        "lasa_prob":  round(lasa_prob, 4),
        "top_match":  top_match,
        "mismatch":   mismatch,
        "message":    message,
        "reasons":    reasons,
        "details": {
            "top_lasa_hits":    lasa_hits[:5],
            "context_result":   context_result,
            "stt_confidence":   stt_confidence,
        },
    }


# ── CLI demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Simulated inputs for testing without running full pipeline
    mock_hits = [
        {"candidate": "dobutamine", "lasa_prob": 0.88, "risk_level": "HIGH"},
        {"candidate": "dopamine",   "lasa_prob": 0.72, "risk_level": "HIGH"},
    ]
    mock_context = {
        "mismatch": True,
        "drug_class": "antidiabetic",
        "note": "'metformin' (antidiabetic) may not be indicated for 'cardiac_arrest'.",
    }

    result = decide(mock_hits, mock_context, stt_confidence=0.5)
    print(f"Risk Level : {result['risk_level']}")
    print(f"Message    : {result['message']}")
