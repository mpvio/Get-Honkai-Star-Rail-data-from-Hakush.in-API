#hakushin json
from collections import defaultdict
import sys
from typing import List
import requests
from pyFileIO.fileReadWriteFuncs import write_to_file
from pyHakushinParsing import character_funcs as cf
from pyHakushinParsing import buildRecommendations as br
from pyCheckNewPages import compareListsToManualInput
from pyFileIO.extra_classes_and_funcs import get_material_names, neatenDesc, getAllItems, convertCharToBetterName
from . import constants as c
from concurrent.futures import ThreadPoolExecutor

path_map : defaultdict = {
    "Warrior": "Destruction",
    "Priest": "Abundance",
    "Knight": "Preservation",
    "Mage": "Erudition",
    "Shaman": "Harmony",
    "Rogue": "Hunt",
    "Warlock": "Nihility",
    "Memory": "Remembrance"
}

element_map : defaultdict = {
    "Fire": "Fire",
    "Thunder": "Lightning",
    "Quantum": "Quantum",
    "Ice": "Ice",
    "Imaginary": "Imaginary",
    "Wind": "Wind",
    "Physical": "Physical"
}

relicEffects : dict = None

blackList : list[str] = []

v1TempList : list[str] = ["1410", "1412", "22005", "23047", "23048"]
version = "3.4.51"

def relic(param):
    if relicEffects != None and param in relicEffects:
        # use relicEffects if possible
        data: dict = relicEffects[param]
        my_data = {}

        my_data[c.NAME] = data['en']
        my_data["Relic Effect/s"] = {}
        effects: dict = data["set"]
        for setBonus in effects:
            effect: dict = effects[setBonus]
            oldDesc = effect['en']
            params = cf.parse_params(oldDesc, effect[c.PARAMLIST])
            newDesc = cf.add_params_to_desc(oldDesc, params)
            my_data["Relic Effect/s"][setBonus] = newDesc
        return True, write_to_file(f"{param}", my_data)

    # call the specific relic file otherwise
    req_string = f"https://api.hakush.in/hsr/data/en/relicset/{param}.json"
    #if param in v1TempList: req_string = f"https://api.hakush.in/hsr/{version}/en/relicset/{param}.json"
    response = requests.get(req_string)
    
    if response.status_code == 200:
        data = response.json()
        my_data = {}
        
        my_data[c.NAME] = data[c.NAME]
        # my_data["Relic Effect/s"] = data["RequireNum"]
        # for effect in my_data["Relic Effect/s"]:
        #     parse_params(my_data["Relic Effect/s"][effect][c.DESC], my_data["Relic Effect/s"][effect]["ParamList"])
        #     #add_params_to_desc()
        
        my_data["Relic Effect/s"] = {}
        for effect in data["RequireNum"]:
            old_desc = data["RequireNum"][effect][c.DESC]
            params = cf.parse_params(old_desc, data["RequireNum"][effect]["ParamList"])
            new_desc = cf.add_params_to_desc(old_desc, params)
            my_data["Relic Effect/s"][effect] = new_desc

        return True, write_to_file(f"{param}", my_data)
    else: 
        output = f"Relic Set {param} not found."
        #print(output)
        return False, output

