# CSE323 # Simple Text Editor — Python Port

## File Structure

| Python file                       Purpose                              |
|------------------------------------------------------------------------|
| `simple_text_editor.py`           Entry point & app constants          |
| `ui.py`                           Main window, menus, toolbar          |
| `about.py`                        About dialogs                        |
| `auto_complete.py`                Keyword & bracket autocomplete       |
| `fedit.py`                        Utility: clear text area             |
| `find.py`                         Find & Replace dialog                |
| `highlight_text.py`               Syntax highlighting via tkinter tags |
| `supported_keywords.py`           keyword lists                        |
 
## Requirements

- Python 3.10+ (uses `match` / union-type hints)
- `tkinter` — included with most Python installations

## Running

```bash
python simple_text_editor.py
```

## Features

- **File operations**: New, Open, Save (with unsaved-change prompts)
- **Edit**: Cut, Copy, Paste, Select All, Clear, Word Wrap toggle
- **Find & Replace**: Find, Find Next, Replace, Replace All
- **Syntax highlighting**: Java and C++ keywords highlighted in light gray
- **Autocomplete**: Keyword completion + bracket/parenthesis auto-closing
- **Font picker**: Family and size combo boxes in the toolbar
- **Bold / Italic** toggle buttons
- **Drag & drop**: Drop supported file types onto the editor
- **About dialogs**: Author info and software version

- **Make sure pillow is installed: pip install pillow
