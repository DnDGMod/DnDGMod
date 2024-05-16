import typing

from .style import inject_style

from importlib import resources
import tkinter
from tkinter import ttk
from collections import namedtuple

Mod = namedtuple("Mod", "name version description cards")
Card = namedtuple("Card", "name description")

def mod_tree_view(frame: ttk.Frame, mods: typing.Iterable[Mod[str, str, str, typing.Iterable[Card[str, str]]]]):
    mod_list = ttk.Treeview(frame, columns=["description"])
    mod_list.heading("#0", text="Name")
    mod_list.heading("description", text="Description")
    mod = mod_list.insert("", 1, text="Mr. Krabs' Mod v0.1.0", values=["MONEY!!!"])
    mod_list.insert(mod, 1, text="Mr. Krabs", values=["On Play: MONEY!!!"])
    return mod_list


root = tkinter.Tk()
inject_style()

header = ttk.Label(text="DnDGMod GUI", style="AppHeader.TLabel")
header.pack()

mod_lists = ttk.Frame(padding=10)
active_mods_header = ttk.Label(mod_lists, text="Active Mods", style="TreeHeader.TLabel")
active_mods_header.grid(row=0, column=0)
mod_tree_view(mod_lists).grid(row=1, column=0)

buttons = ttk.Frame(mod_lists, padding=10)
plus_icon = tkinter.PhotoImage(file=str(resources.files("dndgmod_gui") / "lefticon.png"))
button1 = ttk.Button(buttons, image=plus_icon)
button1.grid(row=0, pady=10)
minus_icon = tkinter.PhotoImage(file=str(resources.files("dndgmod_gui") / "righticon.png"))
button2 = ttk.Button(buttons, image=minus_icon)
button2.grid(row=1, pady=10)
buttons.grid(row=1, column=1)

active_mods_header = ttk.Label(mod_lists, text="Inactive Mods", style="TreeHeader.TLabel")
active_mods_header.grid(row=0, column=2)
mod_tree_view(mod_lists).grid(row=1, column=2)
mod_lists.pack()

# root.resizable(False, False)
root.mainloop()
