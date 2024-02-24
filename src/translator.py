import time
import threading
import re

from GameUtility.game_cmd import CMD
from GameUtility.game_state import GameState

from pathlib import Path
from deep_translator import GoogleTranslator

class Message:
    def __init__(self, team, name, location, message):
        self.team:str     = team
        self.name:str     = name
        self.location:str = location
        self.message:str  = message
        
    def smallStr(self):
        return f"[{self.team}] {self.name}: {self.message}"
    
    def __str__(self):
        return self.smallStr()

class TranslatedMessage(Message):
    def __init__(self, team, name, location, message, translatedMessage):
        super().__init__(team, name, location, message)
        self.translatedMessage:str = translatedMessage
    
    def smallStr(self):
        return f"[{self.team}] {self.name}: {self.message}\nTranslated: {self.translatedMessage}"
    
    def __str__(self):
        return self.smallStr()
    
    def hasTranslation(self):
        return self.translatedMessage != None
    
    def isTranslationDifferent(self):
        return self.translatedMessage != self.message
    
    def getTranslation(self):
        return f"[Translated] {self.name}: {self.translatedMessage}"
    
    #[Statics]
    
    def fromMessage(message: Message, translatedMessage: str):
        return TranslatedMessage(message.team, message.name, message.location, message.message, translatedMessage)

class Translator:
    
    languageCodes = ['en', 'de', 'es', 'fr', 'it', 'nl', 'pl', 'pt', 'ru', 
                     'zh', 'ja', 'ko', 'tur', 'sv', 'no', 'da', 'fi']
    
    def __init__(self, gameState: GameState):
        self.gameState: GameState = gameState
        self.targetLanguage = 'en'
        self.messageQueue = []
        self.outputTranslatedMessages = True
        self.onlyOutputToTeam = True
    
        self.gameState.attachMessageHandler(self.addMessage)

        threading.Thread(target=self.run).start()
    
    def run(self):
        while True:
            if len(self.messageQueue) > 0:
                message: Message = self.messageQueue.pop(0)
                
                if message.message.startswith("[") and message.message[3] == "]":
                    self.processMessageCommand(message)
                elif not message.message.startswith("[Translated]"):
                    self.processMessage(message)
            else:
                time.sleep(1)
    
    def addMessage(self, team, name, location, message):
        self.messageQueue.append(Message(team, name, location, message))
    
    def processMessage(self, message: Message):
        
        print(message.smallStr())
        
        translatedMessage = TranslatedMessage.fromMessage(message, self.translate(message.message))
        if translatedMessage.hasTranslation():
            print(translatedMessage.getTranslation())
            if self.outputTranslatedMessages:
                self.writeMessageTranslation(translatedMessage)
            
    def processMessageCommand(self, message: Message):
        
        print(message.smallStr())
        #[<languageCode>] message
        languageCode = message.message[1:3].lower()
        
        #Check if language code is valid
        if languageCode not in Translator.languageCodes:
            return
        
        translatedMessage = TranslatedMessage.fromMessage(message, self.translateTo(message.message[4:], languageCode))
        if translatedMessage.hasTranslation():
            print(f"[{languageCode}] {translatedMessage.getTranslation()}")
            if self.outputTranslatedMessages:
                self.writeMessageTranslation(translatedMessage)
    
    def translate(self, text: str) -> str:
        return GoogleTranslator(source='auto', target=self.targetLanguage).translate(text)
    
    def translateTo(self, text: str, targetLanguage: str) -> str:
        return GoogleTranslator(source='auto', target=targetLanguage).translate(text)
    
    def setTargetLanguage(self, targetLanguage: str):
        self.targetLanguage = targetLanguage
    
    def writeMessageTranslation(self, translatedMessage: TranslatedMessage):
        if translatedMessage.hasTranslation() and translatedMessage.isTranslationDifferent():
            if self.onlyOutputToTeam or translatedMessage.team != "ALL":
                self.gameState.write_team_message(translatedMessage.getTranslation())
            else:
                self.gameState.write_all_message(translatedMessage.getTranslation())
        

if __name__ == "__main__":
    
    csgoPath = Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/")
    
    cmd = CMD(csgoPath)
    cmd.start()
    
    gameState = GameState(cmd)
    
    translator = Translator(gameState)
    
    