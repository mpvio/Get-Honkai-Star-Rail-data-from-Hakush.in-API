import json
from deepdiff import DeepDiff

from pyFileIO.getBetterFileDifferences import getBetterDiffFile, removeRootFromList
from pyHakushinParsing import constants as c

def jsonListToStr(page: str) -> str:
    content: list[str] = jsonToList(page)
    return '\n'.join(content)

def jsonToList(page: str) -> list[str]:
    content: dict = readListFile(page)
    res = [f"{k}: {v}" for k, v in content]
    return res

def readListFile(page: str) -> dict:
    res: dict = json.loads(read_from_file(c.formatListLocation(f"{page}.json")))
    return res

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

def write_to_file(item_id: str, dictionary, blackListed = False, simplified = False):
    name: str = item_id if blackListed else dictionary["Name"]
    if simplified: name += " (Simple)"
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
            diff_title = c.dynamicFileName(fileName, True)
            diff_file_name = diff_title.split("/")[-1].strip(".json")
            print(diff_file_name)
            with open(diff_title, "w+", encoding="utf8") as diff_file:
                json.dump(difference, diff_file, indent=4, ensure_ascii=False)
            output = f"{name} updated and {diff_file_name} created."
    new_file = open(title, "w+", encoding="utf8")
    json.dump(dictionary, new_file, indent=4, ensure_ascii=False) #print(json.dumps(dictionary, indent=4, ensure_ascii=False))
    new_file.close()
    #TODO: check size of item_id and check appropriate list of entities to add if needed.
    ##cj.manual_add_id(item_id)
    return output

def deepdiff_converter(diffs : dict):
    # can simplify these fields to just lists
    fields_to_check = ['dictionary_item_added', 'dictionary_item_removed', 'type_changes', "iterable_item_removed"] #, 'values_changed'
    for field in fields_to_check:
        if field in diffs:
            diffs[field] = removeRootFromList(list(diffs[field]))