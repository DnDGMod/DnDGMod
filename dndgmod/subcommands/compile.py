from .._util.find import find_dndg

import subprocess
import shutil
from typing import Annotated

import typer

def compile_(
        ctx: typer.Context,
        debug: Annotated[bool, typer.Option(help="Compile the debug version of Dungeons and Degenerate Gamblers."
                                            )] = False,
):
    """Compile Dungeons & Degenerate Gamblers with any installed mods."""
    pck_path = find_dndg()
    exe_path = pck_path.parent / "DnDG_64.exe"
    data_directory = ctx.obj["data_directory"]

    shutil.move(pck_path, data_directory / "DnDG_Backup.pck")
    shutil.move(exe_path, data_directory / "DnDG_Backup.exe")

    godot_path = data_directory / "dependencies" / "Godot_v3.5.3-stable_win64.exe"
    input_directory = data_directory / "decomped_src"
    subprocess.run([godot_path, "--no-window", "--path", input_directory,
                    "--export" + ("-debug"*debug), "dndgmod", exe_path])
