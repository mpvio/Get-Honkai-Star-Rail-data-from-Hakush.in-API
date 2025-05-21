WEEKLY_BOSSES = 7
FIRST_WEEKLY_BOSS = 110501

def formatListLocation(location: str):
    return f"checkNewPages/{location}"

def formatDataLocation(fileName: str):
    return f"results/{fileName}"

def formatChangesLocation(fileName: str):
    return f"changes/{fileName}"