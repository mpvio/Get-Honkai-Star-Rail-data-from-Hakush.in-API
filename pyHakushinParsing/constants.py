from datetime import datetime
import os
import pathlib

WEEKLY_BOSSES = 7 # TODO: move to file to allow user input
FIRST_WEEKLY_BOSS = 110501

#types of items
CHARACTER = "character"
LIGHTCONE = "lightcone"
RELICSET = "relicset"

# args of these lengths need relicset data
NEEDRELICS = [4, 5]

#dict keys:
NAME = "Name"
RARITY = "Rarity"
PATH = "Path"
DESC = "Desc"
STATS = "Stats"
MEMOSPRITE = "Memosprite"
MATERIALS = "Materials"
MINOR_TRACES = "Minor Traces"
TRACE = "Trace"
TRACE_TREE = "Trace Tree"
RELICS = "Relics"
UNLOCKS = "Unlocks"
PARAMLIST = "ParamList"
REQUIRES = "Requires"
EXTRA = "Extra"

# list names
shortlist = "shortlist"
blacklist = "blacklist"

# folder names
all_lists = "_all_lists/"
updates = "updates"
results = "_results/"
changes = "_changes/"

# other file names
weeklies = "weekly bosses.txt"

def createAllFoldersAndTextFiles():
    # define seven directories (with parents)
    folders = [f"{all_lists}{updates}"]
    for word in [CHARACTER, LIGHTCONE, RELICSET]:
        folders.append(f"{results}{word}")
        folders.append(f"{changes}{word}")
    # create them if they don't already exist
    for folder in folders:
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    # create shortlist and blacklist if they don't exist already
    for txtFile in [shortlist, blacklist]:
        file = pathlib.Path(f"{txtFile}.txt")
        if not file.exists(): file.touch()
    # create empty json files for character/ lightcone/ relicset if they don't already exist
    for word in [CHARACTER, LIGHTCONE, RELICSET]:
        path = f"{all_lists}{word}.json"
        file = pathlib.Path(path)
        if not file.exists():
            from pyCheckNewPages.check_new_pages_json import write_items_to_file
            emptyDict = {}
            write_items_to_file(path, emptyDict)
    # load or create weekly bosses tracker
    file = pathlib.Path(weeklies)
    if file.exists(): setWeekliesViaFile() # update constant value based on txt file
    else: writeToWeekliesFile(0) # assume a new user hasn't done any of the weekly bosses yet

def writeToWeekliesFile(weeklies_done: int):
    with open(weeklies, "w") as file:
        file.write(str(weeklies_done))

def setWeekliesViaFile():
    with open(weeklies, "r") as file:
        res = file.readline()
        if res and res != "":
            val = int(res)
        else:
            val = 0 # assume 0 if file is empty
        updateWeekliesViaInt(val)
        return val
    return 0 # assume no weekly bosses done if file reading error

# separated for potential future use
def updateWeekliesViaInt(val: int):
    global WEEKLY_BOSSES
    WEEKLY_BOSSES = val

def formatListLocation(location: str):
    return f"{all_lists}{location}"

def formatListChangesLocation(location: str):
    return f"{all_lists}{updates}/{location}"

def formatDataLocation(fileName: str):
    return f"{results}{fileName}"

def formatChangesLocation(fileName: str):
    return f"{changes}{fileName}"

def dynamicFileName(name: str, change: bool) -> str:
    date = datetime.today().strftime('%y-%m-%d')
    filename = f"{name} {date}"
    ext = ".json"
    if change:
        title = formatChangesLocation(filename)
    else:
        title = formatListChangesLocation(filename)
    counter = 1
    path = title+ext

    while os.path.exists(path):
        path = title+" ("+str(counter)+")"+ext
        counter += 1
    
    return path

# read txt files
def readList(page) -> list[str]:
	entries = []
	try:
		with open(f"{page}.txt", 'r', encoding='UTF-8') as file:
			while line := file.readline():
				entries.append(line.strip())
	except Exception as e:
		print(e)
	return entries

def get_shortlist() -> list[str]:
    return readList("shortlist")

def get_blackList() -> list[str]:
    return readList("blacklist")

def writeTxtList(page: str, content: list[str]):
    try:
        with open(f"{page}.txt", "w", encoding="UTF-8") as file:
            file.writelines(content)
    except Exception as e:
         print(e)