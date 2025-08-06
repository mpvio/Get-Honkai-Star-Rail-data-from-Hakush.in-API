import re

def abbreviate_string(text):
    """Abbreviates an entire string to initials while preserving punctuation."""
    # Improved regex: splits words (including contractions) and punctuation
    tokens = re.findall(r"(\w[\w']*)|([.,!?;:])", text)
    initials = []
    for word, punct in tokens:
        if word:
            # Take first letter of each word (including contractions)
            initials.append(word[0].upper())
        if punct:
            initials.append(punct)
    return ''.join(initials)

def abbreviate_quoted_text(text):
    """
    Safely abbreviates ONLY genuine single-quoted phrases (like 'Core Resonance'),
    while ignoring:
    - Contractions outside quotes (Saber's)
    - Game data formatting ([75|150|165]%)
    - Possessive forms
    """
    def process_match(match):
        quoted_text = match.group(1)
        # Skip if it's just a single word or contraction
        if re.fullmatch(r"\w+('\w+)?", quoted_text):
            return f"'{quoted_text}'"
        # Abbreviate multi-word phrases (using str.format() to avoid f-string backslash)
        initials = ''.join(word[0].upper() for word in re.findall(r'\b\w+\b', quoted_text))
        return "'{}'".format(initials)

    # More precise quote matching that excludes [...] and contractions
    return re.sub(r"(?<!\w)'([^']+)'(?!\w)", process_match, text)