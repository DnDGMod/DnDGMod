import functools
import sys
import threading
import typing
from pathlib import Path

from .about_window import about_window

from importlib import resources
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
from collections import namedtuple
import webbrowser
from ctypes import windll
import logging

from dndgmod.subcommands.compile import compile_dndg
from dndgmod.subcommands.revert import revert
from dndgmod.subcommands.decompile import decompile

Card = namedtuple("Card", "name description")
Card_typehint = Card[str, str]
Deck = namedtuple("Deck", "name description")
Decks_typehint = Deck[str, str]
Mod = namedtuple("Mod", "name version author cards decks")
Mod_typehint = Mod[str, str, str, typing.Iterable[Card_typehint], typing.Iterable[Decks_typehint]]

threads = {}


def new_thread(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        threads[func.__name__] = threading.Thread(target=func, args=args, kwargs=kwargs)
        threads[func.__name__].start()

    return new_func


class DnDGModGUILayout:
    STYLES = {
        "AppHeader.TLabel": {
            "font": ("Segoe UI", 20),
            "padding": 15,
        },
        "TreeHeader.TLabel": {
            "font": ("Segoe UI", 15, "underline"),
            "padding": 5,
        },
        "AboutWindow.TLabel": {
            "font": ("Segoe UI", 12),
        },
        "AboutWindowLink.TLabel": {
            "font": ("Segoe UI", 12, "underline"),
            "foreground": "blue",
        },
        "AboutWindowHeader.TLabel": {
            "font": ("Segoe UI", 14, "bold"),
        },
        "AboutWindowFooter.TLabel": {
            "font": ("Segoe UI", 12, "italic"),
        },
        "TButton": {
            "font": ("Segoe UI", 10),
            "padding": 5,
        },
        "Treeview": {
            "font": ("Segoe UI", 10),
            "rowheight": 30,
        },
        "Treeview.Heading": {
            "font": ("Segoe UI", 10, "bold")
        },
        "TNotebook.Tab": {
            "font": ("Segoe UI", 10),
            "padding": 5,
        },
        "PlaceholderPrompt.TLabel": {
            "font": ("Segoe UI", 12, "bold")
        }
    }

    def __init__(self):
        windll.shcore.SetProcessDpiAwareness(1)
        self.root = tk.Tk()

        self.app_header = ttk.Label(self.root, text="DnDGMod GUI", style="AppHeader.TLabel")
        self.main_notebook = ttk.Notebook(self.root)
        self.compile_dndg_tab = self.CompileDnDGTab(self.main_notebook)
        self.main_notebook.add(self.compile_dndg_tab.frame, text="Compile D&DG")
        self.mod_editor_tab = self.ModEditorTab(self.main_notebook)
        self.main_notebook.add(self.mod_editor_tab.frame, text="Mod Editor")
        self.save_file_editor_tab = self.SaveFileEditorTab(self.main_notebook)
        self.main_notebook.add(self.save_file_editor_tab.frame, text="Save File Editor")

        self.settings_window = self.SettingsWindow()

        self.app_header.pack()
        self.main_notebook.pack(expand=True, fill="both")
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.style = ttk.Style()
        for name, style_config in self.STYLES.items():
            self.style.configure(name, **style_config)
        self.style.layout("Tabless.TNotebook.Tab", [])

        self.menubar = self.Menubar(self.root)
        self.root.config(menu=self.menubar.menu)
        self.root.geometry("1400x700")
        self.root.minsize(700, 500)
        self.root.title("DnDGMod GUI")

    def mainloop(self):
        self.root.mainloop()

    class CompileDnDGTab:
        def __init__(self, parent: ttk.Notebook):
            self.parent = parent
            self.frame = ttk.Frame(self.parent)

            self.dual_mod_lists = self.DualModLists(self.frame)
            self.action_buttons = self.ActionButtons(self.frame)

            self.dual_mod_lists.frame.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
            self.action_buttons.frame.grid(row=1, column=0, sticky=tk.E)

            self.frame.rowconfigure(0, weight=1)
            self.frame.columnconfigure(0, weight=1)

        class DualModLists:
            def __init__(self, parent: ttk.Frame):
                self.parent = parent
                self.frame = ttk.Frame(self.parent, padding=10)

                self.active_mods_header = ttk.Label(self.frame, text="Active Mods", style="TreeHeader.TLabel")
                self.active_mods_treeview = DnDGModGUILayout.ModTreeview(
                    self.frame, [Mod("The Best Mod Ever", "1.1.0", "TotallyNotSeth",
                                     [Card("Really cool card", "On Play: is cool"),
                                      Card("Cooler card", "On Play: is cooler")], []
                                     )])

                self.mod_swap_buttons = self.ModSwapButtons(self.frame)

                self.inactive_mods_header = ttk.Label(self.frame, text="Inactive Mods", style="TreeHeader.TLabel")
                self.inactive_mods_treeview = DnDGModGUILayout.ModTreeview(
                    self.frame, [Mod("The Worst Mod Ever", "1.1.0", "TotallyNotSeth",
                                     [Card("Really lame card", "On Play: is lame"),
                                      Card("Lamer card", "On Play: is lamer")], []
                                     )])

                self.active_mods_header.grid(row=0, column=0)
                self.active_mods_treeview.frame.grid(row=1, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
                self.mod_swap_buttons.frame.grid(row=1, column=1)
                self.inactive_mods_header.grid(row=0, column=2)
                self.inactive_mods_treeview.frame.grid(row=1, column=2, sticky=tk.N + tk.E + tk.S + tk.W)

                self.frame.rowconfigure(1, weight=1)
                self.frame.columnconfigure((0, 2), weight=1)

            class ModSwapButtons:
                def __init__(self, parent: ttk.Frame):
                    if getattr(sys, 'frozen', False):
                        # we are running in a bundle (i.e. Portable EXE)
                        self.bundle_dir = Path(sys._MEIPASS)
                    else:
                        self.bundle_dir = Path(__file__).parent.parent

                    self.parent = parent
                    self.frame = ttk.Frame(self.parent, padding=10)

                    self.left_icon = (tk.PhotoImage(file=str(self.bundle_dir / "assets" / "lefticon.png"))
                                      .subsample(15, 15))
                    self.left_button = ttk.Button(self.frame, image=self.left_icon)
                    self.right_icon = (tk.PhotoImage(file=str(self.bundle_dir / "assets" / "righticon.png"))
                                       .subsample(15, 15))
                    self.right_button = ttk.Button(self.frame, image=self.right_icon)

                    self.left_button.grid(row=0, column=0, pady=10)
                    self.right_button.grid(row=1, column=0, pady=10)

        class ActionButtons:
            def __init__(self, parent: ttk.Frame):
                if getattr(sys, 'frozen', False):
                    # we are running in a bundle (i.e. Portable EXE)
                    self.bundle_dir = Path(sys._MEIPASS)
                else:
                    self.bundle_dir = Path(__file__).parent.parent

                self.parent = parent
                self.frame = ttk.Frame(self.parent, padding=10)

                self.revert_image = tk.PhotoImage(file=str(self.bundle_dir / "assets" / "revert.png"))
                self.revert_button = ttk.Button(self.frame, text=" Revert D&DG to Vanilla", image=self.revert_image,
                                                compound="left")
                self.compile_image = tk.PhotoImage(file=str(self.bundle_dir / "assets" / "compile.png"))
                self.compile_button = ttk.Button(self.frame, text=" Compile Modded D&DG", image=self.compile_image,
                                                 compound="left")

                self.revert_button.grid(row=0, column=0, padx=5)
                self.compile_button.grid(row=0, column=1, padx=5)

    class ModEditorTab:
        def __init__(self, parent: ttk.Notebook):
            self.parent = parent
            self.frame = ttk.Frame(self.parent)

            self.mod_treeview = DnDGModGUILayout.ModTreeview(
                self.frame, [Mod("The worst mod ever", "1.1.0", "TotallyNotSeth",
                                 [Card("Really lame card", "On Play: is not cool"),
                                  Card("Lamer card", "On Play: is uncool")],
                                 [Deck("Booster Pack Deck", "5 x Booster Packs"),
                                  Deck("Tarot Deck", "All Tarot Cards")]
                                 )])
            self.properties_panel = self.PropertiesPanel(self.frame)

            self.mod_treeview.frame.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W, padx=15, pady=15)
            self.properties_panel.notebook.grid(row=0, column=1, sticky=tk.N + tk.E + tk.S + tk.W)

            self.frame.rowconfigure(0, weight=1)
            self.frame.columnconfigure("all", weight=1)

        class PropertiesPanel:
            def __init__(self, parent: ttk.Frame):
                self.parent = parent
                self.notebook = ttk.Notebook(self.parent, style="Tabless.TNotebook")

                self.properties_hint_panel = self.PropertiesHintPanel(self.notebook)
                self.mod_properties_panel = self.ModPropertiesPanel(self.notebook)
                self.card_properties_panel = self.CardPropertiesPanel(self.notebook)

                self.notebook.add(self.properties_hint_panel.frame)
                self.notebook.add(self.mod_properties_panel.frame)
                self.notebook.add(self.card_properties_panel.frame)

            class PropertiesHintPanel:
                def __init__(self, parent: ttk.Notebook):
                    self.parent = parent
                    self.frame = ttk.Frame(self.parent)

                    self.label = ttk.Label(self.frame, text="Select a mod or card on the right to edit it.",
                                           style="PlaceholderPrompt.TLabel", justify="center", padding=5)
                    self.label.pack()

            class ModPropertiesPanel:
                def __init__(self, parent: ttk.Notebook):
                    self.parent = parent
                    self.frame = ttk.Frame(self.parent)

                    self.metadata_subpanel = self.MetadataSubpanel(self.frame)
                    self.quick_actions_subpanel = self.QuickActionsSubpanel(self.frame)

                    self.metadata_subpanel.frame.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W, padx=10,
                                                      pady=5)
                    self.quick_actions_subpanel.frame.grid(row=1, column=0, sticky=tk.N + tk.E + tk.S + tk.W, padx=10,
                                                           pady=5)

                    self.frame.columnconfigure("all", weight=1)
                    self.frame.rowconfigure("all", weight=1)

                class MetadataSubpanel:
                    def __init__(self, parent: ttk.Frame):
                        self.parent = parent
                        subpanel = DnDGModGUILayout.Subpanel(self.parent, "Mod Metadata")
                        self.frame, self.inner_frame = subpanel.frame, subpanel.inner_frame

                        self.name_label = ttk.Label(self.inner_frame, text="Mod Name: ")
                        self.name_entry = ttk.Entry(self.inner_frame)
                        self.name_entry.insert(0, "The worst mod ever")
                        self.version_label = ttk.Label(self.inner_frame, text="Version: ")
                        self.version_entry = ttk.Entry(self.inner_frame)
                        self.version_entry.insert(0, "1.1.0")
                        self.description_label = ttk.Label(self.inner_frame, text="Description: ")
                        self.description_entry = ttk.Entry(self.inner_frame)
                        self.description_entry.insert(0, "This is the worst mod ever")

                        self.name_label.grid(row=0, column=0, sticky=tk.E, pady=1)
                        self.name_entry.grid(row=0, column=1, sticky=tk.E + tk.W)
                        self.version_label.grid(row=1, column=0, sticky=tk.E, pady=1)
                        self.version_entry.grid(row=1, column=1, sticky=tk.E + tk.W)
                        self.description_label.grid(row=2, column=0, sticky=tk.E, pady=1)
                        self.description_entry.grid(row=2, column=1, sticky=tk.E + tk.W)

                class QuickActionsSubpanel:
                    def __init__(self, parent: ttk.Frame):
                        self.parent = parent
                        subpanel = DnDGModGUILayout.Subpanel(self.parent, "Quick Actions")
                        self.frame, self.inner_frame = subpanel.frame, subpanel.inner_frame

                        self.demo_button = ttk.Button(self.inner_frame, text="Demo Button")
                        self.demo_button.grid(sticky=tk.W)

            class CardPropertiesPanel:
                def __init__(self, parent: ttk.Notebook):
                    self.parent = parent
                    self.frame = ttk.Frame(self.parent)

                    self.test_label = ttk.Label(self.frame, text="Hi")
                    self.test_label.grid()

    class SaveFileEditorTab:
        def __init__(self, parent: ttk.Notebook):
            self.parent = parent
            self.frame = ttk.Frame(self.parent)

    class Menubar:
        def __init__(self, parent: tk.Tk):
            self.parent = parent
            self.menu = tk.Menu(self.parent)
            self.file_cascade = self.FileCascade(self.menu)
            self.menu.add_cascade(menu=self.file_cascade.menu, label="File")
            self.dndg_cascade = self.DnDGCascade(self.menu)
            self.menu.add_cascade(menu=self.dndg_cascade.menu, label="D&DG")
            self.help_cascade = self.HelpCascade(self.menu)
            self.menu.add_cascade(menu=self.help_cascade.menu, label="Help")

        class FileCascade:
            def __init__(self, parent: tk.Menu):
                self.parent = parent
                self.menu = tk.Menu(self.parent, tearoff=False)
                self.menu.add_command(label="Import Mod From .zip")
                self.menu.add_command(label="Export Mod To .zip")
                self.menu.add_separator()
                self.menu.add_command(label="Create New Mod")
                self.menu.add_command(label="Remove Mod From List")
                self.menu.add_separator()
                self.menu.add_command(label="Open Mods Folder")

        class DnDGCascade:
            def __init__(self, parent: tk.Menu):
                self.parent = parent
                self.menu = tk.Menu(self.parent, tearoff=False)
                self.menu.add_command(label="Decompile D&DG")
                self.menu.add_command(label="Launch D&DG")

        class HelpCascade:
            def __init__(self, parent: tk.Menu):
                self.parent = parent
                self.menu = tk.Menu(self.parent, tearoff=False)
                self.menu.add_command(label="About")
                self.menu.add_command(label="Settings")
                self.menu.add_separator()
                self.menu.add_command(label="Buy Me A Coffee")
                self.menu.add_command(label="Join the DnDGMod Discord")

    class ModTreeview:
        def __init__(self, parent: ttk.Frame, mods: typing.Iterable[Mod_typehint]):
            self.frame = ttk.Frame(parent)
            self.mod_list = ttk.Treeview(self.frame, columns=["description"])
            self.mod_list.heading("#0", text="Name")
            self.mod_list.heading("description", text="Description")
            self.mod_list.tag_configure("create", font=("Segue UI", 8, "bold"))
            for mod in mods:
                mod_entry = self.mod_list.insert("", 1, text=f"{mod.name} v{mod.version}",
                                                 values=[f"Author: {mod.author}"], open=True, tags=("mod",))

                cards_subentry = self.mod_list.insert(mod_entry, 1, text="=== Cards ===", open=True,
                                                      tags=("subheader",))
                for card in mod.cards:
                    self.mod_list.insert(cards_subentry, "end", text=card.name, values=[card.description],
                                         tags=("card",))
                self.mod_list.insert(cards_subentry, "end", text="+ Create New Card", tags=("card", "create"))

                decks_subentry = self.mod_list.insert(mod_entry, 2, text="=== Decks ===", open=True,
                                                      tags=("subheader",))
                for deck in mod.decks:
                    self.mod_list.insert(decks_subentry, "end", text=deck.name, values=[deck.description],
                                         tags=("deck",))
                self.mod_list.insert(decks_subentry, "end", text="+ Create New Deck", tags=("deck", "create"))
            scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.mod_list.yview)
            self.mod_list.configure(yscrollcommand=scrollbar.set)

            self.mod_list.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
            scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
            self.frame.rowconfigure(0, weight=1)
            self.frame.columnconfigure(0, weight=1)

    class Subpanel:
        def __init__(self, parent: ttk.Frame, label: str):
            self.frame = ttk.LabelFrame(parent, text=label)
            self.inner_frame = ttk.Frame(self.frame)
            self.inner_frame.grid(sticky=tk.N + tk.E + tk.S + tk.W, padx=15, pady=10)
            self.inner_frame.columnconfigure(1, weight=1)
            self.frame.rowconfigure(0, weight=1)
            self.frame.columnconfigure(0, weight=1)

    class TerminalWindow:
        def __init__(self, action, root):
            self.win = tk.Toplevel()
            self.win.geometry(f"+{root.winfo_rootx()}+{root.winfo_rooty()}")
            self.win.title(action)

            self.header = ttk.Label(self.win, text=action, style="AboutWindowHeader.TLabel")
            self.textbox = scrolledtext.ScrolledText(self.win, state="disabled")
            self.textbox.bind("<1>", lambda e: self.textbox.focus_set())
            self.autoscroll = tk.BooleanVar()
            self.autoscroll.set(True)
            self.autoscroll_checkbtn = ttk.Checkbutton(self.win, variable=self.autoscroll, text="Auto-Scroll")

            self.header.grid(row=0, column=0)
            self.textbox.grid(row=1, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
            self.autoscroll_checkbtn.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)

            self.win.rowconfigure(1, weight=1)
            self.win.columnconfigure(0, weight=1)

        class TextHandler(logging.Handler):
            # This class allows you to log to a Tkinter Text or ScrolledText widget
            # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

            def __init__(self, textbox, autoscroll):
                super().__init__()
                self.textbox = textbox
                self.autoscroll = autoscroll

            def emit(self, record):
                msg = self.format(record)

                def append():
                    self.textbox.configure(state='normal')
                    if msg[-1] == "\n":
                        self.textbox.insert(tk.END, msg)
                    else:
                        self.textbox.insert(tk.END, msg + "\n")
                    self.textbox.configure(state='disabled')
                    # Autoscroll to the bottom
                    if self.autoscroll.get():
                        self.textbox.yview(tk.END)

                # This is necessary because we can't modify the Text from other threads
                self.textbox.after(0, append)

    class SettingsWindow:
        def __init__(self):
            self.win = None
            self.debug_toggle = None
            self.debug_state = tk.BooleanVar()

        def spawn_window(self):
            self.win = tk.Toplevel()
            self.debug_toggle = ttk.Checkbutton(self.win, text="Terminal Debug Mode", variable=self.debug_state)
            self.debug_toggle.grid()


