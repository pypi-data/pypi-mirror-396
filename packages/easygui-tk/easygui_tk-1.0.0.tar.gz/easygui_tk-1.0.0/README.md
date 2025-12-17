# easygui-tk

**A modern, declarative wrapper for Tkinter.**

`easygui-tk` is a lightweight Python library designed to make building desktop applications fast, readable, and fun. It wraps the standard `tkinter` library in a clean, declarative API, allowing you to build complex interfaces—including layouts, menus, and custom widgets—with minimal code.

## 🚀 Features

* **Declarative Syntax:** Define your entire UI hierarchy in a single `with` block.
* **Lazy Execution:** Windows are configured first and launched only when you're ready.
* **Built-in Themes:** Switch between "Default", "Dark", "SciFi", and "Terminal" instantly, or inject your own.
* **Rich Widgets:** Includes standard inputs plus Tables (Treeview), Date Pickers, Color Pickers, and Canvas support.
* **Layout Management:** Easy-to-use Rows, Tabs, and Scrollable Columns.
* **Modal Dialogs:** Create blocking popup forms to collect user input mid-execution.
* **Zero Dependencies:** Built entirely on the standard library (tkinter, calendar, datetime).

## 📦 Installation

This library is designed to be installed as a local package or via pip.

```bash
pip install easygui-tk
```
(Note: If you are building from source, run pip install -e . in the root directory)

## ⚡ Quick Start

```python
import easygui_tk as eg

def greet(app):
    name = app.get_data("name_field")
    app.msg(f"Hello, {name}!")

# Define the UI Blueprint
with eg.args(title="My First App", theme="Dark") as bp:
    bp.add("label", "Welcome to easygui-tk", font=("Arial", 16, "bold"))
    bp.add_spacer(10)
    
    bp.add("label", "Enter your name:")
    bp.add("inputbox", id="name_field")
    
    bp.add("button", "Say Hello", command=greet)

# Launch the Window
mw = eg.window(bp)
mw()
```
## 📖 Widget Reference
Use bp.add("type", ...) to add widgets. Common arguments include id (to retrieve data later), text, command, and standard styling options like bg, fg, width.

## Basic Inputs
Type	    Description
label	    Static text display.
button	    Clickable button. Calls command(app).
inputbox	Single-line text entry.
textbox	    Multi-line text area.
dropdown	Selection list (Combobox). Use values=["A", "B"].
checkbox	Toggle switch (0 or 1).
radio	    Exclusive selection group. Use values=["A", "B"].


## Visuals
Type	    Description
image	    Displays a PNG/GIF. Use image_path="logo.png".
progress	Progress bar (min, max).
slider	    Draggable scale.
canvas	    Drawing area. Use app.draw() to add shapes dynamically.

## Advanced Widgets
Type	    Description
treeview	Data table. Use columns=["Name", "Age"] and data=[("Alice", 30)].
date	    Input with a popup calendar selector.
color	    Color preview with a popup color chooser.

## 🏗 Layouts

Nest these context managers inside your main with block to organize widgets.

Rows (Side-by-Side):

```python
with bp.row():
    bp.add("button", "Left")
    bp.add("button", "Right")

```

Tabs:

```python
with bp.tabs():
    with bp.tab("General"):
        bp.add("label", "Settings here...")
    with bp.tab("Profile"):
        bp.add("inputbox", id="username")

```

Scrollable Areas:

```python
with bp.scrollable_column(height=300):
    # Add as many widgets as you want here
    for i in range(50):
        bp.add("label", f"Item {i}")

```

## 🎨 Theming

Built-in Themes
Pass theme="Name" to eg.args().

Default (Standard System Look)

Dark (Modern Dark Mode)

SciFi (High Contrast Neon/Black)

Terminal (Green on Black)

Custom Themes
Register your own theme at the start of your script:

```python
eg.add_theme("Ocean", bg="#e0f7fa", fg="#006064", select="#4dd0e1")

with eg.args(theme="Ocean") as bp:
    ...

```

## 🛠 Interaction API

The app object passed to your functions provides powerful tools:

Data: app.get_data("id"), app.set_value("id", val)

Popups: app.msg("Hello"), app.error("Oops"), app.confirm("Are you sure?"), app.ask_string("Name?")

Files: app.open_file(), app.save_file(), app.pick_folder()

Drawing: app.draw("canvas_id", "oval", [x1, y1, x2, y2], fill="red")

Modals: data = app.dialog(blueprint) (Blocks code execution until closed)

## 📄 License
MIT License. Free to use for personal and commercial projects.
