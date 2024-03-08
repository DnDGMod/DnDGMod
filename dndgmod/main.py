from .subcommands import create, delete, open, init, decompile, compile
from ._util.logger import logger_setup, LogLevels

import pathlib
from typing import Annotated

import appdirs
import typer

EPILOG = ("[orange1][bold]DnDGMod by TotallyNotSeth[/] | "
          "[italic]Docs: [link=https://dndgmod.rtfd.io]dndgmod.rtfd.io[/][/]")

app = typer.Typer(
    context_settings={
        "help_option_names": ["--help", "-h"]
    },
    rich_markup_mode="rich",
    no_args_is_help=True
)
app.command(epilog=EPILOG)(init.init)
app.command(epilog=EPILOG)(decompile.decompile)
app.command(epilog=EPILOG)(create.create)
app.command("open", epilog=EPILOG)(open.open_)
app.command("compile", epilog=EPILOG)(compile.compile_)
app.command(epilog=EPILOG)(delete.delete)

@app.callback()
def dndgmod_callback(
        ctx: typer.Context,
        log_level: Annotated[LogLevels, typer.Option("--log-level", "-l")] = "info",
):
    """
    [underline]DnDGMod: The Dungeons & Degenerate Gamblers Modloader[/]

    Created by TotallyNotSeth in California with :heart:
    Check out our documentation at [link=https://dndgmod.rtfd.io]dndgmod.rtfd.io[/] for help getting started!
    """
    data_directory = pathlib.Path(appdirs.user_data_dir("DnDGMod", "TotallyNotSeth")).resolve()
    if not (data_directory.exists() or ctx.invoked_subcommand == "init"):
        raise FileNotFoundError(f"Directory {data_directory} doesn't exist! Try running `dndgmod init`")

    ctx.ensure_object(dict)
    ctx.obj["data_directory"] = data_directory
    logger_setup(ctx, log_level)


if __name__ == "__main__":
    app()
