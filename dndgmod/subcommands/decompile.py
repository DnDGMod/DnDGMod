from ..util import files

import subprocess
import shutil

import typer

def decompile(
        ctx: typer.Context
):
    """Decompile Dungeons & Degenerate Gamblers."""
    data_directory = ctx.obj["data_directory"]
    dependencies_directory = ctx.obj["dependencies_directory"]
    gdre_tools_path = dependencies_directory / "gdre_tools.exe"
    output_directory = data_directory / "src"
    pck_path = files.find_dndg()

    shutil.copy(pck_path, new_pck_path := data_directory / "DnDG_vanilla.pck")
    shutil.copy(pck_path.parent / "DnDG_64.exe", data_directory / "DnDG_vanilla.exe")
    files.nuke_directory(output_directory)
    subprocess.run([gdre_tools_path, "--headless", f"--recover={new_pck_path}", f"--output-dir={output_directory}"])
    shutil.copy(dependencies_directory / "export_presets.cfg", output_directory / "export_presets.cfg")

