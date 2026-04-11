# 🤖 Part 3 — How the AI Model Works
### *Machine learning explained from scratch, with no assumed knowledge*

> **What this file covers:** What machine learning actually is, how your system learned from data, what Random Forest and Gradient Boosting mean, and how the model makes decisions. Every concept explained with a real-life analogy.

---

## First — What Even Is Machine Learning?

### The old way: Rule-based systems

Before machine learning, programmers wrote rules to make computers make decisions:

```
IF drug_name_similarity > 0.85 THEN flag as dangerous
```

Simple. But the problem is: **who decides 0.85?** Why not 0.80? Or 0.90?

If you set it too low → too many false alarms.
If you set it too high → you miss real dangers.

And what if some drug pairs are dangerous even at 0.70 similarity (because they're used in emergency settings), while others are fine at 0.90 (because they're given in clearly labeled pill bottles)?

A single hardcoded rule can't capture all that nuance. And writing hundreds of rules manually is impossible.

---

### The machine learning way: Learn from examples

Instead of writing rules, you **show the computer examples** and let it **figure out the rules itself**.

This is exactly how children learn. You don't teach a child to identify dogs by explaining: *"Four legs, fur, barks, tail."* You show them a dog and say *"dog."* Show them a cat and say *"not dog."* After enough examples, they just... know.

Machine learning works the same way:

> **"Here are 800 drug pairs. Some are dangerous LASA pairs, some are safe. Study them. Learn the patterns. Now tell me about new pairs you've never seen."**

---

## What Data Did the Model Learn From?

Your model was trained on data built in **Module 01 and Module 02**.

The training data looks like this (simplified):

| drug1 | drug2 | lev | jw | soundex | ... 6 more | **label** |
|:---|:---|:---|:---|:---|:---|:---|
| dopamine | dobutamine | 0.70 | 0.89 | 1 | ... | **1** (dangerous) |
| hydroxyzine | hydralazine | 0.83 | 0.96 | 1 | ... | **1** (dangerous) |
| aspirin | ibuprofen | 0.22 | 0.41 | 0 | ... | **0** (safe) |
| morphine | aspirin | 0.14 | 0.35 | 0 | ... | **0** (safe) |

Each row = one drug pair, described by 9 numbers + a label (1 = LASA, 0 = not LASA).

The model reads all of this during training. It never memorizes specific pairs — it learns **patterns** in the 9 numbers that tend to lead to `label = 1`.

---

## What Input Does the Model Take?

When a new drug pair comes in during real use, the system:
1. Calculates the same 9 numbers for the new pair
2. Hands them to the model as a list

Think of it like handing a student a set of test results and asking them to predict a diagnosis.

**Input (for hydralazine vs hydroxyzine):**
```
[0.83, 0.96, 0.96, 0.75, 0.54, 1, 0, 0, 0.92]
  ↑      ↑      ↑     ↑     ↑   ↑  ↑  ↑   ↑
 lev    jw    tok   bi  tri  sx  mt  pf  len
```

Just 9 numbers. That's all the model sees.

---

## What Output Does the Model Give?

The model outputs a **probability** — a number between 0 and 1.

- **0.97** → 97% probability this is a LASA pair → **very dangerous**
- **0.20** → 20% probability → **probably safe**
- **0.55** → 55% → **uncertain — needs context to decide**

This probability is called the **LASA probability** or `lasa_prob` in the code.

> **Important:** The model doesn't give a yes/no answer. It gives a *confidence level*. The decision engine (Module 08) is responsible for converting that probability + other signals into a final risk level.

---

## How Random Forest Works

### The analogy: A committee of 200 experts

Imagine you need to decide whether a restaurant is good. You could ask one food critic — but what if they had a bad day? What if they have weird preferences?

Better idea: **ask 200 different food critics**. Each one visits the restaurant and votes yes or no. You take the majority vote. This is more reliable than any single critic.

**That's Random Forest.**

The "forest" = 200 decision trees (each tree is one expert).
Each "tree" = a simple sequence of yes/no questions.

**How one tree might look:**

```
Is levenshtein_norm > 0.75?
├── YES → Is soundex_match = 1?
│         ├── YES → Is ngram_bigram > 0.60?
│         │         ├── YES → LASA (dangerous) ✓
│         │         └── NO  → Not LASA ✗
│         └── NO  → Not LASA ✗
└── NO  → Not LASA ✗
```

Each tree asks slightly different questions (because the training data is shuffled differently for each tree). Some trees might be wrong. But when 200 of them vote, the majority tends to be right.

**Final answer:** If 170 out of 200 trees say "LASA", the model reports: `probability = 170/200 = 0.85`.

---

## How Gradient Boosting Works

### The analogy: Learning from your mistakes, step by step

Imagine a student who takes a practice test. They get some answers wrong. Instead of just moving on, they go back, identify exactly which questions they got wrong, and study those specifically. They take another test. They focus again on new mistakes. After many rounds, they're very good at the hard questions.

**That's Gradient Boosting.**

It trains models one after another. Each new model specifically tries to fix the mistakes the previous one made.

