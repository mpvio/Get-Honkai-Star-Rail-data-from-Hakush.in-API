from pyHakushinParsing.character_funcs import add_params_to_desc
import pyUi.hakushin_reader_ui as h
import pyHakushinParsing.constants as c

# test srtools
import pyFileIO.srToolsData as s

def main(): #args
    c.createAllFoldersAndTextFiles()
    h.start_up()

def srtoolsTest():
    currentVersion = s.getCurrentVersion()
    textmap = s.getTextMaps(currentVersion)
    data = s.getAllData(currentVersion)
    testIds = ["1407", "1005", "129", "326", "23056"]
    characters, lightcones, relicSets = s.sortData(testIds)
    charKits = s.getBasicKits(characters, data["avatars"])
    lcKits = s.getBasicKits(lightcones, data["lightcones"])
    relicKits = s.getBasicKits(relicSets, data["relic-sets"])
    s.handleCharacters(charKits, textmap)
    s.handleLightCones(lcKits, textmap)
    s.handleRelics(relicKits, textmap)

if __name__ == "__main__":
    main() #sys.argv[1:] #first arg is always file name, so skip it
    # srtoolsTest()