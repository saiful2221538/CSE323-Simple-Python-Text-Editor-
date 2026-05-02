"""
ui.py
Main application window.
Mirrors Java UI class.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, font as tkfont
from tkinter import ttk
from PIL import Image, ImageTk

import simple_text_editor as app_info
from fedit import FEdit
from find import Find
from about import About
from highlight_text import HighlightText
from auto_complete import AutoComplete
from supported_keywords import SupportedKeywords

# ---------------------------------------------------------------------------
# Helper: resolve the icons folder relative to this file
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ICONS_DIR = os.path.join(_HERE, "icons")


def _load_icon(name: str, size: tuple[int, int] = (20, 20)) -> ImageTk.PhotoImage | None:
    """Load a PNG icon from the icons/ folder.  Returns None on failure."""
    path = os.path.join(_ICONS_DIR, f"{name}.png")
    try:
        img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class UI(tk.Tk):
    """
    Main editor window. Mirrors Java UI (JFrame) class.
    All features: File menu, Edit menu, Search, About, toolbar,
    font picker, syntax highlighting, drag-and-drop, autocomplete.
    """

    DRAG_DROP_EXTENSIONS = {".txt", ".dat", ".log", ".xml", ".mf", ".html"}

    def __init__(self):
        super().__init__()
        self.title(f"Untitled | {app_info.NAME}")
        self.geometry("900x600")

        # ---- Load all icons (kept as instance attrs to prevent GC) ----
        self._icons: dict[str, ImageTk.PhotoImage | None] = {}
        for name in (
            "new", "open", "save", "clear", "search",
            "about", "about_me", "close",
            "bold", "italic", "wordwrap",
            "copy", "cut", "paste", "selectall",
        ):
            self._icons[name] = _load_icon(name)

        # ---- App window icon ----
        app_icon = _load_icon("ste", size=(32, 32))
        if app_icon:
            self.iconphoto(True, app_icon)
            self._icons["ste"] = app_icon  # keep reference

        self._kw = SupportedKeywords()
        self._highlighter = HighlightText("lightgray")
        self._autocomplete: AutoComplete | None = None
        self._has_listener = False
        self._edited = False
        self._current_file: str | None = None

        self._build_toolbar()
        self._build_text_area()
        self._build_menu()
        self._bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------ #
    #  Build UI                                                            #
    # ------------------------------------------------------------------ #

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        def tb_btn(icon_name: str, label: str, cmd, tooltip: str = ""):
            icon = self._icons.get(icon_name)
            if icon:
                b = tk.Button(toolbar, image=icon, command=cmd,
                              relief=tk.FLAT, padx=3, pady=2,
                              cursor="hand2")
            else:
                b = tk.Button(toolbar, text=label, command=cmd,
                              relief=tk.FLAT, padx=4, pady=2,
                              cursor="hand2")
            b.pack(side=tk.LEFT, padx=1, pady=1)
            _Tooltip(b, tooltip)
            return b

        sep = lambda: ttk.Separator(toolbar, orient="vertical")

        tb_btn("new",      "New",            self._new_file,      "New file (Ctrl+N)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("open",     "Open",           self._open_file,     "Open file (Ctrl+O)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("save",     "Save",           self._save_file,     "Save file (Ctrl+S)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("clear",    "Clear",          self._clear_file,    "Clear all text (Ctrl+K)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("cut",      "Cut",            lambda: self._text.event_generate("<<Cut>>"),   "Cut (Ctrl+X)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("copy",     "Copy",           lambda: self._text.event_generate("<<Copy>>"),  "Copy (Ctrl+C)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("paste",    "Paste",          lambda: self._text.event_generate("<<Paste>>"), "Paste (Ctrl+V)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("selectall","Select All",     lambda: self._text.tag_add(tk.SEL, "1.0", tk.END), "Select All (Ctrl+A)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("search",   "🔍 Find",        self._open_find,     "Quick search (Ctrl+F)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("wordwrap", "Word Wrap",      self._toggle_word_wrap, "Toggle word wrap (Ctrl+W)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("bold",     "Bold",           self._toggle_bold,   "Toggle bold")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("italic",   "Italic",         self._toggle_italic, "Toggle italic")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("about_me", "About Me",       self._about_me,      "About the author (F1)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("about",    "About Software", self._about_software,"About this software (F2)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)
        tb_btn("close",    "Quit",           self._on_close,      "Quit (Ctrl+Q)")
        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # ---- Font family picker ----
        all_fonts = sorted(tkfont.families())
        self._font_family_var = tk.StringVar(value="Courier")
        font_box = ttk.Combobox(toolbar, textvariable=self._font_family_var,
                                values=all_fonts, width=22, state="readonly")
        font_box.pack(side=tk.LEFT, padx=2)
        font_box.bind("<<ComboboxSelected>>", self._on_font_change)

        sep().pack(side=tk.LEFT, fill=tk.Y, padx=2)

        # ---- Font size picker ----
        self._font_size_var = tk.IntVar(value=12)
        size_box = ttk.Combobox(toolbar, textvariable=self._font_size_var,
                                values=list(range(5, 101)), width=5, state="readonly")
        size_box.pack(side=tk.LEFT, padx=2)
        size_box.bind("<<ComboboxSelected>>", self._on_font_change)

    def _build_text_area(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._text = tk.Text(
            frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Courier", 12),
            undo=True,
            tabs=("1c",),
        )
        self._text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._text.yview)

        self._text.bind("<Key>", self._on_key_press, add="+")

        self._text.drop_target_register = lambda *a: None
        try:
            self._text.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _build_menu(self):
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New",  accelerator="Ctrl+N", command=self._new_file)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self._open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", accelerator="Ctrl+Q", command=self._on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Select All",  accelerator="Ctrl+A", command=lambda: self._text.tag_add(tk.SEL, "1.0", tk.END))
        edit_menu.add_command(label="Clear",       accelerator="Ctrl+K", command=self._clear_file)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut",         accelerator="Ctrl+X", command=lambda: self._text.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy",        accelerator="Ctrl+C", command=lambda: self._text.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste",       accelerator="Ctrl+V", command=lambda: self._text.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Word Wrap",   accelerator="Ctrl+W", command=self._toggle_word_wrap)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # Search menu
        search_menu = tk.Menu(menubar, tearoff=0)
        search_menu.add_command(label="Quick Find", accelerator="Ctrl+F", command=self._open_find)
        menubar.add_cascade(label="Search", menu=search_menu)

        # About menu
        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="About Me",       accelerator="F1", command=self._about_me)
        about_menu.add_command(label="About Software", accelerator="F2", command=self._about_software)
        menubar.add_cascade(label="About", menu=about_menu)

        self.config(menu=menubar)

    def _bind_shortcuts(self):
        self.bind_all("<Control-n>", lambda e: self._new_file())
        self.bind_all("<Control-o>", lambda e: self._open_file())
        self.bind_all("<Control-s>", lambda e: self._save_file())
        self.bind_all("<Control-q>", lambda e: self._on_close())
        self.bind_all("<Control-k>", lambda e: self._clear_file())
        self.bind_all("<Control-f>", lambda e: self._open_find())
        self.bind_all("<Control-w>", lambda e: self._toggle_word_wrap())
        self.bind_all("<F1>",        lambda e: self._about_me())
        self.bind_all("<F2>",        lambda e: self._about_software())

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _update_title(self):
        content = self._text.get("1.0", tk.END)
        lines = content.count("\n") or 1
        words = len(content.split())
        chars = len(content) - 1
        name = os.path.basename(self._current_file) if self._current_file else "Untitled"
        self.title(
            f"{name} | {app_info.NAME}     "
            f"[ Length: {chars}    Lines: {lines}    Words: {words} ]"
        )

    def _on_key_press(self, event=None):
        self._edited = True
        self._update_title()
        all_kw = self._kw.get_java_keywords() + self._kw.get_cpp_keywords()
        self._highlighter.highlight(self._text, all_kw)

    def _ask_save_before(self, action_label="continue") -> bool:
        if not self._edited:
            return True
        choice = messagebox.askyesnocancel(
            "Unsaved changes",
            f"Do you want to save the file before you {action_label}?"
        )
        if choice is True:
            self._save_file()
            return True
        elif choice is False:
            return True
        else:
            return False

    def _enable_autocomplete(self, filepath: str):
        if self._has_listener and self._autocomplete:
            self._autocomplete.detach()
            self._has_listener = False

        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".java":
            keywords = self._kw.set_keywords(self._kw.get_java_keywords())
        elif ext in (".cpp", ".c", ".h"):
            keywords = self._kw.set_keywords(self._kw.get_cpp_keywords())
        else:
            return

        self._autocomplete = AutoComplete(self._text, keywords)
        self._has_listener = True

    # ------------------------------------------------------------------ #
    #  Font                                                                #
    # ------------------------------------------------------------------ #

    def _current_font(self) -> tkfont.Font:
        return tkfont.Font(font=self._text.cget("font"))

    def _on_font_change(self, event=None):
        family = self._font_family_var.get()
        size = self._font_size_var.get()
        self._text.config(font=(family, size))

    def _toggle_bold(self):
        f = self._current_font()
        weight = "normal" if f.actual("weight") == "bold" else "bold"
        self._text.config(font=(f.actual("family"), f.actual("size"), weight))

    def _toggle_italic(self):
        f = self._current_font()
        slant = "roman" if f.actual("slant") == "italic" else "italic"
        self._text.config(font=(f.actual("family"), f.actual("size"), slant))

    # ------------------------------------------------------------------ #
    #  File operations                                                     #
    # ------------------------------------------------------------------ #

    def _new_file(self):
        if not self._ask_save_before("open a new file"):
            return
        FEdit.clear(self._text)
        self._current_file = None
        self._edited = False
        self.title(f"Untitled | {app_info.NAME}")

    def _open_file(self):
        if not self._ask_save_before("open another file"):
            return
        path = filedialog.askopenfilename(
            filetypes=[
                ("Text files", "*.txt *.dat *.log *.xml *.mf *.html *.java *.cpp *.c *.h"),
                ("All files", "*.*"),
            ]
        )
        if path:
            FEdit.clear(self._text)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    self._text.insert("1.0", f.read())
                self._current_file = path
                self._edited = False
                self._enable_autocomplete(path)
                self._update_title()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

    def _save_file(self):
        path = self._current_file or filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._text.get("1.0", tk.END))
                self._current_file = path
                self._edited = False
                self._enable_autocomplete(path)
                self._update_title()
            except Exception as ex:
                messagebox.showerror("Error", str(ex))

    def _clear_file(self):
        if messagebox.askyesno("Clear", "Are you sure you want to clear the text area?"):
            FEdit.clear(self._text)
            self._edited = False

    def _toggle_word_wrap(self):
        current = self._text.cget("wrap")
        self._text.config(wrap=tk.NONE if current != tk.NONE else tk.WORD)

    # ------------------------------------------------------------------ #
    #  Dialogs                                                             #
    # ------------------------------------------------------------------ #

    def _open_find(self):
        Find(self._text)

    def _about_me(self):
        dlg = About(self)
        dlg.show_me()

    def _about_software(self):
        dlg = About(self)
        dlg.show_software()

    # ------------------------------------------------------------------ #
    #  Window close                                                        #
    # ------------------------------------------------------------------ #

    def _on_close(self):
        if self._edited:
            choice = messagebox.askyesnocancel(
                "Quit", "Do you want to save the file before quitting?"
            )
            if choice is True:
                self._save_file()
                self.destroy()
            elif choice is False:
                self.destroy()
        else:
            self.destroy()

    # ------------------------------------------------------------------ #
    #  Drag and drop                                                       #
    # ------------------------------------------------------------------ #

    def _on_drop(self, event):
        raw = event.data
        path = raw.strip("{}").strip()
        ext = os.path.splitext(path)[1].lower()
        if ext not in self.DRAG_DROP_EXTENSIONS:
            messagebox.showerror("Error", "This file type is not allowed for drag & drop.")
            return
        if not self._ask_save_before("open the dropped file"):
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                FEdit.clear(self._text)
                self._text.insert("1.0", f.read())
            self._current_file = path
            self._edited = False
            self._update_title()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))


# ------------------------------------------------------------------ #
#  Lightweight tooltip widget                                          #
# ------------------------------------------------------------------ #

class _Tooltip:
    """Show a small tooltip label when the mouse hovers over a widget."""

    def __init__(self, widget: tk.Widget, text: str):
        self._widget = widget
        self._text = text
        self._tip: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, event=None):
        if not self._text or self._tip:
            return
        x = self._widget.winfo_rootx() + 2
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 2
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._tip, text=self._text, justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("TkDefaultFont", 8),
        ).pack(ipadx=4, ipady=2)

    def _hide(self, event=None):
        if self._tip:
            self._tip.destroy()
            self._tip = None
