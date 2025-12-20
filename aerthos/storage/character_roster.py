"""
Character Roster - Persistent character storage

Manages a library of created characters that can be reused across multiple games.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from ..entities.player import PlayerCharacter, Weapon, Armor, Shield, LightSource, Item, Spell
from ..constants import CHARACTER_DIR
from ..systems.ability_modifiers import AbilityModifierSystem


class CharacterRoster:
    """Manages persistent character storage"""

    def __init__(self, roster_dir: str = None):
        if roster_dir is None:
            self.roster_dir = Path(CHARACTER_DIR)
        else:
            self.roster_dir = Path(roster_dir)

        # Create directory if it doesn't exist
        self.roster_dir.mkdir(parents=True, exist_ok=True)

    def save_character(self, character: PlayerCharacter, character_id: str = None) -> str:
        """
        Save a character to the roster

        Args:
            character: PlayerCharacter instance to save
            character_id: Optional ID (generates UUID if not provided)

        Returns:
            Character ID
        """
        if character_id is None:
            character_id = str(uuid.uuid4())[:8]

        char_data = {
            'id': character_id,
            'created': datetime.now().isoformat(),
            'name': character.name,
            'race': character.race,
            'class': character.char_class,
            'level': character.level,
            'xp': character.xp,
            'alignment': character.alignment,
            'hp_max': character.hp_max,
            'hp_current': character.hp_current,
            'ac': character.ac,
            'thac0': character.thac0,
            'thac0_progress': getattr(character, '_thac0_progress', 0.0),  # Track fractional THAC0 progress
            'gold': character.gold,  # Kept for backward compatibility

            # Money breakdown (new system)
            'copper_pieces': getattr(character, 'copper_pieces', 0),
            'silver_pieces': getattr(character, 'silver_pieces', 0),
            'electrum_pieces': getattr(character, 'electrum_pieces', 0),
            'gold_pieces': getattr(character, 'gold_pieces', 0),
            'platinum_pieces': getattr(character, 'platinum_pieces', 0),

            # Abilities
            'strength': character.strength,
            'strength_percentile': character.strength_percentile,
            'dexterity': character.dexterity,
            'constitution': character.constitution,
            'intelligence': character.intelligence,
            'wisdom': character.wisdom,
            'charisma': character.charisma,

            # Inventory
            'inventory': self._serialize_inventory(character.inventory),
            'equipped': self._serialize_equipment(character.equipment),

            # Spells
            'spells_known': [self._serialize_spell(s) for s in character.spells_known],
            'spells_memorized': self._serialize_spell_slots(character.spells_memorized),

            # Conditions
            'conditions': list(character.conditions),
        }

        filename = f"{character.name.lower().replace(' ', '_')}_{character_id}.json"
        filepath = self.roster_dir / filename

        with open(filepath, 'w') as f:
            json.dump(char_data, f, indent=2)

        return character_id

    def load_character(self, character_id: str = None, character_name: str = None) -> Optional[PlayerCharacter]:
        """
        Load a character from the roster

        Args:
            character_id: Character ID to load
            character_name: Or character name to load

        Returns:
            PlayerCharacter instance or None if not found
        """
        if character_id:
            # Find by ID
            for filepath in self.roster_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data['id'] == character_id:
                            return self._deserialize_character(data)
                except FileNotFoundError:
                    print(f"Warning: {filepath} not found (may have been deleted)")
                    continue
                except json.JSONDecodeError as e:
                    print(f"Error: {filepath} contains invalid JSON: {e}")
                    continue
                except (PermissionError, OSError) as e:
                    print(f"Error reading {filepath}: {e}")
                    continue

        if character_name:
            # Find by name
            for filepath in self.roster_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data['name'].lower() == character_name.lower():
                            return self._deserialize_character(data)
                except FileNotFoundError:
                    print(f"Warning: {filepath} not found (may have been deleted)")
                    continue
                except json.JSONDecodeError as e:
                    print(f"Error: {filepath} contains invalid JSON: {e}")
                    continue
                except (PermissionError, OSError) as e:
                    print(f"Error reading {filepath}: {e}")
                    continue

        return None

    def list_characters(self) -> List[Dict]:
        """
        List all characters in the roster

        Returns:
            List of character summary dictionaries
        """
        characters = []

        for filepath in self.roster_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                    # Calculate total gold value for display
                    total_gold = (
                        data.get('copper_pieces', 0) * 0.01 +
                        data.get('silver_pieces', 0) * 0.1 +
                        data.get('electrum_pieces', 0) * 0.5 +
                        data.get('gold_pieces', 0) +
                        data.get('platinum_pieces', 0) * 5
                    )

                    # Calculate effective AC (with DEX bonus and equipment)
                    try:
                        ability_system = AbilityModifierSystem()
                        dex = data.get('dexterity', 10)
                        dex_mods = ability_system.get_dexterity_modifiers(dex)
                        dex_bonus = dex_mods.get('defensive_adj', 0)

                        # Get armor and shield from equipment
                        equipped = data.get('equipped', {})
                        base_ac = data.get('ac', 10)
                        effective_ac = base_ac

                        # If armor is equipped, use armor AC instead of base AC
                        if equipped.get('armor'):
                            armor_data = equipped['armor']
                            effective_ac = armor_data.get('ac', base_ac)

                        # Add shield bonus (negative improves AC)
                        if equipped.get('shield'):
                            shield_data = equipped['shield']
                            effective_ac -= shield_data.get('ac_bonus', 0)

                        # Add DEX bonus (negative improves AC)
                        effective_ac += dex_bonus
                    except Exception as e:
                        # If AC calculation fails, fall back to base AC
                        print(f"Warning: AC calculation failed for {data.get('name', 'unknown')}: {e}")
                        effective_ac = data.get('ac', 10)

                    characters.append({
                        'id': data['id'],
                        'name': data['name'],
                        'race': data['race'],
                        'char_class': data['class'],  # Use char_class for consistency
                        'level': data['level'],
                        'xp': data['xp'],
                        'alignment': data.get('alignment', 'True Neutral'),  # Backward compatible
                        'hp_current': data['hp_current'],  # Separate current/max
                        'hp_max': data['hp_max'],
                        'ac': effective_ac,
                        'thac0': data.get('thac0', 20),
                        'gold': int(total_gold), # Calculated total value
                        'copper_pieces': data.get('copper_pieces', 0),                        'silver_pieces': data.get('silver_pieces', 0),
                        'electrum_pieces': data.get('electrum_pieces', 0),
                        'gold_pieces': data.get('gold_pieces', 0),
                        'platinum_pieces': data.get('platinum_pieces', 0),
                        'created': data['created'],
                        # Also include full stats for detail view
                        'strength': data.get('strength', 10),
                        'dexterity': data.get('dexterity', 10),
                        'constitution': data.get('constitution', 10),
                        'intelligence': data.get('intelligence', 10),
                        'wisdom': data.get('wisdom', 10),
                        'charisma': data.get('charisma', 10),
                        'inventory': self._extract_item_names(data.get('inventory', [])),
                        'equipment': data.get('equipped', {}),  # Include equipment for UI images
                        'spells': data.get('spells', []),
                        'experience_points': data.get('xp', 0)
                    })
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

        return sorted(characters, key=lambda c: c['name'])

    def _extract_item_names(self, inventory) -> List[str]:
        """
        Extract item names from inventory data

        Inventory can be either:
        - List of strings (item names)
        - List of dicts with 'name' key
        """
        if not inventory:
            return []

        item_names = []
        for item in inventory:
            if isinstance(item, str):
                item_names.append(item)
            elif isinstance(item, dict):
                # Get name from dict
                name = item.get('name', str(item))
                item_names.append(name)
            else:
                item_names.append(str(item))

        return item_names

    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character from the roster

        Args:
            character_id: Character ID to delete

        Returns:
            True if deleted, False if not found
        """
        found_path = None
        for filepath in self.roster_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if data['id'] == character_id:
                        # Store path, delete after iteration
                        found_path = filepath
                        break
            except FileNotFoundError:
                print(f"Warning: {filepath} not found (may have been deleted)")
                continue
            except json.JSONDecodeError as e:
                print(f"Error: {filepath} contains invalid JSON: {e}")
                continue
            except (PermissionError, OSError) as e:
                print(f"Error reading {filepath}: {e}")
                continue

        if found_path:
            found_path.unlink()
            return True

        return False

    def _serialize_inventory(self, inventory) -> List[Dict]:
        """Serialize inventory items"""
        items = []
        for item in inventory.items:
            item_data = {
                'name': item.name,
                'type': item.item_type,
                'weight': item.weight
            }

            if isinstance(item, Weapon):
                item_data.update({
                    'damage_sm': item.damage_sm,
                    'damage_l': item.damage_l,
                    'speed_factor': item.speed_factor,
                    'magic_bonus': item.magic_bonus
                })
            elif isinstance(item, Armor):
                item_data.update({
                    'ac': item.ac,
                    'armor_type': item.armor_type,
                    'movement_rate': item.movement_rate,
                    'magic_bonus': getattr(item, 'magic_bonus', 0)
                })
            elif isinstance(item, LightSource):
                item_data.update({
                    'burn_time_turns': item.burn_time_turns,
                    'light_radius': item.light_radius,
                    'turns_remaining': item.turns_remaining
                })

            items.append(item_data)

        return items

    def _serialize_equipment(self, equipment) -> Dict:
        """Serialize equipped items"""
        equipped = {}

        if equipment.weapon:
            equipped['weapon'] = {
                'name': equipment.weapon.name,
                'type': 'weapon',
                'damage_sm': equipment.weapon.damage_sm,
                'damage_l': equipment.weapon.damage_l,
                'speed_factor': equipment.weapon.speed_factor,
                'magic_bonus': equipment.weapon.magic_bonus,
                'weight': equipment.weapon.weight
            }

        if equipment.armor:
            equipped['armor'] = {
                'name': equipment.armor.name,
                'type': 'armor',
                'ac': equipment.armor.ac,
                'armor_type': equipment.armor.armor_type,
                'movement_rate': equipment.armor.movement_rate,
                'magic_bonus': getattr(equipment.armor, 'magic_bonus', 0),
                'weight': equipment.armor.weight
            }

        if equipment.shield:
            equipped['shield'] = {
                'name': equipment.shield.name,
                'type': 'shield',
                'ac_bonus': equipment.shield.ac_bonus,
                'magic_bonus': getattr(equipment.shield, 'magic_bonus', 0),
                'weight': equipment.shield.weight
            }

        if equipment.light_source:
            equipped['light'] = {
                'name': equipment.light_source.name,
                'type': 'light_source',
                'burn_time_turns': equipment.light_source.burn_time_turns,
                'turns_remaining': equipment.light_source.turns_remaining,
                'weight': equipment.light_source.weight
            }

        return equipped

    def _is_complete_spell_data(self, spell_data: Dict) -> bool:
        """Check if spell data has all required fields"""
        required_fields = [
            'name', 'level', 'school', 'casting_time', 'range',
            'duration', 'area_of_effect', 'saving_throw', 'components', 'description'
        ]
        return all(field in spell_data for field in required_fields)

    def _serialize_spell(self, spell: Spell) -> Dict:
        """Serialize a spell"""
        return {
            'name': spell.name,
            'level': spell.level,
            'school': spell.school,
            'casting_time': spell.casting_time,
            'range': spell.range,
            'duration': spell.duration,
            'area_of_effect': spell.area_of_effect,
            'saving_throw': spell.saving_throw,
            'components': spell.components,
            'description': spell.description,
            'class_availability': spell.class_availability if hasattr(spell, 'class_availability') else []
        }

    def _serialize_spell_slots(self, spell_slots) -> List[Dict]:
        """Serialize memorized spell slots"""
        slots = []
        for slot in spell_slots:
            slot_data = {
                'level': slot.level,
                'is_used': slot.is_used
            }
            if slot.spell:
                slot_data['spell'] = self._serialize_spell(slot.spell)
            slots.append(slot_data)
        return slots

    def _deserialize_character(self, data: Dict) -> PlayerCharacter:
        """Deserialize character data into PlayerCharacter instance"""
        from ..entities.player import PlayerCharacter, Inventory, Equipment, SpellSlot

        # Load money - migrate old gold to new system if needed
        old_gold = data.get('gold', 0)
        cp = data.get('copper_pieces', 0)
        sp = data.get('silver_pieces', 0)
        ep = data.get('electrum_pieces', 0)
        gp = data.get('gold_pieces', 0)
        pp = data.get('platinum_pieces', 0)

        # Migration: if no money breakdown but has old gold, migrate it
        if (cp == 0 and sp == 0 and ep == 0 and gp == 0 and pp == 0) and old_gold > 0:
            gp = old_gold
            old_gold = 0  # Clear old field after migration

        # Create character
        character = PlayerCharacter(
            id=data['id'],  # Pass the ID from the loaded data
            name=data['name'],
            race=data['race'],
            char_class=data['class'],
            alignment=data.get('alignment', 'True Neutral'),  # Backward compatible with old saves
            strength=data['strength'],
            strength_percentile=data.get('strength_percentile', 0),
            dexterity=data['dexterity'],
            constitution=data['constitution'],
            intelligence=data['intelligence'],
            wisdom=data['wisdom'],
            charisma=data['charisma'],
            hp_max=data['hp_max'],
            hp_current=data['hp_current'],
            ac=data['ac'],
            thac0=data['thac0'],
            level=data['level'],
            xp=data['xp'],
            gold=old_gold,  # Will be 0 after migration
            # Money breakdown (new system)
            copper_pieces=cp,
            silver_pieces=sp,
            electrum_pieces=ep,
            gold_pieces=gp,
            platinum_pieces=pp
        )

        # Restore THAC0 progress (for fractional progression tracking)
        character._thac0_progress = data.get('thac0_progress', 0.0)

        # Restore inventory
        for item_data in data['inventory']:
            item = self._deserialize_item(item_data)
            if item:
                character.inventory.add_item(item)

        # Restore equipment
        if 'equipped' in data:
            if 'weapon' in data['equipped']:
                weapon_data = data['equipped']['weapon']
                character.equipment.weapon = Weapon(
                    name=weapon_data['name'],
                    weight=weapon_data['weight'],
                    damage_sm=weapon_data['damage_sm'],
                    damage_l=weapon_data['damage_l'],
                    speed_factor=weapon_data['speed_factor'],
                    magic_bonus=weapon_data.get('magic_bonus', 0)
                )

            if 'armor' in data['equipped']:
                armor_data = data['equipped']['armor']
                character.equipment.armor = Armor(
                    name=armor_data['name'],
                    weight=armor_data['weight'],
                    ac=armor_data['ac'],
                    armor_type=armor_data.get('armor_type', 'light'),
                    movement_rate=armor_data.get('movement_rate', 12),
                    magic_bonus=armor_data.get('magic_bonus', 0)
                )

            if 'shield' in data['equipped']:
                shield_data = data['equipped']['shield']
                character.equipment.shield = Shield(
                    name=shield_data['name'],
                    weight=shield_data['weight'],
                    ac_bonus=shield_data['ac_bonus'],
                    magic_bonus=shield_data.get('magic_bonus', 0)
                )

            if 'light' in data['equipped']:
                light_data = data['equipped']['light']
                character.equipment.light_source = LightSource(
                    name=light_data['name'],
                    weight=light_data['weight'],
                    burn_time_turns=light_data['burn_time_turns'],
                    light_radius=30,
                    turns_remaining=light_data['turns_remaining']
                )

        # Restore spells
        character.spells_known = []
        for spell_data in data.get('spells_known', []):
            # Handle both old and new format
            if self._is_complete_spell_data(spell_data):
                character.spells_known.append(Spell(**spell_data))
            # Skip incomplete spell data (old format)

        character.spells_memorized = []
        for slot_data in data.get('spells_memorized', []):
            slot = SpellSlot(level=slot_data['level'], is_used=slot_data['is_used'])
            if 'spell' in slot_data and slot_data['spell'] is not None and self._is_complete_spell_data(slot_data['spell']):
                slot.spell = Spell(**slot_data['spell'])
            character.spells_memorized.append(slot)

        # Restore conditions
        character.conditions = set(data.get('conditions', []))

        return character

    def _deserialize_item(self, item_data: Dict):
        """Deserialize item data into Item instance"""
        item_type = item_data.get('type', 'generic')

        if item_type == 'weapon':
            # Use defensive defaults for backward compatibility with old save files
            # that may have been created before Bug #1 fix (treasure conversion)
            return Weapon(
                name=item_data.get('name', 'Unknown Weapon'),
                weight=item_data.get('weight', 1.0),
                damage_sm=item_data.get('damage_sm', '1d4'),  # Default to dagger damage
                damage_l=item_data.get('damage_l', '1d4'),
                speed_factor=item_data.get('speed_factor', 5),
                magic_bonus=item_data.get('magic_bonus', 0)
            )
        elif item_type == 'armor':
            # Use defensive defaults for backward compatibility
            return Armor(
                name=item_data.get('name', 'Unknown Armor'),
                weight=item_data.get('weight', 10.0),
                ac=item_data.get('ac', 10),  # Default to unarmored AC
                armor_type=item_data.get('armor_type', 'light'),
                movement_rate=item_data.get('movement_rate', 12),
                magic_bonus=item_data.get('magic_bonus', 0)
            )
        elif item_type == 'light_source':
            # Use defaults for backward compatibility with legacy saves
            burn_time = item_data.get('burn_time_turns', 6)  # Default: torch (6 turns)
            return LightSource(
                name=item_data['name'],
                weight=item_data['weight'],
                burn_time_turns=burn_time,
                light_radius=item_data.get('light_radius', 30),
                turns_remaining=item_data.get('turns_remaining', burn_time)
            )
        else:
            # Generic item with defensive defaults
            return Item(
                name=item_data.get('name', 'Unknown Item'),
                item_type=item_type,
                weight=item_data.get('weight', 0.1)
            )
