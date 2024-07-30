import typing

from .about_window import about_window

from importlib import resources
import tkinter as tk
from tkinter import ttk
from collections import namedtuple
import webbrowser
from ctypes import windll

from dndgmod.subcommands.compile import compile

Card = namedtuple("Card", "name description")
Card_typehint = Card[str, str]
Mod = namedtuple("Mod", "name version author cards")
Mod_typehint = Mod[str, str, str, typing.Iterable[Card_typehint]]


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
                self.active_mods_treeview = DnDGModGUILayout.generic_mod_treeview(
                    self.frame, [Mod("The Best Mod Ever", "1.1.0", "TotallyNotSeth",
                                     [Card("Really cool card", "On Play: is cool"),
                                      Card("Cooler card", "On Play: is cooler")]
                                     )])

                self.mod_swap_buttons = self.ModSwapButtons(self.frame)

                self.inactive_mods_header = ttk.Label(self.frame, text="Inactive Mods", style="TreeHeader.TLabel")
                self.inactive_mods_treeview = DnDGModGUILayout.generic_mod_treeview(
                    self.frame, [Mod("The Worst Mod Ever", "1.1.0", "TotallyNotSeth",
                                     [Card("Really lame card", "On Play: is lame"),
                                      Card("Lamer card", "On Play: is lamer")]
                                     )])

                self.active_mods_header.grid(row=0, column=0)
                self.active_mods_treeview.grid(row=1, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
                self.mod_swap_buttons.frame.grid(row=1, column=1)
                self.inactive_mods_header.grid(row=0, column=2)
                self.inactive_mods_treeview.grid(row=1, column=2, sticky=tk.N + tk.E + tk.S + tk.W)

                self.frame.rowconfigure(1, weight=1)
                self.frame.columnconfigure((0, 2), weight=1)

            class ModSwapButtons:
                def __init__(self, parent: ttk.Frame):
                    self.parent = parent
                    self.frame = ttk.Frame(self.parent, padding=10)

                    self.left_icon = (tk.PhotoImage(file=str(resources.files("dndgmod_gui") / "lefticon.png"))
                                      .subsample(15, 15))
                    self.left_button = ttk.Button(self.frame, image=self.left_icon)
                    self.right_icon = (tk.PhotoImage(file=str(resources.files("dndgmod_gui") / "righticon.png"))
                                       .subsample(15, 15))
                    self.right_button = ttk.Button(self.frame, image=self.right_icon)

                    self.left_button.grid(row=0, column=0, pady=10)
                    self.right_button.grid(row=1, column=0, pady=10)

        class ActionButtons:
            def __init__(self, parent: ttk.Frame):
                self.parent = parent
                self.frame = ttk.Frame(self.parent, padding=10)

                self.revert_image = tk.PhotoImage(file=str(resources.files("dndgmod_gui") / "revert.png"))
                self.revert_button = ttk.Button(self.frame, text=" Revert D&DG to Vanilla", image=self.revert_image,
                                                compound="left")
                self.compile_image = tk.PhotoImage(file=str(resources.files("dndgmod_gui") / "compile.png"))
                self.compile_button = ttk.Button(self.frame, text=" Compile Modded D&DG", image=self.compile_image,
                                                 compound="left")

                self.revert_button.grid(row=0, column=0, padx=5)
                self.compile_button.grid(row=0, column=1, padx=5)

    class ModEditorTab:
        def __init__(self, parent: ttk.Notebook):
            self.parent = parent
            self.frame = ttk.Frame(self.parent)

            self.mod_treeview = DnDGModGUILayout.generic_mod_treeview(
                self.frame, [Mod("The worst mod ever", "1.1.0", "TotallyNotSeth",
                                 [Card("Really lame card", "On Play: is not cool"),
                                  Card("Lamer card", "On Play: is uncool")]
                                 )])
            self.properties_panel = self.PropertiesPanel(self.frame)

            self.mod_treeview.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W, padx=15, pady=15)
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

                    self.metadata_subpanel.frame.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W, padx=10, pady=5)
                    self.quick_actions_subpanel.frame.grid(row=1, column=0, sticky=tk.N + tk.E + tk.S + tk.W, padx=10, pady=5)

                    self.frame.columnconfigure("all", weight=1)

                class MetadataSubpanel:
                    def __init__(self, parent: ttk.Frame):
                        self.parent = parent
                        self.frame, self.inner_frame = DnDGModGUILayout.generic_subpanel(self.parent, "Mod Metadata")

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
                        self.frame, self.inner_frame = DnDGModGUILayout.generic_subpanel(self.parent, "Quick Actions")

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

    @staticmethod
    def generic_mod_treeview(frame: ttk.Frame, mods: typing.Iterable[Mod_typehint]):
        inner_frame = ttk.Frame(frame)
        mod_list = ttk.Treeview(inner_frame, columns=["description"])
        mod_list.heading("#0", text="Name")
        mod_list.heading("description", text="Description")
        for mod in mods:
            mod_entry = mod_list.insert("", 1, text=f"{mod.name} v{mod.version}",
                                        values=[f"Author: {mod.author}"], open=True)
            cards_subentry = mod_list.insert(mod_entry, 1, text="=== Cards ===", open=True)
            for card in mod.cards:
                mod_list.insert(cards_subentry, 1, text=card.name, values=[card.description])
        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=mod_list.yview)
        mod_list.configure(yscrollcommand=scrollbar.set)

        mod_list.bind("<ButtonRelease-1>", lambda e: print(mod_list.item(mod_list.focus())))

        mod_list.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
        scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        inner_frame.rowconfigure(0, weight=1)
        inner_frame.columnconfigure(0, weight=1)
        return inner_frame

    @staticmethod
    def generic_subpanel(frame: ttk.Frame, label: str):
        inner_frame = ttk.LabelFrame(frame, text=label)
        frame = ttk.Frame(inner_frame)
        frame.grid(sticky=tk.N + tk.E + tk.S + tk.W, padx=15, pady=10)
        frame.columnconfigure(1, weight=1)
        inner_frame.rowconfigure(0, weight=1)
        inner_frame.columnconfigure(0, weight=1)
        return inner_frame, frame


class DnDGModGUIBridge:
    def __init__(self):
        self.layout = DnDGModGUILayout()

        help_cascade_menu = self.layout.menubar.help_cascade.menu
        help_cascade_menu.entryconfigure("About", command=lambda: about_window(self.layout.root))
        help_cascade_menu.entryconfigure("Buy Me A Coffee",
                                         command=lambda: webbrowser.open("https://buymeacoffee.com/dndgmod"))
        help_cascade_menu.entryconfigure("Join the DnDGMod Discord",
                                         command=lambda: webbrowser.open("https://discord.gg/yudTFrxUJB"))

        self.layout.mainloop()


DnDGModGUIBridge()
