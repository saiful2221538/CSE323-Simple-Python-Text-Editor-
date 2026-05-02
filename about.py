"""
about.py
About dialog windows.
Mirrors Java About class.
"""

import tkinter as tk
from tkinter import ttk
import simple_text_editor as app_info


class About(tk.Toplevel):
    """About dialog. Mirrors Java About class."""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.resizable(False, False)
        self.geometry("500x200")
        self.transient(parent)
        self.lift()

        self._label = tk.Label(self, wraplength=460, justify="left",
                               padx=8, pady=8)
        self._label.pack(fill="both", expand=True)

    def show_me(self):
        """Display author information."""
        self.title(f"About Me - {app_info.NAME}")
        self._label.config(text=(
            f"Author: Pierre-Henry Soria\n"
            f"Contact: {app_info.AUTHOR_EMAIL}\n\n"
            f"Modified By: Saiful Islam\n"
            f"Contact: {app_info.EDITOR_EMAIL}"
        ))

    def show_software(self):
        """Display software information."""
        self.title(f"About Software - {app_info.NAME}")
        self._label.config(text=(
            f"Name: {app_info.NAME}\n"
            f"Version: {app_info.VERSION}"
        ))
