import os
from pathlib import Path
import shutil
import sys
import logging

import jinja2
import yaml

from .spritesheet import CardSpritesheet, OpponentSpritesheet
from . import files, exceptions
from ..pregex import room_list

FIRST_CARD = 313
# new 'globals' needed
FIRST_DECK = 18
VALID_TRIGGERS = ["play", "clicked", "bust_limit_exceeded", "stand", "start_of_turn", "sleeve_played",
                  "another_card_drawn", "card_instanced", 'hit', 'discarded', 'click']
VALID_EXPORTS = ['cards', 'decks', 'encounters']


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

        fm = CardSpritesheet(
            self.modified_src / "assets" / "art" / 'card_visual_effects' / 'foil_card_assets' / "card_foil_mapping.png",
            self.builtin_templates)
        card_number = last_card_number = FIRST_CARD - 1
        deck_number = last_deck_number = FIRST_DECK - 1
        card_spritesheet = CardSpritesheet(self.modified_src / "assets" / "art" / "card_sprite_sheet.png",
                                           self.builtin_templates)
        opponent_spritesheet = OpponentSpritesheet(self.modified_src / "assets" / "art" / "portraits" /
                                                   "spritesheet.png", self.builtin_templates)

        self.j2.globals["wait_for"] = self.builtin_templates.get_template(
            "wait_for.gd.j2").module.wait_for  # type: ignore

        # patching for decks
        self.patch_file('ChoiceUI.gd', 'macro_controller.player_starting_deck = starting_deck_string',
                        'for deck in DeckList.starting_deck_dictionary:\n\t\t\tif card_choice.card_name == '
                        'DeckList.starting_deck_dictionary[deck].name:\n\t\t\t\tstarting_deck_string = deck',
                        'before', True)

        for mod in self.mods:
            with open(mod / "mod.yaml") as f:
                metadata = self.clean_dict(yaml.safe_load(f))
            self.logger.info(f"Patching mod `{metadata["name"]}`")
            if ('enabled' in metadata and metadata['enabled']) or not 'enabled' in metadata:
                # check all exports are valid
                for export in metadata['exports']:
                    if export not in VALID_EXPORTS:
                        raise exceptions.InvalidModYamlException(f"Mod `{metadata["name"]}` attempted exporting something "
                                                                 f"other than {VALID_EXPORTS}")

                card_ids = {}
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
                            card_spritesheet.add_art(card_number, mod / "res" / card_data["image"])
                        except KeyError:
                            self.logger.debug(
                                f"WARNING: Card `{name}` from mod `{metadata["name"]}` is missing the `Image` property, "
                                f"using placeholder image")
                            card_spritesheet.add_art(card_number, self.bundle_dir / "assets" / "placeholder.png")
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
                    # deck_ids = self.get_deck_ids_dict(decks=decks, last_deck_number=last_deck_number)
                    # self.logger.debug(f"Deck IDs: {deck_ids}")
                    for deck_number, (name, deck_data) in enumerate(decks.items(), start=last_deck_number + 1):
                        deck_data = self.clean_dict(deck_data)
                        # more logging
                        self.logger.debug(f"Deck `{name}` (ID: {deck_number}) Data: {deck_data}")
                        self.patch_deck_list_entry(name=name, deck_data=deck_data, deck_number=deck_number,
                                                   card_ids=card_ids)
                    last_deck_number = deck_number

                if "encounters" in metadata["exports"]:
                    self.logger.info(f"Patching encounters from mod `{metadata["name"]}`")
                    with open(mod / "encounters.yaml") as f:
                        encounters = yaml.safe_load(f)
                    for sprite_id, (name, encounter_data) in enumerate(encounters.items(), 42000):
                        encounter_data = self.clean_dict(encounter_data)
                        self.logger.debug(f"Encounter `{name}` Data: {encounter_data}")
                        self.create_encounter_files(name=name, encounter_data=encounter_data, sprite_id=sprite_id,
                                                    card_ids=card_ids)
                        self.logger.debug(f"Patching opponent portrait for encounter `{name}`")
                        opponent_spritesheet.add_art(sprite_id, mod / "res" / encounter_data["sprite"])

        self.logger.info("Patching card spritesheet")
        card_spritesheet.update_spritesheet()
        card_spritesheet.update_tres(self.modified_src / "assets" / "art" / "card_art_sprite_frames.tres")

        self.logger.info("Patching opponent spritesheet")
        opponent_spritesheet.update_spritesheet()
        opponent_spritesheet.update_tres(self.modified_src / "assets" / "art" / "portraits" /
                                         "portrait_spriteframes.tres")

        self.logger.info("Patching foil map")
        fm.update_spritesheet()
        fm.update_tres(
            self.modified_src / "assets" / "art" / 'card_visual_effects' / 'foil_card_assets' / "FoilMapping.tres")

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
                    file_contents.insert(curr_index, new_payload)
                    patched = True
                else:
                    file_contents.insert(curr_index + 1, new_payload)
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

    def patch_deck_list_entry(self, name, deck_data, deck_number, card_ids):
        deck_list = self.modified_src / "singletons" / "DeckList.gd"
        with open(deck_list) as f:
            # get a list of all lines in the file
            deck_list_contents = f.readlines()
        with open(deck_list, "w") as f:
            entry = (self.builtin_templates.get_template("deck_list_entry.j2")
                     .render(name=name, cover_card_id=deck_data['cover_card_id'],
                             id=deck_number, description=deck_data["description"],
                             deck_list=deck_data['deck_list'], card_ids=card_ids))

            # split the entry into a list of lines
            entry = entry.split('\n')

            # new entry starts with the entire file minus one bracket to close off the table
            new_entry = deck_list_contents[0:len(deck_list_contents) - 1]
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
        effect_resources = self.modified_src / "card_effect_resources"
        events = []
        play_effect = 'play' in card_data['triggers']
        discard_effect = 'discarded' in card_data['triggers']
        for trigger, source in card_data["triggers"].items():
            if not trigger in VALID_TRIGGERS:
                self.logger.debug(f"WARNING: Invalid trigger `{trigger}` not in {VALID_TRIGGERS}")
            else:
                if type(source) is dict:
                    arguments = source
                    source = source["filename"]
                    self.logger.debug(f"Arguments for trigger `{trigger}`: {arguments}")
                else:
                    arguments = {}
                # we got backwards compat now no way
                if trigger == 'click':
                    self.logger.debug(f"WARNING: Trigger `Clicked` preferred over `Click`")
                    trigger = 'clicked'
                # this is for automatically adding the connection the play event
                # or if theres no play event then one is created with just the connection
                extra = ''
                if trigger.lower() == 'play' and discard_effect:
                    extra = '\n    card.connect("card_discarded", self, "_on_card_discarded", [card])'
                with open(mod / "src" / source) as f:
                    template = f.read().replace("\n", "\n    ")
                events.append((trigger, self.j2.from_string(template).render(card_ids=card_ids, **arguments) + extra))


        if not play_effect and discard_effect:
            events.append(('play', 'card.connect("card_discarded", self, "_on_card_discarded", [card])'))
        on_event = self.builtin_templates.get_template("on_event.gd.j2").module.on_event  # type: ignore
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

    def create_encounter_files(self, name, encounter_data, sprite_id, card_ids):
        hard = "difficulty" in encounter_data and encounter_data["difficulty"].lower().strip() == "hard"
        room_list.add_encounter_to_room(room_list_file=self.modified_src / "singletons" / "RoomList.gd",
                                        room_name=encounter_data["location"], encounter_name=name)
        room_list.add_encounter_to_random_pool(room_list_file=self.modified_src / "singletons" / "RoomList.gd",
                                               room_name=encounter_data["location"], encounter_name=name,
                                               difficulty="hard" if hard else "easy")

        room_list_file = self.modified_src / "singletons" / "RoomList.gd"
        with open(room_list_file) as f:
            room_list_contents = f.read()
        with open(room_list_file, "w") as f:
            room_list_entry = (self.builtin_templates.get_template("room_list_entry.j2")
                               .render(room_name=encounter_data["location"], encounter_name=name, sprite_id=sprite_id,
                                       healthpoints=encounter_data.get("healthpoints", 21), deck=encounter_data["deck"],
                                       hard_deck=encounter_data.get("hard_deck", None),
                                       foils=encounter_data.get("foils", None),
                                       hard_foils=encounter_data.get("hard_foils", None),
                                       modified_stand_point=encounter_data.get("modified_stand_point", None),
                                       chip_reward=encounter_data["chip_reward"],
                                       start_dialogue=encounter_data["start_dialogue"],
                                       end_dialogue=encounter_data["end_dialogue"], card_ids=card_ids))
            room_list_contents = "},\n}".join(room_list_contents.rsplit("}\n}", 1))
            room_list_contents = (room_list_entry + "\n}").join(room_list_contents.rsplit("}", 1))
            f.write(room_list_contents)

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
