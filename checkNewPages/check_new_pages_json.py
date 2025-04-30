#check new pages json
import json
import sys
from typing import List
import requests
from fileIO.extra_classes_and_funcs import read_from_file
from hakushinParsing import hakushin_json_fetcher as hf, constants as c
import bisect

def getAll(type : str, via_ui = False):
	req_string = f"https://api.hakush.in/hsr/data/{type}.json"
	response = requests.get(req_string)
	if response.status_code == 200:
		data : dict = response.json()
		items: dict = {}
		for key in data:
			charName = data[key]['en']
			items[key] = "Trailblazer" if charName == "{NICKNAME}" else charName
		return compare_lists(type, items, via_ui)
	else:
		return {}
	
def compareOneItem(page: str, items: dict):
	pageName = f"__{page}.json"
	old_list = json.loads(read_from_file(c.formatListLocation(pageName)))
	differences = {id:name for id,name in items.items() if id not in old_list}
	if differences != {}:
		write_items_to_file(c.formatListLocation(f"__manual{pageName}"), differences)
		for diff in differences:
			bisect.insort(old_list, diff)
		write_items_to_file(pageName, old_list)

def compareListsToManualInput(items: List[str]):
	chars : List[str] = []
	cones : List[str] = []
	relics : List[str] = []
	for item in items:
		match len(item):
			case 3: relics.append(item)
			case 4: chars.append(item)
			case 5: cones.append(item)
	if chars != []: updateListsForManualInputs("character", chars)
	if cones != []: updateListsForManualInputs("lightcone", chars)
	if relics != []: updateListsForManualInputs("relicset", chars)

def updateListsForManualInputs(page : str, items: List[str]):
	pageName = f"__{page}.json"
	old_list: dict = json.loads(read_from_file(c.formatListLocation(pageName)))
	differences = {id for id in items if id not in old_list}
	if differences != {}:
		getAll(page, True)
		manualUpdatesFileName = c.formatListLocation(f"__manualUpdates.txt")
		try:
			with open(manualUpdatesFileName, 'a+', encoding="UTF-8") as file:
				tempList: List[str] = []
				while line := file.readline():
					tempList.append(line.strip())
				for diff in differences:
					if tempList.__contains__(diff) == False: file.write(f"{diff}\n")
		except: pass

def compare_lists(page: str, items: dict, via_ui = False):
	pageName = f"__{page}.json"
	pageLocation = c.formatListLocation(pageName)
	old_list = read_from_file(pageLocation)
	if old_list == '':
		write_items_to_file(pageLocation, items)
		return items
	else:
		old_as_json = json.loads(old_list)
		differences = {id:name for id,name in items.items() if id not in old_as_json}
		if differences != {}:
			write_items_to_file(c.formatListLocation(f"__new{pageName}"), differences)
			write_items_to_file(pageLocation, items)
			if not via_ui:
				check_haku = input("Check new items on Hakush.in?: ")
				if check_haku not in ["n", "N"]: 
					return hf.main(differences)
		return differences
		
def write_items_to_file(page, items):
		newFile = open(page, "w+", encoding="utf8")
		json.dump(items, newFile, indent=4, ensure_ascii=False)
		newFile.close()
          
def readShortlist(page):
	entries = []
	try:
		with open(f"{page}.txt", 'r', encoding='UTF-8') as file:
			while line := file.readline():
				entries.append(line.strip())
	except:
		pass
	return entries

# def list_diffs(old_list, new_list):
# 	diffs = list(set(new_list).difference(old_list))
# 	return diffs

# def compare_lists(page, item_ids, via_ui = False):
# 	old_list = read_items_from_file(page)
# 	diffs = list_diffs(old_list, item_ids)
# 	if not diffs: 
# 		#print(f"No changes in {page} page.")
# 		return []
# 	else:
# 		#print(f"Change(s) to {page} page: {diffs}")
# 		write_items_to_file(f"new_{page}", diffs)
# 		write_items_to_file(page, item_ids)
# 		if not via_ui:
# 			check_haku = input("Check new items on Hakush.in?: ")
# 			if check_haku not in ["n", "N"]: 
# 				return hf.main(diffs)
# 			else: return diffs
# 		else: return diffs

# def manual_add_id(item_id: str):
# 	if len(item_id) == 3: page = "__relicset.json"
# 	elif len(item_id) == 4: page = "__character.json"
# 	else: page = "__lightcone.json"
# 	items = read_items_from_file(page)
# 	if items.__contains__(item_id) == False:
# 		bisect.insort(items, item_id)
# 		write_items_to_file(page, items)
# 		write_items_to_file(f"__manual_{page}", [item_id])


url_map = {
	0: "character",
	1: "relicset",
	2: "lightcone",
	"c": "character",
	"r": "relicset",
	"l": "lightcone",
	"character": "character",
	"relicset": "relicset",
	"lightcone": "lightcone"
}

def selector(args, via_ui=False):
	result = {}
	if len(args) < 1:
		args = [url_map[x] for x in range (3)]
	for arg in args:
		arg = url_map[arg] if arg in url_map else arg
		results_temp = getAll(arg, via_ui)
		if results_temp != None:
			result.update(results_temp)
			#result = [*result, *results_temp]
	return result

if __name__ == "__main__":
    selector(sys.argv[1:]) #first arg is always file name, so skip it