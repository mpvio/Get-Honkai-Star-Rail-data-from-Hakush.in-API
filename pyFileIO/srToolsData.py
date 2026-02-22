from collections import defaultdict

import requests

from pyFileIO.extra_classes_and_funcs import Skill_Counter
from pyFileIO.fileReadWriteFuncs import write_to_file
from pyHakushinParsing.character_funcs import add_params_to_desc, formatNumber, reorder_base_kit
import pyHakushinParsing.constants as c

def getCurrentVersion() -> str:
    url = "https://cdn.neonteam.dev/neonteam/Metadata.json"
    response = requests.get(url)
    if response.status_code == 200:
        data: dict = response.json()
        return data["CurrentVersion"]
    else:
        print(f"Failed to fetch metadata. Status code: {response.status_code}")
        return "Unknown"
    
def getTextMaps(version: str) -> dict:
    url = f"https://cdn.neonteam.dev/neonteam/{version}/textmaps.json"
    response = requests.get(url)
    if response.status_code == 200:
        data: dict = response.json()
        return data["EN"]
    else:
        print(f"Failed to fetch text maps. Status code: {response.status_code}")
        return {}
    
def getAllData(version: str) -> dict:
    data = {}
    endpoints = ["avatars", "lightcones", "relic-sets"]
    for endpoint in endpoints:
        url = f"https://cdn.neonteam.dev/neonteam/{version}/{endpoint}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data[endpoint] = response.json()
        else:
            print(f"Failed to fetch {endpoint}. Status code: {response.status_code}")
            data[endpoint] = {}
    return data
    
'''
Get "CurrentVersion" from here:
https://cdn.neonteam.dev/neonteam/Metadata.json
Insert it into the URLs below to get the latest data (replace "4.0.52-14095714"):
https://cdn.neonteam.dev/neonteam/4.0.52-14095714/avatars.json
https://cdn.neonteam.dev/neonteam/4.0.52-14095714/lightcones.json
https://cdn.neonteam.dev/neonteam/4.0.52-14095714/relic-sets.json
Get skill names/ descriptions from here:
https://cdn.neonteam.dev/neonteam/4.0.52-14095714/textmaps.json
'''

'''
Castorice:
Netherwing is split between 1407301 and 1407302 (Point19 and Point20).
[skill_trees][1407301][servants] = dict of skills, null otherwise
1407301 has skills 1140701, 1140702, 1140710, 1140711
1407302 has skills 1140703, 1140705, 1140706, 1140712
'''

def sortData(testIds: list[str]) -> tuple[list[str], list[str], list[str]]:
    avatars = []
    lightcones = []
    relicSets = []
    for id in testIds:
        if len(id) == 4: avatars.append(id)
        elif len(id) == 5: lightcones.append(id)
        elif len(id) == 3: relicSets.append(id)
    return avatars, lightcones, relicSets

def getBasicKits(ids: list[str], data: dict) -> dict:
    results = {}
    for id in ids:
        results[id] = data[id]
    return results

def addTextToCharacters(character: dict, textmap: dict):
    # add name
    character["name"] = textmap.get(str(character["name"]), None)
    # update energy if changed
    if character["max_sp_enhanced"]: character["max_sp"] = character["max_sp_enhanced"]
    # add text to kit
    categories = ["ranks", "skills", "skill_trees"]
    for category in categories:
        if character[category + "_enhanced"] != {}: 
            character[category] = character[category + "_enhanced"]
        for item in character[category]:
            name_id = str(character[category][item]["name"])
            desc_id = str(character[category][item]["desc"])
            character[category][item]["name"] = textmap.get(name_id, None)
            character[category][item]["desc"] = textmap.get(desc_id, None)

def addTextToMemosprites(memosprite: dict, textmap: dict):
    name_id = str(memosprite["name"])
    desc_id = str(memosprite["desc"])
    memosprite["name"] = textmap.get(name_id, None)
    memosprite["desc"] = textmap.get(desc_id, None)

skill_names = {
    "Normal": "Basic",
    "BPSkill": "Skill",
    "Ultra": "Ultimate",
    "Talent": "Talent",
    None: "Talent",
    "MazeNormal": "Overworld",
    "Maze": "Technique",
    "Servant": "Skill",
    "ElationDamage": "Elation Skill"
}

