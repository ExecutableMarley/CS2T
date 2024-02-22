import time
import threading
import re
import enum

from GameUtility.cmd import CMD
from pathlib import Path


class UI_STATE(enum.Enum):
    UI_STATE_MAINMENU = 1
    UI_STATE_LOADING = 2
    UI_STATE_INGAME = 3
    CSGO_GAME_UI_STATE_PAUSEMENU = 4
    
    def getFromStr(string: str):
        if string == "CSGO_GAME_UI_STATE_MAINMENU":
            return UI_STATE.UI_STATE_MAINMENU
        elif string == "CSGO_GAME_UI_STATE_LOADINGSCREEN":
            return UI_STATE.UI_STATE_LOADING
        elif string == "CSGO_GAME_UI_STATE_INGAME":
            return UI_STATE.UI_STATE_INGAME
        elif string == "CSGO_GAME_UI_STATE_PAUSEMENU":
            return UI_STATE.CSGO_GAME_UI_STATE_PAUSEMENU
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
    
    playerListHeaderPattern = re.compile(r"\[Client\]\s+id\s+time\s+ping\s+loss\s+state\s+rate\s+name")
    playerListPattern = re.compile(
        r"\[Client\]\s+" # Match the [Client] tag
        r"(?P<id>\d{1,3})\s+" # Capture the id (1-3 digits)
        r"\d{1,2}:\d{2}\s+" # Match the time (2 digits:2 digits)
        r"\d+\s+" # Match the ping (Ignored)
        r"\d+\s+" # Match the loss (Ignored)
        r"\w+\s+" # Match the state (Ignored)
        r"\d+\s+" # Match the rate (Ignored)
        r"(?P<name>.+)" # Capture the name
        )
    
    def __init__(self, cmd: CMD = None):
        self.thread = None
        self.currentUIState = UI_STATE.UI_STATE_MAINMENU
        self.previousUIState = UI_STATE.UI_STATE_MAINMENU
        # Dictionary of players id: name
        self.playerDict = []
        self.isParsingPlayerList = False
        self.messageHandlers = []
        self.cmd = cmd
        
        if cmd:
            self.attach(cmd)
    
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
            string = self.cleanString(string)
            match = GameState.teamMessagePattern.match(string)
            if match:
                self.parseMessage(match.group("team"), match.group("name"), match.group("location"), match.group("message"))
                return
    
        match = GameState.playerListHeaderPattern.match(string)
        if match:
            self.isParsingPlayerList = True
            return
        
        # Parse player list
        if self.isParsingPlayerList:
            self.isParsingPlayerList = self.parsePlayerListFromString(string)
    
    def parsePlayerListFromString(self, string: str):
        if string.startswith("[Client] "):
            match = GameState.playerListPattern.match(string)
            if match:
                #self.playerList.append(match.group("name"))
                id = int(match.group("id"))
                if id > 0 and id < 64:
                    self.playerDict[id] = match.group("name")      
                return True
        return False
    
    def parseMessage(self, team, name, location, message):
        #print(f"[{team}] {name}: {location} {message}")
        for handler in self.messageHandlers:
            handler(team, name, location, message)

    def cleanString(self, string: str):
        #Delete \u200e
        string = string.replace('\u200e', '')
        #Replace "﹫" by "@"
        string = string.replace('﹫', '@')
        return string

    def attachMessageHandler(self, handler):
        self.messageHandlers.append(handler)

    def observe(self, observable):
        if isinstance(observable,CMD):
            self.parseFromString(observable.getLastLine())
    
    def attach(self, cmd: CMD):
        cmd.attach(self)      
      
    def getCurrentUIState(self):
        return self.currentUIState
    def getPreviousUIState(self):
        return self.previousUIState
    
    def write_team_message(self, rawMessage: str):
        if self.cmd:
            self.cmd.write_teamchat(rawMessage)
    def write_all_message(self, rawMessage: str):
        if self.cmd:
            self.cmd.write_allchat(rawMessage)