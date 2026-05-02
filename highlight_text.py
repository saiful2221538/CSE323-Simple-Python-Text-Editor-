"""
highlight_text.py
Syntax highlighting for the text editor using tkinter tags.
"""

import tkinter as tk


class HighlightText:
    """
    Applies syntax highlighting to a tkinter Text widget.
    Mirrors the Java HighlightText class.
    """

    TAG_NAME = "highlight"

    def __init__(self, color: str = "lightgray"):
        self.color = color

    def highlight(self, text_widget: tk.Text, patterns: list[str]):
        """Highlight all occurrences of each pattern in the text widget."""
        self.remove_highlights(text_widget)

        content = text_widget.get("1.0", tk.END)

        for pattern in patterns:
            if not pattern:
                continue
            start = 0
            while True:
                idx = content.find(pattern, start)
                if idx == -1:
                    break
                # Convert character offset to tkinter line.col index
                row = content[:idx].count("\n") + 1
                col = idx - content[:idx].rfind("\n") - 1
                start_idx = f"{row}.{col}"
                end_idx = f"{row}.{col + len(pattern)}"
                text_widget.tag_add(self.TAG_NAME, start_idx, end_idx)
                start = idx + len(pattern)

        text_widget.tag_config(self.TAG_NAME, background=self.color)

    def remove_highlights(self, text_widget: tk.Text):
        """Remove all highlight tags from the text widget."""
        text_widget.tag_remove(self.TAG_NAME, "1.0", tk.END)
