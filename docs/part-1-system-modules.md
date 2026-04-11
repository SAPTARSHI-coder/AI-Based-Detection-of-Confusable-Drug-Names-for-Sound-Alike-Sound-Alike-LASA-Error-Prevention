# 🗂️ Part 1 — Understanding Each Module of the System
### *What every file in the `modules/` folder actually does, explained simply*

> **This document covers:** The 9 modules that make up the system — what they do, why they exist, and how they connect to each other. No coding knowledge required.

---

## The Big Idea: Why Are There 9 Separate Modules?

Think of building a hospital.

You don't build one giant room where everything happens. You have:
- A reception desk (to register the patient)
- A lab (to do blood tests)
- A radiology room (for X-rays)
- A doctor's office (to diagnose)
- A pharmacy (to dispense medicine)

Each room does exactly one job. If you need to change the lab equipment, you don't need to rebuild the hospital.

Your software works the same way. Each module does **one job**. If you want to swap out the AI model, you only change `03_model_training.py`. Nothing else breaks.

This design is called **modular architecture** — and it's exactly how professional software is built.

---

## The Two Pipelines

Your system has two separate workflows:

**Pipeline 1 — Training (happens once, before launch)**

> This is like studying for an exam. You do it once, and then you're ready.

```
PDFs from ISMP
   → Module 01: Extract drug pairs
   → Module 02: Calculate similarity numbers
   → Module 03: Train the AI model
   → Save the model to a file
```

**Pipeline 2 — Inference (happens every time someone uses the system)**

> This is like sitting the exam — using what you learned.

```
User input (text or voice)
   → Module 06: Voice → Text
   → Module 05: Text → Drug name
   → Module 04: Drug name → Risk scores
   → Module 07: Check patient context
   → Module 08: Make final decision
   → Module 09 (app.py): Show result on screen
```

---

## Module 01 — `01_data_preprocessing.py`

### What job does it do?

**This module reads the official ISMP danger list and builds the training data.**

### Real-life analogy

Imagine you're a chef learning to identify rotten fruit. Someone gives you a list from a food safety authority: *"These 400 pairs of fruits look similar but one is rotten."* You study the list to learn what to watch out for.

That's exactly what Module 01 does. It reads PDF documents from ISMP (the official medication safety organization), extracts the dangerous drug name pairs from tables inside the PDF, and saves them as a spreadsheet.

### What it creates

A file called `drug_pairs.csv` with 400+ rows, each row being:

```
drug1      | drug2       | label
---------- | ----------- | -----
dopamine   | dobutamine  | 1       ← 1 means "dangerous LASA pair"
metformin  | metronidazole | 1
aspirin    | ibuprofen   | 0       ← 0 means "not a LASA pair" (safe)
```

The `0` rows (non-LASA pairs) are called **negative samples** — they're pairs the system invents by randomly combining drug names that are NOT known to be confused. These are needed so the model learns both what dangerous looks like AND what normal looks like.

> **Why do we need both?** Imagine training a fraud detector. You need examples of real fraud AND examples of normal transactions. Without normal examples, the model can't learn the difference.

---

## Module 02 — `02_feature_engineering.py`

### What job does it do?

**This module takes each drug pair and calculates 9 numbers that describe how similar the two names are.**

### Real-life analogy

Think of comparing two people's faces for identification. You don't just say "they look the same" or "they don't." A forensic expert measures:
- Distance between the eyes
- Width of the nose
- Jaw shape
- Ear shape

Each measurement is a number. Together, the set of numbers gives a complete picture.

Module 02 does the same thing — but for drug names instead of faces. For every pair like `(dopamine, dobutamine)`, it calculates 9 numbers:

| Number | What it measures | Example |
|:---|:---|:---|
| Levenshtein distance | How many letters need to change | dopamine → dobutamine = 3 changes |
| Jaro-Winkler | How much the character positions align | High for drug names starting alike |
| Token Sort Ratio | Fuzzy text match (like a generous version of spell-check) | Catches reordered words |
| Bigram overlap | How many 2-letter chunks they share | "do", "op", "pa" |
| Trigram overlap | How many 3-letter chunks they share | "dop", "opa", "pam" |
| Soundex match | Do they sound the same when spoken? | Yes/No |
| Metaphone match | Deeper phonetic check | Yes/No |
| Prefix match | Do the first 5 letters match? | Yes/No |
| Length ratio | Are they similar in length? | 0.8 = one is 80% as long as the other |

