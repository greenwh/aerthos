"""
Character creation system - AD&D 1e style
"""

import random
from typing import Dict, List
from ..entities.player import PlayerCharacter, Weapon, Armor, Shield, Item, LightSource, Spell, SpellSlot, XP_TABLES
from ..engine.combat import DiceRoller
from ..systems.armor_system import ArmorSystem


class CharacterCreator:
    """Handles character creation flow"""

    def __init__(self, game_data):
        self.game_data = game_data
        self.armor_system = ArmorSystem()

    def create_character(self) -> PlayerCharacter:
        """
        Full character creation flow

        Returns:
            New PlayerCharacter
        """

        print("═══════════════════════════════════════════════════════════════")
        print("CHARACTER CREATION - AD&D 1st Edition")
        print("═══════════════════════════════════════════════════════════════")
        print()

        # Roll ability scores
        print("Rolling ability scores (3d6 in order)...")
        print()

        strength = DiceRoller.roll_3d6()
        dexterity = DiceRoller.roll_3d6()
        constitution = DiceRoller.roll_3d6()
        intelligence = DiceRoller.roll_3d6()
        wisdom = DiceRoller.roll_3d6()
        charisma = DiceRoller.roll_3d6()

        print(f"STR: {strength}")
        print(f"DEX: {dexterity}")
        print(f"CON: {constitution}")
        print(f"INT: {intelligence}")
        print(f"WIS: {wisdom}")
        print(f"CHA: {charisma}")
        print()

        # Optional rerolls
        while True:
            reroll_choice = input("Reroll these ability scores? (y/n): ").strip().lower()

            if reroll_choice not in ['y', 'yes']:
                break

            # Save current scores
            old_str, old_dex, old_con = strength, dexterity, constitution
            old_int, old_wis, old_cha = intelligence, wisdom, charisma

            # Roll new scores
            new_str = DiceRoller.roll_3d6()
            new_dex = DiceRoller.roll_3d6()
            new_con = DiceRoller.roll_3d6()
            new_int = DiceRoller.roll_3d6()
            new_wis = DiceRoller.roll_3d6()
            new_cha = DiceRoller.roll_3d6()

            print("\n--- NEW ROLLS ---")
            print(f"STR: {new_str}")
            print(f"DEX: {new_dex}")
            print(f"CON: {new_con}")
            print(f"INT: {new_int}")
            print(f"WIS: {new_wis}")
            print(f"CHA: {new_cha}")
            print("\n--- PREVIOUS ROLLS ---")
            print(f"STR: {old_str}")
            print(f"DEX: {old_dex}")
            print(f"CON: {old_con}")
            print(f"INT: {old_int}")
            print(f"WIS: {old_wis}")
            print(f"CHA: {old_cha}")
            print()

            keep_choice = input("Keep NEW rolls? (y/n): ").strip().lower()

            if keep_choice in ['y', 'yes']:
                strength = new_str
                dexterity = new_dex
                constitution = new_con
                intelligence = new_int
                wisdom = new_wis
                charisma = new_cha
                print("✓ Keeping new rolls!\n")
            else:
                print("✓ Keeping previous rolls!\n")

        print("Final ability scores:")
        print(f"STR: {strength}")
        print(f"DEX: {dexterity}")
        print(f"CON: {constitution}")
        print(f"INT: {intelligence}")
        print(f"WIS: {wisdom}")
        print(f"CHA: {charisma}")
        print()

        # Roll exceptional strength if Fighter with 18 STR
        strength_percentile = 0

        # Choose name
        name = input("Enter your character's name: ").strip()
        if not name:
            name = "Adventurer"

        # Choose race (with stat requirements)
        print("\nAvailable Races:")
        available_races = self._get_available_races(strength, dexterity, constitution, intelligence, wisdom, charisma)

        race_list = []
        race_index = 1
        for race_name in ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']:
            race_data = self.game_data.races.get(race_name, {})
            is_available, reason = self._check_race_requirements(race_name, strength, dexterity, constitution, intelligence, wisdom, charisma)

            if is_available:
                mods = race_data.get('ability_modifiers', {})
                mod_str = self._format_ability_modifiers(mods)
                print(f"{race_index}. {race_name} {mod_str}")
                race_list.append(race_name)
                race_index += 1
            else:
                print(f"   {race_name} - UNAVAILABLE ({reason})")

        race_choice = input(f"\nChoose race (1-{len(race_list)}): ").strip()

        try:
            race_idx = int(race_choice) - 1
            if 0 <= race_idx < len(race_list):
                race = race_list[race_idx]
            else:
                race = race_list[0] if race_list else 'Human'
        except ValueError:
            race = race_list[0] if race_list else 'Human'

        # Apply racial modifiers
        race_data = self.game_data.races[race]
        for ability, modifier in race_data['ability_modifiers'].items():
            if ability == 'strength':
                strength += modifier
            elif ability == 'dexterity':
                dexterity += modifier
            elif ability == 'constitution':
                constitution += modifier
            elif ability == 'intelligence':
                intelligence += modifier
            elif ability == 'wisdom':
                wisdom += modifier
            elif ability == 'charisma':
                charisma += modifier

        # Apply racial maximums
        maximums = race_data.get('ability_maximums', {})
        if 'strength' in maximums:
            strength = min(strength, maximums['strength'])
        if 'dexterity' in maximums:
            dexterity = min(dexterity, maximums['dexterity'])
        if 'constitution' in maximums:
            constitution = min(constitution, maximums['constitution'])
        if 'intelligence' in maximums:
            intelligence = min(intelligence, maximums['intelligence'])
        if 'wisdom' in maximums:
            wisdom = min(wisdom, maximums['wisdom'])
        if 'charisma' in maximums:
            charisma = min(charisma, maximums['charisma'])

        # Choose class (with stat and race requirements)
        print(f"\nAvailable Classes for {race}:")
        available_classes = []
        class_index = 1

        all_classes = ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard']

        for class_name in all_classes:
            if class_name not in self.game_data.classes:
                continue

            is_available, reason = self._check_class_requirements(class_name, race, strength, dexterity, constitution, intelligence, wisdom, charisma)

            if is_available:
                class_data = self.game_data.classes[class_name]
                desc = class_data.get('description', '')
                print(f"{class_index}. {class_name} - {desc}")
                available_classes.append(class_name)
                class_index += 1
            else:
                print(f"   {class_name} - UNAVAILABLE ({reason})")

        if not available_classes:
            print("\nNo classes available with these stats and race! Defaulting to Fighter.")
            available_classes = ['Fighter']

        class_choice = input(f"\nChoose class (1-{len(available_classes)}): ").strip()

        try:
            class_idx = int(class_choice) - 1
            if 0 <= class_idx < len(available_classes):
                char_class = available_classes[class_idx]
            else:
                char_class = available_classes[0]
        except ValueError:
            char_class = available_classes[0]

        # Handle exceptional strength for Fighters, Rangers, and Paladins
        if char_class in ['Fighter', 'Ranger', 'Paladin'] and strength == 18:
            strength_percentile = random.randint(1, 100)
            print(f"\nExceptional Strength! You rolled 18/{strength_percentile:02d}!")

        # Choose Alignment (based on class restrictions)
        from ..systems.alignment import get_allowed_alignments_for_class, get_alignment_description
        from ..entities.character import ALIGNMENTS, ALIGNMENT_ABBREV

        class_data = self.game_data.classes[char_class]
        allowed_alignments = get_allowed_alignments_for_class(char_class, class_data)

        print(f"\nChoose Alignment for {char_class}:")
        print("─" * 70)

        alignment_index = 1
        alignment_choices = []

        for alignment in ALIGNMENTS:
            abbrev = ALIGNMENT_ABBREV[alignment]
            desc = get_alignment_description(alignment)

            if alignment in allowed_alignments:
                print(f"{alignment_index}. {alignment:16s} ({abbrev}) - {desc}")
                alignment_choices.append(alignment)
                alignment_index += 1
            else:
                # Grayed out / unavailable
                print(f"   {alignment:16s} ({abbrev}) - UNAVAILABLE for {char_class}")

        if len(alignment_choices) == 1:
            # Only one choice, auto-select
            alignment = alignment_choices[0]
            print(f"\n✓ {char_class} must be {alignment}")
        else:
            # Player chooses
            alignment_choice = input(f"\nChoose alignment (1-{len(alignment_choices)}): ").strip()

            try:
                align_idx = int(alignment_choice) - 1
                if 0 <= align_idx < len(alignment_choices):
                    alignment = alignment_choices[align_idx]
                else:
                    alignment = alignment_choices[0]
            except ValueError:
                alignment = alignment_choices[0]

            print(f"✓ Selected: {alignment}")

        # Roll HP
        class_data = self.game_data.classes[char_class]
        hit_die = class_data['hit_die']

        hp = max(1, DiceRoller.roll(hit_die))

        # Apply CON bonus
        con_bonus = self._get_con_bonus(constitution)
        hp = max(1, hp + con_bonus)

        print(f"\nStarting HP: {hp}")

        # Get class-specific data
        saves = class_data['saves']
        thac0 = class_data['thac0_base']

        # Get XP needed for level 2
        xp_to_level_2 = XP_TABLES.get(char_class, [0, 2000])[1]

        # Create character
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            alignment=alignment,
            level=1,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp,
            ac=10,
            thac0=thac0,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            xp=0,
            xp_to_next_level=xp_to_level_2
        )

        # Add starting equipment
        self._add_starting_equipment(player, char_class)

        # Add skills for skill-based classes
        if char_class in ['Thief', 'Assassin']:
            player.thief_skills = class_data.get('skills', {}).copy()
        elif char_class == 'Bard':
            player.thief_skills = class_data.get('skills', {}).copy()
        elif char_class == 'Monk':
            # Monks have special abilities but no thief skills
            pass

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            spell_slots_key = 'spell_slots_level_1'
            if spell_slots_key in class_data:
                num_slots = class_data[spell_slots_key][0]
                if num_slots > 0:
                    for _ in range(num_slots):
                        player.add_spell_slot(1)

                    # Give starting spells
                    self._add_starting_spells(player, char_class)

        print("\n═══════════════════════════════════════════════════════════════")
        print(f"Character created: {name} the {race} {char_class}")
        print("═══════════════════════════════════════════════════════════════")
        print()

        return player

    def _get_available_races(self, str_val, dex_val, con_val, int_val, wis_val, cha_val) -> List[str]:
        """Get list of available races based on ability scores"""
        available = []
        for race_name in ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']:
            is_available, _ = self._check_race_requirements(race_name, str_val, dex_val, con_val, int_val, wis_val, cha_val)
            if is_available:
                available.append(race_name)
        return available

    def _check_race_requirements(self, race_name: str, str_val, dex_val, con_val, int_val, wis_val, cha_val):
        """Check if character meets race requirements. Returns (is_available, reason)"""
        if race_name not in self.game_data.races:
            return False, "Race not found"

        race_data = self.game_data.races[race_name]
        minimums = race_data.get('ability_minimums', {})

        stats = {
            'strength': str_val,
            'dexterity': dex_val,
            'constitution': con_val,
            'intelligence': int_val,
            'wisdom': wis_val,
            'charisma': cha_val
        }

        for ability, min_val in minimums.items():
            if stats.get(ability, 0) < min_val:
                return False, f"Need {ability.upper()} {min_val}+"

        return True, ""

    def _check_class_requirements(self, class_name: str, race: str, str_val, dex_val, con_val, int_val, wis_val, cha_val):
        """Check if character meets class requirements. Returns (is_available, reason)"""
        if class_name not in self.game_data.classes:
            return False, "Class not found"

        # Check race restrictions
        race_data = self.game_data.races.get(race, {})
        restrictions = race_data.get('class_restrictions', [])
        if class_name in restrictions:
            return False, f"{race} cannot be {class_name}"

        # Check ability minimums
        class_data = self.game_data.classes[class_name]
        minimums = class_data.get('ability_minimums', {})

        stats = {
            'strength': str_val,
            'dexterity': dex_val,
            'constitution': con_val,
            'intelligence': int_val,
            'wisdom': wis_val,
            'charisma': cha_val
        }

        for ability, min_val in minimums.items():
            if stats.get(ability, 0) < min_val:
                return False, f"Need {ability.upper()} {min_val}+"

        return True, ""

    def _format_ability_modifiers(self, modifiers: Dict[str, int]) -> str:
        """Format ability modifiers for display"""
        mods = []
        for ability, value in modifiers.items():
            if value > 0:
                mods.append(f"+{value} {ability[:3].upper()}")
            elif value < 0:
                mods.append(f"{value} {ability[:3].upper()}")

        return f"({', '.join(mods)})" if mods else ""

    def _get_available_classes(self, race: str) -> List[str]:
        """Get available classes for a race (legacy method)"""
        race_data = self.game_data.races.get(race, {})
        restrictions = race_data.get('class_restrictions', [])

        all_classes = ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard']
        available = [c for c in all_classes if c not in restrictions and c in self.game_data.classes]

        return available if available else ['Fighter']

    def _get_con_bonus(self, constitution: int) -> int:
        """Get HP bonus from CON"""

        if constitution >= 17:
            return 3
        elif constitution >= 16:
            return 2
        elif constitution >= 15:
            return 1
        elif constitution <= 6:
            return -1
        elif constitution <= 3:
            return -2
        return 0

    def _add_starting_equipment(self, player: PlayerCharacter, char_class: str):
        """Add starting equipment based on class"""

        # Everyone gets basic supplies (use proper item types!)
        torch1 = LightSource(name="Torch", weight=0.1, burn_time_turns=6, light_radius=30)  # 1 GP = 0.1 lbs
        torch2 = LightSource(name="Torch", weight=0.1, burn_time_turns=6, light_radius=30)
        ration1 = Item(name="Rations (1 day)", item_type="consumable", weight=0.1, properties={'healing': '0'})
        ration2 = Item(name="Rations (1 day)", item_type="consumable", weight=0.1, properties={'healing': '0'})

        player.inventory.add_item(torch1)
        player.inventory.add_item(torch2)
        player.inventory.add_item(ration1)
        player.inventory.add_item(ration2)
        # Add 100 starting gold pieces
        player.gold_pieces += 100

        # Class-specific equipment
        if char_class in ['Fighter', 'Ranger', 'Paladin']:
            longsword = Weapon(name="Longsword", weight=0.4, damage_sm="1d8", damage_l="1d12", speed_factor=5)  # 4 GP = 0.4 lbs
            chain = self.armor_system.create_armor('chain_mail')
            shield = self.armor_system.create_shield('shield_small')

            player.inventory.add_item(longsword)
            player.inventory.add_item(chain)
            player.inventory.add_item(shield)

            player.equip_weapon(longsword)
            player.equipment.armor = chain
            player.equipment.shield = shield
            # Calculate AC: armor base AC - shield bonus
            player.ac = chain.ac - shield.ac_bonus

        elif char_class in ['Cleric', 'Druid']:
            mace = Weapon(name="Mace", weight=0.8, damage_sm="1d6", damage_l="1d6", speed_factor=7)  # 8 GP = 0.8 lbs
            chain = self.armor_system.create_armor('chain_mail')
            shield = self.armor_system.create_shield('shield_small')

            player.inventory.add_item(mace)
            player.inventory.add_item(chain)
            player.inventory.add_item(shield)

            player.equip_weapon(mace)
            player.equipment.armor = chain
            player.equipment.shield = shield
            # Calculate AC: armor base AC - shield bonus
            player.ac = chain.ac - shield.ac_bonus

        elif char_class in ['Magic-User', 'Illusionist']:
            staff = Weapon(name="Staff", weight=0.4, damage_sm="1d6", damage_l="1d6", speed_factor=4)  # 4 GP = 0.4 lbs
            dagger = Weapon(name="Dagger", weight=0.1, damage_sm="1d4", damage_l="1d3", speed_factor=2)  # 1 GP = 0.1 lbs

            player.inventory.add_item(staff)
            player.inventory.add_item(dagger)

            player.equip_weapon(dagger)

        elif char_class in ['Thief', 'Assassin', 'Bard']:
            shortsword = Weapon(name="Shortsword", weight=0.3, damage_sm="1d6", damage_l="1d8", speed_factor=3)  # 3 GP = 0.3 lbs
            leather = self.armor_system.create_armor('leather')

            player.inventory.add_item(shortsword)
            player.inventory.add_item(leather)

            player.equip_weapon(shortsword)
            player.equipment.armor = leather
            # Calculate AC: armor base AC (no shield)
            player.ac = leather.ac

        elif char_class == 'Monk':
            # Monks use their fists and wear no armor
            staff = Weapon(name="Staff", weight=0.4, damage_sm="1d6", damage_l="1d6", speed_factor=4)  # 4 GP = 0.4 lbs
            player.inventory.add_item(staff)
            player.equip_weapon(staff)

        # Equip a torch
        torch = LightSource(name="Torch", weight=0.1, burn_time_turns=6)  # 1 GP = 0.1 lbs
        player.equip_light(torch)

    def _add_starting_spells(self, player: PlayerCharacter, char_class: str):
        """Add starting spells for spellcasters"""

        if char_class in ['Magic-User', 'Illusionist']:
            # Mages start with 2-4 level 1 spells
            starting_spell_ids = ['magic_missile', 'sleep', 'detect_magic']

            print("\nStarting Spells:")
            for spell_id in starting_spell_ids:
                if spell_id in self.game_data.spells:
                    spell_data = self.game_data.spells[spell_id]
                    # Check class availability
                    if char_class not in spell_data.get('class_availability', []):
                        continue

                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data['class_availability']
                    )
                    player.spells_known.append(spell)
                    print(f"  - {spell.name}: {spell.description}")

        elif char_class in ['Cleric', 'Druid']:
            # Divine casters know all spells of their class
            print(f"\nAs a {char_class}, you have access to all level 1 {char_class} spells.")
            print("Use 'spells' to see available spells, 'memorize <spell>' to prepare them.")

            for spell_id, spell_data in self.game_data.spells.items():
                if char_class in spell_data.get('class_availability', []) and spell_data['level'] == 1:
                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data['class_availability']
                    )
                    player.spells_known.append(spell)
                    print(f"  - {spell.name}")

        elif char_class == 'Bard':
            # Bards have limited spells
            print("\nAs a Bard, you know a limited selection of spells.")
            for spell_id in ['charm_person', 'detect_magic']:
                if spell_id in self.game_data.spells:
                    spell_data = self.game_data.spells[spell_id]
                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data.get('class_availability', [])
                    )
                    player.spells_known.append(spell)
                    print(f"  - {spell.name}")

    def quick_create(self, name: str, race: str, char_class: str) -> PlayerCharacter:
        """
        Quick character creation for demos/testing

        Args:
            name: Character name
            race: Race (Human, Elf, Dwarf, Halfling)
            char_class: Class (Fighter, Cleric, Magic-User, Thief)

        Returns:
            PlayerCharacter with reasonable stats
        """

        # Generate decent stats
        strength = random.randint(13, 16)
        dexterity = random.randint(13, 16)
        constitution = random.randint(13, 16)
        intelligence = random.randint(13, 16)
        wisdom = random.randint(13, 16)
        charisma = random.randint(10, 14)

        # Optimize primary stat for class
        if char_class == 'Fighter':
            strength = 16
        elif char_class == 'Cleric':
            wisdom = 16
        elif char_class == 'Magic-User':
            intelligence = 16
        elif char_class == 'Thief':
            dexterity = 16

        strength_percentile = 0

        # Apply racial modifiers (same as main character creation)
        if race == 'Elf':
            dexterity += 1
            constitution -= 1
        elif race == 'Dwarf':
            constitution += 1
            charisma -= 1
        elif race == 'Halfling':
            dexterity += 1
            strength -= 1

        # Handle exceptional strength for Fighters
        if char_class == 'Fighter' and strength == 18:
            strength_percentile = 50

        # Roll HP
        class_data = self.game_data.classes[char_class]
        hit_die = class_data['hit_die']
        hp = max(1, DiceRoller.roll(hit_die))

        # Apply CON bonus
        con_bonus = self._get_con_bonus(constitution)
        hp = max(1, hp + con_bonus)

        # Get class-specific data
        saves = class_data['saves']
        thac0 = class_data['thac0_base']

        # Get XP needed for level 2
        xp_to_level_2 = XP_TABLES.get(char_class, [0, 2000])[1]

        # Create character (same as main method)
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            level=1,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp,
            ac=10,
            thac0=thac0,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            xp=0,
            xp_to_next_level=xp_to_level_2
        )

        # Add starting equipment
        self._add_starting_equipment(player, char_class)

        # Add skills for skill-based classes
        if char_class in ['Thief', 'Assassin']:
            player.thief_skills = class_data.get('skills', {}).copy()
        elif char_class == 'Bard':
            player.thief_skills = class_data.get('skills', {}).copy()

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            spell_slots_key = 'spell_slots_level_1'
            if spell_slots_key in class_data:
                num_slots = class_data[spell_slots_key][0]
                if num_slots > 0:
                    for _ in range(num_slots):
                        player.add_spell_slot(1)

                    # Add starting spells (silently for quick creation)
                    if char_class in ['Magic-User', 'Illusionist']:
                        for spell_id in ['magic_missile', 'sleep']:
                            if spell_id in self.game_data.spells:
                                spell_data = self.game_data.spells[spell_id]
                                if char_class in spell_data.get('class_availability', []):
                                    spell = Spell(
                                        name=spell_data['name'],
                                        level=spell_data['level'],
                                        school=spell_data['school'],
                                        casting_time=spell_data['casting_time'],
                                        range=spell_data['range'],
                                        duration=spell_data['duration'],
                                        area_of_effect=spell_data['area'],
                                        saving_throw=spell_data['saving_throw'],
                                        components=spell_data['components'],
                                        description=spell_data['description'],
                                        class_availability=spell_data['class_availability']
                                    )
                                    player.spells_known.append(spell)

                    elif char_class in ['Cleric', 'Druid']:
                        for spell_id, spell_data in self.game_data.spells.items():
                            if char_class in spell_data.get('class_availability', []) and spell_data['level'] == 1:
                                spell = Spell(
                                    name=spell_data['name'],
                                    level=spell_data['level'],
                                    school=spell_data['school'],
                                    casting_time=spell_data['casting_time'],
                                    range=spell_data['range'],
                                    duration=spell_data['duration'],
                                    area_of_effect=spell_data['area'],
                                    saving_throw=spell_data['saving_throw'],
                                    components=spell_data['components'],
                                    description=spell_data['description'],
                                    class_availability=spell_data['class_availability']
                                )
                                player.spells_known.append(spell)

        return player


