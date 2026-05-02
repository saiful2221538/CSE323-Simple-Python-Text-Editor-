"""
find.py
Find and Replace dialog window.
Mirrors Java Find class.
"""

import tkinter as tk
from tkinter import messagebox


class Find(tk.Toplevel):
    """Find and Replace dialog. Mirrors Java Find class."""

    def __init__(self, text_widget: tk.Text):
        super().__init__()
        self.text_widget = text_widget
        self.start_index = "1.0"

        self.title("Find & Replace")
        self.resizable(False, False)
        self.geometry("380x160")

        # ---- Labels ----
        tk.Label(self, text="Find:").place(x=10, y=10, width=80, height=20)
        tk.Label(self, text="Replace:").place(x=10, y=40, width=80, height=20)

        # ---- Text fields ----
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        tk.Entry(self, textvariable=self.find_var).place(x=90, y=10, width=120, height=20)
        tk.Entry(self, textvariable=self.replace_var).place(x=90, y=40, width=120, height=20)

        # ---- Buttons ----
        btn_x, btn_w, btn_h = 225, 115, 22
        tk.Button(self, text="Find",        command=self.find       ).place(x=btn_x, y=6,  width=btn_w, height=btn_h)
        tk.Button(self, text="Find Next",   command=self.find_next  ).place(x=btn_x, y=30, width=btn_w, height=btn_h)
        tk.Button(self, text="Replace",     command=self.replace    ).place(x=btn_x, y=54, width=btn_w, height=btn_h)
        tk.Button(self, text="Replace All", command=self.replace_all).place(x=btn_x, y=78, width=btn_w, height=btn_h)
        tk.Button(self, text="Cancel",      command=self.destroy    ).place(x=btn_x, y=102, width=btn_w, height=btn_h)

        # Centre relative to the text widget's top-level window
        self.transient(text_widget.winfo_toplevel())
        self.lift()

    # ------------------------------------------------------------------
    def find(self):
        """Find first occurrence and select it."""
        self.text_widget.tag_remove("found", "1.0", tk.END)
        needle = self.find_var.get()
        if not needle:
            return

        idx = self.text_widget.search(needle, "1.0", nocase=True, stopindex=tk.END)
        if not idx:
            messagebox.showinfo("Find", f'Could not find "{needle}"!', parent=self)
            self.start_index = "1.0"
            return

        end_idx = f"{idx}+{len(needle)}c"
        self.text_widget.tag_add("found", idx, end_idx)
        self.text_widget.tag_config("found", background="yellow", foreground="black")
        self.text_widget.see(idx)
        self.text_widget.mark_set(tk.INSERT, idx)
        self.start_index = end_idx

    def find_next(self):
        """Find the next occurrence after the current position."""
        needle = self.find_var.get() or self.text_widget.tag_ranges("found") and ""
        if not needle:
            needle = self.find_var.get()
        if not needle:
            return

        self.text_widget.tag_remove("found", "1.0", tk.END)
        idx = self.text_widget.search(needle, self.start_index, nocase=True, stopindex=tk.END)

        if not idx:
            # Wrap around
            idx = self.text_widget.search(needle, "1.0", nocase=True, stopindex=tk.END)
            if not idx:
                messagebox.showinfo("Find", f'Could not find "{needle}"!', parent=self)
                return

        end_idx = f"{idx}+{len(needle)}c"
        self.text_widget.tag_add("found", idx, end_idx)
        self.text_widget.tag_config("found", background="yellow", foreground="black")
        self.text_widget.see(idx)
        self.text_widget.mark_set(tk.INSERT, idx)
        self.start_index = end_idx

    def replace(self):
        """Replace the current selection / first found occurrence."""
        self.find()
        ranges = self.text_widget.tag_ranges("found")
        if ranges:
            self.text_widget.delete(ranges[0], ranges[1])
            self.text_widget.insert(ranges[0], self.replace_var.get())
            self.text_widget.tag_remove("found", "1.0", tk.END)

    def replace_all(self):
        """Replace every occurrence in the document."""
        needle = self.find_var.get()
        replacement = self.replace_var.get()
        if not needle:
            return
        content = self.text_widget.get("1.0", tk.END)
        new_content = content.replace(needle, replacement)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", new_content)
