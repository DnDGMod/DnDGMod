from ..util import files

import subprocess
import shutil

import typer

def decompile(
        ctx: typer.Context
):
    """Decompile Dungeons & Degenerate Gamblers."""
    dndg_path = files.find_dndg()
    data_directory = ctx.obj["data_directory"]
    gdre_tools_path = data_directory / "dependencies" / "gdre_tools.exe"
    output_directory = data_directory / "decomped_src"
    pck_path = files.find_dndg()
    exe_path = pck_path.parent / "DnDG_64.exe"

    shutil.copy(pck_path, data_directory / "DnDG_Backup.pck")
    shutil.copy(exe_path, data_directory / "DnDG_Backup.exe")
    # files.nuke_directory(output_directory)  # TODO: make sure export_presets.cfg stays!!
    subprocess.run([gdre_tools_path, "--headless", f"--recover={dndg_path}", f"--output-dir={output_directory}"])
