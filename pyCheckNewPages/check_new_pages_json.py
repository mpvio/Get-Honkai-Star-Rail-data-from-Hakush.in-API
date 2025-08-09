#check new pages json
from datetime import datetime
import json
import sys
from typing import List
from pyFileIO.extra_classes_and_funcs import convertCharToBetterName, getAllItems
from pyFileIO.fileReadWriteFuncs import read_from_file
from pyHakushinParsing import hakushin_json_fetcher as hf, constants as c
import bisect

character = "character"
lightcone = "lightcone"
relicset = "relicset"

def getAll(type : str, via_ui = False):
	data: dict = getAllItems(type)
	items: dict = {}
	for key in data:
		charName = data[key]['en']
		betterName = convertCharToBetterName(key)
		items[key] = betterName if betterName else charName
	return compare_lists(type, items, via_ui)
	
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
	if chars != []: updateListsForManualInputs(character, chars)
	if cones != []: updateListsForManualInputs(lightcone, chars)
	if relics != []: updateListsForManualInputs(relicset, chars)

characterList : dict = {}
relicList : dict = {}
lightconeList : dict = {}

def getOldList(page: str):
	if page == character:
		global characterList
		current : dict = characterList
	elif page == lightcone:
		global lightconeList
		current : dict  = lightconeList
	else:
		global relicList
		current : dict  = relicList
	pageName = f"__{page}.json"	
	if current == {}:
		current = json.loads(read_from_file(c.formatListLocation(pageName)))
	return current


def updateListsForManualInputs(page : str, items: List[str]):
	#pageName = f"__{page}.json"
	old_list: dict = getOldList(page)
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
			date = datetime.today().strftime('%y-%m-%d')
			write_items_to_file(c.formatListLocation(f"__new__{page} {date}.json"), differences)
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
          
def readList(page):
	entries = []
	try:
		with open(f"{page}.txt", 'r', encoding='UTF-8') as file:
			while line := file.readline():
				entries.append(line.strip())
	except Exception as e:
		print(e)
	return entries

URL_MAP = {
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
		args = [URL_MAP[x] for x in range (3)]
	for arg in args:
		arg = URL_MAP[arg] if arg in URL_MAP else arg
		results_temp = getAll(arg, via_ui)
		if results_temp != None:
			result.update(results_temp)
			#result = [*result, *results_temp]
	return result

if __name__ == "__main__":
    selector(sys.argv[1:]) #first arg is always file name, so skip it