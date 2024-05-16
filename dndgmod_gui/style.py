from tkinter import ttk
import sv_ttk

STYLES = {
    "AppHeader.TLabel": {
        "font": ("Helvetica", 30),
        "padding": 15,
    },
    "TreeHeader.TLabel": {
        "font": ("Helvetica", 15, "underline"),
        "padding": 5,
    },
}

def inject_style():
    sv_ttk.set_theme("dark")
    style_obj = ttk.Style()
    for style in STYLES:
        style_obj.configure(style, **STYLES[style])
