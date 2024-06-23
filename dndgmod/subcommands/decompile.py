from ..util import files

import subprocess
import shutil
from pathlib import Path
import os

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

    if not (new_pck_path := data_directory / "DnDG_vanilla.pck").exists():
        shutil.copy(pck_path, new_pck_path)
    if not (new_exe_path := data_directory / "DnDG_vanilla.exe").exists():
        shutil.copy(pck_path.parent / "DnDG_64.exe", new_exe_path)
    files.nuke_directory(output_directory)
    print(new_pck_path)
    subprocess.run([gdre_tools_path, "--headless", f"--recover={new_pck_path}", f"--output-dir={output_directory}"])
    print("completed gdre_tools")
    shutil.copy(dependencies_directory / "export_presets.cfg", output_directory / "export_presets.cfg")

    if not (templates_directory := ctx.obj["godot_directory"] / "templates" / "3.5.3.stable").exists():
        templates_directory.mkdir(parents=True)
        for template in ["windows_32_debug.exe", "windows_64_debug.exe",
                         "windows_32_release.exe", "windows_64_release.exe"]:
            shutil.copy(dependencies_directory / template, templates_directory / template)
