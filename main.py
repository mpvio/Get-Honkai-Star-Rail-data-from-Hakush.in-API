import pyUi.hakushin_reader_ui as h
import pyHakushinParsing.constants as c
# import pyUi.hakushinUIv2 as h2

def main(): #args
    c.createAllFolders()
    h.start_up()

if __name__ == "__main__":
    main() #sys.argv[1:] #first arg is always file name, so skip it