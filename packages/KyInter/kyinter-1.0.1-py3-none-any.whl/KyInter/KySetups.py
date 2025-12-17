from ctypes import c_int, windll

class ScreenSetup():
    @staticmethod
    def setDPIAwareness(awareness: int = 2) -> None:
        awareness: c_int = c_int(awareness) # convert int to c_int

        # after Windows 8.1
        try:
            windll.shcore.SetProcessDpiAwareness(awareness)
        # before Windows 8.0
        except (AttributeError, OSError):
            windll.user32.SetProcessDPIAware()

    @staticmethod
    def setHighDefinition(highDefinition: bool = True) -> None:
        awareness: c_int = c_int(2 if highDefinition else 0) # convert int to c_int

        # after Windows 8.1
        try:
            windll.shcore.SetProcessDpiAwareness(awareness)
        # before Windows 8.0
        except (AttributeError, OSError):
            windll.user32.SetProcessDPIAware()
