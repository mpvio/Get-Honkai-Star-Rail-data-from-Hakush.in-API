#hakushin json
from collections import defaultdict
import sys
from typing import List
import requests
from hakushinParsing import character_funcs as cf
from checkNewPages import read_items_from_file
from fileIO.extra_classes_and_funcs import get_material_names, write_to_file

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

def get_shortlist():
    return read_items_from_file("shortlist")

def relic(param):
    req_string = f"https://api.hakush.in/hsr/data/en/relicset/{param}.json"
    response = requests.get(req_string)
    
    if response.status_code == 200:
        data = response.json()
        my_data = {}
        
        my_data["Name"] = data["Name"]
        # my_data["Relic Effect/s"] = data["RequireNum"]
        # for effect in my_data["Relic Effect/s"]:
        #     parse_params(my_data["Relic Effect/s"][effect]["Desc"], my_data["Relic Effect/s"][effect]["ParamList"])
        #     #add_params_to_desc()
        
        my_data["Relic Effect/s"] = {}
        for effect in data["RequireNum"]:
            old_desc = data["RequireNum"][effect]["Desc"]
            params = cf.parse_params(old_desc, data["RequireNum"][effect]["ParamList"])
            new_desc = cf.add_params_to_desc(old_desc, params)
            my_data["Relic Effect/s"][effect] = new_desc

        return write_to_file(f"{param}", my_data)
    else: 
        output = f"Relic Set {param} not found."
        #print(output)
        return output

def lightcone(param):
    req_string = f"https://api.hakush.in/hsr/data/en/lightcone/{param}.json"
    response = requests.get(req_string)

    if response.status_code == 200:
        data = response.json()
        my_data = {}
        material_set = set()

        my_data["Name"] = data["Name"]
        #my_data["Rarity"] = 5 if data["Rarity"] == "CombatPowerLightconeRarity5" else 4
        if data["Rarity"] == "CombatPowerLightconeRarity5": my_data["Rarity"] = 5
        elif data["Rarity"] == "CombatPowerLightconeRarity4": my_data["Rarity"] = 4
        else: my_data["Rarity"] = 3
        my_data["Path"] = path_map[data["BaseType"]] if data["BaseType"] in path_map else data["BaseType"]
        
        description = data["Refinements"]["Desc"]
        #S1 and S5 values
        s1_params = cf.parse_params(description, data["Refinements"]["Level"]["1"]["ParamList"])
        s5_params = cf.parse_params(description, data["Refinements"]["Level"]["5"]["ParamList"])
        new_desc = cf.add_params_to_desc(description, s1_params, s5_params)

        my_data["Desc"] = new_desc #data["Refinements"]["Desc"]
        #my_data["S1"] = data["Refinements"]["Level"]["1"]["ParamList"]
        #my_data["S5"] = data["Refinements"]["Level"]["5"]["ParamList"]
        #get stats at Lv80
        get_stats(my_data, data, False)

        #get materials
        stats = data["Stats"]
        for stat in stats:
            cost = stat["PromotionCostList"]
            for material in cost:
                material_set.add(material["ItemID"])
        my_data["Materials"] = get_material_names(material_set)
        
        return write_to_file(f"{param}", my_data)
    else: 
        output = f"Light Cone {param} not found."
        #print(output)
        return output

def character(param):
    req_string = f"https://api.hakush.in/hsr/data/en/character/{param}.json"
    response = requests.get(req_string)

    if response.status_code == 200:
        data = response.json()
        my_data = {}

        my_data["Name"] = "Trailblazer" if data["Name"] == "{NICKNAME}" else data["Name"]
        get_stats(my_data, data, True)
        my_data["SkillTrees"] = {}
        my_data["Kit"] = {}
        summoner_talent_id = None

        if data["Memosprite"] != {}:
            my_data["Memosprite"], summoner_talent_id = cf.parse_memosprite(data)

        cf.mainskills(my_data, data, str(summoner_talent_id))
        cf.uniqueSkills(my_data, data)      
        cf.skilltrees(my_data, data)
        cf.eidolons(my_data, data)

        my_data["Stats"]["Rarity"] = 5 if data["Rarity"] == "CombatPowerAvatarRarityType5" else 4
        my_data["Stats"]["Energy"] = data["SPNeed"]
        my_data["Stats"]["Path"] = path_map[data["BaseType"]] if data["BaseType"] in path_map else data["BaseType"]
        my_data["Stats"]["Element"] = "Lightning" if data["DamageType"] == "Thunder" else data["DamageType"]
        
        return write_to_file(f"{param}", my_data)
    else: 
        output = f"Character {param} not found."
        #print(output)
        return output

def get_stats(my_dict : dict, data : dict, character : bool):
     stat_dict : dict = {}
     if character:
         stats = data["Stats"]["6"]
         hp, hpAdd = "HPBase", "HPAdd"
         atk, atkAdd = "AttackBase", "AttackAdd"
         defe, defAdd = "DefenceBase", "DefenceAdd"
     else:
         stats = data["Stats"][-1]
         hp, hpAdd = "BaseHP", "BaseHPAdd"
         atk, atkAdd = "BaseAttack", "BaseAttackAdd"
         defe, defAdd = "BaseDefence", "BaseDefenceAdd"
     stat_dict["HP"] = round(stats[hp] + (stats[hpAdd]*79))
     stat_dict["ATK"] = round(stats[atk] + (stats[atkAdd]*79))
     stat_dict["DEF"] = round(stats[defe] + (stats[defAdd]*79))
     if character:
          stat_dict["Speed"] = stats["SpeedBase"]
          stat_dict["Aggro"] = stats["BaseAggro"]
     my_dict["Stats"] = stat_dict

def main(args):
     outputs : List[str] = []
     if len(args) < 1: 
          try: args = get_shortlist() #["1301"]  #["1304", "1305", "1308", "1309", "1310", "1314", "23025"] #
          except: args = ["8001", "1308", "1310"]
     for arg in args:
          if len(arg) == 3: outputs.append(relic(arg))
          elif len(arg) == 4: outputs.append(character(arg))
          elif len(arg) == 5: outputs.append(lightcone(arg))
          #check_new_pages_json.manual_add_id(arg)
     return outputs

if __name__ == "__main__":
    main(sys.argv[1:]) #first arg is always file name, so skip it