def lightcone(param):
    req_string = f"https://api.hakush.in/hsr/data/en/lightcone/{param}.json"
    #if param in v1TempList: req_string = f"https://api.hakush.in/hsr/{version}/en/lightcone/{param}.json"
    response = requests.get(req_string)

    if response.status_code == 200:
        data = response.json()
        my_data = {}
        material_set = set()

        my_data[c.NAME] = data[c.NAME]
        #my_data[c.RARITY] = 5 if data[c.RARITY] == "CombatPowerLightconeRarity5" else 4
        if data[c.RARITY] == "CombatPowerLightconeRarity5": my_data[c.RARITY] = 5
        elif data[c.RARITY] == "CombatPowerLightconeRarity4": my_data[c.RARITY] = 4
        else: my_data[c.RARITY] = 3
        my_data[c.PATH] = path_map[data["BaseType"]] if data["BaseType"] in path_map else data["BaseType"]
        
        description = data["Refinements"][c.DESC]
        #S1 and S5 values
        s1_params = cf.parse_params(description, data["Refinements"]["Level"]["1"]["ParamList"])
        s5_params = cf.parse_params(description, data["Refinements"]["Level"]["5"]["ParamList"])
        new_desc = cf.add_params_to_desc(description, s1_params, s5_params)

        my_data[c.DESC] = new_desc #data["Refinements"][c.DESC]
        #my_data["S1"] = data["Refinements"]["Level"]["1"]["ParamList"]
        #my_data["S5"] = data["Refinements"]["Level"]["5"]["ParamList"]
        #get stats at Lv80
        get_stats(my_data, data, False)

        #get materials
        stats = data[c.STATS]
        for stat in stats:
            cost = stat["PromotionCostList"]
            for material in cost:
                material_set.add(material["ItemID"])
        my_data[c.MATERIALS] = get_material_names(material_set)
        
        return True, write_to_file(f"{param}", my_data)
    else: 
        output = f"Light Cone {param} not found."
        #print(output)
        return False, output

def character(param):
    req_string = f"https://api.hakush.in/hsr/data/en/character/{param}.json"
    #if param in v1TempList: req_string = f"https://api.hakush.in/hsr/{version}/en/character/{param}.json"
    response = requests.get(req_string)

    if response.status_code == 200:
        data = response.json()
        my_data = {}
        extras : dict = {}

        better = convertCharToBetterName(param)
        my_data[c.NAME] = better if better != None else data[c.NAME]
        get_stats(my_data, data, True)
        my_data["Kit"] = {}
        summoner_talent_id = None

        if data["Enhanced"] != {}:
            enhancements : dict = data["Enhanced"]
            latestEnh : dict = enhancements.get(list(enhancements)[-1])
            for key in latestEnh.keys():
                data[key] = latestEnh[key]
            # get description of changes
            enhancementDesc = []
            descs: dict = data["Descs"]
            for desc in descs:
                enhancementDesc.append(neatenDesc(desc))
            # add desc to main file
            my_data["Enhanced"] = enhancementDesc

        if data[c.MEMOSPRITE] != {}:
            my_data[c.MEMOSPRITE], summoner_talent_id, memoExtras = cf.parse_memosprite(data)
            extras.update(memoExtras)

        # add main + unique skills, traces, materials & eidolons to myData
        # while also collecting terminology
        extras.update(cf.mainskills(my_data, data, str(summoner_talent_id)))
        extras.update(cf.uniqueSkills(my_data, data))
        extras.update(cf.skilltreesAndMaterials(my_data, data))
        extras.update(cf.eidolons(my_data, data))

        my_data["Terms"] = extras
        my_data[c.RELICS] = br.getBuildRecommendations(data[c.RELICS], relicEffects)

        my_data[c.STATS][c.RARITY] = 5 if data[c.RARITY] == "CombatPowerAvatarRarityType5" else 4
        my_data[c.STATS]["Energy"] = data["SPNeed"]
        my_data[c.STATS][c.PATH] = path_map[data["BaseType"]] if data["BaseType"] in path_map else data["BaseType"]
        my_data[c.STATS]["Element"] = "Lightning" if data["DamageType"] == "Thunder" else data["DamageType"]

        blackListResult : str = None
        blacklisted = param in blackList
        writeToFileResult = write_to_file(f"{param}", my_data, blackListed=blacklisted)
        if blacklisted:
            blackListResult = blackListedItem(param, my_data)
            writeToFileResult = writeToFileResult.replace(my_data[c.NAME], f"X{param}")
            writeToFileResult += "\n" + blackListResult
            #return True, blackListResult
        return True, writeToFileResult
    else: 
        output = f"Character {param} not found."
        #print(output)
        return False, output
    
