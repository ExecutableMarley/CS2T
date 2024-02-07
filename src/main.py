import time
import threading
import re

from pathlib import Path

def getFileReader(file: File) -> str:
    file.seek(0,2) # Go to the end of the file
    while True:
        line = file.readline()
        if not line:
            time.sleep(1) # Sleep briefly
            continue
        yield line

def writeConfigFile(csgoPath: Path):
    file = open(csgoPath.joinpath("cfg/tracker.cfg"), "w")
    
    if not file.writable():
        raise Exception("Failed to open tracker.cfg config file for writing")
    
    #con_logfile console.log
    file.write("con_logfile \"console.log\" \n")
    #alias update "status; echo 'Updated'"
    file.write("alias update \"status; echo 'Updated'\"\n")
    #status
    file.write("status\n")
    
    file.write("echo Damage Tracker Loaded!\n")
    file.write("echo https://github.com/ExecutableMarley/\n")
    
    file.close()

class UI_STATE(Enum):
    UI_STATE_MAINMENU = 1
    UI_STATE_LOADING = 2
    UI_STATE_INGAME = 3

class GameState:
    
    logFilePath: Path = ""
    
    statePattern = re.compile(r"ChangeGameUIState: (\w+) -> (\w+)")
    
    def GameState(self):
        self.thread = None
        self.currentUIState = UI_STATE.UI_STATE_MAINMENU
        self.previousUIState = UI_STATE.UI_STATE_MAINMENU
    
    def start(self):
        self.thread = threading.Thread(target=self.run)
    
    def run(self):
        
        file = open(GameState.logFilePath, "r", encoding="utf-8")
        
        fileReader = getFileReader()
        
        
        while True:
            nextLine = next(fileReader)
            
    def parseFromString(self, string: str):
        #ChangeGameUIState: <PreviousUiState> -> <CurrentUiState>
        #match = re.search(r"ChangeGameUIState: (\w+) -> (\w+)", string)
        match = GameState.statePattern.match(string)
        if match:
            self.previousUIState = match.group(1)
            self.currentUIState = match.group(2)









