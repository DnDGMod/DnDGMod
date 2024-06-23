from ..util.files import find_dndg, nuke_directory
from .decompile import decompile

import shutil

from typer import Context


def revert(ctx: Context):
    pck_path = find_dndg()
    exe_path = pck_path.parent / "DnDG_64.exe"
    data_directory = ctx.obj["data_directory"]

    nuke_directory(ctx.obj["godot_directory"] / "app_userdata" / "Dungeons & Degenerate Gamblers")
    shutil.copy(data_directory / "DnDG_vanilla.pck", pck_path)
    shutil.copy(data_directory / "DnDG_vanilla.exe", exe_path)
