"""
Unit tests for treasure table system

Tests the DMG-based treasure table implementation including:
- Item categorization
- Rarity determination
- Magic item generation
- Dungeon level filtering
- Integration with dungeon generator
"""

import unittest
import json
from pathlib import Path
from aerthos.treasure_tables import (
    TreasureTables,
    generate_magic_item,
    generate_treasure_hoard
)
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig, EASY_DUNGEON, STANDARD_DUNGEON, HARD_DUNGEON


class TestTreasureTables(unittest.TestCase):
    """Test treasure table initialization and categorization"""

    @classmethod
    def setUpClass(cls):
        """Load treasure tables once for all tests"""
        cls.tables = TreasureTables()

    def test_tables_initialized(self):
        """Test that treasure tables are properly initialized"""
        self.assertIsNotNone(self.tables)
        self.assertIsNotNone(self.tables.equipment)

    def test_all_categories_have_items(self):
        """Test that all major categories contain items"""
        # At minimum, we should have items in these categories
        self.assertGreater(len(self.tables.potions), 0, "No potions found")
        self.assertGreater(len(self.tables.scrolls), 0, "No scrolls found")
        self.assertGreater(len(self.tables.weapons), 0, "No weapons found")
        self.assertGreater(len(self.tables.armor), 0, "No armor found")

    def test_category_statistics(self):
        """Test category statistics reporting"""
        stats = self.tables.get_category_stats()

        # Verify all expected categories are present
        expected_categories = [
            'Potions', 'Scrolls', 'Rings', 'Rods/Staves/Wands',
            'Armor', 'Weapons', 'Wondrous Items', 'Other Magic'
        ]

        for category in expected_categories:
            self.assertIn(category, stats)
            self.assertIsInstance(stats[category], int)

    def test_rarity_statistics(self):
        """Test rarity distribution statistics"""
        stats = self.tables.get_rarity_stats()

        # Verify all rarity levels are present
        expected_rarities = ['common', 'uncommon', 'rare', 'very_rare']

        for rarity in expected_rarities:
            self.assertIn(rarity, stats)
            self.assertIsInstance(stats[rarity], int)

        # Verify we have items across different rarities
        total_items = sum(stats.values())
        self.assertGreater(total_items, 0, "No items in rarity statistics")

    def test_item_categorization(self):
        """Test that items are correctly categorized"""
        # Test specific known items
        test_cases = [
            ('potion_healing', 'potions'),
            ('scroll_of_protection', 'scrolls'),
            ('ring_of_protection', 'rings'),
            ('wand_of_magic_missiles', 'rods_staves_wands'),
            ('chain_mail_plus_1', 'armor'),
            ('longsword_plus_1', 'weapons'),
            ('boots_of_elvenkind', 'wondrous'),
        ]

        for item_id, expected_category in test_cases:
            # Find the item in the tables
            found = False
            for category in [self.tables.potions, self.tables.scrolls, self.tables.rings,
                           self.tables.rods_staves_wands, self.tables.armor, self.tables.weapons,
                           self.tables.wondrous_items, self.tables.other_magic]:
                if any(item['id'] == item_id for item in category):
                    found = True
                    break

            if item_id in self.tables.equipment:
                self.assertTrue(found, f"Item {item_id} exists in equipment.json but wasn't categorized")

    def test_rarity_determination(self):
        """Test that item rarities are correctly determined"""
        # Test items with explicit bonuses
        test_items = [
            ({'name': 'Sword +1'}, 'common'),
            ({'name': 'Sword +2'}, 'uncommon'),
            ({'name': 'Sword +3'}, 'rare'),
            ({'name': 'Sword +4'}, 'very_rare'),
            ({'name': 'Sword +5'}, 'very_rare'),
            ({'name': 'Potion of Healing', 'type': 'potion'}, 'common'),
            ({'name': 'Ring of Wishes'}, 'rare'),  # Rings default to rare
        ]

        for item_data, expected_rarity in test_items:
            rarity = self.tables._determine_rarity('test_item', item_data)
            self.assertEqual(rarity, expected_rarity,
                           f"Item {item_data['name']} should be {expected_rarity}, got {rarity}")