class ManualCharacterCreator:
    """
    Manual character import system - allows players to bring in their favorite characters
    with full customization and validation
    """

    def __init__(self, game_data):
        self.game_data = game_data
        self.armor_system = ArmorSystem()

        # Load proper item databases (not deprecated items.json)
        import json
        from pathlib import Path

        # Load weapons
        weapons_path = Path("aerthos/data/weapons.json")
        if weapons_path.exists():
            with open(weapons_path) as f:
                self.weapons = json.load(f)
        else:
            self.weapons = {}

        # Load armor (contains both armor and shields sections)
        armor_path = Path("aerthos/data/armor.json")
        if armor_path.exists():
            with open(armor_path) as f:
                armor_data = json.load(f)
                self.armor = armor_data.get('armor', {})
                self.shields = armor_data.get('shields', {})
        else:
            self.armor = {}
            self.shields = {}

        # Load equipment
        equipment_path = Path("aerthos/data/equipment.json")
        if equipment_path.exists():
            with open(equipment_path) as f:
                self.equipment = json.load(f)
        else:
            self.equipment = {}

    def create_manual_character(self) -> PlayerCharacter:
        """
        Manual character creation with full customization

        Returns:
            New PlayerCharacter with user-specified attributes
        """
        print("═══════════════════════════════════════════════════════════════")
        print("MANUAL CHARACTER IMPORT - Bring Your Favorite Character to Aerthos!")
        print("═══════════════════════════════════════════════════════════════")
        print()

        # Step 1: Name
        name = input("Character Name: ").strip()
        if not name:
            name = "Imported Character"

        # Step 2: Race selection
        race = self._select_race()

        # Step 3: Class selection (with race validation)
        char_class = self._select_class(race)

        # Step 4: Level
        level = self._get_level()

        # Step 5: Ability Scores
        print("\n--- Ability Scores ---")
        strength, strength_percentile = self._get_ability_score("Strength", char_class)
        dexterity = self._get_ability_score("Dexterity", char_class)[0]
        constitution = self._get_ability_score("Constitution", char_class)[0]
        intelligence = self._get_ability_score("Intelligence", char_class)[0]
        wisdom = self._get_ability_score("Wisdom", char_class)[0]
        charisma = self._get_ability_score("Charisma", char_class)[0]

        # Apply racial modifiers
        race_data = self.game_data.races[race]
        for ability, modifier in race_data.get('ability_modifiers', {}).items():
            if ability == 'strength':
                strength += modifier
            elif ability == 'dexterity':
                dexterity += modifier
            elif ability == 'constitution':
                constitution += modifier
            elif ability == 'intelligence':
                intelligence += modifier
            elif ability == 'wisdom':
                wisdom += modifier
            elif ability == 'charisma':
                charisma += modifier

        print(f"\nFinal ability scores (after racial modifiers):")
        print(f"STR: {strength}{f'/{strength_percentile}' if strength_percentile > 0 else ''}")
        print(f"DEX: {dexterity}, CON: {constitution}")
        print(f"INT: {intelligence}, WIS: {wisdom}, CHA: {charisma}")

        # Step 6: XP
        xp = self._get_xp(char_class, level)

        # Step 7: Alignment
        alignment = self._select_alignment(char_class)

        # Step 8: HP (manual, max, or auto)
        hp, hp_max = self._get_hp(char_class, level, constitution)

        # Auto-calculate derived stats
        print("\n--- Calculating Derived Stats ---")

        # THAC0
        class_data = self.game_data.classes[char_class]
        thac0 = self._calculate_thac0(class_data, level)
        print(f"THAC0: {thac0}")

        # Saving Throws
        saves = self._calculate_saves(class_data, level)
        print(f"Saves - Poison: {saves['poison']}, Wand: {saves['rod_staff_wand']}, "
              f"Petrify: {saves['petrify_paralyze']}, Breath: {saves['breath']}, Spell: {saves['spell']}")

        # Create character
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            level=level,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp_max,
            ac=10,  # Will be updated after equipment
            thac0=thac0,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            xp=xp,
            xp_to_next_level=self._get_xp_to_next_level(char_class, level),
            alignment=alignment
        )

        # Step 9: Equipment selection
        self._select_equipment(player)

        # Step 10: Magic Items (optional)
        self._select_magic_items(player)

        # Step 11: Money (optional)
        self._set_money(player)

        # Step 12: Spells (if spellcaster)
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            self._select_spells(player, char_class, level)

        # Step 13: Thief skills (if thief)
        if char_class in ['Thief', 'Assassin', 'Bard']:
            player.thief_skills = class_data.get('skills', {}).copy()
            # Apply level bonuses
            for skill in player.thief_skills:
                player.thief_skills[skill] += (level - 1) * 5  # +5% per level (simplified)

        # Recalculate AC after equipment
        player.ac = player.get_effective_ac()

        print("\n✓ Character creation complete!")
        print(f"\n{name} - Level {level} {race} {char_class}")
        print(f"HP: {hp}/{hp_max}, AC: {player.ac}, THAC0: {thac0}")
        print()

        return player

    def _select_race(self) -> str:
        """Let user select race"""
        print("\n--- Select Race ---")
        races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']
        available_races = [r for r in races if r in self.game_data.races]

        for idx, race in enumerate(available_races, 1):
            race_data = self.game_data.races[race]
            mods = race_data.get('ability_modifiers', {})
            mod_str = ', '.join([f"{k.upper()} {'+' if v > 0 else ''}{v}" for k, v in mods.items()])
            print(f"{idx}. {race} {f'({mod_str})' if mod_str else ''}")

        while True:
            choice = input(f"\nChoose race (1-{len(available_races)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_races):
                    return available_races[idx]
            except ValueError:
                pass
            print("Invalid choice. Try again.")

    def _select_class(self, race: str) -> str:
        """Let user select class (validated against race restrictions)"""
        print("\n--- Select Class ---")

        # Get race restrictions
        race_data = self.game_data.races[race]
        allowed_classes = race_data.get('allowed_classes', [])

        # Show available classes
        classes = ['Fighter', 'Cleric', 'Magic-User', 'Thief', 'Ranger', 'Paladin', 'Druid', 'Bard', 'Assassin', 'Illusionist']
        available_classes = []

        for char_class in classes:
            if char_class not in self.game_data.classes:
                continue

            # Check if race allows this class
            if allowed_classes and char_class not in allowed_classes:
                print(f"   {char_class} - UNAVAILABLE for {race}")
                continue

            available_classes.append(char_class)
            class_data = self.game_data.classes[char_class]
            prime_req = class_data.get('prime_requisite', 'N/A')
            print(f"{len(available_classes)}. {char_class} (Prime: {prime_req})")

        while True:
            choice = input(f"\nChoose class (1-{len(available_classes)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_classes):
                    return available_classes[idx]
            except ValueError:
                pass
            print("Invalid choice. Try again.")

    def _get_level(self) -> int:
        """Get character level"""
        while True:
            level_input = input("\nCharacter Level (1-20): ").strip()
            try:
                level = int(level_input)
                if 1 <= level <= 20:
                    return level
                print("Level must be between 1 and 20.")
            except ValueError:
                print("Invalid input. Enter a number.")

    def _get_ability_score(self, ability_name: str, char_class: str) -> tuple:
        """
        Get ability score from user

        Returns:
            (score, percentile) - percentile is 0 unless it's Strength for Fighter
        """
        while True:
            score_input = input(f"{ability_name} (3-18): ").strip()
            try:
                score = int(score_input)
                if 3 <= score <= 18:
                    # Check for exceptional strength (Fighter, Ranger, Paladin)
                    if ability_name == "Strength" and score == 18 and char_class in ['Fighter', 'Ranger', 'Paladin']:
                        perc_input = input("Exceptional Strength percentile (01-00, or 0 for none): ").strip()
                        try:
                            percentile = int(perc_input)
                            if 0 <= percentile <= 100:
                                return (score, percentile)
                            print("Percentile must be 0-100.")
                        except ValueError:
                            print("Invalid percentile. Enter a number.")
                    else:
                        return (score, 0)
                else:
                    print("Ability score must be between 3 and 18.")
            except ValueError:
                print("Invalid input. Enter a number.")

    def _get_xp(self, char_class: str, level: int) -> int:
        """Get XP from user"""
        print(f"\n--- Experience Points ---")

        # Show XP requirements for current level
        xp_table = XP_TABLES.get(char_class, [0] * 11)
        if level <= len(xp_table) - 1:
            xp_min = xp_table[level - 1] if level > 1 else 0
            xp_max = xp_table[level] if level < len(xp_table) else xp_table[-1] * 2
            print(f"Level {level} requires {xp_min} - {xp_max - 1} XP")

        while True:
            xp_input = input(f"Enter XP: ").strip()
            try:
                xp = int(xp_input)
                if xp >= 0:
                    return xp
                print("XP cannot be negative.")
            except ValueError:
                print("Invalid input. Enter a number.")

    def _select_alignment(self, char_class: str) -> str:
        """
        Select alignment with class restrictions

        Returns:
            Alignment string
        """
        from ..entities.character import ALIGNMENTS

        print("\n--- Select Alignment ---")

        # Get class alignment restrictions
        class_data = self.game_data.classes.get(char_class, {})
        allowed_alignments = class_data.get('allowed_alignments', ALIGNMENTS)

        # Show alignments
        available = []
        for idx, alignment in enumerate(ALIGNMENTS, 1):
            if alignment in allowed_alignments:
                print(f"{idx}. {alignment}")
                available.append(alignment)
            else:
                print(f"   {alignment} - UNAVAILABLE for {char_class}")

        while True:
            choice = input(f"\nChoose alignment (1-{len(available)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    return available[idx]
            except ValueError:
                pass
            print("Invalid choice. Try again.")

    def _get_hp(self, char_class: str, level: int, constitution: int) -> tuple:
        """
        Get HP with three options: manual, max, or auto-roll

        Returns:
            (hp_current, hp_max)
        """
        print("\n--- Hit Points ---")
        print("1. Enter manually")
        print("2. Maximum possible for level/stats")
        print("3. Auto-calculate (roll dice)")

        class_data = self.game_data.classes[char_class]
        hit_die = class_data.get('hit_die', 'd8')

        while True:
            choice = input("\nChoose HP method (1-3): ").strip()

            if choice == '1':
                # Manual entry
                while True:
                    hp_input = input("Enter HP: ").strip()
                    try:
                        hp = int(hp_input)
                        if hp > 0:
                            return (hp, hp)
                        print("HP must be positive.")
                    except ValueError:
                        print("Invalid input. Enter a number.")

            elif choice == '2':
                # Maximum possible
                from ..systems.ability_modifiers import AbilityModifierSystem
                ability_system = AbilityModifierSystem()
                is_fighter = char_class in ['Fighter', 'Paladin', 'Ranger']
                con_mods = ability_system.get_constitution_modifiers(constitution, is_fighter)
                hp_bonus = con_mods.get('hp_per_level', 0)

                # Parse hit die
                die_size = int(hit_die[1:])  # 'd8' -> 8
                max_hp = (die_size * level) + (hp_bonus * level)

                print(f"Maximum HP: {max_hp} ({die_size} × {level} + {hp_bonus} × {level})")
                return (max_hp, max_hp)

            elif choice == '3':
                # Auto-roll
                from ..systems.ability_modifiers import AbilityModifierSystem
                ability_system = AbilityModifierSystem()
                is_fighter = char_class in ['Fighter', 'Paladin', 'Ranger']
                con_mods = ability_system.get_constitution_modifiers(constitution, is_fighter)
                hp_bonus = con_mods.get('hp_per_level', 0)

                # Roll HP for each level
                total_hp = 0
                for lvl in range(1, level + 1):
                    if hit_die == 'd4':
                        roll = DiceRoller.roll_dice(1, 4)
                    elif hit_die == 'd6':
                        roll = DiceRoller.roll_dice(1, 6)
                    elif hit_die == 'd8':
                        roll = DiceRoller.roll_dice(1, 8)
                    elif hit_die == 'd10':
                        roll = DiceRoller.roll_dice(1, 10)
                    else:
                        roll = DiceRoller.roll_dice(1, 6)

                    # Level 1 is always max
                    if lvl == 1:
                        roll = int(hit_die[1:])

                    total_hp += roll + hp_bonus

                print(f"Rolled HP: {total_hp}")
                return (total_hp, total_hp)

            else:
                print("Invalid choice. Choose 1, 2, or 3.")

    def _calculate_thac0(self, class_data: Dict, level: int) -> int:
        """Calculate THAC0 for given class and level"""
        base_thac0 = class_data.get('thac0_base', 20)

        # Apply level progression
        # Fighters improve by 1 per level, others slower
        if class_data.get('thac0_progression') == 'fighter':
            thac0 = base_thac0 - level
        elif class_data.get('thac0_progression') == 'cleric':
            thac0 = base_thac0 - (level // 3) * 2
        else:  # Magic-User, Thief
            thac0 = base_thac0 - (level // 3)

        return max(1, thac0)  # Minimum THAC0 is 1

    def _calculate_saves(self, class_data: Dict, level: int) -> Dict[str, int]:
        """Calculate saving throws for given class and level"""
        base_saves = class_data.get('saving_throws', {})

        # Apply level improvements (every 3-4 levels)
        improvement = (level - 1) // 3

        return {
            'poison': max(1, base_saves.get('poison', 16) - improvement),
            'rod_staff_wand': max(1, base_saves.get('rod_staff_wand', 17) - improvement),
            'petrify_paralyze': max(1, base_saves.get('petrify_paralyze', 15) - improvement),
            'breath': max(1, base_saves.get('breath', 20) - improvement),
            'spell': max(1, base_saves.get('spell', 18) - improvement)
        }

    def _get_xp_to_next_level(self, char_class: str, level: int) -> int:
        """Get XP required for next level"""
        xp_table = XP_TABLES.get(char_class, [0] * 11)
        if level < len(xp_table) - 1:
            return xp_table[level]
        return xp_table[-1] * 2  # Double last value for higher levels

    def _select_equipment(self, player: PlayerCharacter):
        """
        Let user select equipment with multi-select or auto-assign
        """
        print("\n--- Equipment Selection ---")
        print("1. Select equipment manually")
        print("2. Auto-assign standard equipment for class")

        choice = input("Choose option (1-2): ").strip()

        if choice == '2':
            # Auto-assign standard equipment
            self._auto_assign_equipment(player)
            return

        # Manual selection
        self._manual_select_weapons(player)
        self._manual_select_armor(player)
        self._manual_select_shield(player)
        self._manual_select_items(player)

    def _auto_assign_equipment(self, player: PlayerCharacter):
        """Auto-assign standard equipment based on class"""
        print("Auto-assigning standard equipment...")

        # This would use the existing _add_starting_equipment method
        # from CharacterCreator class
        creator = CharacterCreator(self.game_data)
        creator._add_starting_equipment(player, player.char_class)

        print("✓ Equipment assigned!")

    def _manual_select_weapons(self, player: PlayerCharacter):
        """Let user select weapons from database"""
        print("\n--- Select Weapons ---")

        weapons = list(self.weapons.items())

        if not weapons:
            print("No weapons available in database.")
            return

        print("Available weapons:")
        for idx, (item_id, item_data) in enumerate(weapons, 1):
            name = item_data.get('name', item_id)
            damage_sm = item_data.get('damage_sm', '1d4')
            damage_l = item_data.get('damage_l', '1d4')
            cost = item_data.get('cost_gp', 0)
            print(f"{idx}. {name} ({damage_sm} vs S/M, {damage_l} vs L, {cost} gp)")

        print("0. Done selecting weapons")

        while True:
            choice = input("\nSelect weapon number (or 0 when done): ").strip()
            try:
                idx = int(choice)
                if idx == 0:
                    break
                if 1 <= idx <= len(weapons):
                    item_id, item_data = weapons[idx - 1]
                    weapon = self._create_weapon_from_data(item_id, item_data)

                    # Check if player can use this weapon
                    can_use, message = player.can_use_weapon(weapon)
                    if not can_use:
                        print(f"✗ {message}")
                        continue

                    player.inventory.add_item(weapon)
                    print(f"✓ Added {weapon.name}")

                    # Ask if they want to equip it
                    equip = input("Equip this weapon? (y/n): ").strip().lower()
                    if equip in ['y', 'yes']:
                        player.equip_weapon(weapon)
                        print(f"✓ Equipped {weapon.name}")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

    def _manual_select_armor(self, player: PlayerCharacter):
        """Let user select armor from database"""
        print("\n--- Select Armor ---")

        armors = list(self.armor.items())

        if not armors:
            print("No armor available in database.")
            return

        print("Available armor:")
        for idx, (item_id, item_data) in enumerate(armors, 1):
            name = item_data.get('name', item_id)
            ac = item_data.get('ac', 10)
            cost = item_data.get('cost_gp', 0)
            print(f"{idx}. {name} (AC {ac}, {cost} gp)")

        print("0. Skip armor selection")

        choice = input("\nSelect armor number (or 0 to skip): ").strip()
        try:
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(armors):
                item_id, item_data = armors[idx - 1]
                armor = self._create_armor_from_data(item_id, item_data)
                player.inventory.add_item(armor)
                player.equip_armor(armor)
                print(f"✓ Equipped {armor.name}")
        except ValueError:
            print("Invalid input. Skipping armor.")

    def _manual_select_shield(self, player: PlayerCharacter):
        """Let user select shield from database"""
        print("\n--- Select Shield ---")

        shields = list(self.shields.items())

        if not shields:
            print("No shields available in database.")
            return

        print("Available shields:")
        for idx, (item_id, item_data) in enumerate(shields, 1):
            name = item_data.get('name', item_id)
            ac_bonus = item_data.get('ac_bonus', 1)
            cost = item_data.get('cost_gp', 0)
            print(f"{idx}. {name} (AC bonus {ac_bonus}, {cost} gp)")

        print("0. Skip shield selection")

        choice = input("\nSelect shield number (or 0 to skip): ").strip()
        try:
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(shields):
                item_id, item_data = shields[idx - 1]
                shield = self._create_shield_from_data(item_id, item_data)
                player.inventory.add_item(shield)
                player.equipment.shield = shield
                print(f"✓ Equipped {shield.name}")
        except ValueError:
            print("Invalid input. Skipping shield.")

    def _manual_select_items(self, player: PlayerCharacter):
        """Let user select misc items"""
        print("\n--- Select Miscellaneous Items ---")

        items = list(self.equipment.items())

        if not items:
            print("No items available.")
            return

        print("Available items:")
        for idx, (item_id, item_data) in enumerate(items, 1):
            name = item_data.get('name', item_id)
            cost = item_data.get('cost_gp', 0)
            print(f"{idx}. {name} ({cost} gp)")

        print("0. Done selecting items")

        while True:
            choice = input("\nSelect item number (or 0 when done): ").strip()
            try:
                idx = int(choice)
                if idx == 0:
                    break
                if 1 <= idx <= len(items):
                    item_id, item_data = items[idx - 1]
                    item = self._create_item_from_data(item_id, item_data)
                    player.inventory.add_item(item)
                    print(f"✓ Added {item.name}")
            except ValueError:
                print("Invalid input.")

    def _select_spells(self, player: PlayerCharacter, char_class: str, level: int):
        """
        Select spells for spellcasters
        """
        print("\n--- Spell Selection ---")
        print("1. Select spells manually")
        print("2. Auto-assign starting spells")

        choice = input("Choose option (1-2): ").strip()

        if choice == '2':
            # Auto-assign
            self._auto_assign_spells(player, char_class, level)
            return

        # Manual selection
        self._manual_select_spells(player, char_class, level)

    def _auto_assign_spells(self, player: PlayerCharacter, char_class: str, level: int):
        """Auto-assign spells based on class and level"""
        print("Auto-assigning spells...")

        class_data = self.game_data.classes[char_class]

        # Add spell slots for each spell level based on character level
        # The slot_key should reference the CHARACTER level, not spell level
        slot_key = f'spell_slots_level_{level}'
        if slot_key in class_data:
            slots_by_level = class_data[slot_key]
            # slots_by_level is an array where index 0 = 1st level spells, index 1 = 2nd level, etc.
            for spell_level_idx, num_slots in enumerate(slots_by_level):
                if num_slots > 0:
                    spell_level = spell_level_idx + 1  # Convert 0-indexed to 1-indexed
                    for _ in range(num_slots):
                        player.add_spell_slot(spell_level)

        # Add spells that the character can cast at their level
        # Only add spells up to the highest spell level they have slots for
        max_spell_level = 0
        if slot_key in class_data and 'spell_slots_level_' in slot_key:
            slots_by_level = class_data[slot_key]
            # Find highest spell level with slots
            for idx, num_slots in enumerate(slots_by_level):
                if num_slots > 0:
                    max_spell_level = idx + 1

        for spell_id, spell_data in self.game_data.spells.items():
            if char_class in spell_data.get('class_availability', []):
                spell_level = spell_data.get('level', 1)
                # Only add spells the character can actually cast
                if spell_level <= max_spell_level:
                    spell = self._create_spell_from_data(spell_data)
                    player.spells_known.append(spell)

        print(f"✓ Added {len(player.spells_known)} spells (levels 1-{max_spell_level})")

    def _manual_select_spells(self, player: PlayerCharacter, char_class: str, level: int):
        """Manually select spells"""
        print("\n--- Manual Spell Selection ---")

        # Get available spells for this class
        available_spells = []
        for spell_id, spell_data in self.game_data.spells.items():
            if char_class in spell_data.get('class_availability', []):
                available_spells.append((spell_id, spell_data))

        if not available_spells:
            print("No spells available for this class.")
            return

        print(f"Available spells for {char_class}:")
        for idx, (spell_id, spell_data) in enumerate(available_spells, 1):
            name = spell_data.get('name', spell_id)
            spell_level = spell_data.get('level', 1)
            school = spell_data.get('school', 'unknown')
            print(f"{idx}. {name} (Level {spell_level}, {school})")

        print("0. Done selecting spells")

        while True:
            choice = input("\nSelect spell number (or 0 when done): ").strip()
            try:
                idx = int(choice)
                if idx == 0:
                    break
                if 1 <= idx <= len(available_spells):
                    spell_id, spell_data = available_spells[idx - 1]
                    spell = self._create_spell_from_data(spell_data)
                    player.spells_known.append(spell)
                    print(f"✓ Added {spell.name}")
            except ValueError:
                print("Invalid input.")

        # Add spell slots
        class_data = self.game_data.classes[char_class]
        slot_key = f'spell_slots_level_{level}'
        if slot_key in class_data:
            slots_by_level = class_data[slot_key]
            for spell_level, num_slots in enumerate(slots_by_level, 1):
                for _ in range(num_slots):
                    player.add_spell_slot(spell_level)

        print(f"✓ Added spell slots for level {level}")

    def _create_weapon_from_data(self, item_id: str, item_data: Dict) -> Weapon:
        """Create Weapon object from item data"""
        # weapon stats are at top level, properties is a list of tags
        return Weapon(
            name=item_data.get('name', item_id),
            weight=item_data.get('weight_gp', 0.0) / 10.0,  # Convert coin weight to pounds
            damage_sm=item_data.get('damage_sm', '1d4'),
            damage_l=item_data.get('damage_l', '1d4'),
            speed_factor=item_data.get('speed_factor', 5),
            magic_bonus=item_data.get('magic_bonus', 0),
            properties=item_data.get('properties', [])
        )

    def _create_armor_from_data(self, item_id: str, item_data: Dict) -> Armor:
        """Create Armor object from item data"""
        # armor stats are at top level
        return Armor(
            name=item_data.get('name', item_id),
            weight=item_data.get('weight_gp', 0.0) / 10.0,  # Convert coin weight to pounds
            ac=item_data.get('ac', 10),
            armor_type=item_data.get('armor_type', 'light'),
            movement_rate=item_data.get('movement_rate', 12),
            magic_bonus=item_data.get('magic_bonus', 0),
            properties=item_data.get('properties', [])
        )

    def _create_shield_from_data(self, item_id: str, item_data: Dict) -> Shield:
        """Create Shield object from item data"""
        # shield stats are at top level
        return Shield(
            name=item_data.get('name', item_id),
            weight=item_data.get('weight_gp', 0.0) / 10.0,  # Convert coin weight to pounds
            ac_bonus=item_data.get('ac_bonus', 1),
            magic_bonus=item_data.get('magic_bonus', 0),
            properties=item_data.get('properties', [])
        )

    def _create_item_from_data(self, item_id: str, item_data: Dict) -> Item:
        """Create Item object from item data"""
        item_type = item_data.get('type', 'generic')

        if item_type == 'light_source':
            return LightSource(
                name=item_data.get('name', item_id),
                weight=item_data.get('weight', 0.0),
                burn_time_turns=item_data.get('properties', {}).get('burn_time_turns', 6),
                light_radius=item_data.get('properties', {}).get('light_radius', 30)
            )
        else:
            return Item(
                name=item_data.get('name', item_id),
                item_type=item_type,
                weight=item_data.get('weight', 0.0),
                properties=item_data.get('properties', {}),
                description=item_data.get('description', '')
            )

    def _create_spell_from_data(self, spell_data: Dict) -> Spell:
        """Create Spell object from spell data"""
        return Spell(
            name=spell_data.get('name', ''),
            level=spell_data.get('level', 1),
            school=spell_data.get('school', ''),
            casting_time=spell_data.get('casting_time', ''),
            range=spell_data.get('range', ''),
            duration=spell_data.get('duration', ''),
            area_of_effect=spell_data.get('area', ''),
            saving_throw=spell_data.get('saving_throw', ''),
            components=spell_data.get('components', ''),
            description=spell_data.get('description', ''),
            class_availability=spell_data.get('class_availability', [])
        )

    def _select_magic_items(self, player: PlayerCharacter):
        """Let user select magic items (optional)"""
        print("\n--- Magic Items (Optional) ---")
        print("Select magic items to add to character inventory")
        print("1. Select magic items")
        print("2. Skip magic items")

        choice = input("Choose option (1-2): ").strip()

        if choice != '1':
            print("Skipping magic items.")
            return

        # Load magic items
        import json
        from pathlib import Path

        magic_items_path = Path("aerthos/data/magic_items.json")
        if not magic_items_path.exists():
            print("Magic items database not found.")
            return

        with open(magic_items_path) as f:
            magic_data = json.load(f)

        # Build simple list of all magic items
        magic_items_list = []

        # Add potions
        for potion in magic_data.get('potions', []):
            magic_items_list.append(('potion', f"Potion of {potion['name']}", 0.1))

        # Add scrolls
        for scroll in magic_data.get('scrolls', {}).get('protection_scrolls', []):
            magic_items_list.append(('scroll', scroll['name'], 0.1))

        # Add rings
        for ring in magic_data.get('rings', []):
            magic_items_list.append(('ring', ring['name'], 0.1))

        # Add wands/staves/rods
        for item in magic_data.get('wands_staves_rods', []):
            magic_items_list.append((item.get('type', 'wand'), item['name'], 1.0))

        # Add misc magic
        for item in magic_data.get('misc_magic', []):
            magic_items_list.append(('misc', item['name'], 1.0))

        # Display and select
        print("\nAvailable magic items:")
        for idx, (item_type, name, weight) in enumerate(magic_items_list, 1):
            print(f"{idx}. [{item_type.upper()}] {name}")

        print("0. Done selecting")

        while True:
            choice = input("\nSelect magic item number (or 0 when done): ").strip()
            try:
                idx = int(choice)
                if idx == 0:
                    break
                if 1 <= idx <= len(magic_items_list):
                    item_type, name, weight = magic_items_list[idx - 1]
                    magic_item = Item(name=name, item_type=item_type, weight=weight)
                    player.inventory.add_item(magic_item)
                    print(f"✓ Added {name}")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

    def _set_money(self, player: PlayerCharacter):
        """Set character's starting money (optional)"""
        print("\n--- Starting Money (Optional) ---")
        print("Enter starting wealth in each coin type (AD&D 1e coinage)")

        # Check if player already has gold from auto-equipment
        existing_gold = player.gold
        if existing_gold > 0:
            print(f"(Auto-equipment gave you {existing_gold} gp - enter values to override, or leave blank to keep it)")
        else:
            print("Leave blank or enter 0 to skip")

        try:
            cp = input("Copper pieces (cp): ").strip()
            entered_cp = int(cp) if cp else 0

            sp = input("Silver pieces (sp): ").strip()
            entered_sp = int(sp) if sp else 0

            ep = input("Electrum pieces (ep): ").strip()
            entered_ep = int(ep) if ep else 0

            gp = input("Gold pieces (gp): ").strip()
            entered_gp = int(gp) if gp else 0

            pp = input("Platinum pieces (pp): ").strip()
            entered_pp = int(pp) if pp else 0

            # Check if user entered any money
            entered_total = entered_cp + entered_sp + entered_ep + entered_gp + entered_pp

            if entered_total > 0:
                # User entered money values - use those and clear old gold
                player.copper_pieces = entered_cp
                player.silver_pieces = entered_sp
                player.electrum_pieces = entered_ep
                player.gold_pieces = entered_gp
                player.platinum_pieces = entered_pp
                player.gold = 0  # Clear old gold field
                print(f"\n✓ Money set: {player.copper_pieces} cp, {player.silver_pieces} sp, {player.electrum_pieces} ep, {player.gold_pieces} gp, {player.platinum_pieces} pp")
            elif existing_gold > 0:
                # User didn't enter money, but has gold from auto-equipment - convert it
                player.gold_pieces = existing_gold
                player.gold = 0  # Clear old gold field
                print(f"\n✓ Kept {existing_gold} gp from auto-equipment")
            else:
                # No money entered and no existing gold
                print("\nNo starting money added.")

        except ValueError:
            print("Invalid input. Keeping existing money if any.")
            # Don't zero out existing gold on error
            if existing_gold > 0:
                player.gold_pieces = existing_gold
                player.gold = 0
