import tkinter as tk
from tkinter import font
from .KyCore import Position, Size
from . import tksvg
import tempfile

class Misc(tk.Misc):
    def __init__(self) -> None:
        super().__init__()

class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.setTitle("Ky")
        self.setSize(Size(400, 300))

        # save data
        self._title = "Ky"

    def setFixedSize(self, fixedSize: bool = True) -> None:
        self.resizable(not fixedSize, not fixedSize)

    def setTitle(self, title: str) -> None:
        self.title(title)
        self._title = title

    def getTitle(self) -> str:
        return self._title

    def setSize(self, size: Size) -> None:
        self.geometry(f"{size.width}x{size.height}")

    def getSize(self) -> Size:
        return Size(self.winfo_width(), self.winfo_height())

    def setPosition(self, position: Position) -> None:
        self.geometry(f"{self.winfo_width}x{self.winfo_height}+{position.x}+{position.y}")

    def exec(self) -> None:
        self.mainloop()

class Font(font.Font):
    def __init__(self, font: str = None, family: str = "Arial", size: int = 10, bold: bool = False, italic: bool = False, underline: bool = False, overstrike: bool = False) -> None:
        super().__init__(font=font, family=family, size=size, 
                         weight="bold" if bold else "normal", 
                         slant="italic" if italic else "roman", 
                         underline=1 if underline else 0, 
                         overstrike=1 if overstrike else 0
                        )

        # save data
        self._family = family
        self._size = size
        self._bold = bold
        self._italic = italic
        self._underline = underline
        self._overstrike = overstrike

        # ensure success
        self.setConfigure()

    def setFamily(self, family: str) -> None:
        self._family: str = family
        self.setConfigure()

    def getFamily(self) -> str:
        return self._family

    def setSize(self, size: int) -> None:
        self._size: int = size
        self.setConfigure()

    def getSize(self) -> int:
        return self._size

    def setBold(self, bold: bool) -> None:
        self._bold: bool = bold
        self.setConfigure()

    def setItalic(self, italic: bool) -> None:
        self._italic: bool = italic
        self.setConfigure()

    def setUnderline(self, underline: bool) -> None:
        self._underline: bool = underline
        self.setConfigure()

    def setOverstrike(self, overstrike: bool) -> None:
        self._overstrike: bool = overstrike
        self.setConfigure()

    def setConfigure(self) -> None:
        self.configure(family=self._family, size=self._size, 
                       weight="bold" if self._bold else "normal", 
                       slant="italic" if self._italic else "roman", 
                       underline=1 if self._underline else 0, 
                       overstrike=1 if self._overstrike else 0,
                      )

class Label(tk.Label):
    def __init__(self, parent: Misc = None, text: str = "Label", font: Font = None) -> None:
        super().__init__(parent, text=text, font=font)

        # save data
        self._parent: Misc = parent
        self._text: str = text
        self._font: Font = font

        self.pack()

    def setSize(self, size: Size) -> None:
        self.configure(width=size.width, height=size.height)

    def getSize(self) -> Size:
        return Size(self.winfo_width(), self.winfo_height())

    def setPosition(self, position: Position) -> None:
        self.place(x=position.x, y=position.y)

    def getPosition(self) -> Position:
        return Position(self.winfo_x(), self.winfo_y())

    def setText(self, text: str) -> None:
        self._text: str = text
        self.setConfigure()

    def getText(self) -> str:
        return self._text

    def setFont(self, font: Font) -> None:
        self._font = font
        self.setConfigure()

    def getFont(self) -> Font:
        return self._font

    def setConfigure(self) -> None:
        self.configure(text=self._text, font=self._font)

class SvgImage(Label):
    def __init__(self, parent: Misc = None, text: str = "Label", font: Font = None, code: str = ""):
        super().__init__(parent, text, font)

        # write svg and render
        with tempfile.NamedTemporaryFile(mode="w+t", delete=False, suffix=".svg") as tempFile:
            tempFile.write(code)
            tempFile.flush()

            # create svg image and set label
            self._svgImage = tksvg.SvgImage(file=tempFile.name)
            self.configure(image=self._svgImage)

        self.pack()

    def scale(self, scale: float|int):
        self._svgImage.configure(scale=scale)
