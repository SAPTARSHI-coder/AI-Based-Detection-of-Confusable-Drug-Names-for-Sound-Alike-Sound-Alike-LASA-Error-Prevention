# 📄 08_decision_engine.py — Full Code Explanation
### *Every single line explained in plain English, no coding knowledge assumed*

---

## What This File Does (One Sentence)

It collects all the evidence gathered by every previous module — the LASA similarity score, the ISMP flag, the patient context mismatch, and the voice confidence — and combines them into one final verdict: **LOW**, **MEDIUM**, or **HIGH** risk, with clear human-readable explanations.

---

## Real-Life Analogy

Imagine a **hospital safety committee** meeting. Several experts have each submitted their reports:

- The pharmacist: *"These two drug names look 97% similar."*
- The ISMP officer: *"Yes, this pair is on the official danger list."*
- The clinician: *"This drug doesn't match the patient's diagnosis at all."*
- The audio technician: *"The voice recording was unclear — low confidence."*

The committee chairman (the decision engine) reads all four reports, applies a weighted judgment, and delivers the final verdict to the prescribing clinician.

This module is the chairman.

---

## The Full Code, Explained Line by Line

---

### Lines 1–6 — Docstring and Imports

```python
"""
Module 8: Decision Engine
Combines LASA probability, STT confidence, and patient context flag
into a final risk level (LOW / MEDIUM / HIGH) with a warning message.
"""
from typing import Dict, List, Optional
```

Only type hints are imported — this module is entirely logic-based with no external library dependencies. It only works with the data passed to it.

---

### Lines 9–13 — The `decide()` Function Signature

```python
def decide(
    lasa_hits:       List[Dict],
    context_result:  Dict,
    stt_confidence:  Optional[float] = None,
) -> Dict:
```

The function takes three inputs (parameters):

| Parameter | Type | Comes From | What It Contains |
|:---|:---|:---|:---|
| `lasa_hits` | `List[Dict]` | Module 04 (`score_drug()`) | Ranked list of LASA match results |
| `context_result` | `Dict` | Module 07 (`validate()`) | Drug-diagnosis mismatch check result |
| `stt_confidence` | `Optional[float]` | Module 06 (Whisper output) | Voice recognition confidence (0–1), or `None` |

The `= None` on `stt_confidence` means it has a default value — if the caller doesn't provide it, the function uses `None`. This is used when the text was typed (not spoken), so there's no voice confidence to consider.

---

### Lines 28–34 — Unpacking the Inputs

```python
    top       = lasa_hits[0] if lasa_hits else None
    lasa_prob = top["lasa_prob"] if top else 0.0
    top_match = top["candidate"] if top else "N/A"
    mismatch  = context_result.get("mismatch", False)
    
    known_ismp = top.get("known_in_ismp", False) if top else False
    feat       = top.get("features", {}) if top else {}
```

This unpacks the most important pieces from the input data.

```python
top = lasa_hits[0] if lasa_hits else None
```
Get the **highest-scoring LASA match** (the most dangerous candidate). `lasa_hits` is already sorted by probability in descending order (Module 04 sorted it). So index `[0]` is the top result.

If the list is empty (no matches found), `top = None`.

```python
lasa_prob = top["lasa_prob"] if top else 0.0
```
Extract the LASA probability from the top match. If there is no top match, use `0.0`.

```python
top_match = top["candidate"] if top else "N/A"
```
Extract the drug name that is the top LASA match (e.g., `"hydroxyzine"`). If no match, use `"N/A"`.

```python
mismatch = context_result.get("mismatch", False)
```
Extract whether a drug-diagnosis mismatch was detected. `.get("mismatch", False)` — if the key doesn't exist for some reason, default to `False`.

```python
known_ismp = top.get("known_in_ismp", False) if top else False
```
Check whether this LASA pair was flagged as a known historical pair from the ISMP list. This field is added by `app.py` before calling `decide()`.

```python
feat = top.get("features", {}) if top else {}
```
Get the feature dictionary (the 9 similarity numbers) from the top match. Used later for the explanation text.

---

### Lines 36–45 — Building the Adjusted Score

```python
    base_score = lasa_prob
    if known_ismp:
        base_score += 0.15
    if mismatch:
        base_score += 0.10
    if stt_confidence is not None and stt_confidence < 0.6:
        base_score += 0.05

    base_score = min(1.0, base_score)
```

This is where the **multi-signal score** is built. The base LASA probability gets boosted by additional evidence.

**Think of it like a security alert system:**

| Signal | Boost | Reasoning |
|:---|:---|:---|
| Base LASA probability | Base (0–1) | The AI model's core prediction |
| Known ISMP pair | +0.15 | Historically documented real-world confusion — extra credence |
| Drug-diagnosis mismatch | +0.10 | The drug doesn't make clinical sense in context — extra danger |
| Low STT confidence | +0.05 | Voice recognition was uncertain — the drug name itself might be misheard |

```python
base_score = min(1.0, base_score)
```
Cap the score at 1.0. Mathematical accumulation could push it above 1.0, which doesn't make sense as a probability. `min(1.0, base_score)` ensures it never exceeds 1.

---

### Lines 47–58 — The Risk Classification Logic

```python
    risk = "LOW"
    if mismatch:
        if base_score > 0.75:
            risk = "HIGH"
        elif base_score > 0.45:
            risk = "MEDIUM"
    else:
        if (known_ismp or (stt_confidence and stt_confidence < 0.8)) and base_score > 0.8:
            risk = "MEDIUM"
        else:
            risk = "LOW"
```

