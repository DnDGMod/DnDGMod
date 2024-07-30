import tkinter as tk
from tkinter import ttk
import webbrowser


def about_window(root):
    win = tk.Toplevel()
    win.geometry(f"+{root.winfo_rootx()}+{root.winfo_rooty()}")
    win.resizable(False, False)
    frame = tk.Frame(win)
    ttk.Label(frame, text="DnDGMod GUI v0.1.0", style="AboutWindowHeader.TLabel").pack()
    ttk.Label(frame, style="AboutWindow.TLabel").pack()
    ttk.Label(frame, text="Primary Developer — TotallyNotSeth", style="AboutWindow.TLabel").pack()
    dndgmod_link = ttk.Label(frame, text="Powered by the DnDGMod API", style="AboutWindowLink.TLabel", cursor="hand2")
    dndgmod_link.bind("<ButtonRelease-1>", lambda _: webbrowser.open("https://github.com/TotallyNotSethP/DnDGMod"))
    dndgmod_link.pack()
    ttk.Label(frame, text="Modded ID Card Art — Roaxial", style="AboutWindow.TLabel").pack()
    ttk.Label(frame, text="Alpha Testers — LieutenantLame, monkeys,", style="AboutWindow.TLabel").pack()
    ttk.Label(frame, text="Rando.Idiot, Roaxial, and spssyy0000", style="AboutWindow.TLabel").pack()
    ttk.Label(frame, style="AboutWindow.TLabel").pack()
    ttk.Label(frame, text="A Huge Thank You to Purple Moss Collectors", style="AboutWindowFooter.TLabel").pack()
    ttk.Label(frame, text="and Yogscast Games for making D&DG!", style="AboutWindowFooter.TLabel").pack()
    frame.pack(padx=25, pady=(25, 0))
    ttk.Button(win, text="Close", command=win.destroy).pack(side="right", padx=15, pady=15)
    win.title("About DnDGMod GUI")
