"""Phonetic analysis for brand names using big-phoney (neural network).

big-phoney can predict pronunciation for any word, including made-up brand names.
This is critical since brand names are rarely in standard dictionaries.
"""

import json
import sys
from typing import Optional

# big-phoney uses a neural network trained on CMU dict to predict any word
try:
    from big_phoney import BigPhoney
    _phoney = BigPhoney()
    HAS_BIG_PHONEY = True
except ImportError:
    _phoney = None
    HAS_BIG_PHONEY = False


def analyze_pronunciation(name: str) -> dict:
    """
    Analyze the pronunciation of a brand name.

    Returns a dict with:
    - name: the input name
    - syllables: syllable count
    - phonetic: ARPAbet phonetic representation
    - sounds_like: list of similar-sounding words
    - confidence: 0-1 confidence score
    - ambiguity_warning: any pronunciation ambiguity detected
    """
    if not HAS_BIG_PHONEY:
        return {
            "name": name,
            "error": "big-phoney not installed. Run: pip install 'namecast[phonetic]' or pip install big-phoney",
        }

    name_lower = name.lower()

    # Get phonetic transcription via neural network
    phonetic = _phoney.phonize(name_lower)
    syllables = _count_syllables_from_arpabet(phonetic)
    confidence = 0.85  # Neural net prediction

    # Find similar-sounding words based on phonetic patterns
    sounds_like = _find_similar_sounds(name_lower, phonetic)

    # Check for spelling-based ambiguity
    ambiguity = _check_ambiguity(name_lower)

    result = {
        "name": name,
        "syllables": syllables,
        "phonetic": phonetic,
        "sounds_like": sounds_like,
        "confidence": round(confidence, 2),
    }

    if ambiguity:
        result["ambiguity_warning"] = ambiguity

    # Add pronunciation difficulty assessment
    result["difficulty"] = _assess_difficulty(name_lower, syllables, ambiguity)

    return result


def _count_syllables_from_arpabet(phonetic: str) -> int:
    """Count syllables from ARPAbet transcription (count vowel phonemes)."""
    if not phonetic:
        return 1
    # Vowel phonemes in ARPAbet end with 0, 1, or 2 (stress markers)
    vowels = sum(1 for phone in phonetic.split() if phone[-1].isdigit())
    return max(1, vowels)


def _find_similar_sounds(name: str, phonetic: str) -> list[str]:
    """Find common words that the name sounds similar to based on phonetic patterns."""
    similar = []

    # Check common spelling patterns that cause confusion
    spelling_patterns = {
        "model": ["model", "modal", "bottle"],
        "sock": ["sock", "stock", "lock"],
        "soc": ["sock", "social", "soak"],
        "tax": ["tax", "tacks", "taxi"],
        "sim": ["sim", "slim", "swim", "gym"],
        "civ": ["sieve", "give", "live", "civic"],
        "silico": ["silica", "silicon"],
        "cosil": ["council", "consul", "fossil"],
        "poli": ["poly", "polly", "policy", "polish"],
        "graph": ["graph", "giraffe", "gaffe"],
        "lex": ["lex", "flex", "next"],
    }

    name_lower = name.lower()
    for pattern, words in spelling_patterns.items():
        if pattern in name_lower:
            similar.extend([w for w in words if w != name_lower])

    # Check phonetic patterns from ARPAbet transcription
    phonetic_patterns = {
        "S AH0 K": ["sock", "stuck", "suck"],  # -sock ending
        "S AA1 K": ["sock", "lock", "rock"],
        "K OW0 S": ["coast", "close"],
        "L IY1 K OW0": ["lico", "leeko"],
        "AH0 L S": ["else", "pulse"],
    }
    for pattern, words in phonetic_patterns.items():
        if pattern in phonetic:
            similar.extend([w for w in words if w not in similar])

    return list(dict.fromkeys(similar))[:5]  # Dedupe, preserve order, limit


def _check_ambiguity(name: str) -> Optional[str]:
    """Check for pronunciation ambiguity."""
    name_lower = name.lower()

    # Common ambiguous patterns
    ambiguous_patterns = {
        "soc": "Ambiguous: could be 'sock', 'soak', or 'sosh' (as in social)",
        "ough": "Highly ambiguous: through/though/tough/cough all differ",
        "ea": "Variable: 'ee' (team) vs 'eh' (bread) vs 'ay' (break)",
        "oo": "Variable: 'oo' (food) vs 'uh' (blood)",
        "ow": "Variable: 'oh' (show) vs 'ow' (cow)",
        "gh": "May be silent, 'f' sound, or hard 'g'",
        "ch": "Variable: 'ch' (chair) vs 'k' (chrome) vs 'sh' (chef)",
        "sc": "Variable: 'sk' (scar) vs 's' (scene)",
    }

    for pattern, warning in ambiguous_patterns.items():
        if pattern in name_lower:
            return warning

    return None


def _assess_difficulty(name: str, syllables: int, ambiguity: Optional[str]) -> str:
    """Assess overall pronunciation difficulty."""
    score = 0

    # Syllable penalty
    if syllables <= 2:
        score += 0
    elif syllables == 3:
        score += 1
    else:
        score += 2

    # Length penalty
    if len(name) > 8:
        score += 1

    # Ambiguity penalty
    if ambiguity:
        score += 2

    # Unusual letter combos
    unusual = ["xc", "zz", "qq", "kk", "yy", "ww", "uu"]
    for combo in unusual:
        if combo in name.lower():
            score += 1

    if score <= 1:
        return "easy"
    elif score <= 3:
        return "medium"
    else:
        return "hard"


def main():
    """CLI entry point for phonetic analysis."""
    if len(sys.argv) < 2:
        print("Usage: python -m namecast.phonetic <name>")
        sys.exit(1)

    name = sys.argv[1]
    result = analyze_pronunciation(name)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
