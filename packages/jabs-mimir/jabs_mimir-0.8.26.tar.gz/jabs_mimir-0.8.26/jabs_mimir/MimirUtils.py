import tkinter as tk
import ttkbootstrap as tb

import tkinter.font as tkFont

class MimirUtils:
    @staticmethod
    def getCurrentFont():
        """Return the default font currently used by ttkbootstrap widgets."""
        style = tb.Style()
        fontName = style.lookup("TLabel", "font")
        return tkFont.Font(font=fontName)
    
    @staticmethod
    def getNextAvailableRow(frame: tk.Widget) -> int:
        """Find the next available row in a grid layout of a given frame."""
        used_rows = [
            int(child.grid_info().get("row", 0))
            for child in frame.winfo_children()
            if "row" in child.grid_info()
        ]
        return max(used_rows, default=-1) + 1