- Model 1: Makes some errors
- Model 2: Studies those errors, corrects some
- Model 3: Studies remaining errors, corrects more
- ... continues for 200 rounds
- Final answer: The combined output of all 200 rounds

> **Key difference from Random Forest:** Random Forest makes all 200 trees independently and votes. Gradient Boosting makes them sequentially — each tree learns from the previous one's failures. Gradient Boosting is often slightly more accurate but slower to train.

---

## Which Model Wins?

Your training code (`03_model_training.py`) trains **both** — Random Forest and Gradient Boosting. Then it evaluates each one on a test set (20% of the data it held back, never used in training — like a surprise exam).

It measures each model's score using a metric called **AUC-ROC**.

### What is AUC-ROC?

- **AUC** = Area Under the Curve
- **ROC** = Receiver Operating Characteristic

Forget the technical name. Here's what it means in plain English:

> **AUC-ROC measures how well the model separates dangerous pairs from safe pairs.**

- **AUC = 1.0** → Perfect — the model always gets it right
- **AUC = 0.5** → Useless — the model is guessing randomly (like a coin flip)
- **AUC = 0.97** → Excellent — the model is almost always correct

Your system achieves **AUC ≈ 0.97**.

The model with the higher AUC is saved to the file:

```
models/lasa_classifier.pkl
```

`.pkl` stands for "pickle" — not the food. It's just a way computers save Python objects into a file so they can be loaded later without retraining from scratch.

> **Analogy:** After a student graduates (finishes training), they get a degree certificate (the `.pkl` file). They don't go back to school every time they want to apply for a job — they just show the certificate.

---

## How Does the Model Decide "Risky"?

Let's trace through a complete example.

**Drug query: "hydralazine"**
**Drug being compared to: "hydroxyzine"**

**Step 1:** Module 02 calculates 9 features:
```
levenshtein_norm : 0.83
jaro_winkler     : 0.96
token_sort_ratio : 0.96
ngram_bigram     : 0.75
ngram_trigram    : 0.54
soundex_match    : 1
metaphone_match  : 0
prefix5_match    : 0
length_ratio     : 0.92
```

**Step 2:** These 9 numbers go into the Random Forest (200 trees voting).

**Step 3:** 194 out of 200 trees say "LASA".

**Step 4:** Model outputs: `lasa_prob = 0.97`

**Step 5:** Module 04 also checks the ISMP list. Yes — this pair is a documented historical confusion pair. So it adds a 0.15 bonus.

**Step 6:** Module 07 checks: hydralazine (antihypertensive) + anxiety diagnosis = MISMATCH. Adds 0.10.

**Step 7:** Module 08 final calculation:
```
adjusted_score = 0.97 + 0.15 + 0.10 = 1.0 (capped)
mismatch = true
score > 0.75 → RISK = HIGH
```

**Result:** `HIGH risk. Possible confusion with hydroxyzine. Context mismatch flagged.`

---

## Why the Model Is Trustworthy

Three reasons:

1. **It was trained on real data** — real documented errors from ISMP, not made-up examples.

2. **It was tested on data it had never seen** — the 20% test split. If it only performed well on training data but failed on new examples, we'd know it wasn't trustworthy (this is called **overfitting**). But at AUC 0.97, it performs nearly as well on unseen data.

3. **It uses 9 independent signals** — it can't be fooled by just one strong feature. All 9 must collectively point to a danger pattern.

---

## A Note on What "Training" Actually Is (Code View, Simplified)

You don't need to understand code. But here's a plain-English description of what each line in `03_model_training.py` does:

1. **Load the feature matrix** — Load the spreadsheet of 9 numbers + labels
2. **Split the data** — 80% for training, 20% for testing (randomly, but balanced)
3. **Train Model A (Random Forest)** — Show it the 80%, let it build 200 trees
4. **Train Model B (Gradient Boosting)** — Show it the 80%, let it build 200 sequential steps
5. **Test both models** — Use the 20% test set to measure AUC-ROC for each
6. **Save the winner** — Whichever has higher AUC gets saved to `lasa_classifier.pkl`
7. **Draw a confusion matrix** — A simple image showing how many correct/incorrect predictions were made (saved to `models/confusion_matrix.png`)

### What is a Confusion Matrix?

It's a table that shows the model's mistakes:

```
                 Predicted: Safe    Predicted: Dangerous
Actual: Safe         TN  ✓              FP  ✗ (false alarm)
Actual: Dangerous    FN  ✗ (missed!)    TP  ✓
```

- **TP (True Positive):** Correctly flagged a dangerous pair — great
- **TN (True Negative):** Correctly said a safe pair is safe — great
- **FP (False Positive):** Raised a false alarm — annoying but not deadly
- **FN (False Negative):** Missed a real danger — **this is the worst kind of mistake**

Your model is trained with `class_weight="balanced"` which means:
> "Pay extra attention to catching dangerous pairs — missing a real LASA pair is much worse than raising an extra false alarm."

---

*Next: Read [`part-4-examples-and-why-better.md`](./part-4-examples-and-why-better.md) for real drug examples walked through the full system, and a detailed comparison between your AI approach and simple text matching.*
