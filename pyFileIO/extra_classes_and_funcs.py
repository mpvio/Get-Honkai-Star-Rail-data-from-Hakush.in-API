import requests
from pyHakushinParsing import constants as c
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

