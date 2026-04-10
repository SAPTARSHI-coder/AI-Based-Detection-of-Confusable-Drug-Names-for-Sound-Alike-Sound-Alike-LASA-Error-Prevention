# AI-Based LASA Drug Name Detection System

> A modular, production-aware clinical decision support system that detects **Look-Alike Sound-Alike (LASA)** drug name confusion errors using machine learning.

---

## Features

- 📄 **PDF Extraction** — Parses ISMP drug confusion PDFs to build positive training pairs
- 🧮 **Feature Engineering** — Levenshtein, Jaro-Winkler, Soundex, Metaphone, n-gram similarity
- 🤖 **ML Classification** — Random Forest + Gradient Boosting with AUC-ROC evaluation
- 🗣 **NLP Drug Extraction** — Regex + dictionary-based entity recognition from clinical text
- 🎙 **Speech-to-Text** — OpenAI Whisper integration for audio input
- 🏥 **Patient Context** — Drug-diagnosis mismatch validation
- ⚖️ **Decision Engine** — Risk-stratified output (LOW / MEDIUM / HIGH)
- 🌐 **Web Interface** — FastAPI + dark-themed HTML frontend

---

## Project Structure

```
lasa_detection/
├── data/
│   ├── raw/                        # Source PDFs
│   ├── processed/
│   │   ├── drug_pairs.csv          # Positive LASA pairs
│   │   ├── training_dataset.csv    # Labeled training data
│   │   └── feature_matrix.csv      # ML features
│   └── drug_list.txt               # Master drug name list
├── modules/
│   ├── 01_data_preprocessing.py
│   ├── 02_feature_engineering.py
│   ├── 03_model_training.py
│   ├── 04_lasa_engine.py
│   ├── 05_nlp_drug_extractor.py
│   ├── 06_speech_to_text.py
│   ├── 07_patient_context.py
│   ├── 08_decision_engine.py
│   └── modules_utils.py
├── models/
│   └── lasa_classifier.pkl
├── app/
│   ├── app.py                      # FastAPI server
│   └── templates/index.html
├── run_pipeline.bat                # One-click setup & run
└── requirements.txt
```

---

## Quick Start

```bash
# Run the full pipeline (installs deps, trains model, starts server)
run_pipeline.bat
```

Then open **http://localhost:8000** in your browser.

---

## Individual Steps

```bash
# Activate venv first
venv\Scripts\activate

# 1. Extract drug pairs from PDFs and generate training data
python modules\01_data_preprocessing.py

# 2. Compute similarity features
python modules\02_feature_engineering.py

# 3. Train and evaluate the classifier
python modules\03_model_training.py

# 4. Start the web server
cd app && python -m uvicorn app:app --reload
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | HTML frontend |
| `POST` | `/analyze` | Analyze text input for LASA risk |
| `POST` | `/voice` | Upload audio file for LASA analysis |

### `/analyze` request body (form)
```
text      : "Administer dopamine 5mg IV"
diagnosis : "cardiac_arrest"   (optional)
```

### Response
```json
{
  "status": "ok",
  "drug": "dopamine",
  "decision": {
    "risk_level": "HIGH",
    "lasa_prob": 0.88,
    "top_match": "dobutamine",
    "message": "⚠ Possible LASA confusion with 'dobutamine' (probability: 88%)."
  },
  "lasa_hits": [...]
}
```

---

## Risk Levels

| Level | Condition |
|-------|-----------|
| 🔴 HIGH | LASA probability > 0.75 **and/or** patient context mismatch |
| 🟡 MEDIUM | LASA probability > 0.45 **or** context mismatch detected |
| 🟢 LOW | No significant LASA similarity found |

---

## Dependencies

```
pdfplumber  pandas  numpy  rapidfuzz  jellyfish
scikit-learn  xgboost  joblib  fastapi  uvicorn
matplotlib  seaborn  openai-whisper (optional)
```

---

> ⚠️ **Disclaimer:** This system is for research and educational purposes only. It is **not validated for clinical use** and must not be used as a sole basis for medication decisions.
"# AI-Based-Detection-of-Confusable-Drug-Names-for-Sound-Alike-Sound-Alike-LASA-Error-Prevention" 