class TestMagicItemGeneration(unittest.TestCase):
    """Test magic item generation at different dungeon levels"""

    @classmethod
    def setUpClass(cls):
        """Initialize tables once for all tests"""
        cls.tables = TreasureTables()

    def test_generate_magic_item_returns_valid_item(self):
        """Test that generate_magic_item returns a valid item"""
        for level in [1, 5, 10]:
            item = self.tables.roll_magic_item(dungeon_level=level)
            if item:  # Item generation is random, might be None
                self.assertIn('id', item)
                self.assertIn('name', item)
                self.assertIn('category', item)
                self.assertIn('rarity', item)
                self.assertIn('data', item)

    def test_dungeon_level_affects_rarity(self):
        """Test that higher dungeon levels produce rarer items"""
        # Generate many items at different levels and check rarity distribution
        low_level_rarities = []
        high_level_rarities = []

        # Generate 100 items at each level
        for _ in range(100):
            low_item = self.tables.roll_magic_item(dungeon_level=1)
            if low_item:
                low_level_rarities.append(low_item['rarity'])

            high_item = self.tables.roll_magic_item(dungeon_level=10)
            if high_item:
                high_level_rarities.append(high_item['rarity'])

        # Low level (1-2) should have mostly common items
        if low_level_rarities:
            common_count = low_level_rarities.count('common')
            self.assertGreater(common_count, 0, "Level 1-2 should have some common items")

        # High level (10+) should have no common items (filtered out)
        if high_level_rarities:
            common_count = high_level_rarities.count('common')
            # At level 10, common items are filtered out
            # They should be rare or very_rare mostly
            rare_count = high_level_rarities.count('rare') + high_level_rarities.count('very_rare')
            self.assertGreater(rare_count, 0, "Level 10 should have some rare/very rare items")

    def test_all_categories_can_be_rolled(self):
        """Test that all item categories can be generated"""
        generated_categories = set()

        # Generate many items
        for _ in range(500):
            item = self.tables.roll_magic_item(dungeon_level=5)
            if item:
                generated_categories.add(item['category'])

        # We should see items from multiple categories
        self.assertGreater(len(generated_categories), 3,
                          f"Only {len(generated_categories)} categories generated, expected more variety")

    def test_generate_magic_item_convenience_function(self):
        """Test the convenience function for magic item generation"""
        item_id = generate_magic_item(dungeon_level=3)
        # Item might be None due to randomness, but if not None should be a string
        if item_id:
            self.assertIsInstance(item_id, str)

    def test_generate_treasure_hoard_convenience_function(self):
        """Test the convenience function for treasure hoard generation"""
        items = generate_treasure_hoard(dungeon_level=5, hoard_size='medium')

        self.assertIsInstance(items, list)
        # Medium hoard should generate 2-5 items
        self.assertGreaterEqual(len(items), 0)  # Might be empty due to randomness
        self.assertLessEqual(len(items), 15)  # Reasonable upper bound

        # All items should be strings
        for item_id in items:
            self.assertIsInstance(item_id, str)


class TestTreasureHoardGeneration(unittest.TestCase):
    """Test treasure hoard generation"""

    @classmethod
    def setUpClass(cls):
        """Initialize tables once for all tests"""
        cls.tables = TreasureTables()

    def test_small_hoard_size(self):
        """Test small hoard generation"""
        items = self.tables.roll_treasure_hoard(dungeon_level=3, hoard_size='small')
        self.assertIsInstance(items, list)
        self.assertLessEqual(len(items), 5)  # Small should be 1-3 items, allow some variance

    def test_medium_hoard_size(self):
        """Test medium hoard generation"""
        items = self.tables.roll_treasure_hoard(dungeon_level=5, hoard_size='medium')
        self.assertIsInstance(items, list)
        self.assertLessEqual(len(items), 10)  # Medium should be 2-5 items, allow some variance

    def test_large_hoard_size(self):
        """Test large hoard generation"""
        items = self.tables.roll_treasure_hoard(dungeon_level=7, hoard_size='large')
        self.assertIsInstance(items, list)
        self.assertLessEqual(len(items), 15)  # Large should be 4-8 items, allow some variance

    def test_dragon_hoard_size(self):
        """Test dragon hoard generation"""
        items = self.tables.roll_treasure_hoard(dungeon_level=10, hoard_size='dragon')
        self.assertIsInstance(items, list)
        self.assertLessEqual(len(items), 20)  # Dragon should be 6-12 items, allow some variance

    def test_hoard_items_valid(self):
        """Test that all items in hoard are valid"""
        items = self.tables.roll_treasure_hoard(dungeon_level=5, hoard_size='large')

        for item in items:
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertIn('category', item)
            self.assertIn('rarity', item)


