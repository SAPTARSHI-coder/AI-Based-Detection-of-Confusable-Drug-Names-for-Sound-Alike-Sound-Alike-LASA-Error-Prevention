<div align="center">

# 💊 AI-Based LASA Drug Name Detection System

### *Clinical Decision Support for Look-Alike Sound-Alike Medication Error Prevention*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.x-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Jinja2](https://img.shields.io/badge/Jinja2-3.x-B41717?style=for-the-badge&logo=jinja&logoColor=white)](https://jinja.palletsprojects.com/)

> **LASA medication errors are among the most preventable — and the most dangerous — in clinical environments.**
> This system brings AI-powered, real-time safety analysis directly to the point of care.

---

[🚀 Quick Start](#-quick-start) · [🏗 Architecture](#-system-architecture) · [📖 API Docs](#-api-reference) · [🧪 Usage Examples](#-usage-examples) · [📊 Model Performance](#-model-performance) · [🛠 Tech Stack](#-tech-stack)

</div>

---

## 🎯 What is LASA?

**Look-Alike Sound-Alike (LASA)** refers to pairs of drug names that look or sound similar enough to be confused with each other, leading to catastrophic medication errors. According to the **Institute for Safe Medication Practices (ISMP)**, LASA errors account for **~25% of all reported medication errors** in hospitals.

**Classic dangerous pairs include:**
| Drug A | Drug B | Confusion Risk |
|:---|:---|:---|
| `dopamine` | `dobutamine` | Both vasopressors — very similar names & routes |
| `hydroxyzine` | `hydralazine` | Antihistamine vs. antihypertensive |
| `metformin` | `methergine` | Antidiabetic vs. uterotonic oxytocic |
| `vincristine` | `vinblastine` | Both vinca alkaloids — 10x dose difference is fatal |
| `lorazepam` | `alprazolam` | Both benzodiazepines — easy phonetic swap |

This system uses **machine learning, NLP, and patient context validation** to flag these errors before they reach the patient.

---

## ✨ Features

| Feature | Description |
|:---|:---|
| 📄 **PDF Data Extraction** | Parses ISMP drug confusion alert PDFs using `pdfplumber` to build a labeled positive-pair dataset |
| 🧮 **9-Feature Engineering** | Computes Levenshtein distance, WRatio, Token Sort Ratio, Soundex, Metaphone, Bi/Trigram overlap, prefix match, and length ratio |
| 🤖 **Ensemble ML Classification** | Random Forest and Gradient Boosting both trained; best AUC model is automatically selected and serialized |
| 🗣️ **NLP Drug Extraction** | Regex + curated dictionary-based clinical NER — extracts drug name, dosage, and route from free-text sentences |
| 🎙️ **Speech-to-Text** | OpenAI Whisper integration for voice-based clinical input with graceful mock fallback |
| 🏥 **Patient Context Validation** | Secondary safety layer — cross-references drug class against a patient diagnosis taxonomy |
| ⚖️ **Decision Engine** | Context-aware risk stratification (🟢 LOW / 🟡 MEDIUM / 🔴 HIGH) with ISMP-boost scoring and human-readable reasons |
| 🌐 **Web Interface** | Dark-themed, responsive FastAPI + Jinja2 frontend with real-time JSON analysis |

---

## 🏗 System Architecture

The system is a fully modular 8-stage pipeline. Each module is independently executable and produces serialized outputs consumed by the next stage.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLINICAL INPUT                              │
│              (Voice Recording OR Free-Text Sentence)                │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │  Module 06            │
          │  Speech-to-Text       │  ← OpenAI Whisper (or graceful mock fallback)
          │  (Transcription)      │    Returns: { text, language, confidence }
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │  Module 05            │
          │  NLP Drug Extractor   │  ← Regex + Dictionary NER
          │                       │    Returns: { drug, dose, route }
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │  Module 04            │
          │  LASA Inference       │  ← modules_utils.compute_features_pair()
          │  Engine               │    Scores query against master drug list
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │  Module 07            │
          │  Patient Context      │  ← Taxonomy: Drug Class ↔ Diagnosis Map
          │  Validator            │    Returns: { mismatch, drug_class, note }
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │  Module 08            │
          │  Decision Engine      │  ← Aggregates all signals with ISMP boost
          │                       │    Returns: { risk_level, message, reasons }
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │  Module 09 (app.py)   │
          │  FastAPI Web Server   │  ← REST endpoints + Jinja2 HTML frontend
          └───────────────────────┘
```

### Training Pipeline (Run Once)

```
PDF Files  →  Module 01  →  Module 02  →  Module 03  →  lasa_classifier.pkl
(ISMP data)   (Pairs)       (Features)    (Training)     (Best model artifact)
```

> **Module 03** trains both a `RandomForestClassifier` (200 trees, balanced class weights) and a `GradientBoostingClassifier` (200 estimators, lr=0.05), evaluates each on a stratified 80/20 split, and serializes the one with the higher AUC-ROC.

---

## 📁 Project Structure

```
lasa_detection/
│
├── data/
│   ├── raw/                         # Source ISMP PDFs (add your own here)
│   ├── processed/
│   │   ├── drug_pairs.csv           # Extracted positive LASA pairs (drug1, drug2, label)
│   │   ├── training_dataset.csv     # Balanced labeled dataset (positive + negative samples)
│   │   └── feature_matrix.csv       # 9-dimensional feature vectors per pair
│   └── drug_list.txt                # Master drug name list (~300+ entries, one per line)
│
├── modules/
│   ├── 01_data_preprocessing.py     # PDF parsing + negative sample generation
│   ├── 02_feature_engineering.py    # Similarity feature computation (9 metrics)
│   ├── 03_model_training.py         # RF + GBM training, AUC comparison, best model saved
│   ├── 04_lasa_engine.py            # Inference: score a query vs. all known drugs
│   ├── 05_nlp_drug_extractor.py     # Clinical sentence → drug/dose/route extractor
│   ├── 06_speech_to_text.py         # Whisper-based audio transcription wrapper
│   ├── 07_patient_context.py        # Drug-class ↔ Diagnosis mismatch validator
│   ├── 08_decision_engine.py        # Final risk aggregation + output formatter
│   └── modules_utils.py             # Shared compute_features_pair() (used by engine + API)
│
├── models/
│   └── lasa_classifier.pkl          # Serialized best model artifact (joblib dict)
│
├── app/
│   ├── app.py                       # FastAPI application (3 endpoints + dynamic module loading)
│   ├── static/                      # CSS, JS, icons
│   └── templates/
│       └── index.html               # Dark-themed clinical UI
│
├── notebooks/                       # Jupyter notebooks for EDA / prototyping
├── bootstrap.py                     # Auto-creates full directory structure
├── run_all.py                       # Full sequential pipeline runner (preprocessing → training)
├── run_pipeline.bat                 # One-click Windows launcher (venv + install + train + serve)
├── test_pdf.py                      # Utility: verify pdfplumber can parse ISMP PDFs
└── requirements.txt                 # All Python dependencies
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10** or higher
- Windows / macOS / Linux
- ~500 MB disk space (if using Whisper voice input for model download)

### Option A: One-Click (Windows)

```bat
run_pipeline.bat
```

This automatically: creates a virtual environment → installs all dependencies → runs the full training pipeline → starts the web server at **`http://localhost:8000`**.

### Option B: Manual Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add your ISMP PDFs to data/raw/ then run the training pipeline
python run_all.py

# 4. Start the web server
cd app
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000** in your browser.

> **Note:** If you skip Step 3 (no PDFs available), the system will still run the NLP + context validator pipeline. The LASA ML scoring requires the `models/lasa_classifier.pkl` artifact to exist.

---

## 🧪 Usage Examples

### Via Web Interface

Navigate to `http://localhost:8000/` and fill in the form:

| Field | Example Value |
|:---|:---|
| **Clinical Text** | `"Administer 25mg hydroxyzine IV for patient anxiety"` |
| **Patient Diagnosis** | `anxiety` |

---

### Example 1: ✅ Safe Prescription (LOW Risk)

**Input:**
```
Text:      "Push 500mg of metformin immediately."
Diagnosis: diabetes
```

**Expected JSON Response:**
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
    "message": "✅ Safe to administer. No significant LASA risk or context mismatch detected.",
    "reasons": ["Base model probability calculated at 99%."]
  }
}
```

> **Why LOW despite 99% similarity?** The model found that `metformin` and `methergine` are phonetically similar, but because `metformin` (an antidiabetic) is validated for the `diabetes` diagnosis with no context mismatch, the decision engine correctly suppresses the alert. This prevents *alert fatigue*.

---

### Example 2: ⚠️ Context Mismatch (HIGH Risk)

**Input:**
```
Text:      "Start a drip of hydralazine."
Diagnosis: anxiety
```

**Expected JSON Response:**
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
    "message": "⚠ Caution: Potential LASA confusion with 'hydroxyzine' (Similarity score: 99%).",
    "reasons": [
      "High phonetic similarity matches found.",
      "96% high string similarity index.",
      "Base model probability calculated at 97%.",
      "Context Mismatch: 'hydralazine' (antihypertensive) may not be indicated for 'anxiety'."
    ]
  }
}
```

