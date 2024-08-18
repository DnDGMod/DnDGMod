from .about_window import about_window
from tkinter import ttk, filedialog
import tkinter as tk
import typing
import logging
from pathlib import Path
import os
import subprocess

from .__main__ import DnDGModGUILayout, new_thread

from dndgmod.subcommands.compile import compile_dndg
from dndgmod.subcommands.revert import revert
from dndgmod.subcommands.decompile import decompile
from dndgmod.subcommands.unpackage import unpackage
from dndgmod.util.files import get_appdata_directory, get_dndg_pck_path


class DnDGModGUILayoutLite:
    def __init__(self):
        self.terminal_win = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.root = tk.Tk()
        self.root.title("DnDGMod GUI Lite")

        self.style = ttk.Style()
        self.style.configure("TButton", padding=3, relief="flat", background="#ccc", font=("Segoe UI", 10))
        self.style.configure("TLabel", padding=6, font=("Segoe UI", 14))

        self.header = ttk.Label(self.root, text="DnDGMod GUI Lite", font=("Segoe UI", 16))
        self.header.grid(sticky=tk.N + tk.E + tk.S + tk.W, padx=10, pady=2)

        self.mod_tools_section = ttk.LabelFrame(self.root, text="Mod Tools", padding=10)
        self.dndg_tools_section = ttk.LabelFrame(self.root, text="D&DG Tools", padding=10)
        self.dndgmod_section = ttk.LabelFrame(self.root, text="DnDGMod", padding=10)

        self.load_mod_button = ttk.Button(self.mod_tools_section, text="Load Mod",
                                          command=lambda *_: self.start_task("Load Mod",
                                                                             lambda: self.select_zip_file()))
        self.load_mod_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.open_mods_folder_button = ttk.Button(self.mod_tools_section, text="Open Mods Folder",
                                                  command=lambda *_: os.system(f"explorer {get_appdata_directory() / 'mods'}"))
        self.open_mods_folder_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.mod_tools_section.grid(sticky=tk.N + tk.E + tk.S + tk.W, padx=10, pady=2)
        self.mod_tools_section.rowconfigure("all", weight=1)
        self.mod_tools_section.columnconfigure("all", weight=1)

        self.decompile_button = ttk.Button(self.dndg_tools_section, text="Decompile D&DG",
                                           command=lambda *_: self.start_task("Decompile D&DG",
                                                                              lambda: decompile(logger=self.logger)))
        self.decompile_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.compile_button = ttk.Button(self.dndg_tools_section, text="Compile D&DG",
                                         command=lambda *_: self.start_task("Compile D&DG",
                                                                            lambda: compile_dndg(logger=self.logger,
                                                                                                 debug=True)))
        self.compile_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.launch_button = ttk.Button(self.dndg_tools_section, text="Launch D&DG",
                                        command=lambda *_: self.start_task("Launch D&DG", self.launch_dndg))
        self.launch_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.revert_button = ttk.Button(self.dndg_tools_section, text="Revert D&DG", command=lambda *_: self.start_task(
            "Revert D&DG", lambda: revert(logger=self.logger)))
        self.revert_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.dndg_tools_section.grid(sticky=tk.N + tk.E + tk.S + tk.W, padx=10, pady=2)
        self.dndg_tools_section.rowconfigure("all", weight=1)
        self.dndg_tools_section.columnconfigure("all", weight=1)

        self.about_button = ttk.Button(self.dndgmod_section, text="Credits", command=lambda *_: about_window(self.root))
        self.about_button.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        self.dndgmod_section.grid(sticky=tk.N + tk.E + tk.S + tk.W, padx=10, pady=2)
        self.dndgmod_section.rowconfigure("all", weight=1)
        self.dndgmod_section.columnconfigure("all", weight=1)

        self.root.rowconfigure([1,2,3], weight=1)
        self.root.columnconfigure("all", weight=1)

    @new_thread
    def start_task(self, task_name: str, task: typing.Callable):
        self.terminal_win = DnDGModGUILayout.TerminalWindow(task_name, self.root)
        self.logger.handlers.clear()
        self.logger.addHandler(self.terminal_win.TextHandler(self.terminal_win.textbox, self.terminal_win.autoscroll))
        task()

    def select_zip_file(self):
        file_path = Path(filedialog.askopenfilename(
            title="Select a DnDGMod-Formatted ZIP File",
            filetypes=[("DnDGMod-Formatted ZIP File", "*.zip")],
            defaultextension=".zip"
        ))
        unpackage(file_path, self.logger)

    def launch_dndg(self):
        process = subprocess.Popen([get_dndg_pck_path().parent / "DnDG_64.exe"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                self.logger.debug(line.decode("utf-8"))


if __name__ == "__main__":
    layout = DnDGModGUILayoutLite()
    layout.root.mainloop()