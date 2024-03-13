from .._util.find import find_dndg
from .decompile import decompile

import shutil

from typer import Context

def revert(ctx: Context):
    pck_path = find_dndg()
    exe_path = pck_path.parent / "DnDG_64.exe"
    data_directory = ctx.obj["data_directory"]

    shutil.move(data_directory / "DnDG_Backup.pck", pck_path)
    shutil.move(data_directory / "DnDG_Backup.exe", exe_path)

    decompile(ctx)