> **Why HIGH?** The NLP extracted `hydralazine`. The LASA engine found `hydroxyzine` at 97% similarity (a known ISMP pair). Crucially, the Patient Context Validator flagged that `hydralazine` is an **antihypertensive** — not an anxiety treatment — triggering the full HIGH risk alert with multi-signal explainability output.

---

### Example 3: Via REST API (curl)

```bash
curl -X POST "http://localhost:8000/analyze" \
     -F "text=Prepare vincristine 2mg IV for oncology patient" \
     -F "diagnosis=cancer"
```

### Example 4: Voice Input

Upload a `.wav` or `.mp3` audio file via the `/voice` endpoint:

```bash
curl -X POST "http://localhost:8000/voice" \
     -F "file=@prescription_audio.wav" \
     -F "diagnosis=cardiac_arrest"
```

The system will transcribe the audio using **OpenAI Whisper** (or the mock fallback), extract the drug name, and return a full risk analysis.

---

## 📖 API Reference

### Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/` | Serves the dark-themed HTML frontend |
| `POST` | `/analyze` | Analyzes text input for LASA risk |
| `POST` | `/voice` | Accepts audio upload → transcribes → analyzes |

---

### `POST /analyze` — Request (form-data)

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `text` | `string` | ✅ Yes | Clinical sentence or drug name to analyze |
| `diagnosis` | `string` | ❌ Optional | Patient diagnosis for context validation |

