import time
import threading
import re
import enum

from ConsoleInterface.CMD import CMD
from pathlib import Path


if __name__ == "__main__":
    
    csgoPath = Path("C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/")
    
    cmd = CMD(csgoPath)
    
    cmd.start()
    

