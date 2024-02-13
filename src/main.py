import time
import threading
import re
import enum

from ConsoleInterface.CMD import CMD
from pathlib import Path


class UI_STATE(enum.Enum):
    UI_STATE_MAINMENU = 1
    UI_STATE_LOADING = 2
    UI_STATE_INGAME = 3

    def getFromStr(string: str):
        if string == "CSGO_GAME_UI_STATE_MAINMENU":
            return UI_STATE.UI_STATE_MAINMENU
        elif string == "CSGO_GAME_UI_STATE_LOADINGSCREEN":
            return UI_STATE.UI_STATE_LOADING
        elif string == "CSGO_GAME_UI_STATE_INGAME":
            return UI_STATE.UI_STATE_INGAME
        raise Exception("Invalid UI_STATE string")

class GameState:
    
    statePattern = re.compile(r"ChangeGameUIState: (\w+) -> (\w+)")
    
    teamMessagePattern = re.compile(
        # Capture the team
        r"\s*\[(?P<team>ALL|T|CT)\]\s*"  
        # Capture the name, stop at brackets, colon, and @
        r"(?P<name>[^\[\]:@]+?)"  
        # Optionally capture the location
        r"(?:\@(?P<location>[^:\[\]]+))?"
        # Optionally match the [DEAD] tag  
        r"(?:\s*\[DEAD\])?"
        # Capture the message following the colon
        r":\s*(?P<message>.*)"  
        )
    
    def __init__(self):
        self.thread = None
        self.currentUIState = UI_STATE.UI_STATE_MAINMENU
        self.previousUIState = UI_STATE.UI_STATE_MAINMENU
    
    def start(self):
        self.thread = threading.Thread(target=self.run)
    
    def run(self):
        pass
            
    def parseFromString(self, string: str):
        #ChangeGameUIState: <PreviousUiState> -> <CurrentUiState>
        match = GameState.statePattern.match(string)
        if match:
            self.previousUIState = UI_STATE.getFromStr(match.group(1))
            self.currentUIState  = UI_STATE.getFromStr(match.group(2))
            return
            
        # [T] <name>@<location>: <message>
        # [CT] <name>@<location>: <message>
        # [ALL] <name>: <message>
        if string.startswith(" [ALL] ") or string.startswith(" [T] ") or string.startswith(" [CT] "):
            match = GameState.teamMessagePattern.match(string)
            if match:
                self.parseMessage(match.group("team"), match.group("name"), match.group("location"), match.group("message"))
                return
    
    def parsePlayerListFromString(self, string: str):
        pass    
    
    def parseMessage(team, name, location, message):
        pass

    def observe(self, observable):
        if observable == CMD:
            self.parseFromString(CMD.lastLine)
            
    def getCurrentUIState(self):
        return self.currentUIState
    def getPreviousUIState(self):
        return self.previousUIState




if __name__ == "__main__":
    
    csgoPath = Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/")
    
    cmd = CMD(csgoPath)
    
    cmd.start()
    