Each pair gets turned into a row of 9 numbers. This is saved as `feature_matrix.csv`.

> **See [`part-2-features-explained.md`](./part-2-features-explained.md) for a full, simple explanation of each of these 9 measurements.**

---

## Module 03 — `03_model_training.py`

### What job does it do?

**This module takes the 9 numbers for each pair and teaches the AI to predict: is this a LASA pair (dangerous) or not?**

### Real-life analogy

Imagine you're training a new security guard. You show them hundreds of photos of real criminals and hundreds of photos of normal people. You say: *"Look at these features — hair, build, expression. Learn which combinations are suspicious."* After enough examples, the guard can look at a stranger and make an educated judgment.

Module 03 does the same. It trains two different AI models:
- **Random Forest** — like asking 200 different security guards and taking a vote
- **Gradient Boosting** — like one security guard who learns from every mistake

Both models are trained. The one that performs better (measured by a score called AUC-ROC) is saved. This saved model is the AI "brain" of your system.

The saved file is: `models/lasa_classifier.pkl`

> **See [`part-3-model-explained.md`](./part-3-model-explained.md) for a full explanation of how Random Forest and Gradient Boosting work.**

---

## Module 04 — `04_lasa_engine.py`

### What job does it do?

**When a user submits a drug name, this module compares it against all 300+ drugs in the master list and returns the most dangerous matches.**

### Real-life analogy

You work at passport control. You have a database of flagged names. When someone's passport comes in, you check their name against every entry in the database and report: *"This name is 95% similar to a flagged name."*

Module 04 does exactly that — for each drug, it:
1. Takes the queried drug name (e.g., "hydralazine")
2. Compares it to every drug in `drug_list.txt` (one by one)
3. For each comparison, calculates the 9 similarity numbers
4. Feeds those numbers into the trained AI model
5. Gets a risk probability score (0 to 1)
6. Returns the top 10 most dangerous matches, ranked by score

