WEEKLY_BOSSES = 7
FIRST_WEEKLY_BOSS = 110501

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
TRACES = "Traces"
RELICS = "Relics"
UNLOCKS = "Unlocks"
PARAMLIST = "ParamList"
REQUIRES = "Requires"

def formatListLocation(location: str):
    return f"checkNewPages/{location}"

def formatDataLocation(fileName: str):
    return f"results/{fileName}"

def formatChangesLocation(fileName: str):
    return f"changes/{fileName}"