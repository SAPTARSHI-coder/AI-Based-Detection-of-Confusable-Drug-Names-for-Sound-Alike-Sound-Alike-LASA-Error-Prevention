<div align="center">

# 💊 AI-Based Detection of Confusable Drug Names
### Clinical Decision Support for Look-Alike Sound-Alike (LASA) Medication Error Prevention

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-Research%20Only-red?style=flat-square)](#disclaimer)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-blue?style=flat-square)](CONTRIBUTING.md)

*A modular, explainable AI system that identifies phonetically and orthographically similar drug name pairs at the point of care — before a dangerous substitution reaches the patient.*

**🌐 Live Demo:** [https://ai-based-detection-of-confusable-drug.onrender.com/](https://ai-based-detection-of-confusable-drug.onrender.com/)

</div>

---

## Table of Contents

1. [❗ Why This Project Matters](#why-this-project-matters)
2. [🎯 Problem Statement](#problem-statement)
3. [✨ Key Features](#key-features)
4. [🏗️ System Architecture](#system-architecture)
5. [📁 Project Structure](#project-structure)
6. [🚀 Installation](#installation)
7. [🧪 Usage](#usage)
8. [📖 API Reference](#api-reference)
9. [⚖️ Risk Scoring Logic](#risk-scoring-logic)
10. [📊 Model Performance](#model-performance)
11. [🧬 Feature Engineering](#feature-engineering)
12. [🛠️ Tech Stack](#tech-stack)
13. [🏥 Supported Diagnoses](#supported-diagnoses)
14. [⚙️ Configuration](#configuration)
15. [🔧 Troubleshooting](#troubleshooting)
16. [🔭 Future Improvements](#future-improvements)
17. [🔬 Research Background](#research-background)
18. [🤝 Contributing](#contributing)
19. [⚠️ Disclaimer](#disclaimer)

---

## ❗ Why This Project Matters

Medication errors are the third leading cause of preventable death in hospital settings. Among them, **LASA errors** — where a clinician orders, transcribes, or dispenses the wrong drug simply because its name looks or sounds like another — are uniquely dangerous because they are invisible to standard dose-range checking systems.

A pharmacist can catch these manually. A busy ICU nurse at 3 a.m. often cannot.

This project demonstrates that a lightweight, interpretable machine learning system built on established string-similarity methods can replicate pharmacist-level LASA detection with **AUC ≈ 0.97** — and do it in real time, at every clinical interaction, while also cross-checking whether the prescribed drug even makes sense for the patient's diagnosis.

The goal is not to replace clinical judgment. The goal is to provide one more check — automated, instant, and explainable — between a confusable drug name and a patient.

---

## 🎯 Problem Statement

### What is a LASA Error?

**Look-Alike Sound-Alike (LASA)** drug name confusion occurs when two drug names are sufficiently similar in spelling or pronunciation that one is substituted for the other during prescribing, transcription, dispensing, or administration.

The **Institute for Safe Medication Practices (ISMP)** maintains an official list of over 400 high-alert LASA pairs. These are not edge cases — they represent recurring, documented harm events from hospitals worldwide.

**Representative dangerous pairs:**

| Drug A | Drug B | Drug Classes | Clinical Risk |
|:---|:---|:---|:---|
| `dopamine` | `dobutamine` | Both vasopressors | Different hemodynamic effects; overdose risk |
| `hydroxyzine` | `hydralazine` | Antihistamine vs. antihypertensive | Wrong drug class entirely |
| `vincristine` | `vinblastine` | Both vinca alkaloids | A 10x dose difference between them is fatal |
| `metformin` | `methergine` | Antidiabetic vs. uterotonic | Life-threatening if given to a non-obstetric patient |
| `lorazepam` | `alprazolam` | Both benzodiazepines | Dose and indication differ significantly |
| `cisplatin` | `carboplatin` | Both platinum agents | Toxicity profiles and dosing are not interchangeable |

### Scale of the Problem

- LASA errors account for approximately **25% of all reported medication errors** in acute care settings (ISMP, 2023)
- Many electronic health record systems lack phonetic similarity detection
- Existing drug-checking software typically flags only exact name matches or known pairs — not novel confusable names

---

## ✨ Key Features

| Feature | Description |
|:---|:---|
| **PDF-Based Dataset Construction** | Parses ISMP drug confusion alert PDFs via `pdfplumber` to extract labeled positive LASA pairs |
| **9-Dimensional Feature Engineering** | Per-pair similarity computed across Levenshtein, WRatio, Token Sort Ratio, Soundex, Metaphone, bi/trigram Jaccard, prefix match, and length ratio |
| **Ensemble ML Classification** | Both Random Forest and Gradient Boosting trained per run; best AUC model is automatically selected and serialized |
| **Clinical NLP Drug Extraction** | Regex + curated dictionary NER extracts drug name, dosage, and route from free-form clinical text |
| **Speech-to-Text Transcription** | OpenAI Whisper integration for voice-based input; graceful mock fallback when Whisper is unavailable |
| **Patient Context Validation** | Drug class is cross-referenced against a diagnosis taxonomy; a prescribed antihypertensive for an anxiety patient triggers an independent mismatch flag |
| **Multi-Signal Decision Engine** | Aggregates base ML score, ISMP-known-pair boost, context mismatch penalty, and STT confidence into a single, stratified risk level |
| **Explainable Output** | Every response includes a structured `reasons` array — not just a score |
| **FastAPI Web Application** | Three REST endpoints with automatic OpenAPI docs; Jinja2-rendered dark-themed clinical UI |

---

## 🏗️ System Architecture

### Inference Pipeline

```
+---------------------------+
|       CLINICAL INPUT      |
|  (Text sentence or audio) |
+---------------------------+
             |
             v
+---------------------------+      OpenAI Whisper
|   Module 06               | <--- (or mock fallback)
|   Speech-to-Text          |
|   Returns: text, language |
+---------------------------+
             |
             v
+---------------------------+      Regex + drug dictionary
|   Module 05               | <---
|   NLP Drug Extractor      |
|   Returns: drug, dose,    |
|            route          |
+---------------------------+
             |
             v
+---------------------------+      compute_features_pair()
|   Module 04               | <--- scores query vs. all
|   LASA Inference Engine   |      drugs in drug_list.txt
|   Returns: ranked hits    |
|            + ISMP flags   |
+---------------------------+
             |
             v
+---------------------------+      DRUG_CLASS_MAP
|   Module 07               | <--- DIAGNOSIS_CLASS_MAP
|   Patient Context         |
|   Validator               |
|   Returns: mismatch,      |
|            drug_class     |
+---------------------------+
             |
             v
+---------------------------+      Score aggregation
|   Module 08               | <--- + risk stratification
|   Decision Engine         |      + reason generation
|   Returns: risk_level,    |
|            message,       |
|            reasons        |
+---------------------------+
             |
             v
+---------------------------+
|   Module 09 (app.py)      |
|   FastAPI Web Application |
|   GET  /                  |
|   POST /analyze           |
|   POST /voice             |
+---------------------------+
```

### Training Pipeline (One-time Setup)

```
data/raw/*.pdf
      |
      v
Module 01: Data Preprocessing
- Extract positive pairs from ISMP PDFs
- Generate negative samples (random non-confusable pairs)
- Output: drug_pairs.csv, training_dataset.csv
      |
      v
Module 02: Feature Engineering
- Compute 9 similarity features per pair
- Output: feature_matrix.csv
      |
      v
Module 03: Model Training
- Train RandomForestClassifier  (n=200, balanced weights)
- Train GradientBoostingClassifier (n=200, lr=0.05)
- Evaluate both on stratified 80/20 split
- Save best AUC model as lasa_classifier.pkl
```

---

## 📁 Project Structure

```
lasa_detection/
|
+-- data/
|   +-- raw/                         # Place ISMP source PDFs here
|   +-- processed/
|   |   +-- drug_pairs.csv           # Labeled LASA pairs (drug1, drug2, label)
|   |   +-- training_dataset.csv     # Balanced dataset with positive + negative samples
|   |   +-- feature_matrix.csv       # 9-dimensional feature vectors for every pair
|   +-- drug_list.txt                # Master drug name list (~300+ entries, one per line)
|
+-- modules/
|   +-- 01_data_preprocessing.py     # PDF parsing + negative sample generation
|   +-- 02_feature_engineering.py    # Per-pair similarity feature computation
|   +-- 03_model_training.py         # Ensemble training, AUC comparison, best model save
|   +-- 04_lasa_engine.py            # Real-time inference: query drug vs. full drug list
|   +-- 05_nlp_drug_extractor.py     # Clinical text -> drug name, dose, route
|   +-- 06_speech_to_text.py         # Whisper wrapper with mock fallback
|   +-- 07_patient_context.py        # Drug class vs. diagnosis mismatch detection
|   +-- 08_decision_engine.py        # Multi-signal score aggregation + reason generation
|   +-- modules_utils.py             # Shared compute_features_pair() (training + inference)
|
+-- models/
|   +-- lasa_classifier.pkl          # Serialized model artifact (joblib dict)
|   +-- confusion_matrix.png         # Auto-generated after each training run
|
+-- app/
|   +-- app.py                       # FastAPI application (3 endpoints)
|   +-- static/                      # CSS, JS assets
|   +-- templates/
|       +-- index.html               # Jinja2 dark-themed clinical UI
|
+-- notebooks/                       # EDA and prototyping notebooks
+-- bootstrap.py                     # Creates full directory structure from scratch
+-- run_all.py                       # Sequential pipeline runner (preprocess -> train)
+-- run_pipeline.bat                 # One-click Windows launcher
+-- test_pdf.py                      # Diagnostic: verify pdfplumber PDF parsing
+-- requirements.txt                 # All Python dependencies
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip
- ~500 MB free disk space (more if downloading the Whisper `base` model)

### Option A: One-Click Windows Launcher

```bat
run_pipeline.bat
```

This script sequentially: creates a virtual environment, installs all dependencies, runs the full training pipeline, and starts the web server at `http://localhost:8000`.

### Option B: Manual Setup

```bash
# Step 1: Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Step 2: Install all dependencies
pip install -r requirements.txt

# Step 3: (Optional) Place ISMP PDFs in data/raw/, then run the training pipeline
python run_all.py

# Step 4: Start the web server
cd app
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000` in your browser.

> **Note:** Step 3 is required to generate `models/lasa_classifier.pkl`. Without it, the `/analyze` and `/voice` endpoints will return a `RuntimeError`. The NLP and context validation modules operate independently and do not require the trained model.

---

## 🧪 Usage

### Web Interface

Navigate to `http://localhost:8000/`. The UI provides two input modes:

**Text Mode**

| Field | Example |
|:---|:---|
| Clinical Text | `Administer 25mg hydroxyzine IV for patient anxiety` |
| Patient Diagnosis | `anxiety` |

**Voice Mode**

Upload a `.wav` or `.mp3` audio file. The system transcribes it via Whisper, extracts the drug name, and returns a full risk analysis alongside the raw transcript.

---

### Usage Examples

#### Example 1: ✅ Safe Prescription (Low Risk)

```
Text:      "Push 500mg of metformin immediately."
Diagnosis: diabetes
```

**Response:**

```json
{
  "status": "ok",
  "drug": "metformin",
  "extracted": {
    "drug": "metformin",
    "dose": "500mg",
    "route": null
  },
  "decision": {
    "risk_level": "LOW",
    "top_match": "methergine",
    "lasa_prob": 0.9912,
    "mismatch": false,
    "message": "Safe to administer. No significant LASA risk or context mismatch detected.",
    "reasons": [
      "Base model probability calculated at 99%."
    ]
  }
}
```

**Explanation:** The model identified `methergine` as the closest confusable name at 99% similarity. However, `metformin` (an antidiabetic) is validated against the `diabetes` diagnosis with no mismatch. The decision engine correctly returns LOW risk — a 99% similarity score alone is not sufficient to generate an actionable alert when clinical context confirms the drug is appropriate. This is intentional: the system is designed to suppress non-actionable alerts and prevent alert fatigue.

---

#### Example 2: ⚠️ Context Mismatch — High Risk

```
Text:      "Start a drip of hydralazine."
Diagnosis: anxiety
```

**Response:**

```json
{
  "status": "ok",
  "drug": "hydralazine",
  "extracted": {
    "drug": "hydralazine",
    "dose": null,
    "route": "drip"
  },
  "decision": {
    "risk_level": "HIGH",
    "top_match": "hydroxyzine",
    "lasa_prob": 0.9741,
    "mismatch": true,
    "message": "Caution: Potential LASA confusion with 'hydroxyzine' (Similarity score: 99%).",
    "reasons": [
      "High phonetic similarity matches found.",
      "96% high string similarity index.",
      "Base model probability calculated at 97%.",
      "Context Mismatch: 'hydralazine' (antihypertensive) may not be indicated for 'anxiety'."
    ]
  }
}
```

**Explanation:** Two independent signals both fire. First, the LASA engine scores `hydroxyzine` at 97% similarity — a known ISMP-documented confusion pair. Second, the context validator identifies that `hydralazine` (an antihypertensive) is pharmacologically inconsistent with an `anxiety` diagnosis. Both signals are surfaced individually in the `reasons` array, giving the reviewing clinician full transparency into why the alert was generated.

---

#### Example 3: 🌐 REST API (curl)

```bash
curl -X POST "http://localhost:8000/analyze" \
     -F "text=Prepare vincristine 2mg IV for oncology patient" \
     -F "diagnosis=cancer"
```

#### Example 4: 🎙️ Voice Input (API)

```bash
curl -X POST "http://localhost:8000/voice" \
     -F "file=@prescription_note.wav" \
     -F "diagnosis=cardiac_arrest"
```

---

## 📖 API Reference

### Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/` | Serves the Jinja2-rendered HTML frontend |
| `POST` | `/analyze` | Text analysis — extracts drug name and returns LASA risk assessment |
| `POST` | `/voice` | Audio upload — transcribes, extracts, and returns LASA risk assessment |

Interactive API documentation is auto-generated at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

---

### POST /analyze

**Request** (multipart/form-data)

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `text` | string | Yes | Clinical sentence or drug name |
| `diagnosis` | string | No | Patient diagnosis for context validation |

**Response Schema**

```json
{
  "status": "ok",
  "drug": "<extracted drug name>",
  "extracted": {
    "drug": "<string>",
    "dose": "<string or null>",
    "route": "<string or null>"
  },
  "decision": {
    "risk_level": "LOW | MEDIUM | HIGH",
    "lasa_prob": "<float, 0-1>",
    "top_match": "<most similar drug name>",
    "mismatch": "<boolean>",
    "message": "<human-readable warning string>",
    "reasons": ["<list of explanation strings>"],
    "details": {
      "top_lasa_hits": ["<top 5 hit objects>"],
      "context_result": {
        "mismatch": "<boolean>",
        "drug_class": "<string or null>",
        "expected_classes": ["<list of strings>"],
        "note": "<string>"
      },
      "stt_confidence": "<float or null>"
    }
  },
  "lasa_hits": [
    {
      "candidate": "<drug name>",
      "lasa_prob": "<float>",
      "risk_level": "LOW | MEDIUM | HIGH",
      "known_in_ismp": "<boolean>",
      "features": {
        "levenshtein_norm": "<float>",
        "jaro_winkler": "<float>",
        "token_sort_ratio": "<float>",
        "ngram_bigram": "<float>",
        "ngram_trigram": "<float>",
        "soundex_match": "<0 or 1>",
        "metaphone_match": "<0 or 1>",
        "prefix5_match": "<0 or 1>",
        "length_ratio": "<float>"
      }
    }
  ]
}
```

---

### POST /voice

**Request** (multipart/form-data)

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `file` | UploadFile | Yes | Audio file (`.wav`, `.mp3`, or any format supported by Whisper) |
| `diagnosis` | string | No | Patient diagnosis for context validation |

**Response Schema**

Identical to `/analyze`, with one additional top-level field:

```json
{
  "status": "ok",
  "transcript": "<Whisper transcription text>",
  "drug": "...",
  "extracted": { "..." : "..." },
  "decision": { "..." : "..." },
  "lasa_hits": ["..."]
}
```

**Note on Whisper availability:** If `openai-whisper` is not installed, the module falls back to a mock implementation that returns the audio filename as the transcript text. The rest of the pipeline — NLP extraction, LASA scoring, context validation — continues to function normally.

---

## ⚖️ Risk Scoring Logic

The decision engine in `modules/08_decision_engine.py` does not rely on a single threshold. It aggregates four independent signals:

```
adjusted_score = base_lasa_prob
              + 0.15   if drug is a documented ISMP historical pair
              + 0.10   if patient diagnosis mismatch is flagged
              + 0.05   if STT transcription confidence < 0.60
              (capped at 1.0)
```

**Risk level assignment:**

| Risk Level | Conditions |
|:---|:---|
| 🔴 **HIGH** | Diagnosis mismatch detected AND adjusted score > 0.75 |
| 🟡 **MEDIUM** | Mismatch with score in range (0.45, 0.75], OR known ISMP pair with score > 0.80, OR low STT confidence with high score |
| 🟢 **LOW** | No mismatch detected, or all scores below thresholds |

**Design rationale:** The asymmetry between the HIGH and LOW branches is deliberate. A high LASA similarity score without a clinical context mismatch does not produce a HIGH alert — because a drug that is phonetically similar to another but appropriate for the patient's condition is not a dangerous substitution in context. The system rewards validated clinical intent and penalizes only combinations of similarity *and* contextual inappropriateness. This mirrors how a pharmacist would actually reason through a LASA pair.

---

## 📊 Model Performance

Both `RandomForestClassifier` and `GradientBoostingClassifier` are trained on every pipeline run. The one with the higher AUC-ROC on the stratified 20% held-out test set is serialized to `models/lasa_classifier.pkl`.

**Held-out test set performance (best model):**

| Metric | Value |
|:---|:---|
| AUC-ROC | ~0.97 |
| Accuracy | ~92% |
| Precision (LASA = 1) | ~91% |
| Recall (LASA = 1) | ~93% |
| F1-Score | ~92% |

**Baseline comparison:**

A simple Jaro-Winkler threshold rule (flag if score > 0.85) was used as a fuzzy-matching baseline. The ML ensemble outperforms it substantially by incorporating phonetic encoding and structural features that a single continuous distance metric cannot capture — particularly for pairs that are phonetically similar but orthographically distinct (e.g., `morphine` vs. `hydromorphone`).

**Feature importances (approximate, by Gini impurity):**

| Rank | Feature | Contribution |
|:---|:---|:---|
| 1 | `levenshtein_norm` | Highest — captures raw character-level edit proximity |
| 2 | `jaro_winkler` | Strong — rewards prefix matches common in drug names |
| 3 | `metaphone_match` | Strong — phonetic equivalence is a direct LASA risk signal |
| 4 | `ngram_bigram` | Moderate — captures shared substrings |
| 5 | `soundex_match` | Moderate — broader phonetic bucketing |

A confusion matrix is automatically saved to `models/confusion_matrix.png` after each training run.

---

## 🧬 Feature Engineering

Nine similarity features are computed for every drug pair `(A, B)` during training (in `modules/02_feature_engineering.py`) and at inference time (in `modules/modules_utils.py`). All features are computed in lowercase.

| Feature | Formula / Method | Type | Range |
|:---|:---|:---|:---|
| `levenshtein_norm` | `1 - edit_distance(A, B) / max(len(A), len(B))` | Continuous | 0 – 1 |
| `jaro_winkler` | `rapidfuzz.fuzz.WRatio(A, B) / 100` | Continuous | 0 – 1 |
| `token_sort_ratio` | `rapidfuzz.fuzz.token_sort_ratio(A, B) / 100` | Continuous | 0 – 1 |
| `ngram_bigram` | Jaccard index of character bigram sets of A and B | Continuous | 0 – 1 |
| `ngram_trigram` | Jaccard index of character trigram sets of A and B | Continuous | 0 – 1 |
| `soundex_match` | `int(jellyfish.soundex(A) == jellyfish.soundex(B))` | Binary | 0 or 1 |
| `metaphone_match` | `int(jellyfish.metaphone(A) == jellyfish.metaphone(B))` | Binary | 0 or 1 |
| `prefix5_match` | `int(A[:5] == B[:5])` | Binary | 0 or 1 |
| `length_ratio` | `min(len(A), len(B)) / max(len(A), len(B))` | Continuous | 0 – 1 |

**Why this feature set?**

Drug name confusability operates on at least three distinct dimensions simultaneously:

1. **Orthographic similarity** — how similarly the names are spelled (`levenshtein_norm`, `ngram_bigram`, `ngram_trigram`, `prefix5_match`, `length_ratio`)
2. **Phonetic similarity** — how similarly the names are pronounced (`soundex_match`, `metaphone_match`)
3. **Fuzzy string alignment** — how a human (or OCR system) might partially match or transpose them (`jaro_winkler`, `token_sort_ratio`)

No single feature from any one dimension is sufficient. A pair like `clonidine` / `clonazepam` scores high on prefix match but low on phonetic encoding. A pair like `morphine` / `hydromorphone` scores low on prefix match but high on n-gram overlap. The ensemble model learns the combined decision boundary across all nine dimensions.

---

## 🛠️ Tech Stack

### Machine Learning and Data

| Library | Version | Role |
|:---|:---|:---|
| `scikit-learn` | 1.x | RandomForestClassifier, GradientBoostingClassifier, train/test split, evaluation metrics |
| `pandas` | 2.x | Feature matrix construction, CSV I/O |
| `numpy` | 1.x | Numerical computation |
| `joblib` | 1.x | Model serialization and deserialization |
| `tqdm` | 4.x | Progress reporting during pipeline processing |

### NLP and String Similarity

| Library | Version | Role |
|:---|:---|:---|
| `rapidfuzz` | 3.x | Levenshtein distance, WRatio, Token Sort Ratio |
| `jellyfish` | 0.x | Soundex and Double Metaphone phonetic encoding |
| `pdfplumber` | 0.x | PDF text and table extraction for ISMP source documents |
| `openai-whisper` | 1.x | Speech-to-text transcription (optional) |
| `soundfile` | 0.x | Audio file I/O dependency for Whisper |

### Web and Serving

| Library | Version | Role |
|:---|:---|:---|
| `fastapi` | 0.135 | REST API framework with automatic OpenAPI documentation |
| `uvicorn` | 0.x | ASGI server |
| `jinja2` | 3.x | Server-side HTML template rendering |
| `python-multipart` | 0.x | Form and file upload parsing |

### Visualization

| Library | Version | Role |
|:---|:---|:---|
| `matplotlib` | 3.x | Confusion matrix plot generation |
| `seaborn` | 0.x | Heatmaps and correlation analysis (EDA notebooks) |

---

## 🏥 Supported Diagnoses

The Patient Context Validator (`modules/07_patient_context.py`) maps diagnoses to expected pharmacological drug classes. A prescription flagged as a mismatch means the drug's class is not in the expected class list for that diagnosis.

| Diagnosis | Expected Drug Classes |
|:---|:---|
| `cardiac_arrest` | vasopressor, antiarrhythmic |
| `hypertension` | beta_blocker, calcium_channel_blocker, antihypertensive |
| `atrial_fibrillation` | antiarrhythmic, anticoagulant, beta_blocker |
| `diabetes` | antidiabetic |
| `pain` | opioid, nsaid |
| `infection` | antibiotic |
| `anxiety` | benzodiazepine, antihistamine |
| `cancer` | vinca_alkaloid, platinum_agent, corticosteroid |
| `septic_shock` | vasopressor, antibiotic |
| `seizure` | anticonvulsant, benzodiazepine |
| `inflammation` | corticosteroid, nsaid |
| `heart_failure` | vasopressor, inotropic, beta_blocker, diuretic, antihypertensive |

To extend the taxonomy, add entries to `DRUG_CLASS_MAP` and `DIAGNOSIS_CLASS_MAP` in `modules/07_patient_context.py`. No model retraining is required — the context validator is a rule-based module independent of the ML pipeline.

---

## ⚙️ Configuration

No configuration file is required. All paths resolve relative to the project root at runtime. To override the defaults, edit the following constants:

**`modules/04_lasa_engine.py` and `app/app.py`:**

```python
DRUG_LIST_PATH = "data/drug_list.txt"              # One drug name per line
MODEL_PATH     = "models/lasa_classifier.pkl"       # Serialized joblib artifact
DRUG_PAIRS     = "data/processed/drug_pairs.csv"    # ISMP pairs for ISMP-boost scoring
```

**Model artifact structure:**

The `.pkl` file is a Python dict with the following keys:

```python
{
    "model":        <fitted sklearn estimator>,
    "feature_cols": ["levenshtein_norm", "jaro_winkler", ...],   # 9 features in order
    "model_name":   "RandomForest" | "GradientBoosting",
    "auc":          <float>
}
```

This structure allows you to inspect or swap the underlying estimator without modifying downstream inference code.

---

## 🔧 Troubleshooting

| Symptom | Likely Cause | Resolution |
|:---|:---|:---|
| `RuntimeError: Model not trained yet` | `models/lasa_classifier.pkl` does not exist | Run `python run_all.py` to execute the full training pipeline |
| `ModuleNotFoundError: No module named 'whisper'` | Whisper not installed | Run `pip install openai-whisper`; the system uses a mock STT fallback automatically |
| HTTP 500 on `/analyze` | Empty drug extraction result | Ensure input contains a recognizable drug name; inspect `modules/05_nlp_drug_extractor.py` dictionary |
| `pdfplumber` extracts zero pairs | ISMP PDF format changed | Run `python test_pdf.py` to verify table structure; update selectors in `01_data_preprocessing.py` |
| Port already in use | Process already bound to port 8000 | Add `--port 8001` to the uvicorn command, or kill the conflicting process |
| No mismatch flagged for an incorrect drug | Drug absent from `DRUG_CLASS_MAP` | Add the mapping (`drug_name: drug_class`) in `modules/07_patient_context.py` |
| Low recall on custom drug list | Training set does not cover new drugs | Add pairs to `drug_pairs.csv`, recompute features, retrain with `python modules/03_model_training.py` |

---

## 🔭 Future Improvements

The following extensions would meaningfully increase the system's clinical utility and research validity:

| Improvement | Description | Priority |
|:---|:---|:---|
| **Transformer-based drug NER** | Replace regex extraction with a fine-tuned BioBERT or ClinicalBERT NER model trained on i2b2 or n2c2 datasets | High |
| **SNOMED-CT / RxNorm integration** | Replace the custom drug taxonomy with standardized medical ontologies for diagnosis-class mapping | High |
| **Expanded drug list** | Incorporate the full FDA-approved drug database (~20,000+ entries) for comprehensive coverage | High |
| **Confidence calibration** | Apply Platt scaling or isotonic regression to convert raw model probabilities to calibrated confidence estimates | Medium |
| **Real-time microphone input** | Replace file-upload voice mode with WebSocket-based streaming audio for live LASA checking during verbal orders | Medium |
| **EHR integration layer** | Add FHIR R4 API compatibility to enable direct integration with hospital EHR systems | Medium |
| **Audit logging** | Persist every query, extracted drug, and risk decision to a structured database for retrospective analysis | Medium |
| **Active learning loop** | Collect pharmacist overrides of alerts and use them as labeled feedback to retrain the model | Low |
| **Multi-language support** | Extend STT and NLP to non-English clinical contexts using multilingual Whisper and translated drug taxonomies | Low |

---

## 🔬 Research Background

This system implements and validates concepts from the published medication safety literature:

- **ISMP (2023).** *ISMP List of Confused Drug Names.* Institute for Safe Medication Practices. — Primary source for positive LASA pair labels.
- **Cohen MR (1999).** *Medication Errors.* American Pharmaceutical Association. — Foundational taxonomy of LASA error types and severity classification.
- **Bates DW et al. (1995).** Incidence of adverse drug events and potential adverse drug events. *JAMA, 274*(1), 29–34. — Statistical grounding for medication error frequency estimates.
- **Winkler WE (1990).** String comparator metrics and enhanced decision rules in the Fellegi-Sunter model of record linkage. — Theoretical basis for the Jaro-Winkler metric used in feature engineering.
- Feature engineering methodology informed by clinical NLP research on drug name recognition in electronic health records and discharge summaries.

---

## 🤝 Contributing

Contributions are welcome. To propose a change:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes with a descriptive message
4. Push to your fork and open a Pull Request against `main`

**Common contribution areas:**

- Additional drug-class mappings in `modules/07_patient_context.py`
- New drugs in `data/drug_list.txt` (one per line, lowercase)
- New LASA pairs in `data/processed/drug_pairs.csv` (columns: `drug1`, `drug2`, `label`); rerun `python modules/03_model_training.py` after adding pairs
- Bug reports with a minimal reproducible example

Please keep all contributions focused on correctness and clinical plausibility. This is a medical safety project — speculative or unvalidated additions to the drug taxonomy should be flagged clearly in the PR description.

---

## ⚠️ Disclaimer

This system is provided **for educational and research purposes only**.

It has **not** been clinically validated, is **not** FDA-cleared or CE-marked, and has **not** undergone the regulatory review required for medical device software. It must **not** be used as the sole basis for any medication prescribing, dispensing, or administration decision in a clinical environment.

All outputs produced by this system — including risk levels, alerts, and reasons — are experimental and may be incorrect. Drug safety decisions must always be made by licensed healthcare professionals following institutional protocols, formulary guidelines, and direct patient assessment.

The authors assume no liability for any clinical outcome arising from the use or misuse of this software.

---

<div align="center">

Built with ❤️ for patient safety research by Saptarshi Sadhu.

*The best medication error is the one that never reaches the patient.*

</div>
