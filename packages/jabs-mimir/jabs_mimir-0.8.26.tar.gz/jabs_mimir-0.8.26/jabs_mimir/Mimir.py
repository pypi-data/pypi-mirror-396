"""
Abstract Mimir (updated): Reusable UI controller with abstract block rendering
"""

from multiprocessing import ProcessError
from typing import List, Tuple

import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as msg
from tokenize import tabsize


import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.widgets import Notebook
from ttkbootstrap.scrolled import ScrolledFrame

import importlib.util
import os
import warnings

from jabs_mimir.DataBlockWrapper import DataBlockWrapper
from jabs_mimir.mimirThemeManager import MimirThemeManager
from jabs_mimir.MimirPaginator import MimirPaginator
from jabs_mimir.MimirUtils import MimirUtils


class Mimir:
    widthEntry = 20
    widthCombo = widthEntry - 2

    def __init__(self, app):
        self.app = app
        self.currentView = None
        self.invalidEntries = set()
        self._validatorResolver = lambda name: None
        self.fieldRenderers = {
            "entry": self._renderEntryField,
            "combobox": self._renderComboboxField,
            "heading": self._renderHeading,
            "fileupload": self._renderFileUploadField
        }

        self.themeManager = MimirThemeManager(self.app.style)
        self.utils = MimirUtils()

        self._globalValidationMessage = {"label": "Validation Error", "text": "Some Fields are not valid"}

    @property
    def themeColors(self):
        return self.themeManager.themeColors
    
    def allowDarkMode(self, enabled=True):
        self.themeManager.allowDarkMode(enabled)
    
    def subscribeToThemeChange(self, callback):
        self.themeManager.subscribeToThemeChange(callback)

    def _toggleTheme(self):
        self.themeManager.toggleTheme()
            
    def setValidatorResolver(self, resolverFunc):
        self._validatorResolver = resolverFunc

    def resolveValidator(self, name):
        return self._validatorResolver(name)

    def setValidatorFile(self, filePath: str):
        """
        Loads a Python file containing validation functions and registers them
        as callable validators by name.

        This enables referencing validators by string name in field definitions,
        e.g., "not_empty", and resolves them via `getattr` from the loaded module.

        Args:
            filePath (str): Absolute or relative path to a Python file defining validation functions.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        filePath = os.path.abspath(filePath)
        if not os.path.exists(filePath):
            raise FileNotFoundError(f"Validator file not found: {filePath}")

        module_name = "_mimir_loaded_validators"
        spec = importlib.util.spec_from_file_location(module_name, filePath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.setValidatorResolver(lambda name: getattr(module, name, None))

        self.setValidatorResolver(lambda name: getattr(module, name, None))

    def addToMenuBar(self, category: str, label: str, command: callable):
        """
        Adds a new item to the menubar under the given category.
        If the category does not exist, it is created.
        
        Args:
            category (str): Top-level menu label (e.g., "Settings", "Tools")
            label (str): Label of the menu item
            command (callable): Function to run when item is selected
        """
        if not hasattr(self.app, "_mimirMenuInitialized"):
            raise RuntimeError("Menu bar is not initialized yet. Call switchView first.")

        # Store a reference to the menubar on first call (if not already)
        if not hasattr(self, "_menuRegistry"):
            self._menuRegistry = {}

        menubar = self.app.nametowidget(self.app["menu"])

        if category not in self._menuRegistry:
            newMenu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label=category, menu=newMenu)
            self._menuRegistry[category] = newMenu
        else:
            newMenu = self._menuRegistry[category]


        newMenu.add_command(label=label, command=command)

    def renderView(self, newFrameFunc, gridOptions=None, **kwargs):
        """
        Replaces the current view with a new frame returned by `newFrameFunc`.
        View func are expected to return a Frame object.

        Destroys any previous view, resets validation state, and sets up layout
        within a new container frame. Also injects a top-level menu bar with a 
        theme toggle if not already initialized.

        Args:
            newFrameFunc (callable): A function that takes **kwargs and returns a Frame.
            gridOptions (dict, optional): Grid placement options for the new view. 
                                        Defaults to row=0, column=0, sticky="nsew", padx=50, pady=20.
            **kwargs: Additional keyword arguments passed to `newFrameFunc`.

        Returns:
            Frame: The newly rendered view/frame.
        """
        if self.currentView:
            self.currentView.destroy()
        self._manualValidations = []
        self.invalidEntries.clear()

        # Create container for the view
        container = tb.Frame(self.app)
        container.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Optional: create a menubar on first switchView call
        if not hasattr(self, "_menuRegistry"):
            self._menuRegistry = {}

        menubar = tk.Menu(self.app)
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Theme", command=self._toggleTheme)

        menubar.add_cascade(label="Settings", menu=viewmenu)
        self._menuRegistry["Settings"] = viewmenu

        self.app.config(menu=menubar)
        self.app._mimirMenuInitialized = True

        # Load and place new view
        newFrame = newFrameFunc(**kwargs)
        options = gridOptions or {"row": 0, "column": 0, "sticky": "nsew", "padx": 50, "pady": 20}
        newFrame.grid(**options)
        self.app.rowconfigure(options.get("row", 0), weight=1)
        self.app.columnconfigure(options.get("column", 0), weight=1)

        self.currentView = newFrame
        self.app.update_idletasks()
        self.app.geometry("")

        return newFrame

    def switchView(self, newFrameFunc, gridOptions=None, **kwargs):
        warnings.warn("switchViews is deprecated. Use renderView instead", UserWarning, stacklevel=2)
        """
        Replaces the current view with a new frame returned by `newFrameFunc`.

        Destroys any previous view, resets validation state, and sets up layout
        within a new container frame. Also injects a top-level menu bar with a 
        theme toggle if not already initialized.

        Args:
            newFrameFunc (callable): A function that takes `(self, **kwargs)` and returns a Frame.
            gridOptions (dict, optional): Grid placement options for the new view. 
                                        Defaults to row=0, column=0, sticky="nsew", padx=50, pady=20.
            **kwargs: Additional keyword arguments passed to `newFrameFunc`.

        Returns:
            Frame: The newly rendered view/frame.
        """
        if self.currentView:
            self.currentView.destroy()
        self._manualValidations = []
        self.invalidEntries.clear()

        # Create container for the view
        container = tb.Frame(self.app)
        container.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Optional: create a menubar on first switchView call
        if not hasattr(self, "_menuRegistry"):
            self._menuRegistry = {}

        menubar = tk.Menu(self.app)
        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Theme", command=self._toggleTheme)

        menubar.add_cascade(label="Settings", menu=viewmenu)
        self._menuRegistry["Settings"] = viewmenu

        self.app.config(menu=menubar)
        self.app._mimirMenuInitialized = True

        # Load and place new view
        newFrame = newFrameFunc(self, **kwargs)
        options = gridOptions or {"row": 0, "column": 0, "sticky": "nsew", "padx": 50, "pady": 20}
        newFrame.grid(**options)
        self.app.rowconfigure(options.get("row", 0), weight=1)
        self.app.columnconfigure(options.get("column", 0), weight=1)

        self.currentView = newFrame
        self.app.update_idletasks()
        self.app.geometry("")

        return newFrame

    def popupView(self, viewFunc, title="Popup", size="fit", width=500, height=400, modal=False):
        """
        Opens a popup (Toplevel) window and renders a view inside it.

        The popup can either auto-size to fit the content or use fixed dimensions.
        Supports modal behavior if needed. The view is created by calling `viewFunc(self, popup)`.

        Args:
            viewFunc (callable): Function that takes `(self, popup)` and returns a Frame to display.
            title (str): Window title. Defaults to "Popup".
            size (str): Either "fit" to auto-resize or any other value to use fixed width/height.
            width (int): Width of the popup window if size != "fit". Default is 500.
            height (int): Height of the popup window if size != "fit". Default is 400.
            modal (bool): If True, the popup becomes modal (blocks interaction with main window).

        Returns:
            Toplevel: The created popup window.
        """
        popup = tk.Toplevel(self.app)
        popup.title(title)
        popup.transient(self.app)
        popup.resizable(False, False)

        if size == "fit":
            popup.update_idletasks()
            popup.geometry("")
        else:
            popup.geometry(f"{width}x{height}")

        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        viewFrame = viewFunc(self, popup)
        viewFrame.grid(row=0, column=0, sticky="nsew")

        if modal:
            popup.grab_set()
            popup.focus_set()

        return popup
    
    def buildDataBlock(self, container, fields, blockList, layout="horizontal", meta=None, label=None, noRemove=False):
        """
        Renders a labeled data block (LabelFrame) and places input fields inside it.
        If an existing block is provided, repopulates data from that

        Args:
            container (tk.Widget): Parent widget where the block should be rendered.
            fields (list): List of field dicts (with keys: label, key, variable, type, etc).
            blockList (list): A list to append the wrapped block to.
            layout (str): "horizontal" or "vertical".
            meta (dict, optional): Additional metadata stored with the block.
            label (str, optional): Optional override for block label/title.
            noRemove (bool): If True, no Remove button is shown.

        Returns:
            DataBlockWrapper: A wrapper containing metadata and access to field vars.
        """
        index = len(blockList) + 1
        labelText = label or f"Block {index}"
        frame = tb.LabelFrame(container, text=labelText)
        frame.configure(labelanchor="n")

        meta = meta or {}
        if "custom_label" not in meta:
            meta["custom_label"] = labelText

        # Place container in layout
        if layout == "vertical":
            row = self.getNextAvailableRow(container)
            frame.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            container.columnconfigure(0, weight=1)
        else:
            frame.grid(row=0, column=index - 1, padx=10, pady=10, sticky="n")

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        blockMeta = {
            "frame": frame,
            "fields": fields,
            "fields_by_key": {f["key"]: f["variable"] for f in fields if "key" in f},
            "layout": layout,
            **meta
        }

        # Instead of creating a new wrapper every time:
        if blockList:
            wrapper = blockList[0]  # Reuse existing block (since we always expect one)
            wrapper.meta["frame"] = frame  # Update container
        else:
            wrapper = DataBlockWrapper(blockMeta)
            blockList.append(wrapper)

        row = 0
        for field in fields:
            ftype = field.get("type", "entry")
            key = field.get("key")

            if key and wrapper.has(key):
                field["variable"] = wrapper.get(key)

            renderer = self.fieldRenderers.get(ftype)
            if renderer:
                renderer(frame, row, field)
                row += (3 if ftype == "fileupload" else 1 if ftype == "heading" else 2)

        # Optional remove button
        if not noRemove and not (len(fields) == 1 and fields[0].get("type") == "fileupload"):
            removeBtn = tb.Button(
                frame,
                text="🗑️ Remove",
                bootstyle="danger-outline",
                command=lambda w=wrapper: self.removeBlock(blockList, w)
            )
            removeBtn.grid(row=row, column=0, columnspan=2, pady=(10, 5))

        return wrapper
    
    def renderBlockUI(self, container, fields, blockList, layout="horizontal", meta=None, label=None, noRemove=False):
        """
        Depcrecated: Use buildDataBlock instead
        Renders a labeled data block (LabelFrame) and places input fields inside it.

        Args:
            container (tk.Widget): Parent widget where the block should be rendered.
            fields (list): List of field dicts (with keys: label, key, variable, type, etc).
            blockList (list): A list to append the wrapped block to.
            layout (str): "horizontal" or "vertical".
            meta (dict, optional): Additional metadata stored with the block.
            label (str, optional): Optional override for block label/title.
            noRemove (bool): If True, no Remove button is shown.

        Returns:
            DataBlockWrapper: A wrapper containing metadata and access to field vars.
        """
        warnings.warn("renderBlockUI is deprecated. Use buildDataBlock instead", DeprecationWarning, stacklevel=2)
        index = len(blockList) + 1
        labelText = label or f"Block {index}"
        frame = tb.LabelFrame(container, text=labelText)
        frame.configure(labelanchor="n")

        meta = meta or {}
        if "custom_label" not in meta:
            meta["custom_label"] = labelText

        # Placement in grid
        if layout == "vertical":
            row = self.getNextAvailableRow(container)
            frame.grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            container.columnconfigure(0, weight=1)
        else:
            frame.grid(row=0, column=index - 1, padx=10, pady=10, sticky="n")

        # Internal layout: label + entry
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        boldFont = self.getCurrentFont()
        boldFont.configure(weight="bold")

        blockMeta = {
            "frame": frame,
            "fields": fields,
            "fields_by_key": {f["key"]: f["variable"] for f in fields if "key" in f},
            "layout": layout,
            **meta
        }

        wrapper = DataBlockWrapper(blockMeta)
        blockList.append(wrapper)

        # Auto-disable remove button for single fileupload field
        if len(fields) == 1 and fields[0].get("type") == "fileupload":
            noRemove = True

        row = 0
        for field in fields:
            ftype = field.get("type", "entry")
            renderer = self.fieldRenderers.get(ftype)
            if renderer:
                renderer(frame, row, field)
                if ftype == "fileupload":
                    row += 3
                elif ftype == "heading":
                    row += 1
                else:
                    row += 2

        if not noRemove:
            removeBtn = tb.Button(
                frame,
                text="🗑️ Remove",
                bootstyle="danger-outline",
                command=lambda w=wrapper: self.removeBlock(blockList, w)
            )
            removeBtn.grid(row=row, column=0, columnspan=2, pady=(10, 5))

        return wrapper

    def registerFieldType(self, name, renderer):
        """
        Register a custom field renderer.
        Automatically injects validation support into entry-like widgets.
        """
        def wrappedRenderer(parent, row, field):
            widget = renderer(parent, row, field)
            # If the renderer returns a widget, auto-attach validation
            if widget is not None:
                self._setupValidation(widget, field.get("validation"))

        self.fieldRenderers[name] = wrappedRenderer

    def _renderEntryField(self, parent, row, field):
        """Internal: Render an entry field with label."""
        self.addLabeledEntry(
            parent=parent,
            row=row,
            label=field["label"],
            variable=field["variable"],
            validation=field.get("validation"),
            **field.get("options", {})  # <-- wildcard pass-through
        )

    def _renderComboboxField(self, parent, row, field):
        """Internal: Render a combobox field with label."""
        self.addLabeledCombobox(
            parent=parent,
            row=row,
            label=field["label"],
            variable=field["variable"],
            values=field["values"],
            **field.get("options", {})  # <-- pass all UI customization
        )
    def _renderHeading(self, parent, row, field):
        """Internal: Render a bold heading label within a form."""
        font = self.getCurrentFont()
        font.configure(weight="bold")

        align = field.get("options", {}).get("align", "w")  # default to left

        tb.Label(
            parent,
            text=field["label"],
            font=font
        ).grid(row=row, column=0, columnspan=2, pady=(10, 5), sticky=align) 

    def _renderFileUploadField(self, parent, row, field):
        """
        Internal: Render a file upload field with entry + browse button.
        Supports multi-select via options['multiple'].
        """
        import os
        import tkinter.filedialog as fd

        var = field["variable"]                      # tk.StringVar
        label = field.get("label", "Browse")
        options = field.get("options", {}) or {}

        # compute column span
        numColumns = (
            max(
                int(ch.grid_info().get("column", 0)) + int(ch.grid_info().get("columnspan", 1))
                for ch in parent.winfo_children()
            )
            if parent.winfo_children() else 2
        )

        entry = tb.Entry(parent, textvariable=var, state="readonly")
        entry.grid(row=row, column=0, columnspan=numColumns, sticky="ew", padx=10, pady=(5, 0))

        self._setupValidation(entry, field.get("validation"))

        def normalizePaths(paths):
            # return a pathsep-joined string, unique and non-empty
            uniq = []
            seen = set()
            for p in paths:
                p = os.path.normpath(p)
                if p and p not in seen:
                    uniq.append(p)
                    seen.add(p)
            return os.pathsep.join(uniq)

        def browse():
            filetypes = options.get("filetypes", [("All files", "*.*")])
            initialdir = options.get("initialdir")
            allowMultiple = bool(options.get("multiple"))

            if allowMultiple:
                chosen = fd.askopenfilenames(filetypes=filetypes, initialdir=initialdir)
                if not chosen:
                    return
                var.set(normalizePaths(chosen))
            else:
                chosen = fd.askopenfilename(filetypes=filetypes, initialdir=initialdir)
                if not chosen:
                    return
                var.set(os.path.normpath(chosen))

        tb.Button(
            parent,
            text=label,
            command=browse,
            bootstyle="secondary-outline"
        ).grid(row=row + 1, column=0, columnspan=numColumns, sticky="ew", padx=10, pady=5)

        return entry

    def setValidationFailureMessage(self, label, text) -> None:
        """
        Sets a custom validation error message. If a value is None, the default is preserved.
        """
        if label is not None:
            self._globalValidationMessage["label"] = label
        if text is not None:
            self._globalValidationMessage["text"] = text

    def _setupValidation(self, widget, validation):
        """
        Bind one or more validation rules to a widget.
        Supports single dict, list of dicts, or direct function.
        """
        if not validation:
            return

        if not isinstance(validation, list):
            validation = [validation]

        if not hasattr(self, "_manualValidations"):
            self._manualValidations = []

        if not hasattr(widget, "_validationMeta"):
            widget._validationMeta = {"validations": []}

        for rule in validation:
            if isinstance(rule, dict):
                func = rule.get("func")
                severity = rule.get("severity", "error")
                on_invalid = rule.get("onInvalid")
                on_valid = rule.get("onValid")
                styling = rule.get("styling", "regularMimir")
            else:
                func = rule
                severity = "error"
                on_invalid = None
                on_valid = None
                styling = "regularMimir"

            if isinstance(func, str):
                func = self._validatorResolver(func)

            if not callable(func):
                continue

            rule_meta = {
                "func": func,
                "severity": severity,
                "onValid": on_valid,
                "onInvalid": on_invalid,
                "styling": styling,
                "validation_failed": None
            }

            widget._validationMeta["validations"].append(rule_meta)

            def makeValidator(rule_ref):
                def validator(event=None):
                    try:
                        value = widget.get()
                        if rule_ref["func"](value):
                            if rule_ref["styling"] == "regularMimir":
                                self.clearInvalid(widget)
                            if callable(rule_ref["onValid"]):
                                rule_ref["onValid"](widget, value)
                            rule_ref["validation_failed"] = None
                        else:
                            if rule_ref["styling"] == "regularMimir":
                                self.markInvalid(widget)
                            if callable(rule_ref["onInvalid"]):
                                rule_ref["onInvalid"](widget, value)
                            rule_ref["validation_failed"] = rule_ref["severity"]
                    except Exception as e:
                        print("Validator raised exception:", e)
                return validator

            validator = makeValidator(rule_meta)
            widget.bind("<FocusOut>", validator)
            self._manualValidations.append((widget, validator))

    def markInvalid(self, widget):
        """Mark a widget as invalid with red border styling."""
        widget.config(bootstyle="danger")
        self.invalidEntries.add(widget)

    def clearInvalid(self, widget):
        """Clear error styling from a widget."""
        widget.config(bootstyle="none")
        self.invalidEntries.discard(widget)

    def _gatherWidgetsRecursively(self, widget):
        yield widget
        for child in widget.winfo_children():
            yield from self._gatherWidgetsRecursively(child)

    def addNextButton(self, parent, row, viewFunc, label="Next", validate=True, tooltip=None, column=None, columnspan=None, **kwargs):
        """
        Add a button that switches to a new view, with optional validation.

        Parameters:
            parent (tk.Widget): The parent container/frame.
            row (int): Grid row to place the button in.
            viewFunc (callable): A function that returns a new view/frame (typically a view initializer).
            label (str): Button text. Defaults to "Nästa".
            validate (bool): If True, validation will block the transition if any fields are invalid.
            tooltip (str, optional): Hover text.
            column (int, optional): Grid column to place button. Auto-calculated if omitted.
            columnspan (int, optional): How many columns the button should span. Auto-calculated if omitted.
            **kwargs: Additional keyword arguments passed to the view function via switchView.

        Returns:
            ttkbootstrap.Button: The rendered button widget.
        """
        def go():
            self.switchView(viewFunc, **kwargs)

        return self.addButton(
            parent=parent,
            row=row,
            command=go,
            label=label,
            validate=validate,
            tooltip=tooltip,
            column=column,
            columnspan=columnspan
        )
    
    def addButton(self, parent, row, command, label="OK", validate=True, tooltip=None, column=None, columnspan=None):
        """
        Add a general-purpose button to the view.

        Parameters:
            parent (tk.Widget): The parent container/frame.
            row (int): Grid row to place the button in.
            command (callable): Function to run when button is pressed.
            label (str): Button text. Defaults to "OK".
            validate (bool): If True, validation will run and block execution if any fields fail.
            tooltip (str, optional): Hover text.
            column (int, optional): Grid column to place button. Auto-calculated if omitted.
            columnspan (int, optional): How many columns the button should span. Auto-calculated if omitted.

        Returns:
            ttkbootstrap.Button: The rendered button widget.
        """
        def wrapped():
            if validate:
                # Trigger <FocusOut> for all nested widgets
                for widget in self._gatherWidgetsRecursively(parent):
                    widget.event_generate("<FocusOut>")

                has_blocking = False
                for widget in self._gatherWidgetsRecursively(parent):
                    meta = getattr(widget, "_validationMeta", None)
                    if not meta:
                        continue

                    for rule in meta.get("validations", []):
                        fn = rule["func"]
                        severity = rule.get("severity", "error")
                        on_valid = rule.get("onValid")
                        on_invalid = rule.get("onInvalid")
                        styling = rule.get("styling", "regularMimir")

                        try:
                            value = widget.get()
                        except Exception:
                            continue

                        if fn(value):
                            if styling == "regularMimir":
                                self.clearInvalid(widget)
                            if callable(on_valid):
                                on_valid(widget, value)
                            rule["validation_failed"] = None
                        else:
                            if styling == "regularMimir":
                                self.markInvalid(widget)
                            if callable(on_invalid):
                                on_invalid(widget, value)
                            rule["validation_failed"] = severity
                            if severity == "error":
                                has_blocking = True

                if has_blocking:
                    msg.showerror(
                        self._globalValidationMessage.get("label"),
                        self._globalValidationMessage.get("text")
                    )
                    return
            command()

        return self._renderButton(parent, row, wrapped, label, tooltip, column, columnspan)

    def _renderButton(self, parent, row, command, label, tooltip, column, columnspan):
        """
        Internal helper to render a button and auto-calculate column/grid placement.
        """
        if column is None:
            used_columns = set(
                int(child.grid_info().get("column", 0))
                for child in parent.winfo_children()
                if int(child.grid_info().get("row", -1)) == row
            )
            column = max(used_columns) + 1 if used_columns else 0

        if columnspan is None:
            columnspan = 1

        btn = tb.Button(parent, text=label, command=command, bootstyle="success")
        btn.grid(row=row, column=column, columnspan=columnspan, padx=5, pady=5, sticky="ew")

        if tooltip:
            self.addTooltip(btn, tooltip)

        return btn

    def getCurrentFont(self):
        """Exists for backwards compatibility, returns the current font."""
        return self.utils.getCurrentFont()
    
    def addTooltip(self, widget, text):
        """Attach a styled tooltip to a widget."""
        ToolTip(widget, text, bootstyle=(SECONDARY, INVERSE))

    def removeBlock(self, blockList, wrapper):
        frame = wrapper.meta.get("frame")
        layout = wrapper.meta.get("layout", "horizontal")
        if frame:
            frame.destroy()
        blockList.remove(wrapper)

        for i, block in enumerate(blockList):
            frame = block.meta["frame"]
            new_label = block.meta.get("custom_label") or f"Block {i + 1}"
            frame.config(text=new_label)

            if layout == "vertical":
                frame.grid_configure(row=i, column=0)
            else:
                frame.grid_configure(row=0, column=i)

    def addLabeledEntry(self, parent, row, label, variable, state="normal", tooltip=None, validation=None, column=0, vertical=False, columnspan=1, sticky="ew", options=None, **kwargs):
        """
        Add a labeled entry input field. Supports vertical and horizontal layouts,
        optional tooltips and validation.
        Options Wildcard: pass a dict with standard tkinter/ttkbootstrap options.
        """
        entry_kwargs = options.copy() if options else {}
        entry_kwargs.update(kwargs)
        entry_kwargs.setdefault("width", self.widthEntry)
        entry_kwargs["textvariable"] = variable
        entry_kwargs["state"] = state

        if vertical:
            tb.Label(parent, text=label).grid(row=row, column=column, columnspan=columnspan, padx=5, pady=(5, 5))
            entry = tb.Entry(parent, **entry_kwargs)
            entry.grid(row=row + 1, column=column, padx=5, columnspan=columnspan, pady=(0, 10), sticky=sticky)
        else:
            tb.Label(parent, text=label).grid(row=row, column=column, padx=5, pady=5, sticky="e")
            entry = tb.Entry(parent, **entry_kwargs)
            entry.grid(row=row, column=column + 1, columnspan=columnspan, padx=5, pady=5, sticky=sticky)

        if tooltip:
            self.addTooltip(entry, tooltip)

        self._setupValidation(entry, validation)

        return entry


    def addLabeledCombobox(self, parent, row, label, variable, values, tooltip=None, state="readonly", column=0, vertical=False, columnspan=1, options=None):
        """
        Add a labeled combobox dropdown field with options.
        Options Wildcard, pass a dict with standard tkinter/ttkbootstrap options
        """
        if vertical:
            tb.Label(parent, text=label).grid(row=row, column=column, columnspan=columnspan, padx=5, pady=(5, 0))
            combo = tb.Combobox(parent, textvariable=variable, values=values, state=state, width=self.widthCombo)
            combo.grid(row=row + 1, column=column, columnspan=columnspan, padx=5, pady=(0, 10))
        else:
            tb.Label(parent, text=label).grid(row=row, column=column, padx=5, pady=5, sticky="e")
            combo = tb.Combobox(parent, textvariable=variable, values=values, state=state, width=self.widthCombo)
            combo.grid(row=row, column=column + 1, columnspan=columnspan, padx=5, pady=5, sticky="ew")

        if tooltip:
            self.addTooltip(combo, tooltip)

        return combo
    
    def rowGen(self, frame: tk.Widget):
        row = self.getNextAvailableRow(frame)
        while True:
            yield row
            row += 1

    def getNextAvailableRow(self, frame: tk.Widget) -> int:
        """Exists for backwards compatibility, returns the next available row."""
        return self.utils.getNextAvailableRow(frame)
    
    def addInfoBox(self, parent, row, text, label=None, column=0, columnspan=1, border=False, fontsize=None, options=None):
        """
        Add an info box with or without a border.
        If border=False, uses a regular Frame instead of a LabelFrame.
        """
        options = options or {}
        parent.columnconfigure(column, weight=1)

        if border:
            container = tb.LabelFrame(parent, text=label or "")
        else:
            container = tb.Frame(parent)

        container.grid(row=row, column=column, columnspan=columnspan, padx=10, pady=10, sticky="ew")
        container.columnconfigure(0, weight=1)

        font = self.getCurrentFont()
        if fontsize is not None:
            font.configure(size=fontsize)

        infoLabel = tb.Label(
            container,
            text=text,
            justify="left",
            wraplength=500,
            font=font,
            **options
        )
        infoLabel.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        return container

    def addTabbedView(self, tabs, parent=None, row=0, column=0, columnspan=1, rowspan=1, sticky="nsew", fit=True, background="#f8f9fa", tabSize=12):
        """
        Adds a multi-tabbed view (Notebook) to the specified parent container.

        Each tab is defined by a dictionary with at least a "label" (tab title)
        and a "view" (callable that returns a Frame). Optionally, a tab can be
        scrollable by setting "scrollable": True. In that case, a ttkbootstrap.ScrolledFrame
        is used as the content wrapper.

        All layout (grid, rowconfigure, columnconfigure) is handled internally —
        tab views only need to return a Frame; no grid() or layout setup is required.

        Args:
            tabs (list): List of dicts with keys:
                        - "label" (str): tab name shown in UI
                        - "view" (callable): function that returns the tab content frame
                        - "scrollable" (bool, optional): if True, wraps content in a ScrolledFrame
            parent (Widget, optional): Parent container. Defaults to self.app.
            row (int): Grid row to place the Notebook in. Defaults to 0.
            column (int): Grid column to place the Notebook in. Defaults to 0.
            columnspan (int): Number of columns to span. Defaults to 1.
            rowspan (int): Number of rows to span. Defaults to 1.
            sticky (str): Sticky setting for the Notebook grid. Defaults to "nsew".
            fit (bool): If True, configures parent row/column weights for auto expansion.
            background (str): Background color for the parent container.

        Returns:
            Notebook: The created ttkbootstrap Notebook widget.
        """
        parent = parent or self.app

        if hasattr(self.app, "configure"):
            self.app.configure(bg=background)

        if fit:
            parent.rowconfigure(row, weight=1)
            parent.columnconfigure(column, weight=1)

        tabSize = tabSize if tabSize else 12

        style = tb.Style()
        style.configure("TNotebook.Tab", font=(self.getCurrentFont(), tabSize))

        notebook = Notebook(parent, bootstyle="primary")
        notebook.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky=sticky, padx=10, pady=10)

        for tab in tabs:
            scrollable = tab.get("scrollable", False)

            outerFrame = tb.Frame(notebook)
            outerFrame.grid_rowconfigure(0, weight=1)
            outerFrame.grid_columnconfigure(0, weight=1)

            if scrollable:
                scroller = ScrolledFrame(outerFrame, autohide=True)
                scroller.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
                scroller.columnconfigure(0, weight=1)
                scroller.rowconfigure(0, weight=1)
                contentFrame = scroller
            else:
                contentFrame = tb.Frame(outerFrame)
                contentFrame.grid(row=0, column=0, sticky="nsew")
                contentFrame.grid_rowconfigure(0, weight=1)
                contentFrame.grid_columnconfigure(0, weight=1)

            viewFunc = tab.get("view")
            if callable(viewFunc):
                inner = viewFunc(self, contentFrame)
                if inner:
                    inner.grid(row=0, column=0, sticky="nsew")
                else:
                    # In case the viewFunc returns None but you still want to use contentFrame
                    inner = contentFrame
            else:
                inner = contentFrame

            notebook.add(outerFrame, text=tab.get("label", "Tab"))

        return notebook
    
    def createContextMenu(self, widget, actions: dict):
        def buildMenu(menu, actions, event):
            def normalizeItems(actionsDict):
                items = []
                for label, action in actionsDict.items():
                    if action is None:
                        continue  # ✅ Skip entries explicitly set to None
                    if isinstance(action, dict):
                        items.append((label, action, 9999, True))  # submenu
                    elif isinstance(action, tuple):
                        func, order = action
                        items.append((label, func, order, False))
                    else:
                        items.append((label, action, 9999, False))
                return sorted(items, key=lambda x: x[2])
            for label, action, _, isSubmenu in normalizeItems(actions):
                if isSubmenu:
                    submenu = tk.Menu(menu, tearoff=0)
                    buildMenu(submenu, action, event)
                    menu.add_cascade(label=label, menu=submenu)
                else:
                    menu.add_command(label=label, command=(lambda f=action, e=event: lambda: f(e))())

        def showMenu(event):
            self.isContextMenuOpen = True
            menu = tk.Menu(widget, tearoff=0)
            buildMenu(menu, actions, event)
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        widget.bind("<Button-3>", showMenu)

    def createPaginator(self, items: list, itemsPerPage: int = 5, parent=None, columnNames: Tuple[str, ...] = None):
        """
        Creates a MimirPaginator instance and injects it into the given parent.

        Args:
            items (List): List of strings/items to paginate.
            itemsPerPage (int): Max items per page.
            parent (Widget): The parent container to render into.

        Returns:
            MimirPaginator: Instantiated paginator (with .tree and .buttonGrid as children).
        """
        return MimirPaginator(items, itemsPerPage, parent or self.app, themeManager=self.themeManager, columnNames=columnNames)