def blackListedItem(param: str, data: dict):
    #if len(param) == 4: 
    abridgedData : dict = {}
    # abridgedData[c.NAME] = data[c.NAME]
    abridgedData[c.STATS] = data[c.STATS]
    if c.MEMOSPRITE in data: abridgedData[c.MEMOSPRITE] = True
    abridgedData[c.MATERIALS] = data[c.MATERIALS]
    abridgedData[c.MINOR_TRACES] = data[c.MINOR_TRACES]
    #TODO: convert Traces to tree with Major traces hidden.
    abridgedData[c.TRACE_TREE] = removeMajorTraceNames(data[c.TRACE_TREE])
    abridgedData[c.RELICS] = data[c.RELICS]
    return write_to_file(f"{param}", abridgedData, blackListed=True, simplified=True)

def removeMajorTraceNames(traces : dict):
    for trace in traces:
        currentTrace = traces[trace]
        if c.TRACE in currentTrace:
            currentTrace.pop(c.NAME)
            currentTrace.pop(c.DESC)
        if c.UNLOCKS in currentTrace:
            currentTrace[c.UNLOCKS] = removeMajorTraceNames(currentTrace[c.UNLOCKS])
    return traces
                    
def get_stats(my_dict : dict, data : dict, character : bool):
     stat_dict : dict = {}
     if character:
         stats = data[c.STATS]["6"]
         hp, hpAdd = "HPBase", "HPAdd"
         atk, atkAdd = "AttackBase", "AttackAdd"
         defe, defAdd = "DefenceBase", "DefenceAdd"
     else:
         stats = data[c.STATS][-1]
         hp, hpAdd = "BaseHP", "BaseHPAdd"
         atk, atkAdd = "BaseAttack", "BaseAttackAdd"
         defe, defAdd = "BaseDefence", "BaseDefenceAdd"
     stat_dict["HP"] = round(stats[hp] + (stats[hpAdd]*79))
     stat_dict["ATK"] = round(stats[atk] + (stats[atkAdd]*79))
     stat_dict["DEF"] = round(stats[defe] + (stats[defAdd]*79))
     if character:
          stat_dict["Speed"] = stats["SpeedBase"]
          stat_dict["Aggro"] = stats["BaseAggro"]
     my_dict[c.STATS] = stat_dict

def main(args: List[str]):
    global blackList
    outputs : List[str] = []
    manualChecks : List[str] = []
    blackList = c.get_blackList()
    if len(args) < 1: 
        try: args = c.get_shortlist() #["1301"]  #["1304", "1305", "1308", "1309", "1310", "1314", "23025"] #
        except: args = ["8001", "1308", "1310"]

    getRelicsIfNeeded(args)

    with ThreadPoolExecutor(4) as exe:
        for arg, (valid, result) in zip(args, exe.map(mainloopLogic, args)):
            if valid: manualChecks.append(arg)
            if "\n" in result:
                outputs.extend(result.split("\n"))
            else:
                outputs.append(result)

    compareListsToManualInput(manualChecks)
    return outputs

def getRelicsIfNeeded(args : list[str]):
    for arg in args:
        # setup relics if needed, then immediately return
        if len(arg) in c.NEEDRELICS and relicEffects == None:
            setupRelics()
            return

def mainloopLogic(arg: str) -> tuple[bool, str]:
    """Move api calls to separate function"""
    if len(arg) == 3: func = relic
    elif len(arg) == 4: func = character
    elif len(arg) == 5: func = lightcone
    valid, result = func(arg) # type: ignore
    return valid, result


def setupRelics():
    """Should only be called once."""
    global relicEffects
    # abort if relicEffects has already been set
    if relicEffects != None: return # possibly redundant
    relicEffects = getAllItems(c.RELICSET)

if __name__ == "__main__":
    main(sys.argv[1:]) #first arg is always file name, so skip it
