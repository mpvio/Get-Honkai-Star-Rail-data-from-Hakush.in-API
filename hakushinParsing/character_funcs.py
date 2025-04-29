import traceback
from typing import List

from fileIO.extra_classes_and_funcs import Skill_Counter, TreeNode, get_material_names

skill_names = {
    "Normal": "Basic",
    "BPSkill": "Skill",
    "Ultra": "Ultimate",
    "Talent": "Talent",
    None: "Talent",
    "MazeNormal": "Overworld",
    "Maze": "Technique",
    "Servant": "Skill"
}

desc = "Desc"
paramlist = "ParamList"

def reorder_base_kit(kit : dict):
    basic = {}
    skill = {}
    ultimate = {}
    talent = {}
    technique = {}
    servant = {}

    for key, val in kit.items():
        if "Basic" in key:
            basic[key] = val
        elif "Skill" in key:
            skill[key] = val
        elif "Ultimate" in key:
            ultimate[key] = val
        elif "Talent" in key:
            talent[key] = val
        elif "Technique" in key:
            technique[key] = val
        elif "Servant" in key:
            servant[key] = val
    
    new_kit = {}
    new_kit_temp = [basic, skill, ultimate, talent, technique, servant]

    for elem in new_kit_temp:
        for key, val in elem.items():
            new_kit[key] = val
    
    return new_kit

def create_parameter_tuple_without_desc(l1_params : List[int | float], max_params : List[int | float] = None, whale_params : List[int | float] = None):
    if max_params == None:
        return " ".join(f"({p})" for p in l1_params)
    else:
        tuples = []
        for i in range ((len(l1_params))):
            if whale_params == None: text = f"[{l1_params[i]}|{max_params[i]}]"
            else: text = f"[{l1_params[i]}|{max_params[i]}|{whale_params[i]}]"
            tuples.append(text)
        return " ".join(tuples)

def params_to_position_and_percent(param_words : List[str]):
    return_dict = {}
    for word in param_words:
        percent = "%" in word
        new_word = int(word.split("[")[0].split("#")[1])-1
        return_dict[new_word] = percent
    return return_dict
    
def parse_params(desc : str, params : List[float], remembrance = False):
    if remembrance: 
        return params
    if desc is None:
        for i in range (len(params)):
            if params[i] % 1 != 0: 
                params[i] = round(params[i] * 100, 2)
            else:
                params[i] = round(params[i], 2)
            params[i] = formatNumber(params[i])
        return params
    words = desc.replace("<unbreak>", "</unbreak>").split("</unbreak>")
    set_param_words = set()
    set_param_words.update([w for w in words if "[" in w])
    param_words = sorted(list(set_param_words))
    param_num_percent_dict = params_to_position_and_percent(param_words)
    for position in param_num_percent_dict:
        try:
            if param_num_percent_dict[position]:
                params[position] = formatNumber(round(params[position] * 100, 2))
            else:
                params[position] = formatNumber(round(params[position], 2))
        except:
            traceback.print_exc()
            print(param_num_percent_dict, params, position)
    return params

def skill_tree_rework(my_data : dict):
    skilltrees = my_data["SkillTrees"]
    better_tree = {}
    tree_nodes : List[TreeNode] = []
    trace_type = 1
    major_trace = 2
    for skilltree in skilltrees:
        root = True if skilltrees[skilltree]["Requires"] == [] else False
        if "PointName" in skilltrees[skilltree]:
            if skilltrees[skilltree]["PointName"] == "None" or skilltrees[skilltree]["PointName"] == None:
                pass
            else:
                trace = skilltrees[skilltree]["PointName"]
                if "Status" in skilltrees[skilltree]:
                    if trace == "SPD Boost": value = skilltrees[skilltree]["Status"]
                    else: value = formatNumber(round(skilltrees[skilltree]["Status"] * 100, 1))
                else: value = None
                new_tree_node = TreeNode(id=skilltree, root=root, trace=trace, value=value, children=None, params=None) #skilltrees[skilltree]["Unlocks"]
                pass
        else:
            if "Desc" in skilltrees[skilltree]: value = skilltrees[skilltree]["Desc"]
            else: value = None
            if "ParamList" in skilltrees[skilltree]: 
                params = skilltrees[skilltree]["ParamList"]
            else: params = None
            new_tree_node = TreeNode(id=skilltree, root=root, trace=f"A{str(major_trace)}", value=value, children=None, params=params) #skilltrees[skilltree]["Unlocks"]
            major_trace += 2

        tree_nodes.append(new_tree_node)
        pass
    
    for node in tree_nodes:
        if node.Root == False:
            parent_node_id = skilltrees[node.Id]["Requires"][0]
            parent = find_node(trees=tree_nodes, nodeId=parent_node_id)
            if parent != None:
                parent.add_child(node)

    for node in tree_nodes:
        if node.Root:
            better_tree[f"Branch {str(trace_type)}"] = node
            trace_type += 1
        pass
    return better_tree
        