class DnDGModGUIBridge:
    def __init__(self):
        self.layout = DnDGModGUILayout()
        self.terminal_win = None
        self.logger = None

        help_cascade_menu = self.layout.menubar.help_cascade.menu
        help_cascade_menu.entryconfigure("About", command=lambda: about_window(self.layout.root))
        help_cascade_menu.entryconfigure("Buy Me A Coffee",
                                         command=lambda: webbrowser.open("https://buymeacoffee.com/dndgmod"))
        help_cascade_menu.entryconfigure("Join the DnDGMod Discord",
                                         command=lambda: webbrowser.open("https://discord.gg/yudTFrxUJB"))

        self.layout.menubar.dndg_cascade.menu.entryconfigure("Decompile D&DG",
                                                             command=lambda: self.start_task(
                                                                 "Decompile D&DG",
                                                                 lambda: decompile(self.logger)))

        compile_tab_action_buttons = self.layout.compile_dndg_tab.action_buttons
        compile_tab_action_buttons.compile_button.configure(
            command=lambda: self.start_task("Compile D&DG", lambda: compile_dndg(self.logger, debug=True))
        )
        compile_tab_action_buttons.revert_button.configure(
            command=lambda: self.start_task("Revert D&DG to Vanilla", lambda: revert(self.logger))
        )

        mod_list = self.layout.mod_editor_tab.mod_treeview.mod_list
        mod_list.bind("<ButtonRelease-1>", self.switch_scenes)

        self.layout.mainloop()

    @new_thread
    def start_task(self, task_name: str, task: typing.Callable):
        self.terminal_win = DnDGModGUILayout.TerminalWindow(task_name, self.layout.root)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        self.logger.addHandler(self.terminal_win.TextHandler(self.terminal_win.textbox, self.terminal_win.autoscroll))
        task()

    def switch_scenes(self, _):
        mod_list = self.layout.mod_editor_tab.mod_treeview.mod_list
        properties_panel_nb = self.layout.mod_editor_tab.properties_panel.notebook
        scene_mapping = {
            'subheader': 0,
            'mod': 1,
            'card': 2,
        }
        properties_panel_nb.select(scene_mapping[mod_list.item(mod_list.focus())['tags'][0]])


DnDGModGUIBridge()
