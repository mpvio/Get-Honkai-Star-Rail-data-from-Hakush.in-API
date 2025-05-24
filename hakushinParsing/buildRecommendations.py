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

def getBuildRecommendations(data : dict):
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