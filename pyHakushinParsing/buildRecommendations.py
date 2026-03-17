relicsets : dict = {}

mainStat : dict = {
    "CriticalDamageBase": "Crit DMG",
    "CriticalChanceBase": "Crit Rate",
    "SPRatioBase": "Energy Regeneration Rate",
    "BreakDamageAddedRatioBase": "Break Effect"
}
partialReplacements : dict = {
    "Delta": "",
    "AddedRatio": "%",
    "Thunder": "Lightning",
    "StatusProbabilityBase": "Effect Hit Rate",
    "StatusResistanceBase": "Effect RES"
}

recommendedStr = "Recommended "
relicSetStr = " Relic Set(s)"
mainStatStr = " Main Stat(s)"

def getBuildRecommendations(data : dict, relics: dict = None):
    global relicsets
    # should only be called once: set relicsets to full relics json and get names from there
    if relics != None and relicsets == {}: relicsets = relics
    cavern = getRelicSetNames(data["set4_id_list"])
    planar = getRelicSetNames(data["set2_id_list"]) #search relicsets for names
    # replace "AddedRatio" and remove "Delta", then use Dict for other values
    body = translateStatNames(data["property_list3"])
    feet = translateStatNames(data["property_list4"])
    sphere = translateStatNames(data["property_list5"])
    rope = translateStatNames(data["property_list6"])
    substats = translateStatNames(data["sub_affix_property_list"])
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
    relicNames : list[str] = []
    for set in arr:
        setStr = str(set)
        if setStr in relicsets: relicNames.append(relicsets[setStr]['en'])
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
                    stat = stat.replace(keyStr, partialReplacements[key])
            result.append(stat)
    return result