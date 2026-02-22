import sys

from pyHakushinParsing.character_funcs import add_params_to_desc
import pyUi.hakushin_reader_ui as h
import pyHakushinParsing.constants as c

# test srtools
import pyFileIO.srToolsData as s

def main(): #args
    c.createAllFoldersAndTextFiles()
    h.start_up()

def getInputs() -> list[str]:
    user_input = input("Enter ids separated by spaces: ").strip()
    if not user_input:
        return []
    return user_input.split()


def srtoolsTest(args: list[str]):
    currentVersion = s.getCurrentVersion()
    textmap = s.getTextMaps(currentVersion)
    data = s.getAllData(currentVersion)
    s.getNamesLists(data, textmap)
    if args: inputs = args
    else: 
        inputs = getInputs()
        if inputs == []:
            inputs = c.get_shortlist()
    characters, lightcones, relicSets = s.sortData(inputs)
    if len(characters) != 0:
        charKits = s.getBasicKits(characters, data["avatars"])
        s.handleCharacters(charKits, textmap)
    if len(lightcones) != 0:
        lcKits = s.getBasicKits(lightcones, data["lightcones"])
        s.handleLightCones(lcKits, textmap)
    if len(relicSets) != 0:
        relicKits = s.getBasicKits(relicSets, data["relic-sets"])
        s.handleRelics(relicKits, textmap)

if __name__ == "__main__":
    srtoolsTest(sys.argv[1:]) #first arg is always file name, so skip it