# Jabs Mimir

**Jabs Mimir** is a lightweight, extensible UI micro-framework built on top of `tkinter` and `ttkbootstrap`, designed for rapid internal tool development and structured form workflows.

It provides:

- Reusable UI primitives with validation and tooltips
- Support for block-based form components with dynamic variable binding
- Integration with custom validation logic (via resolver, file loader, or direct function)
- Modular architecture suitable for internal tooling and small boilerplate projects

---

## Installation

```bash
pip install jabs-mimir
```

---

## Quick Start

```python
from jabs_mimir import Mimir, DataBlockWrapper, UtilityModule
import tkinter as tk
import ttkbootstrap as tb

class App(tb.Window):
    def __init__(self):
        super().__init__(title="Mimir Demo")
        self.ui = Mimir(self)
        self.testBlocks = []

        # Option 1: Inline validator resolver (string-based)
        self.ui.setValidatorResolver(lambda name: {
            "not_empty": lambda val: bool(str(val).strip())
        }.get(name))

        # Option 2 (alternative): load from file
        # self.ui.setValidatorFile("include/validator.py")

        self.ui.switchView(self.mainView)

    def mainView(self, ui, *args):
        index = len(self.testBlocks)
        frame = tb.Frame(self)
        fields = [
            {"type": "heading", "label": "Basic Info"},
            {"label": "Name", "key": "name", "variable": tk.StringVar(), "validation": "not_empty"},
            {"label": "Age", "key": "age", "variable": tk.IntVar()}
        ]

        meta = UtilityModule.buildBlockMeta(fields)
        block = DataBlockWrapper(meta)

        ui.renderBlockUI(
            container=frame,
            fields=fields,
            blockList=self.testBlocks,
            meta={"storeID": index},
            label=f"Label {index}",
            layout="vertical"
            )
        ui.addNextButton(frame, row=len(fields)+1, viewFunc=self.mainView)

        return frame

if __name__ == "__main__":
    app = App()
    app.mainloop()
```

---

## Validation

Jabs Mimir supports **both automatic and manual validation**, triggered on field focus-out and verified again when clicking "Next".

### You can define validation in two ways:

#### 1. **String-based validation (via file or resolver)**

**Define a validator in a file**:

```python
# include/validator.py
def not_empty(value):
    return bool(str(value).strip())
```

**Load it**:

```python
self.ui.setValidatorFile("include/validator.py")
```

**Use string key in field**:

```python
{"label": "Name", "variable": tk.StringVar(), "validation": "not_empty"}
```

#### 2. **Direct function reference**

```python
from include.validator import not_empty

fields = [
    {"label": "Name", "variable": tk.StringVar(), "validation": not_empty}
]
```

Both methods are fully supported and interchangeable.

Mimir automatically:
- Binds validation on focus-out
- Stores all validators internally
- Re-validates all fields when clicking "Next"
- Blocks navigation if any invalid inputs remain
- Highlights invalid fields with red styling

Works even for readonly fields (like file upload paths), which normally can't be focused.

---

## Buttons & Navigation

Mimir provides helpers for both view transitions and general-purpose action buttons.

### `addNextButton(...)`

Use this when you want a button that:
- Runs validation on all fields
- Automatically switches to a new view
- Looks like a "next step" button

```python
self.ui.addNextButton(parent, row=5, viewFunc=initERPInput, label="Next")
```

### `addButton(...)`

Use this when you want full control over what happens on click.
- Can be used with or without validation (`validate=True` or `False`)
- Perfect for "Save", "Preview", or conditional logic buttons

```python
self.ui.addButton(parent, row=6, command=self.doSomething, label="Save", validate=True)
```

If you just want to go to the next frame **with validation**, use `addNextButton`. If you want to run custom logic (e.g. saving data, previewing content, or optionally switching views), use `addButton` instead.

---

## Working with Blocks

Mimir makes it easy to group inputs into reusable, structured blocks of fields (also called *Data Blocks*). These blocks:

- Are defined using a list of field dictionaries
- Can be rendered vertically or horizontally
- Are assigned metadata for identification (`store_id`, `custom_label`, etc.)
- Can be validated, modified, and repeated dynamically
- Wrap all data in a `DataBlockWrapper`

### Creating a Field Block

```python
fields = [
    {"type": "heading", "label": "Store 1"},
    {"label": "Cash", "key": "cash", "variable": tk.DoubleVar()},
    {"label": "Card", "key": "card", "variable": tk.DoubleVar()}
]

meta = UtilityModule.buildBlockMeta(fields, store_id=1)
block = DataBlockWrapper(meta)
```

### Rendering a Block in the UI

