# difflib functions
import difflib

def getBetterDiffFile(diffs: dict):
    better: dict = {}
    for key in diffs:
        field: dict = diffs[key]
        if key != "values_changed":
            # capture the lists as is
            better[key] = field
        else:
            # convert changed values to inline strings
            for changeKey in field:
                value: dict = field[changeKey]
                oldVal = value["old_value"]
                newVal = value["new_value"]
                inline = genericCall(oldVal, newVal)
                better[removeRoot(changeKey)] = inline
    return better

# generic entry point
def genericCall(a, b) -> str | None:
    # invalid
    if type(a) != type(b): return None
    # no changes
    if a == b: return None
    match a:
        case str(): return diffStrings(a, b)
        case int() | float(): return diffNumbers(a, b)
        case _: return None

# handling strings (inc helper function)
def one_or_no_words(s: str) -> bool:
    return len(s.split()) < 2

def format_change(part: str, change_type: str) -> str:
    """Handles whitespace on both sides of changed text"""
    stripped = part.strip()
    if not stripped:  # Pure whitespace
        return part
    
    # Preserve original spacing
    leading = ' ' if part.startswith(' ') else ''
    trailing = ' ' if part.endswith(' ') else ''
    
    if change_type == 'delete':
        return f"{leading}--{{{stripped}}}{trailing}"
    elif change_type == 'insert':
        return f"{leading}++{{{stripped}}}{trailing}"
    elif change_type == 'replace_old':
        return f"{leading}{{{stripped}"
    elif change_type == 'replace_new':
        return f"{stripped}}}{trailing}"
    
    return part

def diffStrings(a: str, b: str) -> str:
    if one_or_no_words(a) and one_or_no_words(b): 
        # if only one or no words, use simpler version
        return diffNumbers(a, b)
    matcher = difflib.SequenceMatcher(None, a, b)
    result = [] # writing to list and converting it to string after is more efficient
    
    for tag, aStart, aEnd, bStart, bEnd in matcher.get_opcodes():
        aPart = a[aStart:aEnd]
        bPart = b[bStart:bEnd]
        
        if tag == 'equal':
            result.append(aPart)
        elif tag == 'delete':
            result.append(format_change(aPart, 'delete'))
        elif tag == 'insert':
            result.append(format_change(bPart, 'insert'))
        elif tag == 'replace':
            result.append(format_change(aPart, 'replace_old'))
            result.append(" -> ")
            result.append(format_change(bPart, 'replace_new'))
    
    # cleanup
    diff = ''.join(result)
    return (diff
        .replace('{  ', '{ ')   # Fix double spaces after opening {
        .replace('  }', ' }')   # Fix double spaces before }
        .replace('{}', '')      # Remove empty braces
        .replace('}{', '')      # Fix adjacent braces
    )

# for numbers
def diffNumbers(x: int|float|str, y: int|float|str):
    return f"{x} -> {y}"

# remove "root" from keys and list entries
def removeRootFromList(s: list[str]) -> list:
    clean = [removeRoot(line) for line in s]
    return clean

def removeRoot(s: str) -> str:
    return s.split("root")[-1]