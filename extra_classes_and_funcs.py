import json
import requests
from deepdiff import DeepDiff
from datetime import datetime
import constants as c

class TreeNode(dict):
    def __init__(self, id, root=True, trace=None, value=None, children=None, params=None):
        super().__init__()
        self.__dict__ = self
        self.Id = id
        self.Root = root
        if trace != None: self.Name = trace
        if value != None: 
            if trace != None and trace in ["A2", "A4", "A6"]: self.Desc = value
            else: self.Value = value
        if params != None: self.Params = params
        self.Unlocks = list(children) if children is not None else []

    def add_child(self, child):
        self.Unlocks.append(child)

    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        node = TreeNode(dict_['effect'], dict_['children'])
        #the below two functions are equivalent
        #node.children = [TreeNode.from_dict(child) for child in node.children]
        node.Unlocks = list(map(TreeNode.from_dict, node.Unlocks))
        return node
    
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
# WEEKLY_BOSSES = 6
# FIRST_WEEKLY_BOSS = 110501

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
               item_name = items_dict[str(material)]["ItemName"]
               if matString.startswith('1105') and matString not in weeklyBossMats and item_name != "...": item_name = "???"
               #else: item_name = items_dict[str(material)]["ItemName"]
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

def write_to_file(item_id: str, dictionary):
    fileName = getTagFromID(item_id) + item_id + "_" + dictionary["Name"]
    title = c.formatDataLocation(fileName + ".json")
    old_file = read_from_file(title)
    if old_file == '':
        output = f"{fileName}.json created."
    else:
        old_as_json = json.loads(old_file)
        difference = DeepDiff(old_as_json, dictionary, ignore_type_in_groups=[dict, TreeNode]).to_dict() # type: ignore
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
    json.dump(dictionary, new_file, indent=4, ensure_ascii=False)
    #print(json.dumps(dictionary, indent=4, ensure_ascii=False))
    new_file.close()
    #TODO: check size of item_id and check appropriate list of entities to add if needed.
    ##cj.manual_add_id(item_id)
    return output

def deepdiff_converter(diffs : dict):
    fields_to_check = ['dictionary_item_added', 'dictionary_item_removed', 'type_changes'] #, 'values_changed'
    for field in fields_to_check:
        if field in diffs:
            diffs[field] = list(diffs[field])

def manual_add_to_list():
    pass