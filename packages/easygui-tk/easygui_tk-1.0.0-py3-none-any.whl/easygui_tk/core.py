"""
easygui-tk core library
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
import contextlib
import calendar
from datetime import datetime

default_size = "600x500"

# --- THEMES ---
THEMES = {
    "Default": {"bg": "#f0f0f0", "fg": "black", "select": "#0078d7", "font": ("Segoe UI", 10)},
    "Dark":    {"bg": "#2b2b2b", "fg": "#ffffff", "select": "#404040", "font": ("Segoe UI", 10)},
    "SciFi":   {"bg": "#050a14", "fg": "#00ffcc", "select": "#004433", "font": ("Courier", 10)},
    "Terminal":{"bg": "#000000", "fg": "#00ff00", "select": "#003300", "font": ("Consolas", 11)}
}

def add_theme(name, bg, fg, select, font_name="Segoe UI", font_size=10):
    """Register a new custom theme."""
    THEMES[name] = {
        "bg": bg, 
        "fg": fg, 
        "select": select, 
        "font": (font_name, font_size)
    }

# --- BUILDER CLASS ---
class args:
    def __init__(self, theme="Default", title="EasyGui App", size=default_size): 
        self.title = title
        self.size = size
        self.widgets = [] 
        self.menus = {}
        self.theme = theme 
        self.current_container = self.widgets

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass

    # --- LAYOUT MANAGERS ---
    @contextlib.contextmanager
    def row(self):
        new_row = {'type': 'row', 'children': []}
        self.current_container.append(new_row)
        parent = self.current_container
        self.current_container = new_row['children']
        try: yield
        finally: self.current_container = parent

    @contextlib.contextmanager
    def tabs(self):
        new_nb = {'type': 'notebook', 'pages': []}
        self.current_container.append(new_nb)
        parent = self.current_container
        self.current_container = new_nb['pages']
        try: yield
        finally: self.current_container = parent

    @contextlib.contextmanager
    def tab(self, title):
        new_page = {'type': 'tab', 'title': title, 'children': []}
        self.current_container.append(new_page)
        parent = self.current_container
        self.current_container = new_page['children']
        try: yield
        finally: self.current_container = parent

    @contextlib.contextmanager
    def scrollable_column(self, height=None):
        new_scroll = {'type': 'scroll_col', 'height': height, 'children': []}
        self.current_container.append(new_scroll)
        parent = self.current_container
        self.current_container = new_scroll['children']
        try: yield
        finally: self.current_container = parent

    # --- WIDGET DEFINITION ---
    def add(self, w_type, text="", id=None, command=None, values=[], image_path=None, 
            min_val=0, max_val=100, context_menu=None, columns=None, data=None, 
            width=None, height=None, tooltip=None, **kwargs):
        self.current_container.append({
            'type': w_type, 'text': text, 'id': id, 
            'command': command, 'values': values, 
            'image_path': image_path, 
            'min': min_val, 'max': max_val,
            'context_menu': context_menu,
            'columns': columns, 'data': data,
            'width': width, 'height': height,
            'tooltip': tooltip,
            'opts': kwargs
        })

    def add_spacer(self, size=20):
        self.current_container.append({'type': 'spacer', 'size': size})
    
    def add_menu(self, menu_name, options):
        self.menus[menu_name] = options

# --- HELPER CLASSES ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                       background="#ffffe0", foreground="black", 
                       relief='solid', borderwidth=1,
                       font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class CalendarDialog(tk.Toplevel):
    def __init__(self, parent, theme_data):
        super().__init__(parent)
        self.title("Select Date")
        self.geometry("250x250")
        self.transient(parent)
        self.grab_set()
        self.selection = None
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.bg = theme_data['bg']
        self.fg = theme_data['fg']
        self.sel_col = theme_data['select']
        self.configure(bg=self.bg)
        
        # Controls
        h_frame = tk.Frame(self, bg=self.bg)
        h_frame.pack(fill='x', pady=5)
        tk.Button(h_frame, text="<", command=self.prev_month, bg=self.bg, fg=self.fg).pack(side='left', padx=5)
        self.lbl_header = tk.Label(h_frame, text="", width=15, font="bold", bg=self.bg, fg=self.fg)
        self.lbl_header.pack(side='left', padx=5)
        tk.Button(h_frame, text=">", command=self.next_month, bg=self.bg, fg=self.fg).pack(side='left', padx=5)
        
        # Grid
        self.grid_frame = tk.Frame(self, bg=self.bg)
        self.grid_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.draw_calendar()

    def draw_calendar(self):
        for w in self.grid_frame.winfo_children(): w.destroy()
        month_name = calendar.month_name[self.month]
        self.lbl_header.config(text=f"{month_name} {self.year}")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(self.grid_frame, text=day, bg=self.bg, fg=self.fg).grid(row=0, column=i)
        cal = calendar.monthcalendar(self.year, self.month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day != 0:
                    btn = tk.Button(self.grid_frame, text=str(day), width=3,
                                    command=lambda d=day: self.select_date(d),
                                    bg=self.bg, fg=self.fg, activebackground=self.sel_col)
                    btn.grid(row=r+1, column=c, padx=1, pady=1)

    def prev_month(self):
        self.month -= 1
        if self.month == 0:
            self.month = 12
            self.year -= 1
        self.draw_calendar()
    def next_month(self):
        self.month += 1
        if self.month == 13:
            self.month = 1
            self.year += 1
        self.draw_calendar()
    def select_date(self, day):
        self.selection = f"{self.year}-{self.month:02d}-{day:02d}"
        self.destroy()

# --- MAIN LOGIC CLASS ---
class BaseWindow:
    def __init__(self):
        self.inputs = {} 
        self.text_widgets = {}
        self.tree_widgets = {} 
        self.canvas_widgets = {} 
        self.images = []

    def build_widgets(self, widget_list, parent, direction="vertical", app_instance=None):
        for item in widget_list:
            if direction == "vertical":
                pack_opts = {'pady': 5, 'padx': 5, 'fill': 'x'}
            else:
                pack_opts = {'side': 'left', 'padx': 5, 'pady': 5, 'fill': 'x', 'expand': True}
            
            extra_opts = item.get('opts', {})
            widget = None

            # --- CONTAINERS ---
            if item['type'] == 'row':
                f = tk.Frame(parent, **extra_opts)
                f.pack(fill='x', pady=0, padx=0)
                self.build_widgets(item['children'], f, "horizontal", app_instance)
            elif item['type'] == 'notebook':
                nb = ttk.Notebook(parent)
                nb.pack(fill='both', expand=True, padx=5, pady=5)
                for page in item['pages']:
                    if page['type'] == 'tab':
                        page_frame = tk.Frame(nb)
                        nb.add(page_frame, text=page['title'])
                        self.build_widgets(page['children'], page_frame, "vertical", app_instance)
            elif item['type'] == 'scroll_col':
                container = tk.Frame(parent)
                container.pack(fill='both', expand=True, pady=5)
                canvas = tk.Canvas(container, highlightthickness=0)
                scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)
                canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                def configure_scroll(event): canvas.configure(scrollregion=canvas.bbox("all"))
                def configure_width(event): canvas.itemconfig(canvas_frame, width=event.width)
                scrollable_frame.bind("<Configure>", configure_scroll)
                canvas.bind("<Configure>", configure_width)
                canvas.configure(yscrollcommand=scrollbar.set)
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                self.build_widgets(item['children'], scrollable_frame, "vertical", app_instance)

            # --- COMPLEX WIDGETS ---
            elif item['type'] == 'treeview':
                container = tk.Frame(parent)
                container.pack(**pack_opts)
                cols = item['columns'] if item['columns'] else []
                tree = ttk.Treeview(container, columns=cols, show='headings', **extra_opts)
                for col in cols:
                    tree.heading(col, text=col)
                    tree.column(col, width=100) 
                if item['data']:
                    for row in item['data']: tree.insert("", tk.END, values=row)
                scrollbar = tk.Scrollbar(container, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                tree.pack(side='left', fill='both', expand=True)
                scrollbar.pack(side='right', fill='y')
                if item['id']: self.tree_widgets[item['id']] = tree
                widget = tree

            elif item['type'] == 'canvas':
                w = item['width'] if item['width'] else 300
                h = item['height'] if item['height'] else 200
                widget = tk.Canvas(parent, width=w, height=h, **extra_opts)
                if item['id']: self.canvas_widgets[item['id']] = widget

            # --- STANDARD WIDGETS ---
            elif item['type'] == 'spacer':
                if direction == "vertical": widget = tk.Frame(parent, height=item['size'], **extra_opts)
                else: widget = tk.Frame(parent, width=item['size'], **extra_opts)
            elif item['type'] == 'label':
                widget = tk.Label(parent, text=item['text'], **extra_opts)
            elif item['type'] == 'button':
                cmd = (lambda func=item['command']: func(app_instance)) if item['command'] else None
                widget = tk.Button(parent, text=item['text'], command=cmd, **extra_opts)
            
            elif item['type'] == 'inputbox': # Renamed from entry
                var = tk.StringVar()
                widget = tk.Entry(parent, textvariable=var, **extra_opts)
                if item['id']: self.inputs[item['id']] = var

            elif item['type'] == 'date':
                f = tk.Frame(parent)
                f.pack(**pack_opts)
                var = tk.StringVar()
                ent = tk.Entry(f, textvariable=var, **extra_opts)
                ent.pack(side='left', fill='x', expand=True)
                def open_cal():
                    theme_name = getattr(app_instance, 'theme_name', 'Default') 
                    t_data = THEMES.get(theme_name, THEMES['Default'])
                    cal = CalendarDialog(parent.winfo_toplevel(), t_data)
                    parent.wait_window(cal) 
                    if cal.selection: var.set(cal.selection)
                btn = tk.Button(f, text="📅", width=3, command=open_cal)
                btn.pack(side='right', padx=2)
                if item['id']: self.inputs[item['id']] = var
                if item.get('tooltip'): ToolTip(ent, item['tooltip'])
                continue 

            elif item['type'] == 'color':
                f = tk.Frame(parent)
                f.pack(**pack_opts)
                default_col = item['values'][0] if item['values'] else "#ffffff"
                var = tk.StringVar(value=default_col)
                preview = tk.Label(f, width=5, bg=var.get(), relief="sunken")
                preview.pack(side='left', padx=5)
                ent = tk.Entry(f, textvariable=var, width=10)
                ent.pack(side='left', padx=5)
                def pick():
                    _, hex_code = colorchooser.askcolor(title="Choose Color", color=var.get())
                    if hex_code:
                        var.set(hex_code)
                        preview.config(bg=hex_code)
                btn = tk.Button(f, text="🎨", width=3, command=pick)
                btn.pack(side='left', padx=2)
                if item['id']: self.inputs[item['id']] = var
                if item.get('tooltip'): ToolTip(btn, item['tooltip'])
                continue

            elif item['type'] == 'dropdown':
                var = tk.StringVar()
                widget = ttk.Combobox(parent, textvariable=var, values=item['values'], **extra_opts)
                if item['values']: widget.current(0)
                if item['id']: self.inputs[item['id']] = var
            elif item['type'] == 'checkbox':
                var = tk.IntVar()
                widget = tk.Checkbutton(parent, text=item['text'], variable=var, onvalue=1, offvalue=0, **extra_opts)
                if item['id']: self.inputs[item['id']] = var
            elif item['type'] == 'textbox':
                if 'height' not in extra_opts: extra_opts['height'] = 5
                widget = tk.Text(parent, **extra_opts)
                if item['id']: self.text_widgets[item['id']] = widget
            elif item['type'] == 'radio':
                var = tk.StringVar()
                if item['values']: var.set(item['values'][0])
                widget = tk.Frame(parent)
                for val in item['values']:
                    tk.Radiobutton(widget, text=val, value=val, variable=var, **extra_opts).pack(side='left')
                if item['id']: self.inputs[item['id']] = var
            elif item['type'] == 'image':
                try:
                    img = tk.PhotoImage(file=item['image_path'])
                    self.images.append(img) 
                    widget = tk.Label(parent, image=img, **extra_opts)
                except: widget = tk.Label(parent, text=f"[Image Error]", fg="red")
            elif item['type'] == 'progress':
                var = tk.DoubleVar(value=item['min']) 
                widget = ttk.Progressbar(parent, variable=var, maximum=item['max'], **extra_opts)
                if item['id']: self.inputs[item['id']] = var
            elif item['type'] == 'slider':
                var = tk.DoubleVar(value=item['min'])
                orient = extra_opts.pop('orient', 'horizontal') 
                widget = tk.Scale(parent, from_=item['min'], to=item['max'], orient=orient, variable=var, **extra_opts)
                if item['id']: self.inputs[item['id']] = var

            # --- FINALIZE WIDGET ---
            if widget:
                if item['type'] == 'spacer':
                     if direction == "vertical": widget.pack()
                     else: widget.pack(side='left')
                elif item['type'] != 'treeview': 
                    widget.pack(**pack_opts)
                if item.get('context_menu'):
                    self.attach_context_menu(widget, item['context_menu'], app_instance)
                if item.get('tooltip'):
                    ToolTip(widget, item['tooltip'])

    def attach_context_menu(self, widget, options, app_instance):
        menu = tk.Menu(widget, tearoff=0)
        for opt in options:
            if isinstance(opt, tuple):
                label, func = opt
                cmd = lambda f=func: f(app_instance)
                menu.add_command(label=label, command=cmd)
            else: menu.add_command(label=opt)
        def do_popup(event):
            try: menu.tk_popup(event.x_root, event.y_root)
            finally: menu.grab_release()
        widget.bind("<Button-3>", do_popup)

    def apply_theme(self, theme_name, root_element):
        if theme_name not in THEMES: theme_name = "Default"
        t = THEMES[theme_name]
        root_element.tk_setPalette(background=t['bg'], foreground=t['fg'], 
                                   activeBackground=t['select'], activeForeground=t['fg'])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=t['bg'], foreground=t['fg'], fieldbackground=t['select'])
        style.configure("Treeview", background=t['bg'], foreground=t['fg'], fieldbackground=t['bg'])
        style.map("Treeview", background=[("selected", t['select'])])
        style.configure("Treeview.Heading", background=t['select'], foreground=t['fg'])
        style.configure("TNotebook", background=t['bg'])
        style.configure("TNotebook.Tab", background=t['bg'], foreground=t['fg'], padding=[10, 2])
        style.map("TNotebook.Tab", background=[("selected", t['select'])])
        style.configure("TEntry", fieldbackground=t['bg'], foreground=t['fg'])
        style.configure("TCombobox", fieldbackground=t['bg'], foreground=t['fg'])
        root_element.option_add("*Font", t['font'])

    # --- PUBLIC API ---
    def dialog(self, blueprint):
        d = Dialog(self.root, blueprint)
        self.root.wait_window(d.root)
        return d.final_data

    def save_file(self, title="Save File", default_name="", filetypes=None, initial_dir=None):
        if filetypes is None: filetypes = [("All Files", "*.*")]
        def_ext = filetypes[0][1].replace("*", "") if filetypes else ""
        return filedialog.asksaveasfilename(title=title, initialfile=default_name, 
                                            initialdir=initial_dir, filetypes=filetypes, defaultextension=def_ext)
    def open_file(self, title="Open File", filetypes=None, initial_dir=None):
        if filetypes is None: filetypes = [("All Files", "*.*")]
        return filedialog.askopenfilename(title=title, initialdir=initial_dir, filetypes=filetypes)
    def pick_folder(self, title="Select Folder"):
        return filedialog.askdirectory(title=title)
    def pick_color(self, title="Pick Color"):
        _, hex_code = colorchooser.askcolor(title=title)
        return hex_code
    
    def msg(self, message, title="Message"): messagebox.showinfo(title, message)
    def error(self, message, title="Error"): messagebox.showerror(title, message)
    def confirm(self, message, title="Confirm"): return messagebox.askyesno(title, message)
    def ask_string(self, prompt, title="Input"): return simpledialog.askstring(title, prompt)

    def set_value(self, id, value):
        if id in self.inputs: self.inputs[id].set(value)
        elif id in self.text_widgets: 
            self.text_widgets[id].delete("1.0", tk.END)
            self.text_widgets[id].insert("1.0", value)
    def get_data(self, key): 
        if key in self.inputs: return self.inputs[key].get()
        if key in self.text_widgets: return self.text_widgets[key].get("1.0", "end-1c")
        if key in self.tree_widgets: return self.get_selection(key)
        return None
    def get_selection(self, id):
        if id in self.tree_widgets:
            tree = self.tree_widgets[id]
            selected_item = tree.focus()
            if selected_item: return tree.item(selected_item)['values']
        return None
    def draw(self, id, shape, coords, **kwargs):
        if id in self.canvas_widgets:
            c = self.canvas_widgets[id]
            if shape == 'line': c.create_line(coords, **kwargs)
            elif shape == 'rectangle': c.create_rectangle(coords, **kwargs)
            elif shape == 'oval': c.create_oval(coords, **kwargs)
            elif shape == 'text': c.create_text(coords[0:2], **kwargs)
            elif shape == 'polygon': c.create_polygon(coords, **kwargs)
    def clear_canvas(self, id):
        if id in self.canvas_widgets: self.canvas_widgets[id].delete("all")

# --- WINDOW IMPLEMENTATIONS ---
class Dialog(BaseWindow):
    def __init__(self, master, blueprint):
        super().__init__()
        self.root = tk.Toplevel(master)
        self.root.title(blueprint.title)
        self.root.geometry(blueprint.size)
        self.root.transient(master)
        self.root.grab_set()
        self.final_data = {}
        self.theme_name = blueprint.theme 
        self.apply_theme(blueprint.theme, self.root)
        self.build_widgets(blueprint.widgets, self.root, "vertical", self)
    def close(self):
        self.final_data = {k: v.get() for k, v in self.inputs.items()}
        for k, w in self.text_widgets.items(): self.final_data[k] = w.get("1.0", "end-1c")
        self.root.destroy()

class ChildWindow(BaseWindow):
    def __init__(self, master, blueprint):
        super().__init__()
        self.root = tk.Toplevel(master)
        self.root.title(blueprint.title)
        self.root.geometry(blueprint.size)
        self.theme_name = blueprint.theme
        self.apply_theme(blueprint.theme, self.root)
        self.build_widgets(blueprint.widgets, self.root, "vertical", self)
    def close(self): self.root.destroy()

class window(BaseWindow):
    def __init__(self, blueprint):
        super().__init__()
        self.root = tk.Tk()
        self.root.title(blueprint.title)
        self.root.geometry(blueprint.size)
        self.theme_name = blueprint.theme 
        self.apply_theme(blueprint.theme, self.root)
        if blueprint.menus:
            menubar = tk.Menu(self.root)
            for name, items in blueprint.menus.items():
                file_menu = tk.Menu(menubar, tearoff=0)
                for item in items:
                    if isinstance(item, str):
                        if item == "---": file_menu.add_separator()
                        else: file_menu.add_command(label=item)
                    elif isinstance(item, tuple):
                        lbl, func = item[0], item[1]
                        shortcut = item[2] if len(item) > 2 else None
                        cmd = lambda f=func: f(self)
                        if shortcut:
                            pretty_accel = shortcut.replace("Control", "Ctrl").replace("-", "+").title()
                            file_menu.add_command(label=lbl, command=cmd, accelerator=pretty_accel)
                            self.root.bind(f"<{shortcut}>", lambda event, f=cmd: f())
                        else: file_menu.add_command(label=lbl, command=cmd)
                menubar.add_cascade(label=name, menu=file_menu)
            self.root.config(menu=menubar)
        self.build_widgets(blueprint.widgets, self.root, "vertical", self)

    def open_child(self, blueprint): return ChildWindow(self.root, blueprint)
    def close(self): self.root.destroy()
    def __call__(self):
        self.root.mainloop()
        return {}