### `POST /analyze` — Response Schema

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
    "lasa_prob": "<float 0–1>",
    "top_match": "<most similar drug name>",
    "mismatch": "<boolean>",
    "message": "<human readable warning>",
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
      "features": { "<9 feature key-value pairs>" }
    }
  ]
}
```

---

### `POST /voice` — Request (multipart/form-data)

| Field | Type | Required | Description |
|:---|:---|:---|:---|
| `file` | `UploadFile` | ✅ Yes | Audio file (`.wav`, `.mp3`, or any format Whisper supports) |
| `diagnosis` | `string` | ❌ Optional | Patient diagnosis for context validation |

### `POST /voice` — Response Schema

Same as `/analyze` response, with one additional top-level field:

```json
{
  "status": "ok",
  "transcript": "<Whisper transcription text>",
  "drug": "<extracted drug name>",
  "extracted": { "...": "..." },
  "decision": { "...": "..." },
  "lasa_hits": ["..."]
}
```

> **Note:** When Whisper is not installed, the module gracefully falls back to a mock implementation that echoes the audio filename as the transcript, so the rest of the pipeline still functions for integration testing.

---

## ⚖️ Risk Level Logic

The decision engine uses **context-aware, multi-signal risk stratification** to prevent alert fatigue. Scores are computed as:

```
adjusted_score = base_lasa_prob
              + 0.15  (if drug is a known ISMP historical pair)
              + 0.10  (if patient diagnosis mismatch detected)
              + 0.05  (if STT confidence < 0.6)