```python
self.blocks = []

self.ui.renderBlockUI(
    container=frame,
    fields=fields,
    blockList=self.blocks,
    layout="vertical",
    label="Store 1",
    meta={"store_id": 1}
)
```

This will create a labeled block frame (with remove button), populate it with your fields, and store the block object in `self.blocks`.

### Accessing Block Data

```python
for block in self.blocks:
    print("Cash:", block.get("cash").get())
    print("Card:", block.get("card").get())
```

You can also loop through and validate them with:

```python
valid_blocks = [b for b in self.blocks if UtilityModule.isBlockValid(b)]
```

### Repeating Dynamic Blocks

```python
for i in range(5):
    self.ui.renderBlockUI(
        container=frame,
        fields=fields,
        blockList=self.blocks,
        label=f"Store {i+1}",
        meta={"store_id": i+1}
    )
```

---

## InfoBox (Information Panels)

Mimir allows you to create **information panels** ("info boxes") easily, styled consistently with your forms.  
You can choose to render them **with or without a border**.

### Basic Example

```python
self.ui.addInfoBox(
    parent=frame,
    row=0,
    text="This is important information for the user to know.",
    label="Important Info",    # Optional title
    border=True                # Optional, default is True
)
```

This will create a framed info box (LabelFrame) at the top of your form.

---

### Borderless InfoBox

If you prefer a clean info panel without a frame or border:

```python
self.ui.addInfoBox(
    parent=frame,
    row=0,
    text="This text will be shown without a surrounding frame.",
    border=False
)
```

When `border=False`, the label title is ignored and only the text is shown inside a standard frame.

---

### How It Works

Internally, the InfoBox:

- Expands horizontally to match the parent container
- Uses the same font and style as the rest of your form
- Supports text wrapping (default 500px)
- Optionally resizes dynamically if you bind a `<Configure>` event
- Fits naturally into both block-style layouts and simple forms

---
# Creating Custom Field Types

Mimir supports **custom, reusable field types** through the `registerFieldType()` method.  
This makes it easy to extend the UI with your own specialized inputs without modifying the core library.

You can register any type of widget — like a `DatePicker`, a custom file selector, a styled text input, etc.

---

## How to Create a Custom Field Type

1. **Define a Renderer Function**  
   A renderer is a function that receives the parent container, row number, and the field definition, and **creates the widget**.

2. **Register the Renderer**  
   Tell Mimir about your new field type with `registerFieldType(name, renderer)`.

3. **Use Your New Field Type**  
   In your field definitions, specify your custom type via `{"type": "your_type", ...}`.

---

## Example: Custom Rating Field

### Step 1: Create a Renderer

```python
def ratingRenderer(parent, row, field):
    import ttkbootstrap as tb
    from tkinter import IntVar

    var = field["variable"]
    var.set(var.get() or 3)  # Default rating

    row_pad = {"padx": 10, "pady": 4}
    label = field.get("label", "Rating")

    tb.Label(parent, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="e")

    combo = tb.Combobox(
        parent,
        textvariable=var,
        values=[1, 2, 3, 4, 5],
        state="readonly",
        width=5
    )
    combo.grid(row=row, column=1, sticky="w", padx=10, pady=5)
    return combo
```

### Step 2: Register It

```python
self.ui.registerFieldType("rating", ratingRenderer)
```

### Step 3: Use It

```python
fields = [
    {"label": "Satisfaction", "key": "rating", "variable": tk.IntVar(), "type": "rating"}
]
```

---

### Important Notes

- Your custom renderer must return the widget if you want automatic validation (focus-out validation) to work.
- Your renderer can return `None` if no validation is needed.
- Mimir will automatically attach validation if the widget supports `.get()`.

---

### Final Tip

You can pass additional widget customization through `options`, e.g.:

```python
{
    "label": "Rating",
    "key": "rating",
    "type": "rating",
    "variable": tk.IntVar(),
    "options": {
        "min": 1,
        "max": 5
    }
}
```

Then in your renderer:

```python
options = field.get("options", {})
min_val = options.get("min", 1)
max_val = options.get("max", 5)
values = list(range(min_val, max_val + 1))
```
---

## `addTabbedView(...)`

The `addTabbedView()` method in Mimir creates a full-featured tabbed interface (`ttkbootstrap.Notebook`) and simplifies layout setup for each tab's content.

You define tabs using a list of dictionaries, each with a `label` and a `view` function. Optionally, you can make individual tabs scrollable by setting `"scrollable": True`.

All layout is handled internally — no need to manually grid or configure rows/columns in your view functions.

---

### **Signature**

```python
addTabbedView(tabs, parent=None, row=0, column=0, columnspan=1, rowspan=1,
              sticky="nsew", fit=True, background="#f8f9fa")
```

---

### **Parameters**