def find_node(trees : List[TreeNode], nodeId):
    for tree in trees:
        if tree.Id == nodeId: return tree
        pass
    return None

def formatNumber(num):
  if num % 1 == 0:
    return int(num)
  else:
    return num
  
def parse_weakness_breaks(wb_list : List[int]):
    weaknesses = {}
    if wb_list[0] != 0: weaknesses["Single Target"] = wb_list[0]
    if wb_list[1] != 0: weaknesses["AoE"] = wb_list[1]
    if wb_list[2] != 0: weaknesses["Blast"] = wb_list[2]
    return weaknesses

def parse_memosprite(data: dict):
    #data_memosprite = data["Memosprite"]
    memosprite: dict = {}
    #memosprite["Name"] = data["Memosprite"]["Name"]
    summoner_talent_id = data["Memosprite"]["HPSkill"]
    if summoner_talent_id == None: summoner_talent_id = data["Memosprite"]["SpeedSkill"]
    talent : dict = data["Skills"][str(summoner_talent_id)]
    l1_params, l6_params, l7_params = get_min_max_params(talent) #e.g. [60, 10]
    memosprite["BaseHP"] = parse_memosprite_value(data["Memosprite"]["HPBase"], l1_params, l6_params, l7_params)
    memosprite["BonusHP"] = parse_memosprite_value(data["Memosprite"]["HPInherit"], l1_params, l6_params, l7_params)+"%"
    memosprite["BaseSpeed"] = parse_memosprite_value(data["Memosprite"]["SpeedBase"], l1_params, l6_params, l7_params)
    memosprite["BonusSpeed"] = parse_memosprite_value(data["Memosprite"]["SpeedInherit"], l1_params, l6_params, l7_params)+"%"
    memosprite["Aggro"] = data["Memosprite"]["Aggro"]
    memosprite["Kit"] = {}
    mainskills(memosprite, data["Memosprite"])
    return memosprite, summoner_talent_id

def parse_memosprite_value(value: str, l1_params: List[float], max_params: List[float], whale_params: List[float] = None):
    if '#' in value:
        value = insert_numbers_into_place(value, l1_params, max_params, whale_params)
    return value

def add_params_to_desc(desc: str, l1_params : List[int | float], max_params : List[int | float] = None, whale_params : List[int | float] = None):
    try:
        words = desc.replace("<unbreak>", "</unbreak>").replace("\\n", " ").replace("<color=#f29e38ff>","").replace("</color>","").replace("<u>","").replace("</u>","").replace("\"", "'").split("</unbreak>")
        for i in range (len(words)):
            if "[" in words[i]:
                percent = "%" if "%" in words[i] else ""
                words[i] = insert_numbers_into_place(words[i], l1_params, max_params, whale_params) + percent
                # param_position = int(words[i].split("[")[0].split("#")[1])-1
                # if max_params == None or l1_params[param_position] == max_params[param_position]:
                #     words[i] = str(l1_params[param_position]) + percent
                # else:
                #     words[i] = f"[{l1_params[param_position]}|{max_params[param_position]}]{percent}"
        return "".join(words)
    except: 
        words = desc
        return ""
    
def insert_numbers_into_place(word: str, l1_params : List[int | float], max_params : List[int | float] = None, whale_params : List[int | float] = None):
    param_position = int(word.split("[")[0].split("#")[1])-1
    if max_params == None or l1_params[param_position] == max_params[param_position]:
        value = str(l1_params[param_position])
    elif whale_params == None:
        value = f"[{l1_params[param_position]}|{max_params[param_position]}]"
    else:
        value = f"[{l1_params[param_position]}|{max_params[param_position]}|{whale_params[param_position]}]"
    return value

def get_min_max_params(skill: dict, alreadyParsed: bool = False):
    #so far, "alreadyParsed" is only for Remembrance chars
    skill_description : str = skill[desc]
    levels : dict = skill["Level"]
    level1_params = parse_params(skill_description, levels["1"]["ParamList"], alreadyParsed)

    if "15" in levels.keys(): 
        levelmax_params = parse_params(skill_description, levels["10"]["ParamList"], alreadyParsed)
        whale_params = parse_params(skill_description, levels["12"]["ParamList"], alreadyParsed)
    elif "6" in levels.keys(): 
        levelmax_params = parse_params(skill_description, levels["6"]["ParamList"], alreadyParsed)
        whale_params = parse_params(skill_description, levels["7"]["ParamList"], alreadyParsed)
    else: 
        levelmax_params = None
        whale_params = None

    return level1_params, levelmax_params, whale_params
  