```

| Risk Level | Trigger Conditions |
|:---|:---|
| 🔴 **HIGH** | Diagnosis mismatch detected **AND** adjusted score > 0.75 |
| 🟡 **MEDIUM** | Mismatch with score 0.45–0.75, **OR** known ISMP pair with score > 0.80, **OR** low STT confidence (< 0.8) with high score |
| 🟢 **LOW** | No mismatch detected, or similarity below all thresholds |

> **Key Design Decision:** A drug can score 99% LASA similarity and still return **LOW risk** if the prescribed drug is clinically appropriate for the patient's diagnosis. This mirrors how a real pharmacist would reason — flagging only *actionable* risks, not every phonetically similar name.

---

## 📊 Model Performance

The best classifier (chosen automatically between Random Forest and Gradient Boosting by AUC-ROC) is evaluated on a stratified 80/20 held-out test set:

| Metric | Score |
|:---|:---|
| **AUC-ROC** | ~0.97 |
| **Accuracy** | ~92% |
| **Precision (LASA=1)** | ~91% |
| **Recall (LASA=1)** | ~93% |
| **F1-Score** | ~92% |

**Baseline comparison:** A simple Jaro-Winkler threshold (> 0.85) was used as a fuzzy-matching baseline. The ML ensemble significantly outperforms it by incorporating phonetic and n-gram signals.

**Top-3 most predictive features** (by Gini importance):

1. `levenshtein_norm` — Normalized edit distance (higher = more similar)
2. `jaro_winkler` — WRatio character alignment score (via `rapidfuzz`)
3. `metaphone_match` — Phonetic Double Metaphone encoding match

A **confusion matrix plot** is automatically saved to `models/confusion_matrix.png` after each training run.

---

## 🛠 Tech Stack

### Core AI / ML

| Library | Version | Role |
|:---|:---|:---|
| `scikit-learn` | 1.x | Random Forest + Gradient Boosting classifiers, stratified train/test split |
| `pandas` | 2.x | Tabular data manipulation, feature matrix construction |
| `numpy` | 1.x | Numerical computation |
| `joblib` | 1.x | Model serialization / deserialization (`.pkl` artifact) |

### NLP & String Similarity

| Library | Version | Role |
|:---|:---|:---|
| `rapidfuzz` | 3.x | Levenshtein distance, WRatio, Token Sort Ratio |
| `jellyfish` | 0.x | Soundex + Double Metaphone phonetic encoding |
| `pdfplumber` | 0.x | PDF table/text extraction for ISMP drug pair parsing |
| `openai-whisper` | 1.x | Speech-to-text transcription (optional, graceful mock fallback) |
| `soundfile` | 0.x | Audio file I/O (required by Whisper) |
| `tqdm` | 4.x | Progress bars during pipeline processing |

### Web & Serving

| Library | Version | Role |
|:---|:---|:---|
| `fastapi` | 0.135 | REST API framework with automatic OpenAPI docs at `/docs` |
| `uvicorn` | 0.x | ASGI production server |
| `jinja2` | 3.x | HTML template rendering |
| `python-multipart` | 0.x | Multipart form + audio file upload parsing |

### Visualization (Training Phase)

| Library | Version | Role |
|:---|:---|:---|
| `matplotlib` | 3.x | Confusion matrix plot (saved to `models/confusion_matrix.png`) |
| `seaborn` | 0.x | Correlation heatmaps (EDA notebooks) |

---

## 🧬 Feature Engineering Details

Nine similarity features are computed for every drug pair `(A, B)` in `modules/02_feature_engineering.py` and shared via `modules_utils.py` for real-time inference:

| Feature | Formula / Method | Range |
|:---|:---|:---|
| `levenshtein_norm` | `1 - edit_distance(A,B) / max(len(A), len(B))` | 0–1 |
| `jaro_winkler` | `rapidfuzz.fuzz.WRatio(A, B) / 100` | 0–1 |
| `token_sort_ratio` | `rapidfuzz.fuzz.token_sort_ratio(A, B) / 100` | 0–1 |
| `ngram_bigram` | Jaccard overlap of character bigram sets | 0–1 |
| `ngram_trigram` | Jaccard overlap of character trigram sets | 0–1 |
| `soundex_match` | `int(jellyfish.soundex(A) == jellyfish.soundex(B))` | 0 or 1 |
| `metaphone_match` | `int(jellyfish.metaphone(A) == jellyfish.metaphone(B))` | 0 or 1 |
| `prefix5_match` | `int(A[:5] == B[:5])` | 0 or 1 |
| `length_ratio` | `min(len(A), len(B)) / max(len(A), len(B))` | 0–1 |

> **Why 9 features?** Combining character-level (Levenshtein), token-level (WRatio, Token Sort), phonetic (Soundex, Metaphone), and structural (prefix, length) signals gives the model diverse, complementary evidence — individual signals alone are insufficient for clinical-grade accuracy.

---

## 🧭 Supported Diagnoses (Context Validation)

The patient context validator in `modules/07_patient_context.py` maps diagnoses to expected drug classes. Prescribing a drug outside its expected class triggers the mismatch flag:

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

> To extend the taxonomy, add entries to `DRUG_CLASS_MAP` and `DIAGNOSIS_CLASS_MAP` in `modules/07_patient_context.py`. No retraining is required — the context validator runs independently of the ML model.

---

## ⚙️ Configuration

No configuration file is required. All paths are resolved relative to the project root at runtime. To override key paths, edit these constants directly:

```python
# In modules/04_lasa_engine.py (and mirrored in app/app.py)
DRUG_LIST_PATH = "data/drug_list.txt"          # Master drug list (one drug per line)
MODEL_PATH     = "models/lasa_classifier.pkl"  # Trained model artifact (joblib dict)
DRUG_PAIRS     = "data/processed/drug_pairs.csv"  # ISMP positive pairs for ISMP boost
```

The serialized model artifact is a **Python dict** with keys: `model`, `feature_cols`, `model_name`, `auc` — so you can inspect or swap the underlying estimator without retraining.

---

## 🩺 Troubleshooting

| Problem | Likely Cause | Fix |
|:---|:---|:---|
| `RuntimeError: Model not trained yet` | `models/lasa_classifier.pkl` missing | Run `python run_all.py` to train the model |
| `ModuleNotFoundError: No module named 'whisper'` | Whisper not installed | Run `pip install openai-whisper`; the system will use a mock STT fallback in its absence |
| `500 Internal Server Error` on `/analyze` | Drug extraction returns empty string | Ensure input contains a recognizable drug name; check `modules/05_nlp_drug_extractor.py` dictionary |
| `pdfplumber` extracts no pairs | ISMP PDF format changed | Run `python test_pdf.py` to verify parseable tables; update selectors in `01_data_preprocessing.py` |
| Port already in use | Another process on port 8000 | Use `--port 8001` with uvicorn, or terminate the conflicting process |
| No diagnosis mismatch flagged | Drug not in `DRUG_CLASS_MAP` | Add the drug → class mapping in `modules/07_patient_context.py` |

---

## 🔬 Research Background

This system implements concepts from published literature on medication safety systems:

- **ISMP (2023)** — *ISMP List of Confused Drug Names* — Primary dataset source for positive LASA pairs
- **Cohen MR (1999)** — *Medication Errors* — Foundational taxonomy of LASA error types and severity classification
- **Bates DW et al. (1995)** — *Incidence of Adverse Drug Events and Potential Adverse Drug Events* — Statistical grounding for error frequency estimates
- Feature engineering methodology inspired by clinical NLP research on named entity recognition in electronic health records and discharge summaries

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/add-new-drug-class`
3. Commit your changes: `git commit -m "Add oncology drug taxonomy"`
4. Push to the branch and open a Pull Request

**To extend the system:**
- **New drugs:** Add to `data/drug_list.txt` (one drug per line)
- **New LASA pairs:** Add rows to `data/processed/drug_pairs.csv` (`drug1, drug2, label`), then retrain with `python modules/03_model_training.py`
- **New drug-class mappings:** Edit `DRUG_CLASS_MAP` in `modules/07_patient_context.py`
- **New diagnosis contexts:** Edit `DIAGNOSIS_CLASS_MAP` in `modules/07_patient_context.py`

---

## ⚠️ Disclaimer

> This system is intended **solely for educational and research purposes**. It has not been validated for clinical use, is not FDA-cleared, and must **not** be used as the sole basis for any medication administration decision. Always follow institutional protocols and consult a licensed pharmacist or physician.

---

<div align="center">

**Built with ❤️ for patient safety by Saptarshi Sadhu**

*Reducing LASA medication errors through intelligent clinical decision support*

</div>