| Name         | Type     | Description                                                                 |
|--------------|----------|-----------------------------------------------------------------------------|
| `tabs`       | list     | List of dicts: each tab requires a `"label"` and `"view"` function.         |
| `parent`     | Widget   | Optional parent widget. Defaults to the main app frame (`self.app`).        |
| `row`        | int      | Row to place the notebook in.                                               |
| `column`     | int      | Column to place the notebook in.                                            |
| `columnspan` | int      | How many columns the notebook spans.                                        |
| `rowspan`    | int      | How many rows the notebook spans.                                           |
| `sticky`     | str      | Tkinter sticky setting (default: `"nsew"`).                                 |
| `fit`        | bool     | If `True`, automatically configures the parent grid to expand.              |
| `background` | str      | Optional background color for the parent frame.                             |

---

### **Tab Definition Format**

Each tab in the `tabs` list is a dictionary with:

- `"label"` *(str)* – Text to show on the tab
- `"view"` *(callable)* – Function that returns a `Frame` to render in the tab
- `"scrollable"` *(optional, bool)* – If `True`, wraps content in a `ScrolledFrame`

Example:

```python
tabs = [
    {"label": "Overview", "view": self.tabOverview},
    {"label": "Settings", "view": self.tabSettings, "scrollable": True}
]
```

---

### **How to Use**

```python
def mainView(self, ui, *args):
    tabs = [
        {"label": "User Form", "view": self.tabUserForm},
        {"label": "Preview", "view": self.tabPreview, "scrollable": True}
    ]
    return ui.addTabbedView(tabs)
```

Each `tabXyz()` method should look like this:

```python
def tabUserForm(self, ui, parent):
    frame = tb.Frame(parent)  # No need to grid it!
    # ... add widgets ...
    return frame
```

If `scrollable: True` is used, `parent` will be a `ScrolledFrame`.  
If not, it's just a regular `ttkbootstrap.Frame`. Either way, the layout is ready to use.

---

### ✅ Benefits

- Minimal boilerplate
- Automatic grid + expansion
- Scroll support per tab
- Works seamlessly with your view-based navigation

---

## Pagination (MimirPaginator)

When working with long lists of rows or items, you can use Mimir's built-in pagination helper to render paged `Treeview` tables with a consistent style and layout.

The paginator creates:
- A `Treeview` for displaying paginated items
- A navigation grid with "Previous", "Next", and page indicators
- Highlighting and theme-aware row styling

### Basic Usage

You can create a paginator using `createPaginator()`:

```python
paginatorFrame = self.ui.createPaginator(
    items=rows,             # List of items to paginate (rows of text or tuples)
    itemsPerPage=10,        # Number of items per page
    parent=frame            # Parent container to render into
)
```

This returns a `Frame` containing both the table and the navigation buttons.  
Simply pack or grid `paginatorFrame` wherever you want in your layout.

### Input Format

- The `items` list should contain strings or lists/tuples of values to show in each row.
- The paginator auto-detects and formats strings into a single-column tree, or tuples into a multi-column layout.

### Example

```python
rows = [("Store A", 1023.50), ("Store B", 880.00), ("Store C", 1123.90)]
frame = tb.Frame(self)
paginatorFrame = self.ui.createPaginator(items=rows, itemsPerPage=5, parent=frame)
paginatorFrame.pack(fill="both", expand=True)
```

If the list exceeds the page size, navigation buttons will appear at the bottom automatically.

### Style and Theme Integration

The paginator:
- Uses ttkbootstrap styling (theme-aware)
- Applies alternating row colors (odd/even)
- Automatically updates on theme change
- Supports hover highlight effects for better UX

You don't need to call any manual styling functions — Mimir handles this through `MimirThemeManager`.

---

### Advanced Usage

If you need to access the `Treeview` directly (e.g. to bind custom context menus), you can still use the full paginator object:

```python
paginator = self.ui.createPaginator(...)  # returns MimirPaginator
tree = paginator.tree
```

…but for most use cases, just returning the `frame` is simpler and preferred.

---

### When to Use

Use `createPaginator()` when:
- You want to display many rows in a scrollable, paged table
- You want to offload pagination logic to Mimir
- You want consistent Treeview theming and navigation controls

You can combine this with block UIs, tabbed views, and InfoBoxes — all layouts work together seamlessly.

---


## Components

### `Mimir`
Manages UI views, tooltips, validation, field rendering, and form logic.  
Supports reusable custom field types via `registerFieldType()`.

### `DataBlockWrapper`
A wrapper for block-level form metadata and values.  
Supports dot-access and `.get()`/`.set()` calls.

### `UtilityModule`
Helper methods for building field metadata, extracting values, validating blocks, and block meta handling.

---

## License

MIT License © 2025 William Lydahl
