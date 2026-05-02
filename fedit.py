"""
fedit.py
Simple utility for clearing the text area.
Mirrors Java FEdit class.
"""

import tkinter as tk


class FEdit:
    @staticmethod
    def clear(text_widget: tk.Text):
        """Clear all text in the given text widget."""
        text_widget.delete("1.0", tk.END)
