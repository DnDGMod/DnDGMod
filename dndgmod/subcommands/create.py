from dndgmod.util.slug import generate_slug

import os
from pathlib import Path

import yaml


def create(name: str, creator: str, mods_directory: Path, description: str = "A DnDGMod Mod", slug: str = None,
           version: str = "1.0.0", open_directory: bool = False, export_cards: bool = True, gen_demo_card: bool = False,
           export_encounters: bool = False):
    """Create a blank mod."""
    if not slug:
        slug = generate_slug(name)
    mod_directory = mods_directory / slug

    if mod_directory.exists():
        raise FileExistsError(f"{mod_directory} exists, a new mod cannot be created there.")
    mod_directory.mkdir()

    exports = []
    if export_cards:
        exports.append("cards")
    if export_encounters:
        exports.append("encounters")
    data = {
        "Name": name,
        "Description": description,
        "Creator": creator,
        "Version": version,
        "Exports": exports,
    }
    with open(mod_directory / "mod.yaml", "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    os.mkdir(mod_directory / "res")
    os.mkdir(mod_directory / "src")

    with open(mod_directory / "cards.yaml", "w") as f:
        if gen_demo_card:
            demo_card = {
                "Demo Card": {
                    "Description": "On Play: Gain 10 chips.",
                    "Image": "test.png",
                    "Value": 5,
                    "Suit": "spades",
                    "Triggers": {
                        "Play": "demo_card_play.gd.j2",
                    },
                },
            }
            yaml.safe_dump(demo_card, f, sort_keys=False)
        else:
            f.write("# Add your cards here!")
    if gen_demo_card:
        with open(mod_directory / "src" / "demo_card_play.gd.j2", "w") as f:
            f.write("current_player.add_chips(10, card.global_position + SystemParameters.CARD_CENTRE_OFFSET)")
    with open(mod_directory / "encounters.yaml", "w") as f:
        f.write("# Add your encounters here!")

    if open_directory:
        os.startfile(mod_directory)