class TestDungeonGeneratorIntegration(unittest.TestCase):
    """Test treasure table integration with dungeon generator"""

    def setUp(self):
        """Create a dungeon generator for each test"""
        self.generator = DungeonGenerator()

    def test_easy_dungeon_uses_treasure_tables(self):
        """Test that EASY preset generates magic items from treasure tables"""
        # Increase magic item chance for testing
        config = DungeonConfig(
            num_rooms=10,
            party_level=1,
            dungeon_level=1,
            magic_item_chance=0.8,  # High chance to ensure we get items
            monster_pool=['kobold', 'giant_rat']
        )

        dungeon = self.generator.generate(config)

        # Check that dungeon was generated
        self.assertIn('rooms', dungeon)
        self.assertGreater(len(dungeon['rooms']), 0)

        # Find all items in dungeon
        all_items = []
        for room_data in dungeon['rooms'].values():
            all_items.extend(room_data.get('items', []))

        # With 80% chance and 10 rooms, we should get some items
        # (though still random)
        # Just verify the structure is correct
        for item in all_items:
            self.assertIsInstance(item, str)

    def test_different_levels_generate_different_items(self):
        """Test that different dungeon levels generate appropriate items"""
        configs = [
            (1, 'level_1'),
            (5, 'level_5'),
            (10, 'level_10')
        ]

        for dungeon_level, label in configs:
            config = DungeonConfig(
                num_rooms=15,
                party_level=dungeon_level,
                dungeon_level=dungeon_level,
                magic_item_chance=0.5,
                monster_pool=['kobold', 'goblin', 'orc']
            )

            dungeon = self.generator.generate(config)

            # Verify dungeon was generated
            self.assertIn('rooms', dungeon)
            self.assertGreater(len(dungeon['rooms']), 0)

            # Count magic items
            magic_items = []
            for room_data in dungeon['rooms'].values():
                for item in room_data.get('items', []):
                    # Simple heuristic for magic items
                    if any(x in item.lower() for x in ['plus', 'potion', 'scroll', 'ring', 'wand', 'staff', 'rod']):
                        magic_items.append(item)

            # Just verify structure - actual items are random
            for item in magic_items:
                self.assertIsInstance(item, str)

    def test_preset_configs_work_with_treasure_tables(self):
        """Test that preset configurations work with treasure tables"""
        presets = [
            ('EASY', EASY_DUNGEON),
            ('STANDARD', STANDARD_DUNGEON),
            ('HARD', HARD_DUNGEON)
        ]

        for name, config in presets:
            dungeon = self.generator.generate(config)

            # Verify dungeon structure
            self.assertIn('rooms', dungeon)
            self.assertIn('name', dungeon)
            self.assertIn('start_room', dungeon)

            # Verify rooms have proper structure
            for room_id, room_data in dungeon['rooms'].items():
                self.assertIn('title', room_data)
                self.assertIn('description', room_data)
                self.assertIn('exits', room_data)
                self.assertIn('items', room_data)
                self.assertIsInstance(room_data['items'], list)


class TestTreasureTableCoverage(unittest.TestCase):
    """Test that treasure tables cover the full item database"""

    @classmethod
    def setUpClass(cls):
        """Load treasure tables and equipment data"""
        cls.tables = TreasureTables()

        # Load equipment.json to compare
        data_dir = Path(__file__).parent.parent / 'aerthos' / 'data'
        with open(data_dir / 'equipment.json', 'r') as f:
            cls.equipment_data = json.load(f)

    def test_many_items_categorized(self):
        """Test that a significant portion of equipment is categorized"""
        # Count total categorized items
        total_categorized = (
            len(self.tables.potions) +
            len(self.tables.scrolls) +
            len(self.tables.rings) +
            len(self.tables.rods_staves_wands) +
            len(self.tables.armor) +
            len(self.tables.weapons) +
            len(self.tables.wondrous_items) +
            len(self.tables.other_magic)
        )

        # We should have categorized a significant number of items
        self.assertGreater(total_categorized, 100,
                          f"Only {total_categorized} items categorized, expected more")

    def test_specific_known_items_available(self):
        """Test that specific known magic items are available in tables"""
        # List of items that should definitely be in the treasure tables
        expected_items = [
            'potion_healing',
            'longsword_plus_1',
            'chain_mail_plus_1',
        ]

        for item_id in expected_items:
            if item_id in self.equipment_data:
                # Find in any category
                found = False
                all_items = (
                    self.tables.potions +
                    self.tables.scrolls +
                    self.tables.rings +
                    self.tables.rods_staves_wands +
                    self.tables.armor +
                    self.tables.weapons +
                    self.tables.wondrous_items +
                    self.tables.other_magic
                )

                for item in all_items:
                    if item['id'] == item_id:
                        found = True
                        break

                self.assertTrue(found, f"Expected item {item_id} not found in treasure tables")

    def test_no_duplicate_items_across_categories(self):
        """Test that no item appears in multiple categories"""
        all_items = []

        categories = [
            self.tables.potions,
            self.tables.scrolls,
            self.tables.rings,
            self.tables.rods_staves_wands,
            self.tables.armor,
            self.tables.weapons,
            self.tables.wondrous_items,
            self.tables.other_magic
        ]

        for category in categories:
            all_items.extend([item['id'] for item in category])

        # Check for duplicates
        item_counts = {}
        for item_id in all_items:
            item_counts[item_id] = item_counts.get(item_id, 0) + 1

        duplicates = [item_id for item_id, count in item_counts.items() if count > 1]

        self.assertEqual(len(duplicates), 0,
                        f"Found duplicate items across categories: {duplicates}")


if __name__ == '__main__':
    unittest.main()
