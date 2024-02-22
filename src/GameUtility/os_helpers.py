import platform

        
#Os specific Imports
os_name = platform.system()
if os_name == "Windows":
    import ctypes
    import win32gui
    
    # Define CURSORINFO structure
    class CURSORINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_int),
                    ("flags", ctypes.c_int),
                    ("hCursor", ctypes.wintypes.HANDLE),
                    ("ptScreenPos", ctypes .wintypes.POINT)]
        
elif os_name == "Linux":
    pass

#
def isMouseCursorVisible() -> bool:
    # Windows
    if os_name == "Windows":
        ci = CURSORINFO()
        ci.cbSize = ctypes.sizeof(CURSORINFO)
        ctypes.windll.user32.GetCursorInfo(ctypes.byref(ci))
        return ci.flags == 1
    # Linux
    elif os_name == "Linux":
        # TODO: Implement this
        return True
    else:
        return True

#
def getForegroundWindow() -> str:
    # Windows
    if os_name == "Windows":
        hwnd = win32gui.GetForegroundWindow()  # Get handle of the foreground window
        return win32gui.GetWindowText(hwnd)
    # Linux
    elif os_name == "Linux":
        return "Linux not supported"
    else:
        return "OS not supported"
    
if __name__ == "__main__":
    print(isMouseCursorVisible())
    print(getForegroundWindow())