def uniqueSkills(my_data: dict, data: dict):
    uniqueSkills = data["Unique"]
    if uniqueSkills == {}: return
    counter = 1
    my_data["Kit"]["Unique"] = {}
    for skillnum in uniqueSkills:
        skill = uniqueSkills[skillnum]
        if len(uniqueSkills) == 1:
            skillPointer = my_data["Kit"]["Unique"]
        else:
            strCounter = str(counter)
            my_data["Kit"]["Unique"][strCounter] = {}
            skillPointer = my_data["Kit"]["Unique"][strCounter]
        #my_data["Kit"]["Unique"][strCounter] = {}
        #skillPointer["Name"] = skill["Name"] #my_data["Kit"]["Unique"][strCounter] 
        skillPointer[desc] = skill[desc] #my_data["Kit"]["Unique"][strCounter]
        skillPointer["Tag"] = skill["Tag"] #my_data["Kit"]["Unique"][strCounter]
        counter += 1

def mainskills(my_data : dict, data : dict, summonSkillNum : str = None):
     skills = data["Skills"]
     #reset_skill_occurrences()
     skill_counts = Skill_Counter()
     for skillnum in skills:
        skill = skills[skillnum]
        skill_type = skill_names[skill["Type"]] if skill["Type"] in skill_names else skill["Type"]
        skill_count = skill_counts.add_skill(skill_type)
        if skill_count > 1: skill_type = f"{skill_type} #{str(skill_count)}"

        my_data["Kit"][skill_type] = {}

        #skill_description : str = None if skill[desc] == None else skill[desc].replace("\\n", " ").replace("<color=#f29e38ff>","").replace("</color>","").replace("<u>","").replace("</u>","")

        #so far, skills are only parsed if needed to calculate Memosprite stats (Skill for RTB, Aglaea, Ult for Castorice)
        if summonSkillNum == skillnum: 
            skillAlreadyParsed = True
        else: skillAlreadyParsed = False

        level1_params, levelmax_params, whale_params = get_min_max_params(skill, skillAlreadyParsed)
        skill_description : str = skill[desc]
        # levels : dict = skill["Level"]
        # level1_params = parse_params(skill["Desc"], levels["1"]["ParamList"])
        
        # if "10" in levels.keys(): 
        #     levelmax_params = parse_params(skill["Desc"], levels["10"]["ParamList"])
        # elif "6" in levels.keys(): 
        #     levelmax_params = parse_params(skill["Desc"], levels["6"]["ParamList"])
        # else: levelmax_params = None

        if skill_description != None:
            new_desc = add_params_to_desc(skill_description, level1_params, levelmax_params, whale_params)
        else:
            new_desc = create_parameter_tuple_without_desc(level1_params, levelmax_params, whale_params)

        #my_data["Kit"][skill_type]["Name"] = skill["Name"]
        my_data["Kit"][skill_type][desc] = new_desc
        my_data["Kit"][skill_type]["Tag"] = skill["Tag"]
        energy = skill["SPBase"]
        if energy != None:
            my_data["Kit"][skill_type]["Energy"] = energy
        if skill["BPAdd"] == 1:
            my_data["Kit"][skill_type]["BP"] = 1
        elif skill["BPNeed"] == 1:
            my_data["Kit"][skill_type]["BP"] = -1
        weakness_break_types : List[int] = skill["ShowStanceList"]
        if weakness_break_types != [0,0,0]:
            my_data["Kit"][skill_type]["Weakness Break"] = parse_weakness_breaks(weakness_break_types) #single target, aoe, blast
     my_data["Kit"] = reorder_base_kit(my_data["Kit"])

