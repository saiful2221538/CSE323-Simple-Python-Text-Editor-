"""
Simple Text Editor - Python Port
Original Java project by Pierre-Henry Soria, Achintha Gunasekara, et al.
Ported to Python/Tkinter.
"""

NAME = "SIPAD"
VERSION = 3.0
AUTHOR_EMAIL = "hi@ph7.me"
EDITOR_EMAIL = "saiful.islam45@northsouth.edu"

if __name__ == "__main__":
    from ui import UI
    app = UI()
    app.mainloop()
