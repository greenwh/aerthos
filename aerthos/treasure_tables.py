"""
Treasure Tables for Aerthos Dungeon Generation

Based on AD&D Dungeon Master's Guide random treasure determination methodology.
Ensures all magic items in equipment.json have a chance to appear, weighted by
type and rarity to maintain game balance.

Design Philosophy (from DMG):
- Consumables (potions, scrolls) are most common
- Permanent items (rings, rods) are rare
- Armor and weapons are moderately common
- Dungeon level affects treasure quality
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TreasureTables:
    """
    Manages random magic item generation with weighted tables.

    Tables are organized by:
    1. Main table - determines category (Potions, Scrolls, Weapons, etc.)
    2. Category tables - specific items within each category
    3. Rarity tiers - Common, Uncommon, Rare, Very Rare
    """

    def __init__(self, equipment_data: Optional[Dict] = None):
        """Initialize treasure tables from equipment data."""
        if equipment_data is None:
            # Load from file
            data_dir = Path(__file__).parent / 'data'
            with open(data_dir / 'equipment.json', 'r') as f:
                equipment_data = json.load(f)

        self.equipment = equipment_data
        self._build_tables()

    def _build_tables(self):
        """Build all treasure tables from equipment data."""
        # Initialize category tables
        self.potions = []
        self.scrolls = []
        self.rings = []
        self.rods_staves_wands = []
        self.armor = []
        self.weapons = []
        self.wondrous_items = []
        self.other_magic = []

        # Categorize all magic items
        for item_id, item_data in self.equipment.items():
            category = self._categorize_item(item_id, item_data)
            if category:
                rarity = self._determine_rarity(item_id, item_data)
                entry = {
                    'id': item_id,
                    'name': item_data.get('name', item_id),
                    'rarity': rarity,
                    'data': item_data
                }

                if category == 'potions':
                    self.potions.append(entry)
                elif category == 'scrolls':
                    self.scrolls.append(entry)
                elif category == 'rings':
                    self.rings.append(entry)
                elif category == 'rods_staves_wands':
                    self.rods_staves_wands.append(entry)
                elif category == 'armor':
                    self.armor.append(entry)
                elif category == 'weapons':
                    self.weapons.append(entry)
                elif category == 'wondrous':
                    self.wondrous_items.append(entry)
                elif category == 'other':
                    self.other_magic.append(entry)

    def _categorize_item(self, item_id: str, item_data: Dict) -> Optional[str]:
        """Categorize an item into treasure table categories."""
        name = item_data.get('name', item_id).lower()
        item_type = item_data.get('type', '').lower()

        # Potions
        if 'potion' in name or 'elixir' in name or item_type == 'potion':
            return 'potions'

        # Scrolls
        if 'scroll' in name or item_type == 'scroll':
            return 'scrolls'

        # Rings
        if 'ring' in name and 'of' in name:
            return 'rings'

        # Rods, Staves, Wands
        if any(x in name for x in ['wand', 'staff', 'rod']):
            return 'rods_staves_wands'

        # Armor (includes shields)
        if (any(x in name for x in ['mail', 'plate', 'leather', 'shield', 'armor']) and '+' in name):
            return 'armor'
        if any(x in item_type for x in ['armor', 'shield']):
            return 'armor'

        # Weapons
        weapon_types = ['sword', 'axe', 'mace', 'hammer', 'dagger', 'spear',
                       'bow', 'arrow', 'bolt', 'flail', 'trident', 'javelin']
        if any(wtype in name for wtype in weapon_types) and ('+' in name or 'magic' in item_type):
            return 'weapons'
        if 'weapon' in item_type and 'magic' in item_type:
            return 'weapons'

        # Wondrous Items
        wondrous_types = ['cloak', 'boots', 'bracers', 'gauntlets', 'belt',
                         'girdle', 'bag of', 'amulet', 'necklace', 'hat',
                         'helm', 'gloves', 'rope', 'carpet', 'gem', 'crystal']
        if any(wtype in name for wtype in wondrous_types):
            return 'wondrous'

        # Other Magic
        if 'magic' in item_type or any(x in name for x in ['magical', 'enchanted', 'mystic', 'arcane']):
            return 'other'

        return None

    def _determine_rarity(self, item_id: str, item_data: Dict) -> str:
        """Determine item rarity based on item properties."""
        name = item_data.get('name', item_id).lower()

        # Rarity indicators
        # Common: +1 items, basic potions, common scrolls
        # Uncommon: +2 items, uncommon potions, protection scrolls
        # Rare: +3 items, special weapons/armor, powerful wondrous items
        # Very Rare: +4/+5 items, artifacts, legendary items

        # Check for explicit rarity
        explicit_rarity = item_data.get('rarity', '').lower()
        if explicit_rarity in ['common', 'uncommon', 'rare', 'very rare', 'legendary']:
            if explicit_rarity == 'legendary':
                return 'very_rare'
            return explicit_rarity.replace(' ', '_')

        # Infer rarity from bonuses
        if '+5' in name or '+4' in name:
            return 'very_rare'
        if '+3' in name:
            return 'rare'
        if '+2' in name:
            return 'uncommon'
        if '+1' in name:
            return 'common'

        # Infer from item type
        if any(x in name for x in ['artifact', 'legendary', 'crown of', 'orb of']):
            return 'very_rare'

        if any(x in name for x in ['greater', 'superior', 'major']):
            return 'rare'

        if any(x in name for x in ['lesser', 'minor', 'basic']):
            return 'common'

        # Default rarities by category
        if item_data.get('type') == 'potion':
            return 'common'
        if item_data.get('type') == 'scroll':
            return 'uncommon'
        if 'ring' in name:
            return 'rare'
        if any(x in name for x in ['wand', 'staff', 'rod']):
            return 'rare'

        # Default to uncommon
        return 'uncommon'

    def roll_magic_item(self, dungeon_level: int = 1) -> Optional[Dict]:
        """
        Roll for a random magic item.

        Args:
            dungeon_level: Dungeon level (1-10+), affects rarity distribution

        Returns:
            Dict with item data or None
        """
        # Main treasure table (weighted like DMG)
        # Percentile roll (1-100)
        roll = random.randint(1, 100)

        # Determine category based on roll
        # Weighted to favor consumables and common items
        if roll <= 20:
            category = 'potions'
        elif roll <= 35:
            category = 'scrolls'
        elif roll <= 40:
            category = 'rings'
        elif roll <= 45:
            category = 'rods_staves_wands'
        elif roll <= 60:
            category = 'armor'
        elif roll <= 76:
            category = 'weapons'
        elif roll <= 90:
            category = 'wondrous'
        else:
            category = 'other'

        # Get items from selected category
        items = self._get_category_items(category)

        if not items:
            return None

        # Filter by dungeon level (higher levels = better items)
        available_items = self._filter_by_dungeon_level(items, dungeon_level)

        if not available_items:
            # Fallback to all items if filtering is too restrictive
            available_items = items

        # Select random item
        item = random.choice(available_items)

        return {
            'id': item['id'],
            'name': item['name'],
            'category': category,
            'rarity': item['rarity'],
            'data': item['data']
        }

    def _get_category_items(self, category: str) -> List[Dict]:
        """Get all items in a category."""
        if category == 'potions':
            return self.potions
        elif category == 'scrolls':
            return self.scrolls
        elif category == 'rings':
            return self.rings
        elif category == 'rods_staves_wands':
            return self.rods_staves_wands
        elif category == 'armor':
            return self.armor
        elif category == 'weapons':
            return self.weapons
        elif category == 'wondrous':
            return self.wondrous_items
        elif category == 'other':
            return self.other_magic
        return []

    def _filter_by_dungeon_level(self, items: List[Dict], dungeon_level: int) -> List[Dict]:
        """Filter items based on dungeon level to appropriate rarity."""
        # Dungeon level -> rarity mapping
        # Level 1-2: Common only
        # Level 3-4: Common + Uncommon
        # Level 5-6: Common + Uncommon + Rare
        # Level 7-8: Uncommon + Rare
        # Level 9+: Uncommon + Rare + Very Rare

        if dungeon_level <= 2:
            allowed_rarities = ['common']
        elif dungeon_level <= 4:
            allowed_rarities = ['common', 'uncommon']
        elif dungeon_level <= 6:
            allowed_rarities = ['common', 'uncommon', 'rare']
        elif dungeon_level <= 8:
            allowed_rarities = ['uncommon', 'rare']
        else:
            allowed_rarities = ['uncommon', 'rare', 'very_rare']

        filtered = [item for item in items if item['rarity'] in allowed_rarities]

        return filtered

    def roll_treasure_hoard(self, dungeon_level: int = 1, hoard_size: str = 'small') -> List[Dict]:
        """
        Roll for a treasure hoard (multiple items).

        Args:
            dungeon_level: Dungeon level (1-10+)
            hoard_size: 'small', 'medium', 'large', or 'dragon'

        Returns:
            List of item dicts
        """
        # Determine number of items based on hoard size
        if hoard_size == 'small':
            num_items = random.randint(1, 3)
        elif hoard_size == 'medium':
            num_items = random.randint(2, 5)
        elif hoard_size == 'large':
            num_items = random.randint(4, 8)
        elif hoard_size == 'dragon':
            num_items = random.randint(6, 12)
        else:
            num_items = 1

        items = []
        for _ in range(num_items):
            item = self.roll_magic_item(dungeon_level)
            if item:
                items.append(item)

        return items

    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics on items in each category."""
        return {
            'Potions': len(self.potions),
            'Scrolls': len(self.scrolls),
            'Rings': len(self.rings),
            'Rods/Staves/Wands': len(self.rods_staves_wands),
            'Armor': len(self.armor),
            'Weapons': len(self.weapons),
            'Wondrous Items': len(self.wondrous_items),
            'Other Magic': len(self.other_magic)
        }

    def get_rarity_stats(self) -> Dict[str, int]:
        """Get statistics on items by rarity."""
        all_items = (self.potions + self.scrolls + self.rings +
                    self.rods_staves_wands + self.armor + self.weapons +
                    self.wondrous_items + self.other_magic)

        rarity_counts = {'common': 0, 'uncommon': 0, 'rare': 0, 'very_rare': 0}
        for item in all_items:
            rarity = item['rarity']
            if rarity in rarity_counts:
                rarity_counts[rarity] += 1

        return rarity_counts


