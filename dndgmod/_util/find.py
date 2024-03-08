import re
import pathlib

def find_dndg() -> pathlib.Path:
    with open("C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        matches = re.finditer("\"path\"\t\t\"(.*?)\"", f.read())
    libraries = [pathlib.Path(match.groups()[0]).resolve() / "steamapps" / "common"
                 for match in matches]
    for library in libraries:
        dndg_path = library / "Dungeons &amp;amp; Degenerate Gamblers Demo" / "DnDG_64.pck"
        if dndg_path.exists():
            return dndg_path
    else:
        raise FileNotFoundError("Dungeons & Degenerate Gamblers could not be found. Make sure it's installed via "
                                "Steam!")
