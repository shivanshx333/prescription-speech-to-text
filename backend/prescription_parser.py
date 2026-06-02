"""
prescription_parser.py
======================
NLP extraction engine for parsing prescription text into structured data.

Uses a multi-pass pipeline:
1. Text normalization (lowercasing, filler removal, number-word replacement)
2. ASR correction (known Whisper mistakes, split-word rejoining)
3. Fuzzy medicine matching (edit distance + phonetic scoring)
4. Field extraction (dosage, frequency, duration, instructions)

Handles multi-medicine prescriptions by splitting on natural delimiters.
"""

import re
from medicine_data import (
    COMMON_MEDICINES,
    MEDICINE_SET,
    BRAND_TO_GENERIC,
    BRAND_SET,
    ASR_CORRECTIONS,
    JOINED_ASR_CORRECTIONS,
    NON_MEDICINE_WORDS,
    FREQUENCY_ALIASES,
    DOSAGE_UNITS,
    DURATION_UNITS,
    INSTRUCTION_PHRASES,
    PRESCRIPTION_DELIMITERS,
    NUMBER_WORDS,
)


# ==========================================================================
# String similarity utilities
# ==========================================================================

def _levenshtein(s1, s2):
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(
                prev[j + 1] + 1,
                curr[j] + 1,
                prev[j] + (c1 != c2),
            ))
        prev = curr
    return prev[-1]


def _soundex(name):
    """Extended Soundex encoding (6 chars) for phonetic matching."""
    if not name:
        return ""
    name = name.upper()
    result = name[0]
    coding = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2',
        'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6',
    }
    prev = coding.get(name[0], '0')
    for ch in name[1:]:
        code = coding.get(ch, '0')
        if code != '0' and code != prev:
            result += code
        prev = code if code != '0' else prev
    return result.ljust(6, '0')[:6]


# Pre-computed phonetic codes for all medicines
_MEDICINE_SOUNDEX = {med: _soundex(med) for med in COMMON_MEDICINES}
_BRAND_SOUNDEX = {brand: _soundex(brand) for brand in BRAND_TO_GENERIC}


def _edit_similarity(a, b):
    """Normalized edit similarity in [0, 1]. 1.0 = identical."""
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    return 1.0 - (_levenshtein(a, b) / max_len)


def _prefix_similarity(a, b):
    """Ratio of matching leading characters to max length."""
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    common = 0
    for ca, cb in zip(a, b):
        if ca == cb:
            common += 1
        else:
            break
    return common / max_len


# ==========================================================================
# Fuzzy medicine matching
# ==========================================================================

def fuzzy_match_medicine(token, threshold=0.80):
    """
    Find the best matching medicine name for a token.

    Scoring combines edit distance (55%), phonetic match (25%),
    and prefix overlap (20%).

    Returns (medicine_name, confidence) or (None, 0.0).
    """
    token = token.lower().strip()

    if not token or len(token) < 3:
        return None, 0.0

    # Exact match against generic names
    if token in MEDICINE_SET:
        return token, 1.0

    # Exact match against brand names
    if token in BRAND_SET:
        return token, 1.0

    # Known ASR correction
    if token in ASR_CORRECTIONS:
        return ASR_CORRECTIONS[token], 0.95

    # Skip short tokens for fuzzy matching (too many false positives)
    if len(token) < 4:
        return None, 0.0

    best_match = None
    best_score = 0.0
    token_sdx = _soundex(token)

    # Score against all generic medicines
    for med in COMMON_MEDICINES:
        if abs(len(token) - len(med)) > 4:
            continue
        edit_sim = _edit_similarity(token, med)
        if edit_sim < 0.5:
            continue
        phonetic_sim = 1.0 if token_sdx == _MEDICINE_SOUNDEX[med] else 0.0
        prefix_sim = _prefix_similarity(token, med)
        score = edit_sim * 0.55 + phonetic_sim * 0.25 + prefix_sim * 0.20
        if score > best_score:
            best_score = score
            best_match = med

    # Score against brand names
    for brand in BRAND_TO_GENERIC:
        if abs(len(token) - len(brand)) > 4:
            continue
        edit_sim = _edit_similarity(token, brand)
        if edit_sim < 0.5:
            continue
        phonetic_sim = 1.0 if token_sdx == _BRAND_SOUNDEX[brand] else 0.0
        prefix_sim = _prefix_similarity(token, brand)
        score = edit_sim * 0.55 + phonetic_sim * 0.25 + prefix_sim * 0.20
        if score > best_score:
            best_score = score
            best_match = brand

    if best_score >= threshold:
        return best_match, round(best_score, 3)
    return None, 0.0


