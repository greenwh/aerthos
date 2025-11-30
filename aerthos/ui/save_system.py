"""
Save/Load system for game checkpoints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class SaveSystem:
    """Handles game saving and loading"""

    def __init__(self, save_dir: str = None):
        if save_dir is None:
            self.save_dir = Path.home() / '.aerthos' / 'saves'
        else:
            self.save_dir = Path(save_dir)

        # Create save directory if it doesn't exist
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def save_game(self, game_state, slot: int = 1, description: str = ""):
        """
        Save game to a slot

        Args:
            game_state: GameState instance
            slot: Save slot number (1-3)
            description: Optional description for this save
        """

        save_data = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'player': self._serialize_player(game_state.player),
            'current_room_id': game_state.current_room.id,
            'dungeon_name': game_state.dungeon.name,
            'dungeon_state': game_state.dungeon.serialize(),
            'turns_elapsed': game_state.time_tracker.turns_elapsed,
            'total_hours': game_state.time_tracker.total_hours
        }

        filepath = self.save_dir / f'save_{slot}.json'

        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)

    def load_game(self, slot: int = 1) -> Optional[dict]:
        """
        Load game from a slot

        Args:
            slot: Save slot number

        Returns:
            Save data dictionary or None if not found
        """

        filepath = self.save_dir / f'save_{slot}.json'

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error: Save file in slot {slot} is corrupted: {e}")
            return None

    def list_saves(self) -> list:
        """
        List all available saves

        Returns:
            List of save info dictionaries
        """

        saves = []

        for slot in range(1, 4):
            filepath = self.save_dir / f'save_{slot}.json'

            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)

                    saves.append({
                        'slot': slot,
                        'character_name': data['player']['name'],
                        'level': data['player']['level'],
                        'class': data['player']['char_class'],
                        'timestamp': data['timestamp'],
                        'description': data.get('description', '')
                    })
                except (json.JSONDecodeError, KeyError, IOError) as e:
                    # Skip corrupted or incomplete save files
                    print(f"Warning: Save slot {slot} is corrupted and will be skipped: {e}")
                    continue

        return saves

    def _serialize_inventory(self, inventory) -> list:
        """Serialize inventory items"""
        from aerthos.entities.player import Weapon, Armor, LightSource

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

    def _serialize_equipment(self, equipment) -> dict:
        """Serialize equipped items"""
        equipped = {}

        if equipment.weapon:
            equipped['weapon'] = {
                'name': equipment.weapon.name,
                'damage_sm': equipment.weapon.damage_sm,
                'damage_l': equipment.weapon.damage_l,
                'speed_factor': equipment.weapon.speed_factor,
                'magic_bonus': equipment.weapon.magic_bonus,
                'weight': equipment.weapon.weight
            }

        if equipment.armor:
            equipped['armor'] = {
                'name': equipment.armor.name,
                'ac': equipment.armor.ac,
                'armor_type': equipment.armor.armor_type,
                'movement_rate': equipment.armor.movement_rate,
                'magic_bonus': getattr(equipment.armor, 'magic_bonus', 0),
                'weight': equipment.armor.weight
            }

        if equipment.shield:
            equipped['shield'] = {
                'name': equipment.shield.name,
                'ac_bonus': equipment.shield.ac_bonus,
                'magic_bonus': getattr(equipment.shield, 'magic_bonus', 0),
                'weight': equipment.shield.weight
            }

        if equipment.light_source:
            equipped['light'] = {
                'name': equipment.light_source.name,
                'burn_time_turns': equipment.light_source.burn_time_turns,
                'turns_remaining': equipment.light_source.turns_remaining,
                'light_radius': getattr(equipment.light_source, 'light_radius', 30),
                'weight': equipment.light_source.weight
            }

        return equipped

    def _serialize_player(self, player) -> dict:
        """Serialize player character"""

        return {
            'name': player.name,
            'race': player.race,
            'char_class': player.char_class,
            'level': player.level,
            'strength': player.strength,
            'dexterity': player.dexterity,
            'constitution': player.constitution,
            'intelligence': player.intelligence,
            'wisdom': player.wisdom,
            'charisma': player.charisma,
            'strength_percentile': player.strength_percentile,
            'hp_current': player.hp_current,
            'hp_max': player.hp_max,
            'ac': player.ac,
            'thac0': player.thac0,
            'xp': player.xp,
            'xp_to_next_level': player.xp_to_next_level,
            'gold': player.gold,  # Deprecated - kept for backward compatibility
            # Money breakdown (AD&D 1e standard coinage)
            'copper_pieces': getattr(player, 'copper_pieces', 0),
            'silver_pieces': getattr(player, 'silver_pieces', 0),
            'electrum_pieces': getattr(player, 'electrum_pieces', 0),
            'gold_pieces': getattr(player, 'gold_pieces', 0),
            'platinum_pieces': getattr(player, 'platinum_pieces', 0),
            'conditions': list(player.conditions),  # Convert set to list for JSON
            'inventory': self._serialize_inventory(player.inventory),
            'equipment': self._serialize_equipment(player.equipment),
            'thief_skills': player.thief_skills,
            # Spells
            'spells_known': [spell.name for spell in player.spells_known],
            'spells_memorized': [
                {
                    'level': slot.level,
                    'spell': slot.spell.name if slot.spell else None,
                    'is_used': slot.is_used
                }
                for slot in player.spells_memorized
            ]
        }