def skilltrees(my_data : dict, data : dict):
    set_of_materials : set = set()
    skill_tree = data["SkillTrees"]
    for skill_in_tree in skill_tree:
        if skill_in_tree not in ["Point01", "Point02", "Point03", "Point04", "Point05", "Point19", "Point20"]:
            current_skill = skill_tree[skill_in_tree]
            skill = current_skill["1"]

        #  for i in range(6,19):
        #     if i < 10: id = "Point0"+str(i)
        #     else: id = "Point"+str(i)
        #     skill = data["SkillTrees"][id]["1"]
            pointId = skill["PointID"]

            my_data["SkillTrees"][pointId] = {}
            if skill_in_tree in ["Point06", "Point07", "Point08"]:
            #if i < 9:
                skill_description = skill["PointDesc"] #.replace("\\n", " ").replace("<color=#f29e38ff>","").replace("</color>","").replace("<u>","").replace("</u>","")
                if "ParamList" in skill:
                    trace_params = parse_params(skill["PointDesc"], skill["ParamList"])
                    new_desc = add_params_to_desc(skill_description, trace_params)
                    my_data["SkillTrees"][pointId][desc] = new_desc
                else:
                    my_data["SkillTrees"][pointId][desc] = skill_description
            else:
            #if i > 8: 
                my_data["SkillTrees"][pointId]["PointName"] = skill["PointName"]
                try:
                    my_data["SkillTrees"][pointId]["Status"] = skill["StatusAddList"][0]["Value"]
                except: pass
            prepoint : List[int] = skill["PrePoint"]
            my_data["SkillTrees"][pointId]["Requires"] = prepoint #prepoint

            for material in skill["MaterialList"]:
                set_of_materials.add(material["ItemID"])
            
    for material in data["Stats"]["5"]["Cost"]:
        set_of_materials.add(material["ItemID"])
        
    my_data["Materials"] = get_material_names(set_of_materials)
    try:
          my_data["Traces"] = skill_tree_rework(my_data)
          my_data.pop("SkillTrees")
    except:
         traceback.print_exc()

def eidolons(character_dict : dict, json_dict : dict):
    raw_eidolons = json_dict["Ranks"]
    #eidolon_list = []
    character_dict["Eidolons"] = {}
    for num in raw_eidolons:
        eidolon = raw_eidolons[num]
        e_num = eidolon["Id"] % 10
        description : str = eidolon[desc]
        parameters = eidolon[paramlist]
        if parameters == []:
            eidolon_dict : dict = {
                desc: description.replace("\\n", " ").replace("<color=#f29e38ff>","").replace("</color>","").replace("<u>","").replace("</u>","").replace("<unbreak>", "</unbreak>").replace("</unbreak>", "")
            }
        else:
            parse_params(description, parameters)
            new_desc = add_params_to_desc(description, parameters)
            eidolon_dict : dict = {
                desc: new_desc
            }
        character_dict["Eidolons"][str(e_num)] = eidolon_dict

#invalid
# def skill_tree_rework_faster(data : dict):
#     skilltrees = data["SkillTrees"]
#     better_tree = {}
#     tree_nodes : List[TreeNode] = []
#     trace_type = 1
#     major_trace = 2
#     for skilltree in skilltrees:
#         if skilltree in ["Point01", "Point02", "Point03", "Point04", "Point05"]: continue
#         root = True if skilltrees[skilltree]["1"]["PrePoint"] == [] else False
#         id = skilltrees[skilltree]["1"]["PointID"]
#         if skilltree not in ["Point06", "Point07", "Point08"]:
#             trace = skilltrees[skilltree]["1"]["PointName"]
#             if trace != None:
#                 if trace == "SPD Boost": 
#                     value = skilltrees[skilltree]["1"]["StatusAddList"][0]["Value"]
#                 else: 
#                     value = round(skilltrees[skilltree]["1"]["StatusAddList"][0]["Value"] * 100, 1)
#                 new_tree_node = TreeNode(id=id, root=root, trace=trace, value=value, children=None, params=None) #skilltrees[skilltree]["Unlocks"]
#                 pass
#         else:
#             if "PointDesc" in skilltrees[skilltree]["1"]: value = skilltrees[skilltree]["1"]["PointDesc"]
#             else: value = None
#             if "ParamList" in skilltrees[skilltree]["1"]: 
#                 params = skilltrees[skilltree]["1"]["ParamList"]
#             else: params = None
#             new_tree_node = TreeNode(id=skilltree, root=root, trace=f"A{str(major_trace)}", value=value, children=None, params=params) #skilltrees[skilltree]["Unlocks"]
#             major_trace += 2
#         new_tree_node["Point"] = skilltree

#         tree_nodes.append(new_tree_node)
#         pass
    
#     for node in tree_nodes:
#         if node.Root == False:
#             parent_node_id = skilltrees[node.Point]["1"]["PrePoint"][0]
#             parent = find_node(trees=tree_nodes, nodeId=parent_node_id)
#             if parent != None:
#                 parent.add_child(node)

#     for node in tree_nodes:
#         if node.Root:
#             better_tree[f"Branch {str(trace_type)}"] = node
#             trace_type += 1
#         pass
#     return better_tree