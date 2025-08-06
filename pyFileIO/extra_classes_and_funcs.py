import json
import requests
from deepdiff import DeepDiff
from datetime import datetime
from pyHakushinParsing import constants as c
import re
import os
import difflib
    
class Skill_Counter(dict):
    def __init__(self):
        super().__init__()
        self.__dict__ = self

    def add_skill(self, skill_type : str):
        if skill_type in self:
            self[skill_type] += 1
        else:
            self[skill_type] = 1
        return self[skill_type]  

    def reset(self):
        self = Skill_Counter()

items_dict = {}
weeklyBossMats = []

def set_items_dict():
    global items_dict, weeklyBossMats
    if items_dict == {}: items_dict = requests.get("https://api.hakush.in/hsr/data/en/item.json").json()
    weeklyBossMats = list(map(str, [x for x in range(c.FIRST_WEEKLY_BOSS, c.FIRST_WEEKLY_BOSS + c.WEEKLY_BOSSES)])) 

def getAllItems(type: str) -> dict:
	req_string = f"https://api.hakush.in/hsr/data/{type}.json"
	response = requests.get(req_string)
	if response.status_code == 200:
		data: dict = response.json()
		if type == c.CHARACTER:
			customCharNames(data)
		return data
	else: return {}

def customCharNames(names: dict):
    for key in names:
        name: str = convertCharToBetterName(key)
        if name != None: names[key]['en'] = name

def convertCharToBetterName(id: str) -> str:
    march7th: dict = {
		"1001": "March 7th (Ice, Preservation)",
		"1224": "March 7th (Imaginary, Hunt)"
    }
    if id in march7th:
        return march7th[id]
    num = int(id)
    if num > 8000:
        gender = "F" if num%2==0 else "M" # F if even, M if not
        element = "Des" if num < 8003 else "Pre" if num < 8005 else "Har" if num < 8007 else "Rem" if num < 8009 else "NEW"
        return f"Trailblazer {element} ({gender})"
    return None

def get_material_names(materials : set):
     set_items_dict()
     material_list = sorted(materials)
     material_names = []
     for material in material_list:
          try: 
               matString = str(material)
               #use this instead of following if statement to censor boss material if desired
               #if matString.startswith('1105') and matString not in weeklyBossMats: matString = weeklyBossMats[-1]
               item_name = items_dict[matString]["ItemName"]
               if matString.startswith('1105') and matString not in weeklyBossMats and item_name != "...": item_name = "???"
               material_names.append(item_name)
          except: pass
     return material_names

def read_from_file(title):
    try:
        old_file = open(title, "r+", encoding="utf8")
        content = old_file.read()
        old_file.close()
        return content
    except:
        return ''

def getTagFromID(itemID: str):
    idLength = len(itemID)
    match idLength:
        case 3: return "relicset/"
        case 4: return "character/"
        case 5: return "lightcone/"
        case _: return ""

def write_to_file(item_id: str, dictionary, blackListed = False):
    name = item_id if blackListed else dictionary["Name"]
    prefix = getTagFromID(item_id)
    fileName = prefix + name
    title = c.formatDataLocation(fileName + ".json")
    old_file = read_from_file(title)
    if old_file == '':
        output = f"{name}.json created."
    else:
        old_as_json = json.loads(old_file)
        difference = DeepDiff(old_as_json, dictionary, ignore_type_in_groups=[dict]).to_dict() # type: ignore
        if difference == {}:
            output = f"No changes for {name}."
            return output
        else:
            deepdiff_converter(difference)
            difference = getBetterDiffFile(difference)
            date = datetime.today().strftime('%y-%m-%d')
            diffName = f"{fileName} {date}"
            diff_title = changesFileName(diffName)
            diff_file_name = diff_title.split("/")[-1].strip(".json")
            with open(diff_title, "w+", encoding="utf8") as diff_file:
                json.dump(difference, diff_file, indent=4, ensure_ascii=False)
            output = f"{name} updated and {diff_file_name} created."
    new_file = open(title, "w+", encoding="utf8")
    json.dump(dictionary, new_file, indent=4, ensure_ascii=False) #print(json.dumps(dictionary, indent=4, ensure_ascii=False))
    new_file.close()
    #TODO: check size of item_id and check appropriate list of entities to add if needed.
    ##cj.manual_add_id(item_id)
    return output

def changesFileName(filename: str):
    ext = ".json"
    title = c.formatChangesLocation(filename)
    counter = 1
    path = title+ext

    while os.path.exists(path):
        path = title+" ("+str(counter)+")"+ext
        counter += 1
    
    return path

def deepdiff_converter(diffs : dict):
    # can simplify these fields to just lists
    fields_to_check = ['dictionary_item_added', 'dictionary_item_removed', 'type_changes'] #, 'values_changed'
    for field in fields_to_check:
        if field in diffs:
            diffs[field] = list(diffs[field])

pattern: re.Pattern[str] = re.compile(
    r'(<unbreak>)|(\\n)|(<u>|<color=[^>]+>|<\/color>)|(</u>)|(")|(–)'  # Added (–) as group 6
)

def replacer(match: re.Match[str]) -> str:
    """Handles replacements with combined <u> and color tags, and dash conversion."""
    if match.group(1):  # <unbreak> → </unbreak>
        return '</unbreak>'
    elif match.group(2):  # \n → space
        return ' '
    elif match.group(3):  # <u> OR color tags → empty
        return ''
    elif match.group(4):  # </u> → *
        return '*'
    elif match.group(5):  # " → '
        return "'"
    elif match.group(6):  # – → -
        return "-"
    return match.group(0)

def neatenDesc(desc : str) -> str:
    return pattern.sub(replacer, desc)

def noUnbreakDesc(desc : str) -> str:
    return neatenDesc(desc).replace('</unbreak>', '')

def splitDesc(desc : str) -> list[str]:
    return neatenDesc(desc).split('</unbreak>')

# difflib functions
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
                better[changeKey] = inline
    return better

# string (inc helper function)
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