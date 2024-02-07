import os
import time
import threading


from pathlib import Path

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

    def notfiy(self, modifier):
        for observer in self._observers:
            if observer != modifier:
                observer.observe(self)


def getFileReader(file) -> str:
    file.seek(0,2) # Go to the end of the file
    while True:
        line = file.readline()
        if not line:
            time.sleep(1) # Sleep briefly
            continue
        yield line


class CMD(Observable):
    
    def __init__(self, rootPath: Path):
        Observable.__init__(self)
        self.rootPath:     Path = rootPath
        self.configPath:   Path = rootPath.joinpath("/game/csgo/cfg/")
        self.logFilePath:  Path = rootPath.joinpath("/game/csgo/console.log")
        self.thread: threading.Thread = None
        self.session_key = 123
        self.is_attached = False
        self.lastLine: str = ""

    def __del__(self):
        #Delete Config
        pass

    def start(self):
        pass

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

        # Wait until config is executed
        # + Verify
        while not self.is_attached:
            line = next(fileReader)
            #Compare keys
            time.sleep(1)

        while True:
            curLine = next(fileReader)

            if True:
                self.lastLine = curLine
                self.notfiy()

            time.sleep(1)


    def execute(self, command: str):
        pass

    def write_allchat(self, message: str):
        pass

    def write_teamchat(self, message: str):
        pass

    def is_input_possible(self) -> bool:
        pass

    def getLastLine(self) -> str:
        return self.lastLine

    def _writeAttachConfigFile(self):
        file = open(self.configPath.joinpath("cmd.cfg"), "w")
    
        if not file.writable():
            raise Exception("Failed to open .cfg file for writing")
    
        file.write("bind \"F9\" \"exec excmd\"\n")
        
        #status
        file.write("status\n")
    
        file.write("echoln SessionKey: " + self.session_key + "\n")
    
        file.write("echo Attempting to attach CMD Interface...\n")
        file.write("echo https://github.com/ExecutableMarley/<projectPath>\n")
    
        file.close()