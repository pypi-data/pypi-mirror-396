class Position():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

class Size():
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

class Text(str):
    def __new__(cls, text: str):
        instance = super().__new__(cls, text)
        
        return instance

    @staticmethod
    def fromFile(filePath: str):
        return Text(open(filePath, "r", encoding="UTF-8").read())