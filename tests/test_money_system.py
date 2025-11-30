"""
Tests for Money System

Tests the AD&D 1e five-coin system:
- Money breakdown (cp, sp, ep, gp, pp)
- Helper methods (add, subtract, has, total value)
- Migration from old gold field
- Persistence through save/load
- Display formatting
"""

import unittest
from aerthos.entities.player import PlayerCharacter
from aerthos.storage.character_roster import CharacterRoster
import tempfile
import shutil
from pathlib import Path


class TestMoneyHelperMethods(unittest.TestCase):
    """Test PlayerCharacter money helper methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.player = PlayerCharacter(
            name="Test Hero",
            race="Human",
            char_class="Fighter",
            alignment="Lawful Good",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=10,
            charisma=13,
            hp_max=10,
            hp_current=10,
            ac=10,
            thac0=19,
            level=1,
            xp=0
        )

    def test_get_total_gold_value_empty(self):
        """Test total gold value with no money"""
        self.assertEqual(self.player.get_total_gold_value(), 0.0)

    def test_get_total_gold_value_single_type(self):
        """Test total gold value with single coin type"""
        self.player.gold_pieces = 100
        self.assertEqual(self.player.get_total_gold_value(), 100.0)

        self.player.gold_pieces = 0
        self.player.platinum_pieces = 10
        self.assertEqual(self.player.get_total_gold_value(), 50.0)  # 10 pp = 50 gp

    def test_get_total_gold_value_all_types(self):
        """Test total gold value with all coin types"""
        self.player.copper_pieces = 100  # 100 cp = 1 gp
        self.player.silver_pieces = 20   # 20 sp = 2 gp
        self.player.electrum_pieces = 10 # 10 ep = 5 gp
        self.player.gold_pieces = 50     # 50 gp = 50 gp
        self.player.platinum_pieces = 5  # 5 pp = 25 gp
        # Total: 1 + 2 + 5 + 50 + 25 = 83 gp
        self.assertEqual(self.player.get_total_gold_value(), 83.0)

    def test_get_total_gold_value_includes_deprecated_gold(self):
        """Test that deprecated gold field is included in total"""
        self.player.gold = 30  # Old field
        self.player.gold_pieces = 20  # New field
        self.assertEqual(self.player.get_total_gold_value(), 50.0)

    def test_add_money_single_type(self):
        """Test adding single coin type"""
        self.player.add_money(gp=100)
        self.assertEqual(self.player.gold_pieces, 100)

    def test_add_money_multiple_types(self):
        """Test adding multiple coin types"""
        self.player.add_money(cp=50, sp=20, ep=10, gp=100, pp=5)
        self.assertEqual(self.player.copper_pieces, 50)
        self.assertEqual(self.player.silver_pieces, 20)
        self.assertEqual(self.player.electrum_pieces, 10)
        self.assertEqual(self.player.gold_pieces, 100)
        self.assertEqual(self.player.platinum_pieces, 5)

    def test_add_money_accumulates(self):
        """Test that adding money accumulates"""
        self.player.add_money(gp=50)
        self.player.add_money(gp=30)
        self.assertEqual(self.player.gold_pieces, 80)

    def test_subtract_money_success(self):
        """Test successful money subtraction"""
        self.player.gold_pieces = 100
        result = self.player.subtract_money(gp=50)
        self.assertTrue(result)
        self.assertEqual(self.player.gold_pieces, 50)

    def test_subtract_money_insufficient_funds(self):
        """Test subtraction with insufficient funds"""
        self.player.gold_pieces = 30
        result = self.player.subtract_money(gp=50)
        self.assertFalse(result)
        self.assertEqual(self.player.gold_pieces, 30)  # Unchanged

    def test_subtract_money_exact_amount(self):
        """Test subtracting exact amount"""
        self.player.gold_pieces = 100
        result = self.player.subtract_money(gp=100)
        self.assertTrue(result)
        self.assertEqual(self.player.gold_pieces, 0)

    def test_subtract_money_multiple_types(self):
        """Test subtracting multiple coin types"""
        self.player.copper_pieces = 100
        self.player.silver_pieces = 50
        self.player.gold_pieces = 100
        result = self.player.subtract_money(cp=50, sp=25, gp=60)
        self.assertTrue(result)
        self.assertEqual(self.player.copper_pieces, 50)
        self.assertEqual(self.player.silver_pieces, 25)
        self.assertEqual(self.player.gold_pieces, 40)

    def test_subtract_money_insufficient_single_type(self):
        """Test subtraction fails if any single type is insufficient"""
        self.player.copper_pieces = 100
        self.player.gold_pieces = 100
        result = self.player.subtract_money(cp=50, gp=200)  # Not enough gold
        self.assertFalse(result)
        # Nothing should be subtracted
        self.assertEqual(self.player.copper_pieces, 100)
        self.assertEqual(self.player.gold_pieces, 100)

    def test_has_money_true(self):
        """Test has_money returns True when funds are sufficient"""
        self.player.gold_pieces = 100
        self.assertTrue(self.player.has_money(gp=50))
        self.assertTrue(self.player.has_money(gp=100))

    def test_has_money_false(self):
        """Test has_money returns False when funds are insufficient"""
        self.player.gold_pieces = 30
        self.assertFalse(self.player.has_money(gp=50))

    def test_has_money_multiple_types(self):
        """Test has_money with multiple coin types"""
        self.player.copper_pieces = 100
        self.player.silver_pieces = 50
        self.player.gold_pieces = 100
        self.assertTrue(self.player.has_money(cp=50, sp=25, gp=60))
        self.assertFalse(self.player.has_money(cp=50, sp=60, gp=60))  # Not enough silver


class TestMoneyMigration(unittest.TestCase):
    """Test migration from old gold field to new money breakdown"""

    def setUp(self):
        """Set up temporary directory for character saves"""
        self.temp_dir = tempfile.mkdtemp()
        self.roster = CharacterRoster(roster_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_save_with_money_breakdown(self):
        """Test saving character with money breakdown"""
        player = PlayerCharacter(
            name="Rich Hero",
            race="Human",
            char_class="Fighter",
            alignment="Lawful Good",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=10,
            charisma=13,
            hp_max=10,
            hp_current=10,
            ac=10,
            thac0=19,
            level=1,
            xp=0,
            copper_pieces=100,
            silver_pieces=50,
            electrum_pieces=25,
            gold_pieces=200,
            platinum_pieces=10
        )

        char_id = self.roster.save_character(player)
        loaded = self.roster.load_character(character_id=char_id)

        self.assertEqual(loaded.copper_pieces, 100)
        self.assertEqual(loaded.silver_pieces, 50)
        self.assertEqual(loaded.electrum_pieces, 25)
        self.assertEqual(loaded.gold_pieces, 200)
        self.assertEqual(loaded.platinum_pieces, 10)

    def test_migration_from_old_gold_field(self):
        """Test migration from old gold field to new breakdown"""
        # Create a character save manually with old format
        import json
        old_save = {
            'id': 'test123',
            'created': '2025-01-01T00:00:00',
            'name': 'Old Hero',
            'race': 'Human',
            'class': 'Fighter',
            'level': 1,
            'xp': 0,
            'alignment': 'Lawful Good',
            'hp_max': 10,
            'hp_current': 10,
            'ac': 10,
            'thac0': 19,
            'gold': 150,  # Old field only
            'strength': 16,
            'dexterity': 14,
            'constitution': 15,
            'intelligence': 12,
            'wisdom': 10,
            'charisma': 13,
            'strength_percentile': 0,
            'inventory': [],
            'equipped': {},
            'spells_known': [],
            'spells_memorized': [],
            'conditions': []
        }

        # Write old format save file
        filepath = Path(self.temp_dir) / 'old_hero_test123.json'
        with open(filepath, 'w') as f:
            json.dump(old_save, f)

        # Load and verify migration
        loaded = self.roster.load_character(character_id='test123')
        self.assertEqual(loaded.gold_pieces, 150)  # Migrated
        self.assertEqual(loaded.gold, 0)  # Cleared after migration
        self.assertEqual(loaded.copper_pieces, 0)
        self.assertEqual(loaded.silver_pieces, 0)
        self.assertEqual(loaded.electrum_pieces, 0)
        self.assertEqual(loaded.platinum_pieces, 0)

    def test_no_migration_when_breakdown_exists(self):
        """Test that migration doesn't happen if breakdown already exists"""
        player = PlayerCharacter(
            name="New Hero",
            race="Human",
            char_class="Fighter",
            alignment="Lawful Good",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=10,
            charisma=13,
            hp_max=10,
            hp_current=10,
            ac=10,
            thac0=19,
            level=1,
            xp=0,
            gold=100,  # Old field (should be ignored)
            gold_pieces=200  # New field (should take precedence)
        )

        char_id = self.roster.save_character(player)
        loaded = self.roster.load_character(character_id=char_id)

        self.assertEqual(loaded.gold_pieces, 200)  # New field preserved
        self.assertEqual(loaded.gold, 100)  # Old field also preserved for backward compat


