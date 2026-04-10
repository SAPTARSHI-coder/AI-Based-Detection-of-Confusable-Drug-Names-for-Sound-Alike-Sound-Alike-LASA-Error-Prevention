"""
Shared utility: compute feature vector for a single (drug1, drug2) pair.
Used by both feature_engineering and lasa_engine.
"""
from rapidfuzz import distance as rfd, fuzz
import jellyfish

FEATURE_COLS = [
    "levenshtein_norm", "jaro_winkler", "token_sort_ratio",
    "ngram_bigram", "ngram_trigram",
    "soundex_match", "metaphone_match", "prefix5_match", "length_ratio",
]

def _ngram_overlap(a, b, n=2):
    def ngrams(s):
        return set(s[i:i+n] for i in range(len(s) - n + 1))
    g1, g2 = ngrams(a), ngrams(b)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)

def compute_features_pair(a: str, b: str) -> dict:
    lev_dist = rfd.Levenshtein.distance(a, b)
    max_len  = max(len(a), len(b)) or 1
    return {
        "levenshtein_norm": 1 - lev_dist / max_len,
        "jaro_winkler":     fuzz.WRatio(a, b) / 100.0,
        "token_sort_ratio": fuzz.token_sort_ratio(a, b) / 100.0,
        "ngram_bigram":     _ngram_overlap(a, b, 2),
        "ngram_trigram":    _ngram_overlap(a, b, 3),
        "soundex_match":    int(jellyfish.soundex(a) == jellyfish.soundex(b)),
        "metaphone_match":  int(jellyfish.metaphone(a) == jellyfish.metaphone(b)),
        "prefix5_match":    int(a[:5] == b[:5]),
        "length_ratio":     min(len(a), len(b)) / max_len,
    }
