import json
from . import constants as c
from fileIO.extra_classes_and_funcs import read_from_file

relicsets : dict = {}

mainStat : dict = {
    "CriticalDamageBase": "Crit DMG",
    "CriticalChanceBase": "Crit Rate",
    "SPRatioBase": "Energy Regeneration Rate"
}
partialReplacements : dict = {
    "Delta": "",
    "AddedRatio": "%"
}

recommendedStr = "Recommended "
relicSetStr = " Relic Set(s)"
mainStatStr = " Main Stat(s)"

def buildRecommendations(data : dict):
    cavern = getRelicSetNames(data["Set4IDList"])
    planar = getRelicSetNames(data["Set2IDList"]) #search relicset.json for names
    # replace "AddedRatio" and remove "Delta", then use Dict for other values
    body = translateStatNames(data["PropertyList3"])
    feet = translateStatNames(data["PropertyList4"])
    sphere = translateStatNames(data["PropertyList5"])
    rope = translateStatNames(data["PropertyList6"])
    substats = translateStatNames(data["SubAffixPropertyList"])
    recommendations : dict = {
        f"{recommendedStr}Cavern{relicSetStr}": cavern,
        f"{recommendedStr}Planar{relicSetStr}": planar,
        f"{recommendedStr}Body{mainStatStr}": body,
        f"{recommendedStr}Feet{mainStatStr}": feet,
        f"{recommendedStr}Sphere{mainStatStr}": sphere,
        f"{recommendedStr}Rope{mainStatStr}": rope,
        f"{recommendedStr}Substats": substats
    }
    return recommendations

def getRelicSetNames(arr: list[str]):
    global relicsets
    if relicsets == {}:
        relicsets = json.loads(read_from_file(c.formatListLocation("__relicset.json")))
    relicNames : list[str] = []
    for set in arr:
        setStr = str(set)
        if setStr in relicsets: relicNames.append(relicsets[setStr])
        else: relicNames.append(set)
    return relicNames

'''
def updateListsForManualInputs(page : str, items: List[str]):
	pageName = f"__{page}.json"
	old_list: dict = json.loads(read_from_file(c.formatListLocation(pageName)))
	differences = {id for id in items if id not in old_list}
	if differences != {}:
		getAll(page, True)
		manualUpdatesFileName = c.formatListLocation(f"__manualUpdates.txt")
		try:
			with open(manualUpdatesFileName, 'a+', encoding="UTF-8") as file:
				file.seek(0)
				tempList: List[str] = []
				while line := file.readline():
					tempList.append(line.strip())
				for diff in differences:
					if diff not in tempList: 
						file.write(f"{diff}\n")
		except: pass
'''

def translateStatNames(arr: list[str]):
    result : list[str] = []
    for stat in arr:
        if stat in mainStat: result.append(mainStat[stat])
        else:
            for key in partialReplacements.keys():
                keyStr = str(key)
                if keyStr in stat:
                    result.append(stat.replace(keyStr, partialReplacements[key]))
    return result
        

'''
    "Relics": 
    {
        "PropertyList3": [ #Body
            "CriticalDamageBase"
        ],
        "PropertyList4": [ #Boots
            "SpeedDelta",
            "HPAddedRatio"
        ],
        "PropertyList5": [ #Sphere
            "IceAddedRatio"
        ],
        "PropertyList6": [ #Rope
            "SPRatioBase",
            "HPAddedRatio"
        ],
        "SubAffixPropertyList": [ #make Dict for these
            "CriticalChanceBase",
            "CriticalDamageBase",
            "HPAddedRatio",
            "SpeedDelta"
        ]
    }
'''

'''
    "Relics": 
    {
        "Set4IDList": [
            108,
            122,
            102
        ],
        "Set2IDList": [
            309,
            301,
            306
        ],
        "PropertyList3": [
            "CriticalChanceBase",
            "CriticalDamageBase"
        ],
        "PropertyList4": [
            "AttackAddedRatio",
            "SpeedDelta"
        ],
        "PropertyList5": [
            "QuantumAddedRatio",
            "AttackAddedRatio"
        ],
        "PropertyList6": [
            "AttackAddedRatio",
            "SPRatioBase"
        ],
        "SubAffixPropertyList": [ #make Dict for these
            "CriticalChanceBase",
            "CriticalDamageBase",
            "AttackAddedRatio",
            "SpeedDelta"
        ]
    }
'''