# Convenience function for dungeon generator
def generate_magic_item(dungeon_level: int = 1, tables: Optional[TreasureTables] = None) -> Optional[str]:
    """
    Generate a single magic item ID for dungeon generation.

    Args:
        dungeon_level: Current dungeon level
        tables: Pre-initialized TreasureTables instance (optional)

    Returns:
        Item ID string or None
    """
    if tables is None:
        tables = TreasureTables()

    item = tables.roll_magic_item(dungeon_level)
    if item:
        return item['id']
    return None


def generate_treasure_hoard(dungeon_level: int = 1, hoard_size: str = 'medium',
                            tables: Optional[TreasureTables] = None) -> List[str]:
    """
    Generate multiple magic items for a treasure hoard.

    Args:
        dungeon_level: Current dungeon level
        hoard_size: 'small', 'medium', 'large', or 'dragon'
        tables: Pre-initialized TreasureTables instance (optional)

    Returns:
        List of item IDs
    """
    if tables is None:
        tables = TreasureTables()

    items = tables.roll_treasure_hoard(dungeon_level, hoard_size)
    return [item['id'] for item in items]


if __name__ == '__main__':
    # Test the treasure tables
    print("=== Aerthos Treasure Tables ===\n")

    tables = TreasureTables()

    print("Category Statistics:")
    for category, count in tables.get_category_stats().items():
        print(f"  {category}: {count} items")

    print("\nRarity Statistics:")
    for rarity, count in tables.get_rarity_stats().items():
        print(f"  {rarity.replace('_', ' ').title()}: {count} items")

    print("\n=== Sample Treasure Rolls ===\n")

    # Test different dungeon levels
    for level in [1, 3, 5, 7, 10]:
        print(f"Dungeon Level {level}:")
        for _ in range(5):
            item = tables.roll_magic_item(level)
            if item:
                print(f"  [{item['rarity']:12s}] {item['name']} ({item['category']})")
        print()

    print("=== Sample Treasure Hoards ===\n")

    # Test different hoard sizes
    for size in ['small', 'medium', 'large']:
        print(f"{size.title()} Hoard (Level 5):")
        items = tables.roll_treasure_hoard(5, size)
        for item in items:
            print(f"  [{item['rarity']:12s}] {item['name']}")
        print()
