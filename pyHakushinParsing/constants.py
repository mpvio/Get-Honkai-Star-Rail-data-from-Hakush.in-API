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

def formatListLocation(location: str):
    return f"_all_lists/{location}"

def formatDataLocation(fileName: str):
    return f"_results/{fileName}"

def formatChangesLocation(fileName: str):
    return f"_changes/{fileName}"