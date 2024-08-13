import rich
from botocore import UNSIGNED
from botocore.config import Config

from ._subcommands_old import delete, open, decompile, compile, revert, upgrade, package, unpackage
from .util.logger import logger_setup, LogLevels

from pathlib import Path
from typing import Annotated
from zipfile import ZipFile
import os
import appdirs
import typer
import boto3
import cmd
import traceback

EPILOG = (f"[orange1][bold]DnDGMod v0.4.4 by TotallyNotSeth[/] | "
          "[italic]Docs: [link=https://dndgmod.rtfd.io]dndgmod.rtfd.io[/][/]")

app = typer.Typer(
    context_settings={
        "help_option_names": ["--help", "-h"]
    },
    rich_markup_mode="rich",
)
# app.command(epilog=EPILOG)(init.init)
app.command(epilog=EPILOG)(decompile.decompile)
app.command(epilog=EPILOG)(create.create)
app.command("open", epilog=EPILOG)(open.open_)
# app.command(epilog=EPILOG)(patch.patch)
app.command("compile", epilog=EPILOG)(compile.compile_)
app.command(epilog=EPILOG)(delete.delete)
app.command(epilog=EPILOG)(revert.revert)
# app.command(epilog=EPILOG)(cycle.cycle)
app.command(epilog=EPILOG)(upgrade.upgrade)
app.command(epilog=EPILOG)(package.package)
app.command(epilog=EPILOG)(unpackage.unpackage)


@app.command(epilog=EPILOG)
def version():
    rich.print(EPILOG)


class DnDGModInteractiveShell(cmd.Cmd):
    intro = """This program comes with ABSOLUTELY NO WARRANTY; for details type `show w`.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c` for details.
"""
    prompt = "DnDGMod> "

    def __init__(self, ctx: typer.Context):
        super().__init__()
        self.ctx: typer.Context = ctx

    def do_show(self, arg):
        if arg == "c":
            print("""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""")
        elif arg == "w":
            print("""
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""")
        else:
            print(f"Unknown argument `{arg}`")

    def do_compile(self, arg):
        compile.compile_(self.ctx)

    def do_open(self, arg):
        open.open_(self.ctx)

    def do_unpackage(self, arg):
        unpackage.unpackage(self.ctx)

    def do_decompile(self, arg):
        decompile.decompile(self.ctx)

    def do_revert(self, arg):
        revert.revert(self.ctx)

    def do_create(self, arg):
        name = input("Mod Name: ")
        creator = input("Creator: ")
        create.create(self.ctx, name, creator, create.generate_slug(name))

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except:
            traceback.print_exc()
            return False  # don't stop


@app.callback(invoke_without_command=True)
def dndgmod_callback(
        ctx: typer.Context,
        log_level: Annotated[LogLevels, typer.Option("--log-level", "-l")] = "info",
):
    """
    [underline]DnDGMod: The Dungeons & Degenerate Gamblers Modloader[/]

    Created by TotallyNotSeth in Tennessee with :heart:
    Check out our documentation at [link=https://dndgmod.rtfd.io]dndgmod.rtfd.io[/] for help getting started!
    """
    if ctx.invoked_subcommand is None:
        print("\nDnDGMod  Copyright (C) 2024  TotallyNotSeth")

    data_directory = Path(appdirs.user_data_dir("DnDGMod", "TotallyNotSeth"))
    if not data_directory.exists():
        data_directory.mkdir(parents=True)
        (data_directory / "mods").mkdir()
        (data_directory / "src").mkdir()

    dependencies_directory = data_directory / "dependencies"
    if not dependencies_directory.exists():
        print("Please wait... dependency acquisition in progress (you won't have to do this again)")
        dependencies_directory.mkdir()
        boto3.client("s3", config=Config(signature_version=UNSIGNED)).download_file(
            Filename=str(dependencies_directory / "tmp.zip"),
            Bucket="dndgmod",
            Key="dndgmod_dependencies.zip",
        )
        with ZipFile(dependencies_directory / "tmp.zip") as f:
            f.extractall(dependencies_directory)
        (dependencies_directory / "tmp.zip").unlink()

    ctx.ensure_object(dict)
    ctx.obj["data_directory"] = data_directory
    ctx.obj["dependencies_directory"] = dependencies_directory
    ctx.obj["godot_directory"] = Path(os.getenv("APPDATA")) / "Godot"
    logger_setup(ctx, log_level)

    if ctx.invoked_subcommand is None:
        DnDGModInteractiveShell(ctx).cmdloop()


if __name__ == "__main__":
    app()
