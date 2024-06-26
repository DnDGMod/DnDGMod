import rich
from botocore import UNSIGNED
from botocore.config import Config

from .subcommands import create, delete, open, decompile, compile, revert, upgrade, package, unpackage
from .util.logger import logger_setup, LogLevels

from pathlib import Path
from typing import Annotated
from zipfile import ZipFile
import os
import appdirs
import typer
import boto3

EPILOG = (f"[orange1][bold]DnDGMod v0.4.3 by TotallyNotSeth[/] | "
          "[italic]Docs: [link=https://dndgmod.rtfd.io]dndgmod.rtfd.io[/][/]")

app = typer.Typer(
    context_settings={
        "help_option_names": ["--help", "-h"]
    },
    rich_markup_mode="rich",
    no_args_is_help=True
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


@app.callback()
def dndgmod_callback(
        ctx: typer.Context,
        log_level: Annotated[LogLevels, typer.Option("--log-level", "-l")] = "info",
):
    """
    [underline]DnDGMod: The Dungeons & Degenerate Gamblers Modloader[/]

    Created by TotallyNotSeth in Tennessee with :heart:
    Check out our documentation at [link=https://dndgmod.rtfd.io]dndgmod.rtfd.io[/] for help getting started!
    """
    data_directory = Path(appdirs.user_data_dir("DnDGMod", "TotallyNotSeth")).resolve()
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


if __name__ == "__main__":
    app()
