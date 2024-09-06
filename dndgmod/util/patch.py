import logging
import os
from pathlib import Path
import shutil
import sys
import logging

import jinja2
import yaml

from .spritesheet import CardSpritesheet
from . import files
from .. import exceptions

FIRST_CARD = 313
# new 'globals' needed
FIRST_DECK = 18
VALID_TRIGGERS = ["play", "clicked", "bust_limit_exceeded", "stand", "start_of_turn", "sleeve_played",
                  "another_card_drawn", "card_instanced"]
VALID_EXPORTS = ['cards', 'decks', 'patches']


class Patcher:
    def __init__(self, logger: logging.Logger = None):
        if not logger:
            self.logger = logging
        else:
            self.logger = logger
        self.logger.info("Starting to Patch D&DG Source Code...")

        if frozen := getattr(sys, 'frozen', False):
            # we are running in a bundle (i.e. Portable EXE)
            self.bundle_dir = Path(sys._MEIPASS)
        else:
            self.bundle_dir = Path(__file__).parent.parent
        self.logger.debug(f"Bundle Directory: {self.bundle_dir} (frozen = {frozen})")

        self.appdata_directory = files.get_appdata_directory(logger=logger)
        self.logger.debug(f"AppData Directory: {self.appdata_directory}")
        self.vanilla_src = self.appdata_directory / "src"
        self.modified_src = self.appdata_directory / "modified_src"

        self.mods = None
        self.builtin_templates = jinja2.Environment(loader=jinja2.FileSystemLoader(self.bundle_dir / "templates"))
        self.j2 = jinja2.Environment(loader=jinja2.BaseLoader())

    def patch(self):
        """Patches all installed self.mods into the decompiled D&DG source code."""
        if self.modified_src.exists():
            self.logger.info("Wiping modified_src directory")
            shutil.rmtree(self.modified_src)
        self.logger.info("Copying src directory to modified_src directory")
        shutil.copytree(self.vanilla_src, self.modified_src)

        self.mods = (Path(f.path) for f in os.scandir(self.appdata_directory / "mods") if f.is_dir())
        self.logger.debug(f"Mods found: {self.mods}")
        # sprite sheet and foil map
        ss = CardSpritesheet(self.modified_src / "assets" / "art" / "card_sprite_sheet.png", self.builtin_templates)
        fm = CardSpritesheet(self.modified_src / "assets" / "art" / 'card_visual_effects' / 'foil_card_assets' / "card_foil_mapping.png", self.builtin_templates)
        card_number = last_card_number = FIRST_CARD - 1
        deck_number = last_deck_number = FIRST_DECK - 1

        self.j2.globals["wait_for"] = self.builtin_templates.get_template("wait_for.gd.j2").module.wait_for  # type: ignore

        # patching for decks
        self.patch_file('ChoiceUI.gd', 'macro_controller.player_starting_deck = starting_deck_string', '''for deck in DeckList.starting_deck_dictionary:\n\t\t\tif card_choice.card_name == DeckList.starting_deck_dictionary[deck].name:\n\t\t\t\tstarting_deck_string = deck''', 'before', True)

        for mod in self.mods:
            with open(mod / "mod.yaml") as f:
                metadata = self.clean_dict(yaml.safe_load(f))
            self.logger.info(f"Patching mod `{metadata["name"]}`")
            # check all exports are valid
            for export in metadata['exports']:
                if export not in VALID_EXPORTS:
                    raise exceptions.InvalidModYamlException(f"Mod `{metadata["name"]}` attempted exporting something "
                                                            f"other than {VALID_EXPORTS}")

            if "cards" in metadata["exports"]:
                self.logger.info(f"Patching cards from mod `{metadata["name"]}`")
                with open(mod / "cards.yaml") as f:
                    cards = yaml.safe_load(f)
                card_ids = self.get_card_ids_dict(cards=cards, last_card_number=last_card_number)
                self.logger.debug(f"Card IDs: {card_ids}")
                for card_number, (name, card_data) in enumerate(cards.items(), start=last_card_number + 1):
                    card_data = self.clean_dict(card_data)
                    self.logger.debug(f"Card `{name}` (ID: {card_number}) Data: {card_data}")
                    if "triggers" in card_data:
                        self.logger.debug(f"Patching triggers for card `{name}`")
                        self.create_card_effect_files(mod=mod, card_number=card_number, card_ids=card_ids,
                                                      card_data=card_data)
                    self.logger.debug(f"Patching card list for card `{name}`")
                    self.patch_card_list_entry(name=name, card_data=card_data, card_number=card_number)
                    try:
                        self.logger.debug(f"Patching card art for card `{name}`")
                        ss.add_art(card_number, mod / "res" / card_data["image"])
                    except KeyError:
                        raise exceptions.InvalidCardsYamlException(f"Card `{name}` from mod `{metadata["name"]}` "
                                                                   f"is missing the `Image` property")
                    try:
                        self.logger.debug(f"Patching foil map for card `{name}`")
                        fm.add_art(card_number, mod / "res" / card_data["foil"])
                    except KeyError:
                        self.logger.debug(f"Card `{name}` from mod `{metadata["name"]}` "
                        f"is missing the `Foil` property "
                        f"using default foil map")
                        fm.add_art(card_number, self.bundle_dir / "assets" / "default_foil.png")
                last_card_number = card_number

            # if exporting decks
            if "decks" in metadata["exports"]:
                # logging
                self.logger.info(f"Patching decks from mod `{metadata["name"]}`")
                with open(mod / "decks.yaml") as f:
                    decks = yaml.safe_load(f)
                deck_ids = self.get_deck_ids_dict(decks=decks, last_deck_number=last_deck_number)
                self.logger.debug(f"Deck IDs: {deck_ids}")
                for deck_number, (name, deck_data) in enumerate(decks.items(), start=last_deck_number + 1):
                    deck_data = self.clean_dict(deck_data)
                    # more logging
                    self.logger.debug(f"Deck `{name}` (ID: {deck_number}) Data: {deck_data}")
                    self.patch_deck_list_entry(name=name, deck_data=deck_data, deck_number=deck_number)
                last_deck_number = deck_number

            # general patches

            if 'patches' in metadata['exports']:
                self.logger.info(f'Applying file patches from `{metadata["name"]}`')
                with open(mod / "patches.yaml") as f:
                    patches = yaml.safe_load(f)
                patch_index = 0
                last_patch = -1
                for patch_index, (name, patch_data) in enumerate(patches.items(), start=last_patch+1):
                    path = patch_data['path']
                    pattern = patch_data['pattern']
                    payload = patch_data['payload']
                    try:
                        position = patch_data['position']
                    except KeyError:
                        position = 'after'
                    try:
                        match_indent = patch_data['match_indent']
                    except KeyError:
                        match_indent = True
                    self.patch_file(path, pattern, payload, position, match_indent)
                    self.logger.info(f'Patch applied to `{path}`')
                last_patch = patch_index

        self.logger.info("Patching card spritesheet")
        ss.update_spritesheet()
        ss.update_tres(self.modified_src / "assets" / "art" / "card_art_sprite_frames.tres")

        self.logger.info("Patching foil map")
        fm.update_spritesheet()
        fm.update_tres(self.modified_src / "assets" / "art" / 'card_visual_effects' / 'foil_card_assets' / "FoilMapping.tres")

        self.logger.info("Updating bust limit font")
        self.update_bust_limit_font()
        self.add_dndgmod_branding()

        self.logger.info("Unencrypting save file")
        self.unencrypt_save_file()

    def unencrypt_save_file(self):
        paths = ["singletons/SystemParameters.gd", "TitleScreen.gd", "events/EventPlayerLost.gd",
                 "singletons/MetaProgression.gd", "singletons/MetaProgression.gd", "singletons/SystemParameters.gd",
                 "MacroController.gd"]
        for path in paths:
            with open(self.vanilla_src / path) as f:
                macro_controller_src = f.read()
            with open(self.modified_src / path, "w") as f:
                f.write(macro_controller_src.replace('OS.has_feature("standalone")', "false"))

    def patch_file(self, path, pattern, payload, position, match_indent):
        if not position:
            position = 'after'
        file = str(self.modified_src) + '/' + path
        with open(file) as f:
            file_contents = f.readlines()
        patch_num = 0
        curr_index = 0
        patched = False
        
        for line in file_contents:
            if line.strip('\t\n') == pattern and not patched:
                indent = len(line) - len(line.strip('\t'))
                new_line = ''
                if match_indent:
                    for i in range(indent):
                        new_line = new_line + '\t'
                new_payload = ''
                if type(payload) is list:
                    for line in payload:
                        new_payload = new_payload + new_line + line + '\n'
                else:
                    new_payload = new_line + payload
                
                new_payload = new_payload + '\n'
                if position == 'at':
                    file_contents[curr_index] = new_payload
                    patched = True
                elif position == 'before':
                    file_contents.insert(curr_index,new_payload)
                    patched = True
                else:
                    file_contents.insert(curr_index+1,new_payload)
                    patched = True
            curr_index = curr_index + 1

        with open(file, "w") as f:
            f.writelines(file_contents)

    def patch_card_list_entry(self, name, card_data, card_number):
        card_list = self.modified_src / "singletons" / "CardList.gd"
        with open(card_list) as f:
            card_list_contents = f.read()
        with open(card_list, "w") as f:
            entry = (self.builtin_templates.get_template("card_list_entry.j2")
                     .render(name=name, value=card_data["value"], suit=card_data.get("suit", "special"),
                             id=card_number, description=card_data["description"],
                             attributes=card_data.get("attributes", ["REWARD"]),
                             collection_entry=42000 + card_number, flexible=card_data.get("flexible", None),
                             keywords=card_data.get("keywords", None)))
            card_list_contents = "},\n}".join(card_list_contents.rsplit("}\n}", 1))
            card_list_contents = entry.join(card_list_contents.rsplit("}", 1))
            f.write(card_list_contents + "\n}")

    def patch_deck_list_entry(self, name, deck_data, deck_number):
        deck_list = self.modified_src / "singletons" / "DeckList.gd"
        with open(deck_list) as f:
            # get a list of all lines in the file
            deck_list_contents = f.readlines()
        with open(deck_list, "w") as f:
            entry = (self.builtin_templates.get_template("deck_list_entry.j2")
                     .render(name=name, cover_card_id=deck_data['cover_card_id'],
                             id=deck_number, description=deck_data["description"],
                             deck_list = deck_data['deck_list']))

            # split the entry into a list of lines
            entry = entry.split('\n')
            
            # new entry starts with the entire file minus one bracket to close off the table
            new_entry = deck_list_contents[0:len(deck_list_contents)-1]
            # chuck a comma at the end of the prexisting deck table
            new_entry[-1] = '\t},\n'

            # append each line in the entry to the new entry, following the original decks
            for line in entry:
                new_entry.append(line + '\n')
            # add the closing bracket to the table
            new_entry.append('}')
            # then write the entire list of new lines to the file
            f.writelines(new_entry)

    def create_card_effect_files(self, mod, card_ids, card_data, card_number):
        events = []
        for trigger, source in card_data["triggers"].items():
            with open(mod / "src" / source) as f:
                template = f.read().replace("\n", "\n    ")
            events.append((trigger, self.j2.from_string(template).render(card_ids=card_ids)))
        on_event = self.builtin_templates.get_template("on_event.gd.j2").module.on_event  # type: ignore
        effect_resources = self.modified_src / "card_effect_resources"
        with open(effect_resources / f"CardEffect{card_number}.gd", "w") as f:
            f.write(self.builtin_templates.get_template("CardEffectXXX.gd.j2")
                    .render(events=events, on_event=on_event))
        with open(effect_resources / f"card_effect_{card_number}.tres", "w") as f:
            f.write(self.builtin_templates.get_template("card_effect_XXX.tres.j2").render(id=card_number))

    def update_bust_limit_font(self):
        shutil.copy(self.bundle_dir / "assets" / "new_font_sheet_3_5.png",
                    self.modified_src / "assets" / "fonts" / "font_sheet_3_5.png")
        files.replace_in_file(self.modified_src / "singletons" / "Fonts.gd",
                              'var three_five_chars = "012/"',
                              'var three_five_chars = "0123456789/"')

    def add_dndgmod_branding(self):
        shutil.copy(self.bundle_dir / "assets" / "roaxial_id_card.png",
                    self.modified_src / "assets" / "art" / "id_card.png")
        shutil.copy(self.bundle_dir / "assets" / "dndgmod_splash_screen.png",
                    self.modified_src / "assets" / "logo" / "splash_screen.png")

    def get_card_ids_dict(self, cards, last_card_number):
        card_ids = {}
        for card_number, (_, card_data) in enumerate(cards.items(), start=last_card_number + 1):
            card_data = self.clean_dict(card_data)
            if "identifier" in card_data:
                card_ids[card_data["identifier"]] = card_number
        return card_ids

    # to be honest im not entirely sure what this does
    # but its used for card ids so im assuming its useful for deck ids
    # please let me know if not
    def get_deck_ids_dict(self, decks, last_deck_number):
        deck_ids = {}
        for deck_number, (_, deck_data) in enumerate(decks.items(), start=last_deck_number + 1):
            deck_data = self.clean_dict(deck_data)
            if "identifier" in deck_data:
                deck_ids[deck_data["identifier"]] = deck_number
        return deck_ids

    @staticmethod
    def clean_dict(dictionary: dict):
        to_return = dict()
        for key, value in dictionary.items():
            key = key.lower().strip().replace(" ", "_")
            if type(value) is dict:
                value = Patcher.clean_dict(value)
            to_return[key] = value
        return to_return


def patch_dndg(logger=None):
    Patcher(logger=logger).patch()
