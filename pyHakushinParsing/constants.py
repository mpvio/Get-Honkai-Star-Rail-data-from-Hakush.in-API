from datetime import datetime
import os
import pathlib

WEEKLY_BOSSES = 7
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

def createAllFoldersAndTextFiles():
    # define seven directories (with parents)
    folders = ["_all_lists/updates"]
    for word in [CHARACTER, LIGHTCONE, RELICSET]:
        folders.append(f"_results/{word}")
        folders.append(f"_changes/{word}")
    # create them if they don't already exist
    for folder in folders:
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
    # create shortlist and blacklist if they don't exist already
    for txtFile in [shortlist, blacklist]:
        file = pathlib.Path(f"{txtFile}.txt")
        if not file.exists(): file.touch()
    # TODO: automatically fetch character/ lightcone/ relicset jsons if they don't already exist?
    # create empty files and write to them to create update files?
              

def formatListLocation(location: str):
    return f"_all_lists/{location}"

def formatListChangesLocation(location: str):
    return f"_all_lists/updates/{location}"

def formatDataLocation(fileName: str):
    return f"_results/{fileName}"

def formatChangesLocation(fileName: str):
    return f"_changes/{fileName}"

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