# ==========================================================================
# Text normalization and medicine token correction
# ==========================================================================

def normalize_text(text):
    """Clean and normalize input text for parsing."""
    text = text.lower().strip()

    # Remove common speech filler phrases (only at the start)
    leading_fillers = [
        "um ", "uh ", "hmm ", "like ", "you know ",
        "so ", "okay ", "ok ",
        "please ", "kindly ",
        "the patient should ", "patient should ",
        "the patient needs to ", "patient needs to ",
        "i am prescribing ", "i prescribe ",
        "prescription is ", "the prescription is ",
        "you need to take ", "you should take ",
    ]
    for filler in leading_fillers:
        if text.startswith(filler):
            text = text[len(filler):]

    # Strip leading "take" only if followed by a medicine-like word
    take_match = re.match(r'^take\s+(.+)', text)
    if take_match:
        text = take_match.group(1)

    # Replace number words with digits
    for word, digit in NUMBER_WORDS.items():
        text = re.sub(r'\b' + re.escape(word) + r'\b', digit, text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def correct_medicine_tokens(text):
    """
    Multi-pass correction of medicine names in transcribed text.

    Pass 1: Apply known joined-word ASR corrections (phrase-level).
    Pass 2: Try joining 2-3 adjacent tokens and fuzzy-matching.
    Pass 3: Single-token fuzzy matching for remaining words.
    """
    # Pass 1: phrase-level ASR corrections (sorted longest-first)
    for wrong, right in sorted(JOINED_ASR_CORRECTIONS.items(),
                               key=lambda x: len(x[0]), reverse=True):
        text = text.replace(wrong, right)

    # Pass 2 & 3: token-level joining and correction
    words = text.split()
    result = []
    i = 0

    while i < len(words):
        word = words[i]
        word_lower = word.lower()

        # If already an exact medicine/brand match, keep it and move on.
        # This prevents the joiner from swallowing dosage tokens that follow.
        if word_lower in MEDICINE_SET or word_lower in BRAND_SET:
            result.append(word_lower)
            i += 1
            continue

        # Known single-word ASR correction
        if word_lower in ASR_CORRECTIONS:
            result.append(ASR_CORRECTIONS[word_lower])
            i += 1
            continue

        # Only try joining if the word looks like a medicine fragment
        # (not a digit, not a common non-medicine word)
        can_join = (word_lower not in NON_MEDICINE_WORDS
                    and not re.match(r'^\d', word))
        matched = False

        # Try joining 3 consecutive tokens
        if can_join and i + 2 < len(words):
            joined3 = words[i] + words[i + 1] + words[i + 2]
            if len(joined3) >= 5:
                match, conf = fuzzy_match_medicine(joined3, threshold=0.78)
                if match:
                    result.append(match)
                    i += 3
                    matched = True

        # Try joining 2 consecutive tokens
        if not matched and can_join and i + 1 < len(words):
            joined2 = words[i] + words[i + 1]
            if len(joined2) >= 5:
                match, conf = fuzzy_match_medicine(joined2, threshold=0.78)
                if match:
                    result.append(match)
                    i += 2
                    matched = True

        # Single-token fuzzy correction
        if not matched:
            if (len(word) >= 4
                    and word_lower not in NON_MEDICINE_WORDS
                    and not re.match(r'^\d', word)):
                match, conf = fuzzy_match_medicine(word, threshold=0.82)
                if match:
                    result.append(match)
                else:
                    result.append(word)
            else:
                result.append(word)
            i += 1

    return ' '.join(result)


# ==========================================================================
# Prescription splitting
# ==========================================================================

def split_prescriptions(text):
    """Split multi-medicine text into individual prescription segments."""
    segments = [text]

    for delimiter in PRESCRIPTION_DELIMITERS:
        new_segments = []
        for segment in segments:
            parts = segment.split(delimiter)
            new_segments.extend(parts)
        segments = new_segments

    segments = [s.strip() for s in segments if s.strip()]

    valid = []
    for seg in segments:
        if len(seg) > 3 and _contains_medical_term(seg):
            valid.append(seg)
        elif valid:
            valid[-1] += " " + seg

    return valid if valid else [text]


def _contains_medical_term(text):
    """Check if text contains a recognizable medicine or dosage pattern."""
    text_lower = text.lower()
    for med in COMMON_MEDICINES:
        if med in text_lower:
            return True
    for brand in BRAND_TO_GENERIC:
        if brand in text_lower:
            return True
    if re.search(r'\d+\s*(?:mg|ml|g|mcg|tablet|capsule|drop|unit)', text_lower):
        return True
    return False


# ==========================================================================
# Field extraction
# ==========================================================================

def extract_medicine_name(text):
    """
    Extract the medicine name from a prescription segment.

    Returns (display_name, generic_name_or_None, confidence).
    """
    text_lower = text.lower()

    # Check brand names first (exact word boundary match)
    for brand, generic in BRAND_TO_GENERIC.items():
        if re.search(r'\b' + re.escape(brand) + r'\b', text_lower):
            return brand.title(), generic.title(), 1.0

    # Check generic medicine names (exact match)
    for med in COMMON_MEDICINES:
        if re.search(r'\b' + re.escape(med) + r'\b', text_lower):
            return med.title(), None, 1.0

    # Fuzzy match: extract candidate tokens and score them
    words = text_lower.split()
    best_candidate = None
    best_confidence = 0.0

    for idx, word in enumerate(words):
        if word in NON_MEDICINE_WORDS or len(word) < 4:
            continue
        if re.match(r'^\d', word):
            continue

        # Boost confidence if word is near a dosage token
        context_boost = 0.0
        neighbors = words[max(0, idx - 2):idx + 3]
        if any(re.match(r'\d+\s*(?:mg|ml|g|mcg)', n) for n in neighbors):
            context_boost = 0.03

        match, conf = fuzzy_match_medicine(word, threshold=0.78)
        if match and (conf + context_boost) > best_confidence:
            best_confidence = conf + context_boost
            # Determine if matched a brand or generic
            if match in BRAND_TO_GENERIC:
                best_candidate = (match.title(),
                                  BRAND_TO_GENERIC[match].title(),
                                  round(best_confidence, 3))
            else:
                best_candidate = (match.title(), None,
                                  round(best_confidence, 3))

    if best_candidate:
        return best_candidate

    # Last resort: pick the first non-common word
    common_words = NON_MEDICINE_WORDS | {"mg", "ml", "tablet", "tablets",
                                         "capsule", "capsules"}
    for word in words:
        clean = re.sub(r'[^a-zA-Z]', '', word)
        if clean and len(clean) > 2 and clean.lower() not in common_words:
            return clean.title(), None, 0.0

    return "Unknown", None, 0.0


def extract_dosage(text):
    """Extract dosage (e.g., '500 mg', '2 tablets')."""
    text_lower = text.lower()
    units_pattern = '|'.join(re.escape(u) for u in DOSAGE_UNITS)

    match = re.search(
        r'(\d+\.?\d*)\s*(' + units_pattern + r')\b',
        text_lower
    )
    if match:
        return f"{match.group(1)} {match.group(2)}"

    match = re.search(
        r'(half|quarter)\s+(' + units_pattern + r')\b',
        text_lower
    )
    if match:
        return f"{match.group(1)} {match.group(2)}"

    return "Not specified"


def extract_frequency(text):
    """Extract frequency (e.g., 'twice daily', 'every 8 hours')."""
    text_lower = text.lower()

    sorted_aliases = sorted(FREQUENCY_ALIASES.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
            return FREQUENCY_ALIASES[alias]

    match = re.search(r'every\s+(\d+)\s+(hour|hours|day|days)', text_lower)
    if match:
        return f"every {match.group(1)} {match.group(2)}"

    match = re.search(r'(\d+)\s+times?\s+(?:a\s+)?(?:day|daily)', text_lower)
    if match:
        num = match.group(1)
        freq_map = {"1": "once daily", "2": "twice daily",
                     "3": "three times daily", "4": "four times daily"}
        return freq_map.get(num, f"{num} times daily")

    return "Not specified"


def extract_duration(text):
    """Extract duration (e.g., '5 days', '2 weeks')."""
    text_lower = text.lower()
    dur_pattern = '|'.join(re.escape(u) for u in DURATION_UNITS)

    match = re.search(
        r'(?:for\s+)?(\d+)\s+(' + dur_pattern + r')\b',
        text_lower
    )
    if match:
        return f"{match.group(1)} {match.group(2)}"

    return "Not specified"


def extract_instructions(text):
    """Extract special instructions (e.g., 'after meals', 'with water')."""
    text_lower = text.lower()
    found = []

    sorted_phrases = sorted(INSTRUCTION_PHRASES, key=len, reverse=True)
    for phrase in sorted_phrases:
        if phrase in text_lower:
            overlap = any(phrase in ex or ex in phrase for ex in found)
            if not overlap:
                found.append(phrase)

    return ", ".join(found) if found else "Not specified"


# ==========================================================================
# Main entry point
# ==========================================================================

def parse_prescription(text):
    """
    Parse full prescription text into structured data.

    Pipeline: normalize -> correct medicine tokens -> split ->
    extract fields per segment.
    """
    raw_text = text
    normalized = normalize_text(text)
    corrected = correct_medicine_tokens(normalized)
    segments = split_prescriptions(corrected)

    prescriptions = []
    for segment in segments:
        med_name, generic_name, confidence = extract_medicine_name(segment)
        dosage = extract_dosage(segment)
        frequency = extract_frequency(segment)
        duration = extract_duration(segment)
        instructions = extract_instructions(segment)

        prescriptions.append({
            "medicine_name": med_name,
            "generic_name": generic_name,
            "dosage": dosage,
            "frequency": frequency,
            "duration": duration,
            "instructions": instructions,
            "confidence": confidence,
            "raw_segment": segment,
        })

    return {
        "raw_text": raw_text,
        "normalized_text": normalized,
        "corrected_text": corrected,
        "prescriptions": prescriptions,
        "num_medicines": len(prescriptions),
    }


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = [
        "Take Paracetamol 500mg twice daily for 5 days after meals",
        "Amoxicillin 250 mg three times a day for 7 days before food and Ibuprofen 400mg once daily for 3 days after food",
        "Dolo 650 mg once daily for three days with water after meals",
        "Crocin 500mg twice a day and Azee 500mg once daily for 5 days on empty stomach",
        "Take metformin 500 mg BD for 1 month after meals with water",
        "Pantoprazole 40mg once daily in the morning on empty stomach for 2 weeks",
        # ASR error test cases
        "a moxicillin 250 mg three times daily for 7 days",
        "paracetmol 500mg twice a day after meals",
        "ciproflaxin 500 mg twice daily for 5 days",
        "amoxcillin 500mg three times a day and ibuprofin 400mg twice daily",
    ]

    print("=" * 80)
    print("PRESCRIPTION PARSER - SELF-TEST")
    print("=" * 80)

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'-' * 80}")
        print(f"TEST {i}: \"{test}\"")
        print(f"{'-' * 80}")

        result = parse_prescription(test)
        print(f"  Normalized: \"{result['normalized_text']}\"")
        print(f"  Corrected:  \"{result['corrected_text']}\"")
        print(f"  Medicines found: {result['num_medicines']}")

        for j, rx in enumerate(result['prescriptions'], 1):
            print(f"\n  Prescription #{j}:")
            print(f"    Medicine:     {rx['medicine_name']}")
            if rx['generic_name']:
                print(f"    Generic:      {rx['generic_name']}")
            print(f"    Confidence:   {rx['confidence']}")
            print(f"    Dosage:       {rx['dosage']}")
            print(f"    Frequency:    {rx['frequency']}")
            print(f"    Duration:     {rx['duration']}")
            print(f"    Instructions: {rx['instructions']}")
            print(f"    Segment:      \"{rx['raw_segment']}\"")

    print(f"\n{'=' * 80}")
    print("SELF-TEST COMPLETE")
    print(f"{'=' * 80}")
