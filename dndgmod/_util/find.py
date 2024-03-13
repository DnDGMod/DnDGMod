import re
from pathlib import Path

def find_dndg() -> Path:
    with open("C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        matches = re.finditer("\"path\"\t\t\"(.*?)\"", f.read())
    for match in matches:
        library = (Path(match.groups()[0]) / "steamapps" / "common").resolve(strict=True)
        dndg_path = library / "Dungeons &amp;amp; Degenerate Gamblers Demo" / "DnDG_64.pck"
        if dndg_path.exists():
            return dndg_path
    else:
        raise FileNotFoundError("Dungeons & Degenerate Gamblers could not be found. Make sure it's installed via "
                                "Steam!")
