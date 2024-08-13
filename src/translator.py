import time
import threading
import re

from GameUtility.game_cmd import CMD
from GameUtility.game_state import GameState

from pathlib import Path
from deep_translator import GoogleTranslator
from googletrans import Translator as GoogleTranslator2

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
    def __init__(self, team, name, location, message, translatedMessage, src = None, dest = None):
        super().__init__(team, name, location, message)
        self.translatedMessage:str = translatedMessage
        self.src = src
        self.dest = dest
    
    def isTranslationDifferent(self):
        if self.dest == None or self.src == None:
            self.translatedMessage != self.message
        else:
            return self.dest != self.src
    
    def smallStr(self):
        return f"[{self.team}] {self.name}: {self.message}\nTranslated: {self.translatedMessage}"
    
    def __str__(self):
        return self.smallStr()
    
    def hasTranslation(self):
        return self.translatedMessage != None
    
    def getTranslation(self):
        if self.src == None or self.dest == None:
            return f"[Translated] {self.name}: {self.translatedMessage}"
        else:
            return f"[{self.src} -> {self.dest}] {self.name}: {self.translatedMessage}"
    
    #[Statics]
    
    def fromMessage(message: Message, translatedMessage: str, src = None, dest = None):
        return TranslatedMessage(message.team, message.name, message.location, message.message, translatedMessage, src, dest)

class Translator:
    
    languageCodes = ['en', 'de', 'es', 'fr', 'it', 'nl', 'pl', 'pt', 'ru', 
                     'ja', 'ko', 'tur', 'sv', 'no', 'da', 'fi']
    
    isTranslatedPattern = re.compile(r"^\[(Translated|\w+ -> \w+)\]")
    
    def __init__(self, gameState: GameState):
        self.gameState: GameState = gameState
        self.targetLanguage = 'en'
        self.messageQueue = []
        self.outputTranslatedMessages = True
        self.onlyOutputToTeam = False
    
        self.gameState.attachMessageHandler(self.addMessage)

        threading.Thread(target=self.run).start()
    
    def run(self):
        while True:
            if len(self.messageQueue) > 0:
                message: Message = self.messageQueue.pop(0)
                
                if len(message.message) > 4 and message.message.startswith("[") and message.message[3] == "]":
                    self.processMessageCommand(message)
                elif not self.isTranslatedPattern.match(message.message):
                    self.processMessage(message)
            else:
                time.sleep(1)
    
    def addMessage(self, team, name, location, message):
        self.messageQueue.append(Message(team, name, location, message))
    
    def processMessage(self, message: Message):
        
        print(message.smallStr())
        
        translatedMessage = self.translate(message)
        if translatedMessage.hasTranslation() and translatedMessage.isTranslationDifferent():
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
        
        #Create a copy of the message without the language code
        messageCopy = Message(message.team, message.name, message.location, message.message[4:])
        
        translatedMessage = self.translateTo(messageCopy, languageCode)
        if translatedMessage.hasTranslation() and translatedMessage.isTranslationDifferent():
            print(f"[{languageCode}] {translatedMessage.getTranslation()}")
            if self.outputTranslatedMessages:
                self.writeMessageTranslation(translatedMessage)
    
    def translate(self, message: Message) -> TranslatedMessage:
        translator = GoogleTranslator2()
        
        translated = translator.translate(message.message, dest=self.targetLanguage)
        return TranslatedMessage.fromMessage(message, translated.text, src=translated.src, dest=translated.dest)
    
    def translateTo(self, message: Message, targetLanguage: str) -> TranslatedMessage:
        translator = GoogleTranslator2()
        
        translated = translator.translate(message.message, dest=targetLanguage)
        return TranslatedMessage.fromMessage(message, translated.text, src=translated.src, dest=translated.dest)
    
    def setTargetLanguage(self, targetLanguage: str):
        self.targetLanguage = targetLanguage
    
    def writeMessageTranslation(self, translatedMessage: TranslatedMessage):
        if translatedMessage.hasTranslation() and translatedMessage.isTranslationDifferent() and translatedMessage.src in Translator.languageCodes:
            if self.onlyOutputToTeam or translatedMessage.team != "ALL":
                self.gameState.write_team_message(translatedMessage.getTranslation())
            else:
                self.gameState.write_all_message(translatedMessage.getTranslation())
        

if __name__ == "__main__":
    
    csgoPath = Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/")
    
    cmd = CMD(csgoPath)
    
    gameState = GameState(cmd)
    
    translator = Translator(gameState)
    
    