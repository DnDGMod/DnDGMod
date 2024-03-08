from .._util.find import find_dndg

import subprocess
from typing import Annotated

import typer

def compile_(
        ctx: typer.Context
):
    """Decompile Dungeons & Degenerate Gamblers Modloader"""
    dndg_path = find_dndg()
    data_directory = ctx.obj["data_directory"]
    godot_path = data_directory / "dependencies" / "Godot_v3.5.3-stable_win64.exe"
    input_directory = data_directory / "decomped_src"
    subprocess.run([godot_path, "--no-window", "--path", input_directory,
                    "--export", "dndgmod", dndg_path.parent / "dndgmod.exe"])
