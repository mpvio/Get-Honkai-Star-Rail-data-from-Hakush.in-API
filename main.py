import pyUi.hakushin_reader_ui as h
import pyHakushinParsing.constants as c

def main(): #args
    c.createAllFoldersAndTextFiles()
    h.start_up()

if __name__ == "__main__":
    main() #sys.argv[1:] #first arg is always file name, so skip it