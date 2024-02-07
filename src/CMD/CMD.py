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

        


class CMD(Observable):
    
    def __init__(self, rootPath: Path):
        Observable.__init__(self)
        self.rootPath:   Path = rootPath
        self.configPath: Path = rootPath.joinpath("/cfg/")
        self.debugPath:  Path = rootPath.joinpath("/debug/")
        self.thread: threading.Thread = None

    def __del__(self):
        #Delete Config
        pass

    def start(self):
        pass

    def run(self):
        pass

    def execute(self, command: str):
        pass

    def write_allchat(self, message: str):
        pass

    def write_teamchat(self, message: str):
        pass

    def is_input_possible(self) -> bool:
        pass

    def getLastLine() -> str:
        pass