import time
import threading

from ConsoleInterface.CMD import CMD
import GameState as GameState

from pathlib import Path
from deep_translator import GoogleTranslator

output = GoogleTranslator(source='auto', target='en').translate('Hola Mundo')

print(output)

class Message:
    def __init__(self, team, name, location, message):
        self.team = team
        self.name:str = name
        self.location = location
        self.message:str = message
        
    def __str__(self):
        return f"[{self.team}] {self.name}: {self.location} {self.message}"
    
    def smallStr(self):
        return f"[{self.team}] {self.name}: {self.message}"

class Translator:   
    def __init__(self, gameState: GameState.GameState):
        self.gameState: GameState.GameState = gameState
        self.targetLanguage = 'en'
        self.messageQueue = []
    
        self.gameState.attachMessageHandler(self.addMessage)

        threading.Thread(target=self.run).start()
    
    def run(self):    
        while True:
            if len(self.messageQueue) > 0:
                message: Message = self.messageQueue.pop(0)
                
                if not message.message.startswith("[Translated]"):
                    self.processMessage(message)
            else:
                time.sleep(1)
    
    def addMessage(self, team, name, location, message):
        self.messageQueue.append(Message(team, name, location, message))
    
    def processMessage(self, message):
        print(message.smallStr())        
        translated = self.translate(message.message)
        print("[Translated] " + translated)
        self.gameState.write_team_message("[Translated] " + translated)
    
    def translate(self, text: str) -> str:
        return GoogleTranslator(source='auto', target=self.targetLanguage).translate(text)
    
    def setTargetLanguage(self, targetLanguage: str):
        self.targetLanguage = targetLanguage
        

if __name__ == "__main__":
    
    csgoPath = Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/")
    
    cmd = CMD(csgoPath)
    cmd.start()
    
    gameState = GameState.GameState(cmd)
    
    translator = Translator(gameState)
    
    