class TestMoneyConversionRates(unittest.TestCase):
    """Test AD&D 1e standard conversion rates"""

    def setUp(self):
        """Set up test fixtures"""
        self.player = PlayerCharacter(
            name="Test Hero",
            race="Human",
            char_class="Fighter",
            alignment="Lawful Good",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=10,
            charisma=13,
            hp_max=10,
            hp_current=10,
            ac=10,
            thac0=19,
            level=1,
            xp=0
        )

    def test_copper_conversion(self):
        """Test copper to gold conversion (100 cp = 1 gp)"""
        self.player.copper_pieces = 100
        self.assertEqual(self.player.get_total_gold_value(), 1.0)

    def test_silver_conversion(self):
        """Test silver to gold conversion (10 sp = 1 gp)"""
        self.player.silver_pieces = 10
        self.assertEqual(self.player.get_total_gold_value(), 1.0)

    def test_electrum_conversion(self):
        """Test electrum to gold conversion (2 ep = 1 gp)"""
        self.player.electrum_pieces = 2
        self.assertEqual(self.player.get_total_gold_value(), 1.0)

    def test_platinum_conversion(self):
        """Test platinum to gold conversion (1 pp = 5 gp)"""
        self.player.platinum_pieces = 1
        self.assertEqual(self.player.get_total_gold_value(), 5.0)

    def test_mixed_conversion(self):
        """Test mixed coin conversion"""
        # 1000 cp = 10 gp
        # 100 sp = 10 gp
        # 20 ep = 10 gp
        # 10 gp = 10 gp
        # 2 pp = 10 gp
        # Total = 50 gp
        self.player.copper_pieces = 1000
        self.player.silver_pieces = 100
        self.player.electrum_pieces = 20
        self.player.gold_pieces = 10
        self.player.platinum_pieces = 2
        self.assertEqual(self.player.get_total_gold_value(), 50.0)


class TestMoneyEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.player = PlayerCharacter(
            name="Test Hero",
            race="Human",
            char_class="Fighter",
            alignment="Lawful Good",
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=12,
            wisdom=10,
            charisma=13,
            hp_max=10,
            hp_current=10,
            ac=10,
            thac0=19,
            level=1,
            xp=0
        )

    def test_add_zero_money(self):
        """Test adding zero money (should work but not change anything)"""
        self.player.add_money()
        self.assertEqual(self.player.get_total_gold_value(), 0.0)

    def test_subtract_zero_money(self):
        """Test subtracting zero money (should always succeed)"""
        result = self.player.subtract_money()
        self.assertTrue(result)

    def test_has_zero_money(self):
        """Test checking for zero money (should always be true)"""
        self.assertTrue(self.player.has_money())

    def test_negative_money_not_allowed(self):
        """Test that negative money values are prevented"""
        self.player.gold_pieces = 10
        result = self.player.subtract_money(gp=20)
        self.assertFalse(result)
        self.assertEqual(self.player.gold_pieces, 10)  # Unchanged

    def test_very_large_amounts(self):
        """Test handling very large money amounts (dragon hoards)"""
        self.player.platinum_pieces = 10000
        self.assertEqual(self.player.get_total_gold_value(), 50000.0)

    def test_fractional_gold_value(self):
        """Test that total value can be fractional"""
        self.player.copper_pieces = 1  # 0.01 gp
        self.assertEqual(self.player.get_total_gold_value(), 0.01)


if __name__ == '__main__':
    unittest.main()
