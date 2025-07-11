import json
import requests
from deepdiff import DeepDiff
from datetime import datetime
from hakushinParsing import constants as c
import re
    
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
        case 3: return "_R"
        case 4: return "_C"
        case 5: return "_L"
        case _: return "_X"

def write_to_file(item_id: str, dictionary, blackListed = False):
    prefix = "_X" if blackListed else getTagFromID(item_id)
    fileName = prefix + item_id + "_" + dictionary["Name"]
    title = c.formatDataLocation(fileName + ".json")
    old_file = read_from_file(title)
    if old_file == '':
        output = f"{fileName}.json created."
    else:
        old_as_json = json.loads(old_file)
        difference = DeepDiff(old_as_json, dictionary, ignore_type_in_groups=[dict]).to_dict() # type: ignore
        if difference == {}:
            output = f"No changes for {fileName}."
            return output
        else:
            deepdiff_converter(difference)
            date = datetime.today().strftime('%y-%m-%d')
            diffName = f"{fileName}_{date}.json"
            diff_title = c.formatChangesLocation(diffName)
            with open(diff_title, "w+", encoding="utf8") as diff_file:
                json.dump(difference, diff_file, indent=4, ensure_ascii=False)
            output = f"{fileName} updated and {diffName} created."
    new_file = open(title, "w+", encoding="utf8")
    json.dump(dictionary, new_file, indent=4, ensure_ascii=False) #print(json.dumps(dictionary, indent=4, ensure_ascii=False))
    new_file.close()
    #TODO: check size of item_id and check appropriate list of entities to add if needed.
    ##cj.manual_add_id(item_id)
    return output

def deepdiff_converter(diffs : dict):
    fields_to_check = ['dictionary_item_added', 'dictionary_item_removed', 'type_changes'] #, 'values_changed'
    for field in fields_to_check:
        if field in diffs:
            diffs[field] = list(diffs[field])

pattern: re.Pattern[str] = re.compile(
    r'(<unbreak>)|(\\n)|(<u>|<color=[^>]+>|<\/color>)|(</u>)|(")'
)

def replacer(match: re.Match[str]) -> str:
    """Handles replacements with combined <u> and color tags."""
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
    return match.group(0)

def neatenDesc(desc : str) -> str:
    return pattern.sub(replacer, desc)

def noUnbreakDesc(desc : str) -> str:
    return neatenDesc(desc).replace('</unbreak>', '')

def splitDesc(desc : str) -> list[str]:
    return neatenDesc(desc).split('</unbreak>')