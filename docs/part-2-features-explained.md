# 🧬 Part 2 — How the System Compares Drug Names
### *The 9 similarity features explained with analogies, examples, and zero jargon*

> **What this file covers:** The 9 different "measurements" the system uses to compare two drug names, why we need all 9 instead of just one, and how they work together.

---

## The Big Question: How Do You Measure "How Similar" Two Words Are?

This is not as simple as it sounds.

Consider these two drug names: **hydralazine** and **hydroxyzine**

Are they similar? Most people would say *yes* — but how do you put a number on it?

You could count the letters that are different.
You could check if they sound alike.
You could see how many letter-chunks they share.

Each of these is a different *way* of measuring similarity. Each one captures something the others miss.

Your system uses **9 different ways** to measure similarity — like 9 different judges each scoring from their own perspective. Their scores are then combined and fed to the AI model for the final verdict.

---

## Feature 1 — Levenshtein Distance

### What it measures
**How many single-character changes are needed to turn one word into the other.**

### Real-life analogy

Imagine you've typed a word incorrectly and AutoCorrect is figuring out what you meant.

If you typed **"hydralazine"** and the correct word is **"hydroxyzine"**, AutoCorrect counts:
- How many letters need to be **added**?
- How many need to be **deleted**?
- How many need to be **replaced**?

Each of those operations costs 1 point. The total is the **Levenshtein distance**.

### Worked example

Turn **"dopamine"** into **"dobutamine"**:

```
dopamine
d o p a m i n e
d o b u t a m i n e

Changes needed:
- Replace 'p' with 'b'
- Insert 'u'
- Insert 't'

Levenshtein distance = 3
```

**In my system**, this raw number is **normalized** (converted to a 0–1 scale) so that:
- 0 means completely different
- 1 means identical

Formula:
```
levenshtein_norm = 1 - (distance / length of the longer word)
```

So for dopamine/dobutamine:
```
levenshtein_norm = 1 - (3 / 10) = 0.70
```

That's 70% similar by this measurement.

> **Why it's useful:** Catches typos, handwriting misreads, and abbreviation confusions.

> **Its weakness:** It only looks at the letters — it doesn't care how they sound.

---

## Feature 2 — Jaro-Winkler (WRatio)

### What it measures
**How well the characters in two words align, with extra credit if they start the same way.**

### Real-life analogy

Imagine two people writing their names. You look at whether the same letters appear in roughly the same positions, and you give **bonus points** if the first few letters match — because in drug names, the beginning of the word is often the most recognizable part.

### Why drug names especially benefit from this

Drug names within the same family often share a common prefix. For example:
- **cef**uroxime, **cef**ixime, **cef**adroxil (all cephalosporin antibiotics, all start with "cef")

Two names starting with the same letters are even more likely to be confused. Jaro-Winkler rewards this and gives a higher score.

> **Its strength:** Extra sensitive to prefix similarities, which is very common in drug names.

> **Its weakness:** Less useful when two drugs sound similar but start differently.

---

## Feature 3 — Token Sort Ratio

### What it measures
**A flexible, lenient string comparison — good at catching matches even when letters are a bit rearranged.**

### Real-life analogy

Imagine a slightly forgetful receptionist who tries to find someone's file. Even if the name is spelled a bit differently or some letters are out of order, they can usually still find the right file. They're lenient.

This feature behaves like that lenient receptionist — it's designed to find matches even in imperfect conditions.

> **Why it matters:** When a voice-to-text system mishears a word, the output might be slightly scrambled. Token Sort Ratio is tolerant to that kind of partial disorder.

---

## Feature 4 — Bigram Overlap

### What it measures
**How many 2-letter chunks (bigrams) the two words share.**

### What is a bigram?

A **bigram** is just every two consecutive letters in a word.

```
"dopamine" → "do", "op", "pa", "am", "mi", "in", "ne"
"dobutamine" → "do", "ob", "bu", "ut", "ta", "am", "mi", "in", "ne"
```

Shared bigrams: `do`, `am`, `mi`, `in`, `ne` → 5 shared out of a larger total.

The system uses a formula called **Jaccard similarity** — it divides the number of shared chunks by the total number of unique chunks between both words.

### Why this is useful

Drugs that are commonly confused often share several letter pairs — because the drug names frequently come from the same chemical root or prefix convention.

> **Think of it like:** Two food items with the same ingredients are more likely to be mixed up than two with completely different ingredients.

---

## Feature 5 — Trigram Overlap

### What it measures
**The same as bigrams, but using 3-letter chunks instead of 2.**

```
"dopamine" → "dop", "opa", "pam", "ami", "min", "ine"
"dobutamine" → "dob", "obu", "but", "uta", "tam", "ami", "min", "ine"
```

Shared trigrams: `ami`, `min`, `ine` → 3 shared.

> **Why both bigrams AND trigrams?** They complement each other. Some pairs share many 2-letter chunks but fewer 3-letter chunks (or vice versa). Using both gives a more complete picture.

---

## Feature 6 — Soundex Match