path_map : defaultdict = {
    "Warrior": "Destruction",
    "Priest": "Abundance",
    "Knight": "Preservation",
    "Mage": "Erudition",
    "Shaman": "Harmony",
    "Rogue": "Hunt",
    "Warlock": "Nihility",
    "Memory": "Remembrance",
    "Elation": "Elation"
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

def handleCharacters(characters: dict, textmap: dict):
    results: list[str] = []
    for character in characters.values():
        new_character = {}
        addTextToCharacters(character, textmap)

        # get name & id
        char_id = str(character["id"])
        new_character["Name"] = character["name"]

        # get stats
        new_character["Stats"] = {}
        stats = character["promotions"]["6"]

        new_character["Stats"] = handleStatCalcs(stats)

        # new_character["Stats"]["HP"] = int(stats["hp"]["base"] + (stats["hp"]["step"] * 79))
        # new_character["Stats"]["ATK"] = int(stats["atk"]["base"] + (stats["atk"]["step"] * 79))
        # new_character["Stats"]["DEF"] = int(stats["def"]["base"] + (stats["def"]["step"] * 79))
        new_character["Stats"]["Speed"] = int(stats["spd"]["base"])
        new_character["Stats"]["Aggro"] = int(stats["taunt"]["base"])
        new_character["Stats"]["Rarity"] = character["rarity"]
        new_character["Stats"]["Energy"] = int(character["max_sp"])
        new_character["Stats"]["Path"] = path_map[character["path"]]
        new_character["Stats"]["Element"] = element_map[character["element"]]

        # prepare for memosprite
        memosprite_skills = Skill_Counter()
        memosprite_kit = {}

        # set up correct order for final dict/ json
        new_character["Kit"] = {}
        new_character["Memosprite"] = {}
        new_character["Minor Traces"] = {}
        new_character["Trace Tree"] = {}
        new_character["Eidolons"] = {}

        # skills
        skill_counter = Skill_Counter()
        for skill in character["skills"].values():
            skillType = skill["type"]
            skillType = skill_names[skillType] if skillType in skill_names else skillType
            skillCount = skill_counter.add_skill(skillType)
            if skillCount > 1: skillType = f"{skillType} #{str(skillCount)}"

            name = skill["name"]
            desc = skill["desc"]
            params = skill["params"]
            if len(params) == 1:
                new_desc = add_params_to_desc(desc, params[0])
            elif len(params) > 10:
                new_desc = add_params_to_desc(desc, params[0], params[9], params[11])
            else:
                new_desc = add_params_to_desc(desc, params[0], params[5], params[6])

            new_character["Kit"][skillType] = {}
            new_character["Kit"][skillType]["Name"] = name
            new_character["Kit"][skillType]["Desc"] = new_desc
            new_character["Kit"][skillType]["Tag"] = skill["effect"]

        
        for eidolon in character["ranks"].values():
            name = eidolon["name"]
            desc = eidolon["desc"]
            params = eidolon["params"]
            new_desc = add_params_to_desc(desc, params)
            
            # print(name, ":", new_desc)
            # eidolon["desc"] = new_desc

            id = eidolon["id"] % 10
            new_character["Eidolons"][str(id)] = new_desc

        for trace in character["skill_trees"].values():
            name = trace["name"]
            desc = trace["desc"]
            if desc:
                params = trace["params"][0]
                new_desc = add_params_to_desc(desc, params)
            else:
                new_desc = desc
            memosprite_info = trace["servants"]
            
            if memosprite_info:
                skillType = "Skill" if trace["id"] % 10 == 1 else "Talent"
                for ms_skill in memosprite_info.values():
                    addTextToMemosprites(ms_skill, textmap)
                    name = ms_skill["name"]
                    desc = ms_skill["desc"]
                    params = ms_skill["params"]
                    new_desc = add_params_to_desc(desc, params[0], params[5], params[6])

                    memoSkillNum = memosprite_skills.add_skill(skillType)
                    memoSkillType = skillType if memoSkillNum == 1 else f"{skillType} #{str(memoSkillNum)}"

                    memosprite_kit[memoSkillType] = {}
                    memosprite_kit[memoSkillType]["Name"] = name
                    if new_desc: memosprite_kit[memoSkillType]["Desc"] = new_desc
                    memosprite_kit[memoSkillType]["Tag"] = textmap[str(ms_skill["tag"])]

            if name:
                id = str(trace["id"])
                new_character["Trace Tree"][id] = {}
                new_character["Trace Tree"][id]["Name"] = name
                new_character["Trace Tree"][id]["max_level"] = trace["max_level"] # will remove later
                if new_desc: new_character["Trace Tree"][id]["Desc"] = new_desc
                if len(trace["pre_points"]) != 0: new_character["Trace Tree"][id]["Requires"] = trace["pre_points"][0]
                if len(trace["status_add_list"]) != 0: 
                    value: float = trace["status_add_list"][0]["value"]
                    if trace["status_add_list"][0]["type"] != "SpeedDelta":
                        value = round(value * 100, 1)
                    new_character["Trace Tree"][id]["Value"] = formatNumber(value)

        # traces to tree & collect minor trace values:
        traceTree = {}
        minorTraces = {}
        for key in new_character["Trace Tree"]:
            trace: dict = new_character["Trace Tree"][key]
            # ignore Memosprite & Elation Skills
            if trace.pop("max_level") != 1: continue
            name = trace.pop("Name")
            # add to minor trace
            if "Value" in trace:
                value = trace["Value"]
                if name in minorTraces: minorTraces[name] += value
                else: minorTraces[name] = value
            # build trace tree
            if c.REQUIRES in trace:
                parentId = str(trace.pop(c.REQUIRES))
                parent: dict = new_character["Trace Tree"][parentId]
                if c.UNLOCKS in parent:
                    parent[c.UNLOCKS][name] = trace
                else:
                    parent[c.UNLOCKS] = {name: trace}
            else:
                traceTree[name] = trace
        
        new_character["Minor Traces"] = minorTraces
        new_character["Trace Tree"] = traceTree

        new_character["Kit"] = reorder_base_kit(new_character["Kit"])
        if memosprite_kit != {}: new_character["Memosprite"] = memosprite_kit
        else: new_character.pop("Memosprite")
        
        # import json
        # textVer = json.dumps(new_character, indent=4)
        # print(textVer)

        result = write_to_file(char_id, new_character, True)
        print(result)
        results.append(result)
    return results

def handleLightCones(lightcones: dict, textmap: dict):
    results = []
    for lightcone in lightcones.values():
        id = str(lightcone["id"])
        name = textmap.get(str(lightcone["name"]), None)
        rarity = lightcone["rarity"]
        path = path_map[lightcone["path"]]
        
        # put params into desc
        desc = textmap.get(str(lightcone["rank"]["desc"]), None)
        params = lightcone["rank"]["params"]
        s1_params = params[0]
        s5_params = params[4]
        new_desc = add_params_to_desc(desc, s1_params, s5_params)

        # get Lv 80 stats
        values = lightcone["promotion"]["values"][6]
        stats = handleStatCalcs(values)

        new_lightcone = {
            "Name": name,
            "Rarity": rarity,
            "Path": path,
            "Desc": new_desc,
            "Stats": stats
        }

        result = write_to_file(id, new_lightcone, True)
        print(result)
        results.append(result)
    return result

def handleStatCalcs(stats: dict):
    types = ["hp", "atk", "def"]
    result = {}
    for t in types:
        val = int(stats[t]["base"] + (stats[t]["step"] * 79))
        result[t.upper()] = val
    return result

def handleRelics(relics: dict, textmap: dict):
    results = []
    for relic in relics.values():
        id = str(relic["id"])
        name = textmap.get(str(relic["name"]), None)
        effects = {}
        for number in relic["set_bonus"]:
            bonus = relic["set_bonus"][number]
            desc = textmap.get(str(bonus["desc"]), None)
            params = [p["value"] for p in bonus["properties"]]
            new_desc = add_params_to_desc(desc, params)
            effects[str(number)] = new_desc
        
        new_relic = {
            "Name": name,
            "Relic Effect/s": effects
        }

        result = write_to_file(id, new_relic, True)
        print(result)
        results.append(result)
    return results

# planar
'''
{
    "Name": "Amphoreus, The Eternal Land",
    "Relic Effect/s": {
        "2": "Increases the wearer's CRIT Rate by 8%. While the wearer's memosprite is on the field, increases all allies' SPD by 8%. This effect cannot be stacked."
    }
}
'''

# cavern
'''
{
    "Name": "World-Remaking Deliverer",
    "Relic Effect/s": {
        "2": "Increases CRIT Rate by 8%.",
        "4": "After the wearer uses Basic ATK or Skill, if the wearer's memosprite is on the field, increases Max HP of the wearer and their memosprite by 24%, and increases all allies' dealt DMG by 15%, lasting until after the wearer's next use of Basic ATK or Skill."
    }
}
'''