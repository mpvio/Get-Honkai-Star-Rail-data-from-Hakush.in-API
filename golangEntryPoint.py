import sys, json
from pyHakushinParsing import constants as c
from pyHakushinParsing import hakushin_json_fetcher as hf
from pyFileIO import extra_classes_and_funcs as ec
from deepdiff import DeepDiff

def parseInput(request: dict):
    relics: dict = request["relics"] if "relics" in request else None
    summary = []
    if c.CHARACTER in request:
        characters = request[c.CHARACTER]
        summary.append(f"Characters: {len(characters)}.")
        for character in characters:
            processItem(character, relics, c.CHARACTER)
    if c.LIGHTCONE in request:
        lightcones = request[c.LIGHTCONE]
        summary.append(f"Lightcones: {len(lightcones)}.")
        for lightcone in lightcones:
            processItem(lightcone, relics, c.LIGHTCONE)
    if c.RELICSET in request:
        relicsets = request[c.RELICSET]
        summary.append(f"Relicsets: {len(relicsets)}.")
        for relicset in relicsets:
            processItem(relicset, relics, c.RELICSET)
    request["Summary"] = " ".join(summary)

def processItem(pyObj : dict, relics: dict, type: str):
    id: str = pyObj["id"]
    result: dict = {}
    # get correct type of result
    if type == c.CHARACTER:
        result: dict = hf.character(id, relics, True)
    elif type == c.LIGHTCONE:
        result: dict = hf.lightcone(id, True)
    elif type == c.RELICSET:
        result: dict = hf.relic(id, relics, True)
    # check if an item already existed, then get difference between old and current versions
    if "item" in pyObj:
        old : dict = pyObj["item"]
        difference: dict = DeepDiff(old, result, ignore_type_in_groups=[dict]).to_dict()
        if difference != {}: 
            # data changed, so return the updated item AND the diffs
            ec.deepdiff_converter(dict)
            difference = ec.getBetterDiffFile(difference)
            pyObj["item"] = result
            pyObj["changes"] = difference
        else:
            # no changes. pop the item so golang knows
            pyObj.pop("item")
    else:
        # new item added
        pyObj["item"] = result
    return pyObj

def test():
    req : dict = {
        "character" : [
            {
                "id": "1408"
            }
        ]
        }
    parseInput(req)
    print(req)

if __name__ == "__main__":
    # test()
    # receive json file
    input = sys.stdin.read()
    request = json.loads(input)
    parseInput(request)
    # print the changed json so golang can capture it
    print(json.dumps(request))