### What it measures
**Whether two words sound the same when spoken aloud — using a simplified sound encoding.**

### Real-life analogy

In the 1800s, Ellis Island immigration officials needed to match names that were spelled differently in English but sounded the same — like "Smith" and "Smyth". They invented a system to convert any name into a 4-character code based purely on how it sounds.

**Soundex** still works the same way today. It converts a word into a short phonetic code:

```
dopamine   → D155
dobutamine → D153
```

If the codes match → the drugs sound similar → **soundex_match = 1**
If the codes don't match → **soundex_match = 0**

> **Note:** Soundex is a simple system — it's not perfect. That's why we also have Metaphone (below).

---

## Feature 7 — Metaphone Match

### What it measures
**A more sophisticated phonetic encoding — better at capturing how English medicine names are actually pronounced.**

### Real-life analogy

Soundex is like a basic music teacher who can tell if two songs are in the same key.
Metaphone is like a professional linguist who can tell if two words are actually pronounced identically.

```
hydroxyzine → HTRKSN
hydralazine → HTRLSN
```

These are close but not identical — which correctly reflects that they sound very similar but not exactly the same.

If the codes are identical → **metaphone_match = 1**
Otherwise → **metaphone_match = 0**

> **Why this matters more than Soundex:** Metaphone handles English pronunciation rules much better. A nurse mishearing over the phone would trigger this feature.

---

## Feature 8 — Prefix Match (First 5 Letters)

### What it measures
**Do the first 5 characters of both drug names match exactly?**

### Real-life analogy

When a doctor writes a prescription quickly by hand, the most legible part is usually the beginning of the word. If two drugs start exactly the same, even a careful nurse might misread one for the other.

```
"vincristine"[:5] = "vinci"
"vinblastine"[:5] = "vinbl"
→ Different → prefix5_match = 0

"hydroxyzine"[:5] = "hydro"
"hydralazine"[:5] = "hydra"
→ Different → prefix5_match = 0

"nimodipine"[:5] = "nimod"
"nifedipine"[:5] = "nifed"
→ Different → prefix5_match = 0
```

> **When it fires most:** When two drugs start with exactly the same prefix — like brand names in the same drug family.

> **Why binary (0 or 1)?** Because prefix matching is a hard rule — either the first 5 letters are the same or they aren't.

---

## Feature 9 — Length Ratio

### What it measures
**How similar the two names are in length (number of characters).**

### Real-life analogy

If someone asks you to find "the box of chocolates" and someone hands you a tiny mint tin, you'd be suspicious — the wrong size. Length is a physical clue.

Similarly, a very long drug name is unlikely to be confused with a very short one in real practice.

Formula:
```
length_ratio = shorter word length / longer word length
```

Example:
```
"morphine" = 8 letters
"hydromorphone" = 13 letters
ratio = 8/13 = 0.615
```

A ratio close to 1 means the words are similar in length (more likely to be confused).
A ratio close to 0 means one is much longer (less likely to be confused).

---

## Why 9 Features Instead of Just 1?

### The core problem

**No single feature is good enough on its own.**

Let's prove this with examples:

**Case 1: morphine vs hydromorphone**

| Feature | Score | Reason |
|:---|:---|:---|
| Levenshtein | 0.38 | Very different — lots of letter changes |
| Prefix match | 0 | "morp" ≠ "hydr" |
| **Phonetic (Soundex)** | **1** | Both encode the "mor" sound identically |
| Bigram overlap | 0.60 | Share "or", "rp", "ph", "in", "ne" chunks |

If you only used Levenshtein, you'd miss this pair. If you only used Soundex, you'd miss pairs that are spelled alike but sound different. You need **all of them working together**.

**Case 2: lorazepam vs alprazolam**

Both are benzodiazepines (calming medicines). Nurses can easily confuse them verbally.

| Feature | Score |
|:---|:---|
| Levenshtein | 0.45 (moderately similar) |
| Soundex | 1 (sound very similar) |
| Bigram | 0.55 (share many chunks: "az", "za", "am") |

No single score is dramatically high, but combined — the model sees a pattern consistent with hundreds of other known LASA pairs it was trained on.

### The analogy of the doctor

A doctor diagnosing a patient doesn't rely on one test. They do:
- Blood test
- X-ray
- MRI
- Patient history
- Physical examination

Each test adds evidence. Together, they build a confident picture. The 9 features are the 9 tests. The AI model is the doctor synthesizing them.

---

## How the 9 Numbers Flow Into the AI

After Module 02 computes all 9 features for a drug pair, the output looks like this:

```
Drug pair: (hydralazine, hydroxyzine)

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

These 9 numbers are handed to the machine learning model (Module 03/04), which says:

> *"Based on what I've learned from 400+ real LASA pairs... this set of numbers looks very similar to the patterns I've seen in confirmed danger pairs. My prediction: 97% probability that this is a dangerous LASA pair."*

---

*Next: Read [`part-3-model-explained.md`](./part-3-model-explained.md) to understand how the AI model actually learned from the data and makes decisions.*
