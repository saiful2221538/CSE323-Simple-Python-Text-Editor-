"""
auto_complete.py
Autocomplete functionality for programming keywords and bracket pairs.
Mirrors Java AutoComplete class.
"""

import tkinter as tk
import bisect
from supported_keywords import SupportedKeywords


class AutoComplete:
    """
    Listens to key events on the text widget and suggests keyword completions.
    Also auto-closes brackets and parentheses.
    """

    def __init__(self, text_widget: tk.Text, keywords: list[str]):
        self.text_widget = text_widget
        self.words = sorted(keywords)
        kw = SupportedKeywords()
        self.brackets = kw.get_brackets()
        self.bracket_completions = kw.get_bracket_completions()

        self._in_completion = False
        self._completion_end = None  # index where inserted completion ends

        self.text_widget.bind("<Key>", self._on_key, add="+")
        self.text_widget.bind("<Return>", self._on_return, add="+")

    def _on_key(self, event):
        """Called on every key press."""
        char = event.char

        if not char or event.keysym in ("Return", "BackSpace", "Delete",
                                        "Escape", "Tab", "Up", "Down",
                                        "Left", "Right"):
            if self._in_completion and event.keysym == "Escape":
                self._cancel_completion()
            return

        # Schedule check after the character is inserted into the widget
        self.text_widget.after(1, self._check_completion)

    def _check_completion(self):
        """Check whether a bracket or keyword completion should fire."""
        try:
            insert_idx = self.text_widget.index(tk.INSERT)
            # Retrieve the char just typed
            before_cursor = self.text_widget.get("1.0", insert_idx)
            if not before_cursor:
                return
            last_char = before_cursor[-1]

            # --- Bracket auto-close ---
            if last_char in self.brackets:
                bracket_idx = self.brackets.index(last_char)
                closing = self.bracket_completions[bracket_idx]
                self.text_widget.insert(tk.INSERT, closing)
                # Move caret back inside the brackets
                self.text_widget.mark_set(tk.INSERT, insert_idx)
                return

            # --- Keyword completion (starts after 2 chars typed) ---
            # Find the beginning of the current word
            col = int(insert_idx.split(".")[1])
            line_start = insert_idx.rsplit(".", 1)[0] + ".0"
            line_text = self.text_widget.get(line_start, insert_idx)

            word_start = len(line_text)
            for i in range(len(line_text) - 1, -1, -1):
                if not line_text[i].isalpha():
                    word_start = i + 1
                    break
            else:
                word_start = 0

            prefix = line_text[word_start:]
            if len(prefix) < 2:
                return

            # Binary search for a matching keyword
            idx = bisect.bisect_left(self.words, prefix)
            if idx < len(self.words) and self.words[idx].startswith(prefix):
                match = self.words[idx]
                completion = match[len(prefix):]
                if completion:
                    self._insert_completion(completion)
        except Exception:
            pass

    def _insert_completion(self, completion: str):
        """Insert the completion text as selected so the user can accept/reject."""
        if self._in_completion:
            return
        start_idx = self.text_widget.index(tk.INSERT)
        self.text_widget.insert(tk.INSERT, completion)
        end_idx = self.text_widget.index(tk.INSERT)
        # Select the inserted completion
        self.text_widget.tag_add(tk.SEL, start_idx, end_idx)
        self.text_widget.mark_set(tk.INSERT, start_idx)
        self._in_completion = True
        self._completion_end = end_idx

    def _on_return(self, event):
        """Accept completion on Enter, or insert newline normally."""
        if self._in_completion:
            # Accept: move caret to end of completion, deselect
            self.text_widget.mark_set(tk.INSERT, self._completion_end)
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
            self._in_completion = False
            self._completion_end = None
            return "break"  # Prevent default newline
        return None

    def _cancel_completion(self):
        """Cancel the current completion suggestion."""
        if self._in_completion and self._completion_end:
            sel_start = self.text_widget.index(tk.SEL_FIRST)
            sel_end = self.text_widget.index(tk.SEL_LAST)
            self.text_widget.delete(sel_start, sel_end)
            self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
        self._in_completion = False
        self._completion_end = None

    def detach(self):
        """Remove event bindings (mirrors removeDocumentListener)."""
        try:
            self.text_widget.unbind("<Key>")
            self.text_widget.unbind("<Return>")
        except Exception:
            pass