It also checks: *"Is this pair in the official ISMP danger list?"* If yes, it adds an extra boost to the danger score (because this is a known historical real-world confusion pair — more evidence it's dangerous).

---

## Module 05 — `05_nlp_drug_extractor.py`

### What job does it do?

**This module reads a full clinical sentence and pulls out just the drug name, dose, and route of administration.**

### Real-life analogy

A doctor writes a prescription letter: *"Please administer 25 milligrams of hydralazine intravenously twice a day for this hypertensive patient."*

A pharmacy assistant reads it and highlights/underlines:
- Drug: **hydralazine**
- Dose: **25mg**
- Route: **IV (intravenous)**

They ignore the rest.

Module 05 does this automatically.

### How it works (the simple version)

It uses two techniques:

1. **Pattern matching (Regex)** — It knows that a dose always looks like a number followed by "mg" or "mcg". It uses a pattern to find it automatically. Think of it like `Ctrl+F` but smarter — it searches for patterns, not just exact words.

2. **Dictionary lookup** — It has a pre-loaded list of all known drug names. It scans the sentence word by word and checks: "Is any of these words in my drug dictionary?" When it finds a match, it says: "Found it!"

---

## Module 06 — `06_speech_to_text.py`

### What job does it do?

**This module converts a voice recording (audio file) into written text.**

### Real-life analogy

This is like a secretary sitting in a meeting, listening carefully to everything said, and typing it all out verbatim. The output is a transcript — a written version of what was spoken.

Your system uses **OpenAI Whisper** for this — a state-of-the-art speech recognition tool that can understand English (and 99 other languages) from audio files.

### What if Whisper is not installed?

The code has a backup plan — a **mock fallback**. If Whisper is not available on the computer, the system doesn't crash. Instead, it echoes the filename as the transcript (for testing purposes). This is like having a backup secretary who just writes *"[audio-recording-1.wav]"* when they can't hear clearly.

This is important: your system is **resilient** — it keeps working even when parts are missing.

---

## Module 07 — `07_patient_context.py`

### What job does it do?

**This module checks whether the prescribed drug is clinically appropriate for the patient's diagnosed condition.**

### Real-life analogy

Imagine a patient walks into a pharmacy and hands over a prescription:

> *"50mg hydralazine for anxiety"*

A good pharmacist doesn't just fill the prescription automatically. They think: *"Hydralazine? That's a blood pressure drug. Why is this prescribed for anxiety? Something doesn't add up."*

That's exactly what Module 07 does — it's the built-in pharmacist double-check.

### How it works

The module has two lookup tables hardcoded inside it:

**Table 1 — Drug → Drug Class**

```
hydralazine   → antihypertensive
hydroxyzine   → antihistamine
metformin     → antidiabetic
vincristine   → vinca_alkaloid
lorazepam     → benzodiazepine
```

**Table 2 — Diagnosis → Expected Drug Classes**

```
anxiety       → benzodiazepine, antihistamine
diabetes      → antidiabetic
cancer        → vinca_alkaloid, platinum_agent
cardiac_arrest → vasopressor, antiarrhythmic
```

When the user provides a diagnosis, the system:
1. Looks up what class the drug belongs to
2. Looks up what classes are expected for that diagnosis
3. If they don't match → **mismatch = true**

> **Example:** `hydralazine` (antihypertensive) for `anxiety` (expects benzodiazepine / antihistamine) → **MISMATCH**

---

## Module 08 — `08_decision_engine.py`

### What job does it do?

**This is the final brain of the system. It collects all the signals from all the other modules and makes one final decision: LOW, MEDIUM, or HIGH risk.**

### Real-life analogy

Think of a court case. The judge doesn't just listen to one witness. They hear:
- The eyewitness testimony (LASA similarity score)
- The forensic expert's report (ISMP confirmation)
- The circumstantial evidence (context mismatch)
- The quality of the recording (voice confidence)

Then they weigh all the evidence and deliver a verdict.

Module 08 is the judge.

### How it calculates the score

```
Final Score = base LASA probability
            + 0.15  (if this is a known ISMP historical danger pair)
            + 0.10  (if the drug doesn't match the patient's diagnosis)
            + 0.05  (if the speech-to-text was uncertain/unclear audio)
```

Then:
- If score > 0.75 AND mismatch is confirmed → **HIGH**
- If score in the 0.45–0.75 range with some danger signals → **MEDIUM**
- Otherwise → **LOW**

### Why the asymmetry matters

Notice that even with a 99% LASA similarity, the system can still return **LOW** — if the drug perfectly matches the patient's diagnosis. This is intentional.

A doctor prescribing metformin to a diabetic patient should NOT get a warning just because metformin sounds a bit like methergine. That would be a false alarm and would train healthcare workers to ignore warnings. Your system is smarter — it only raises alarms that are genuinely actionable.

---

## Module 09 — `app/app.py`

### What job does it do?

**This is the web application — the front door of the system. It receives requests from the user, coordinates all the other modules, and sends back the result.**

### Real-life analogy

Think of a restaurant. The kitchen does all the actual cooking (that's modules 01-08). But customers don't walk into the kitchen. They interact with the **waiter** — who takes their order, gives it to the kitchen, waits, and brings the food back to the table.

`app.py` is the waiter.

### What it manages

It runs a **FastAPI** web server — imagine a small program that sits on your computer and listens for requests from a web browser. When a request comes in, it:

1. Receives the text or audio from the user
2. Calls the relevant modules (speech-to-text, drug extractor, LASA engine, context validator, decision engine)
3. Collects all the results
4. Packages them into a neat JSON response (like a structured data envelope)
5. Sends it back to the user's browser

**Three doors (endpoints) the waiter manages:**

| Door | Who uses it | What they send | What they get back |
|:---|:---|:---|:---|
| `GET /` | Anyone opening the website | Nothing (just visiting) | The web page (HTML) |
| `POST /analyze` | Someone typing a clinical sentence | Text + optional diagnosis | Full risk analysis (JSON) |
| `POST /voice` | Someone uploading an audio file | Audio file + optional diagnosis | Transcript + full risk analysis (JSON) |

---

*Next: Read [`part-2-features-explained.md`](./part-2-features-explained.md) to understand how the 9 similarity measures work.*
