import tkinter as tk
from tkinter import font

class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

    def setTitle(self, title: str = "MainWindow") -> None:
        self.title(title)

    def setSize(self, width: int = 400, height: int = 300) -> None:
        self.geometry(f"{width}x{height}")

    def exec(self) -> None:
        self.mainloop()

class Font(font.Font):
    def __init__(self, font: str = None, family: str = "Arial", size: int = 10, bold: bool = False, italic: bool = False, underline: bool = False, overstrike: bool = False) -> None:
        super().__init__(
            font=font, family=family, size=size, 
            weight="bold" if bold else "normal", 
            slant="italic" if italic else "roman", 
            underline=1 if underline else 0, 
            overstrike=1 if overstrike else 0
        )

        # ensure success
        self.configure(
            family=family, size=size, 
            weight="bold" if bold else "normal", 
            slant="italic" if italic else "roman", 
            underline=1 if underline else 0, 
            overstrike=1 if overstrike else 0,
        )

class Label(tk.Label):
    def __init__(self, parent: MainWindow = None, text: str = "Label", font: Font = None) -> None:
        super().__init__(
            parent, text=text, font=font, 
        )

        self.pack()