**Start with `risk = "LOW"`** — the system is innocent until proven guilty.

Then apply rules:

**Branch A: Context mismatch EXISTS**

The drug doesn't match the patient's condition — this is already a clinical warning sign.

| Score | Decision | Why |
|:---|:---|:---|
| > 0.75 | **HIGH** | High LASA similarity + wrong drug = max danger |
| > 0.45 | **MEDIUM** | Moderate-to-high LASA similarity + wrong drug = serious concern |
| ≤ 0.45 | **LOW** | Mismatch exists but LASA similarity is low — may just be coincidence |

**Branch B: No context mismatch**

The drug is appropriate for the patient's diagnosis — this is reassuring. But we still want to warn about known ISMP pairs.

```python
if (known_ismp or (stt_confidence and stt_confidence < 0.8)) and base_score > 0.8:
    risk = "MEDIUM"
```

Even without a mismatch, raise MEDIUM if:
- This is a **documented ISMP historical pair** (real-world confusion has occurred before) AND the score is very high (> 0.8)
- OR the voice recognition was **uncertain** (< 80% confidence) AND the score is very high

Otherwise: **LOW** — no alarm.

**Why is HIGH never assigned without a mismatch?**

This is a deliberate clinical design decision. Without a context mismatch, even a 99% similar drug name is not necessarily dangerous — because the right drug is being prescribed for the right condition. Raising HIGH in that case would create false alarms that erode trust in the system.

---

### Lines 61–77 — Generating the Explanation (Reasons)

```python
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
```

This builds the **list of reasons** — the human-readable explanations shown to the clinician.

```python
sim_pct = feat.get("jaro_winkler", 0) * 100
```
Convert the Jaro-Winkler score (0–1) to a percentage (0–100) for human reading.

```python
phonetic = bool(feat.get("metaphone_match") or feat.get("soundex_match"))
```
Check if either phonetic similarity feature fired. `bool(...)` converts `0/1/None` to `True/False`.

```python
reasons.append("High phonetic similarity matches found.")
```
`.append()` adds an item to the end of the list.

Each `reasons.append(...)` adds one bullet point of evidence that the clinician will see.

```python
reasons.append(f"Base model probability calculated at {lasa_prob:.0%}.")
```
`{lasa_prob:.0%}` formats a decimal as a percentage with 0 decimal places. E.g., `0.974` → `"97%"`.

```python
if not reasons and not mismatch:
    reasons.append("No significant similarity or context mismatch detected.")
```
Fallback for edge cases where no specific evidence was generated — always ensure there's at least one explanation.

---

### Lines 79–82 — The Warning Message

```python
    if top and risk != "LOW":
        message = f"⚠ Caution: Potential LASA confusion with '{top_match}' (Similarity score: {base_score:.0%})."
    else:
        message = "✅ Safe to administer. No significant LASA risk or context mismatch detected."
```

This sets the **main message** — the most prominent text shown to the clinician.

- If risk is MEDIUM or HIGH → show a warning with the confusable drug and score
- If risk is LOW → show a green checkmark reassurance message

The `⚠` and `✅` are Unicode characters — they render as emoji in the browser UI.

---

### Lines 85–97 — The Return Value

```python
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
```

Returns a single dictionary with everything the web app needs to display:

| Key | What it contains |
|:---|:---|
| `risk_level` | `"LOW"`, `"MEDIUM"`, or `"HIGH"` |
| `lasa_prob` | Base probability from the AI model (4 decimal places) |
| `top_match` | Name of the most confusable drug |
| `mismatch` | True or False |
| `message` | The main human-readable verdict |
| `reasons` | List of bullet-point explanations |
| `details` | Full raw data for transparency (top 5 hits, context result, voice confidence) |

The `details` field exists for **explainability** — good clinical AI doesn't just give a verdict, it shows all the evidence so a clinician can understand and verify the reasoning.

---

### Lines 100–115 — CLI Demo

```python
if __name__ == "__main__":
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
```

Tests the engine with hand-crafted (mock) inputs — simulating what Module 04 and 07 would return.

Notice `stt_confidence=0.5` — below 0.6, so the +0.05 boost applies.

With `mismatch=True` and `base_score = 0.88 + 0.15 + 0.10 + 0.05 = 1.0` → risk = **HIGH**.

---

## Summary: The Complete Decision Flow

```
Inputs:
  lasa_hits = [{"candidate": "hydroxyzine", "lasa_prob": 0.97, "known_in_ismp": True, ...}]
  context_result = {"mismatch": True, "note": "..."}
  stt_confidence = 0.55

Step 1 — Build adjusted score:
  base_score = 0.97
  + 0.15 (known ISMP pair)    = 1.12 → capped to 1.0
  + 0.10 (mismatch)           = (capped)
  + 0.05 (low STT confidence) = (capped)
  final: base_score = 1.0

Step 2 — Classify risk:
  mismatch = True, base_score = 1.0 > 0.75 → risk = HIGH

Step 3 — Generate reasons:
  "High phonetic similarity matches found."
  "99% high string similarity index."
  "Known historical LASA pair in ISMP dataset (High Risk)."
  "Base model probability calculated at 97%."
  "Context Mismatch: 'hydralazine' (antihypertensive) may not be indicated for 'anxiety'."

Step 4 — Set message:
  "⚠ Caution: Potential LASA confusion with 'hydroxyzine' (Similarity score: 100%)."

Output:
  risk_level = "HIGH"
  top_match  = "hydroxyzine"
  message    = "⚠ Caution: ..."
  reasons    = [5 bullet points]
```
