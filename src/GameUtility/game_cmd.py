import os
import platform
import time
import threading
import re
import pyautogui

from pathlib import Path
try:
    from os_helpers import isMouseCursorVisible, getForegroundWindow
except ModuleNotFoundError:
    from GameUtility.os_helpers import isMouseCursorVisible, getForegroundWindow
    
    
    
#Os specific Imports
os_name = platform.system()
if os_name == "Windows":
    pass
elif os_name == "Linux":
    pass

class Observable:
    def __init__(self):
        self._observers: list = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier = None):
        for observer in self._observers:
            if observer != modifier:
                observer.observe(self)


def getFileReader(file):
    file.seek(0,2) # Go to the end of the file
    while True:
        line = file.readline()
        if not line:
            time.sleep(1) # Sleep briefly
            continue
        yield line

class Command:
    def __init__(self, command: str, timeOutSeconds: int = 60):
        self.command = command
        self.timeOutSeconds = timeOutSeconds
        self.creationTime = time.time()
    
    def get(self) -> str:
        return self.command
    
    def isTimedOut(self) -> bool:
        return time.time() - self.creationTime > self.timeOutSeconds

class CMD(Observable):
    
    def __init__(self, rootPath: Path):
        Observable.__init__(self)
        self.rootPath:     Path = rootPath
        self.configPath:   Path = rootPath.joinpath("game/csgo/cfg/")
        self.logFilePath:  Path = rootPath.joinpath("game/csgo/console.log")
        self.thread: threading.Thread = None
        self.session_key = "123"
        self.is_attached = False
        self.lastLine: str = ""
        self.commandQueue: list = []

        if not self.rootPath.is_dir():
            raise Exception("Root Path is not a directory")
        if not self.configPath.is_dir():
            raise Exception("Config Path is not a directory")


    def __del__(self):
        #Delete Config
        if self.configPath.joinpath("cmd.cfg").is_file():
            os.remove(self.configPath.joinpath("cmd.cfg"))

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        
        threading.Thread(target=self._outputThread).start()

    def run(self):
        # Write "attach" Config
        self._writeAttachConfigFile()

        # Wait for debug.log file is created
        while not self.logFilePath.is_file():
            time.sleep(1)

        file = open(self.logFilePath, "r", encoding="utf-8")
        if not file.readable():
            raise Exception("Console Log File was not readable")

        fileReader = getFileReader(file)

        print("[CMD] Waiting for CSGO to exec...")

        # Wait until config is executed
        # + Verify Session Key
        sessionKeyPattern = re.compile(r".*SessionKey : \[(\w+)\]")
        while not self.is_attached:
            line = next(fileReader)
            #Compare keys
            if sessionKeyPattern.match(line) and sessionKeyPattern.match(line).group(1) == self.session_key:
                self.is_attached = True
            time.sleep(1)

        print("[CMD] Attached to CSGO")

        dateTimePattern = r"^\d{2}/\d{2} \d{2}:\d{2}:\d{2} "
        while True:
            curLine:str = next(fileReader)
            
            curLine = re.sub(dateTimePattern, '', curLine)
            
            #print(curLine)
            
            if True:
                self.lastLine = curLine
                self.notify()

            #time.sleep(1)
    
    def _outputThread(self):
        while True:
            if self.is_input_possible() and len(self.commandQueue) > 0:
                command = self.commandQueue.pop(0)
                if not command.isTimedOut():
                    self.quick_execute(command.get())
                
            time.sleep(1)
         
    def _writeExecuteConfigFile(self, fileContent: str):
        file = open(self.configPath.joinpath("excmd.cfg"), "w", encoding='utf-8')
    
        if not file.writable():
            raise Exception("Failed to open <execute>.cfg file for writing")
        
        file.write(fileContent)
        
        file.close()

    def _deleteExecuteConfigFile(self):
        if self.configPath.joinpath("excmd.cfg").is_file():
            os.remove(self.configPath.joinpath("excmd.cfg"))

    def _executeConfigFile(self):
        pyautogui.press('f8')
        

    def quick_execute(self, command: str):
        self._writeExecuteConfigFile(command)
        self._executeConfigFile()
        self._deleteExecuteConfigFile()

    def execute(self, command: str):
        self.commandQueue.append(Command(command))

    def write_allchat(self, message: str):
        self.execute("say " + message)

    def write_teamchat(self, message: str):
        self.execute("say_team " + message)

    def is_input_possible(self) -> bool:
        global os_name
        if os_name == "Windows":
            return not isMouseCursorVisible() and getForegroundWindow() == "Counter-Strike: Global Offensive"
        elif os_name == "Linux":
            return True
        else:
            return True

    def getLastLine(self) -> str:
        return self.lastLine

    def _writeAttachConfigFile(self):
        file = open(self.configPath.joinpath("cmd.cfg"), "w")
    
        if not file.writable():
            raise Exception("Failed to open .cfg file for writing")
    
        file.write("bind \"F8\" \"exec excmd\"\n")
        
        #SessionKey: [<sessionKey>]
        file.write("echoln SessionKey: [" + self.session_key + "]\n")
        
        #status
        file.write("status\n")
    
        file.write("echo Attempting to attach CMD Interface...\n")
        file.write("echo https://github.com/ExecutableMarley/<projectPath>\n")
    
        file.close()