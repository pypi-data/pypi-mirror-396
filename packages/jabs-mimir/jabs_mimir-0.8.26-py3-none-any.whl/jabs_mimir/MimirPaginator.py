from typing import List, Tuple
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.widgets import Treeview
import tkinter.font as tkFont

from jabs_mimir.MimirUtils import MimirUtils

class MimirPaginator:
    def __init__(self, items: List[str], itemsPerPage: int, parent: tk.Widget, themeManager, columnNames: Tuple[str, ...] = None):
        self.frame = parent
        self.items = items
        self.columnNames = columnNames
        self.useTwoColumns = self.checkIfTuples(self.items)
        self.itemsPerPage = itemsPerPage
        self.itemsByPage = self._split(items, itemsPerPage)
        self.maxPage = len(self.itemsByPage) - 1
        self.state = {"page": 0}
        self.pageLabelVar = tk.StringVar()

        self.tree = self.createTree(self.useTwoColumns, self.columnNames)

        self.style = tb.Style()
        self.themeManager = themeManager
        self.utils = MimirUtils()

        self.themeManager.subscribeToThemeChange(lambda: self.setupStyle(self.tree))
        self.setupStyle(self.tree)
        self._createWidgets(parent)

    def checkIfTuples(self, items):
        return all(isinstance(item, tuple) for item in items)
    
    def createTree(self, useTwoColumns, columnNames):
        if useTwoColumns and columnNames is not None:
            tree = Treeview(self.frame, columns=("col1", "col2"), show="headings")

            tree.heading("col1", anchor="w", text=columnNames[0])
            tree.heading("col2", anchor="center", text=columnNames[1])
            tree.column("col1", width=100, anchor="w")
            tree.column("col2", width=250, anchor="center")
        else:
            tree = Treeview(self.frame, show="tree")
        
        return tree

    def setupStyle(self, tree):
        colors = self.themeManager.themeColors
        self.style.configure("Treeview", rowheight=25)

        tree.tag_configure("odd", background=colors.secondary)
        tree.tag_configure("highlight", background="lightblue", foreground="black")

        rowFont = self.utils.getCurrentFont()
        headerFont = self.utils.getCurrentFont()
        self.style.configure("Treeview", font=(rowFont, 13))
        self.style.configure("Treeview.Heading", font=(headerFont, 12))

    def _split(self, items, perPage):
        pages = []
        totalItems = len(items)

        # Loop through the list in steps of 'perPage'
        for startIndex in range(0, totalItems, perPage):
            endIndex = startIndex + perPage
            page = items[startIndex:endIndex]
            pages.append(page)

        return pages

    def _createWidgets(self, parent):
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=0)
        parent.columnconfigure(0, weight=1)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self._populateTree()

        self.buttonGrid = tb.Frame(parent)
        self.buttonGrid.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        for i in range(3):
            self.buttonGrid.columnconfigure(i, weight=1)

        self.backButton = tb.Button(
            self.buttonGrid, text="Back",
            command=self.goToPreviousPage
        )
        self.backButton.grid(row=0, column=0, sticky="ew", padx=5)

        tb.Label(
            self.buttonGrid, textvariable=self.pageLabelVar,
            anchor="center"
        ).grid(row=0, column=1, sticky="ew")

        self.nextButton = tb.Button(
            self.buttonGrid, text="Next",
            command=self.goToNextPage
        )
        self.nextButton.grid(row=0, column=2, sticky="ew", padx=5)

    def _populateTree(self):
        self.tree.delete(*self.tree.get_children())

        if self.useTwoColumns:
            for i, (name, value) in enumerate(self.itemsByPage[self.state["page"]]):
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", "end", values=(name, value), tags=(tag,))
        
        else:
            for i, item in enumerate(self.itemsByPage[self.state["page"]]):
                tag = "even" if i % 2 == 0 else "odd"
                self.tree.insert("", "end", text=str(item), tags=(tag,))

        self.pageLabelVar.set(str(self.state["page"] + 1))

    def goToNextPage(self):
        self.state["page"] = min(self.state["page"] + 1, self.maxPage)
        self._populateTree()

    def goToPreviousPage(self):
        self.state["page"] = max(0, self.state["page"] - 1)
        self._populateTree()
