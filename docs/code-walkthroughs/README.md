# 📚 Code Walkthroughs — Index
### *Line-by-line explanations of every file in the LASA Detection System*

> **Purpose:** These files explain every single line of code across all 9 modules in very simple English — no Python knowledge assumed. Each file covers what the module does, why it exists, and walks through every function and line with real-life analogies.

---

## 📂 Files in This Folder

| # | File | Module | What It Explains |
|:---|:---|:---|:---|
| 1 | [`01_data_preprocessing.md`](./01_data_preprocessing.md) | `01_data_preprocessing.py` | Reading ISMP PDFs, cleaning drug names, generating negative samples, saving training data |
| 2 | [`02_feature_engineering.md`](./02_feature_engineering.md) | `02_feature_engineering.py` | Calculating the 9 similarity features for every drug pair |
| 3 | [`03_model_training.md`](./03_model_training.md) | `03_model_training.py` | Training Random Forest & Gradient Boosting, comparing models, saving the best one |
| 4 | [`04_lasa_engine.md`](./04_lasa_engine.md) | `04_lasa_engine.py` | Comparing a query drug against the full drug list and scoring LASA probability |
| 5 | [`05_nlp_drug_extractor.md`](./05_nlp_drug_extractor.md) | `05_nlp_drug_extractor.py` | Extracting drug name, dose, and route from free-text clinical sentences |
| 6 | [`06_speech_to_text.md`](./06_speech_to_text.md) | `06_speech_to_text.py` | Converting audio recordings to text using Whisper, with graceful mock fallback |
| 7 | [`07_patient_context.md`](./07_patient_context.md) | `07_patient_context.py` | Checking if a drug's class matches the patient's diagnosis |
| 8 | [`08_decision_engine.md`](./08_decision_engine.md) | `08_decision_engine.py` | Combining all signals into a final LOW/MEDIUM/HIGH risk verdict with explanations |
| 9 | [`modules_utils.md`](./modules_utils.md) | `modules_utils.py` | The shared feature calculator — the file that keeps training and live use consistent |
| + | [`app_py.md`](./app_py.md) | `app/app.py` | The FastAPI web server — all three endpoints, module loading, file upload handling |
| + | [`index_html.md`](./index_html.md) | `app/templates/index.html` | The complete frontend — CSS design system, HTML structure, JavaScript (Matrix rain, fetch API, renderResult) |

---

## 🗺️ How the Modules Connect

```
           ┌──────────────────────────────────────┐
           │           TRAINING PIPELINE           │
           │  (Run once using: python run_all.py)  │
           └──────────────────────────────────────┘

  ISMP PDFs ──► 01_data_preprocessing ──► drug_pairs.csv
                                      └──► training_dataset.csv
                                               │
              modules_utils ◄──────────────────┤
              (shared feature calculator)       │
                    │                           ▼
                    └──────────────── 02_feature_engineering
                                               │
                                               ▼
                                      03_model_training
                                               │
                                               ▼
                                      lasa_classifier.pkl ✅


           ┌──────────────────────────────────────┐
           │           INFERENCE PIPELINE          │
           │    (Every time a request is made)     │
           └──────────────────────────────────────┘

  User Input (text/audio)
       │
       ▼
  app/app.py  ─────────────────────────────────────────────┐
       │                                                     │
       │  (audio only)                                       │
       ├──► 06_speech_to_text ──► transcript text           │
       │                               │                    │
       ├──► 05_nlp_drug_extractor ◄────┘  ──► drug name     │
       │                                          │         │
       │         modules_utils ◄──────────────────┤         │
       │         (shared feature calc)            │         │
       │                                          ▼         │
       ├──► 04_lasa_engine ──────────────► LASA hits list   │
       │         + lasa_classifier.pkl                      │
       │                                                     │
       ├──► 07_patient_context ──────────► mismatch flag    │
       │                                                     │
       └──► 08_decision_engine ──────────────────────────────┘
                                       └──► { risk_level, message, reasons }
                                                    │
                                                    ▼
                                         JSON Response to Browser
```

---

## ⚡ Quick Reference: What Each Module Outputs

| Module | Output |
|:---|:---|
| `01_data_preprocessing` | `drug_list.txt`, `drug_pairs.csv`, `training_dataset.csv` |
| `02_feature_engineering` | `feature_matrix.csv` (9 feature columns + label) |
| `03_model_training` | `lasa_classifier.pkl`, `confusion_matrix.png` |
| `04_lasa_engine` | `List[Dict]` — ranked LASA matches with probabilities |
| `05_nlp_drug_extractor` | `Dict` — `{drug, dosage, route, raw}` |
| `06_speech_to_text` | `Dict` — `{text, language, confidence}` |
| `07_patient_context` | `Dict` — `{mismatch, drug_class, expected_classes, note}` |
| `08_decision_engine` | `Dict` — `{risk_level, message, reasons, details}` |
| `modules_utils` | One function: `compute_features_pair(a, b) → dict` |
| `app/app.py` | JSON HTTP response via `/analyze` or `/voice` endpoint |

---

## 💡 Tips for Reading These Files

1. **Start with `01` and work forward** if you want to understand the full training pipeline
2. **Start with `app_py`** if you want to understand how a request flows through the system
3. **Read `modules_utils` first** if a teacher asks "how do you ensure consistency between training and live use?"
4. **For any viva question about a specific feature** → go directly to `02_feature_engineering.md`
5. **For the risk logic question** → go directly to `08_decision_engine.md`

---

*Parent folder: [`../project-overview.md`](../project-overview.md)*
