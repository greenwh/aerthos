"""
Test suite for Combat System

Tests THAC0 combat resolution and dice rolling.
Critical for both CLI and Web UI game mechanics.
"""

import unittest
from unittest.mock import Mock, patch
from aerthos.engine.combat import DiceRoller, CombatResolver
from aerthos.entities.character import Character
from aerthos.entities.player import PlayerCharacter, Weapon


class TestDiceRoller(unittest.TestCase):
    """Test dice rolling mechanics"""

    def setUp(self):
        self.roller = DiceRoller()

    def test_roll_d20_range(self):
        """Test d20 roll is in valid range"""
        for _ in range(100):
            roll = self.roller.roll_d20()
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 20)

    def test_roll_dice_single_die(self):
        """Test rolling single die"""
        for _ in range(50):
            roll = self.roller.roll_dice(1, 6)
            self.assertGreaterEqual(roll, 1)
            self.assertLessEqual(roll, 6)

    def test_roll_dice_multiple_dice(self):
        """Test rolling multiple dice"""
        for _ in range(50):
            roll = self.roller.roll_dice(3, 6)
            self.assertGreaterEqual(roll, 3)
            self.assertLessEqual(roll, 18)

    def test_roll_dice_with_modifier(self):
        """Test dice roll with modifier"""
        for _ in range(50):
            roll = self.roller.roll_dice(2, 4, 3)
            self.assertGreaterEqual(roll, 5)  # 2*1 + 3
            self.assertLessEqual(roll, 11)    # 2*4 + 3

    def test_roll_dice_negative_modifier(self):
        """Test dice roll with negative modifier"""
        for _ in range(50):
            roll = self.roller.roll_dice(1, 6, -2)
            self.assertGreaterEqual(roll, -1)  # 1 - 2
            self.assertLessEqual(roll, 4)      # 6 - 2

    def test_parse_dice_notation_simple(self):
        """Test parsing simple dice notation"""
        num, sides, mod = self.roller.parse_dice_notation("1d6")
        self.assertEqual(num, 1)
        self.assertEqual(sides, 6)
        self.assertEqual(mod, 0)

    def test_parse_dice_notation_multiple(self):
        """Test parsing multiple dice"""
        num, sides, mod = self.roller.parse_dice_notation("3d8")
        self.assertEqual(num, 3)
        self.assertEqual(sides, 8)
        self.assertEqual(mod, 0)

    def test_parse_dice_notation_with_plus(self):
        """Test parsing with positive modifier"""
        num, sides, mod = self.roller.parse_dice_notation("2d6+3")
        self.assertEqual(num, 2)
        self.assertEqual(sides, 6)
        self.assertEqual(mod, 3)

    def test_parse_dice_notation_with_minus(self):
        """Test parsing with negative modifier"""
        num, sides, mod = self.roller.parse_dice_notation("1d8-1")
        self.assertEqual(num, 1)
        self.assertEqual(sides, 8)
        self.assertEqual(mod, -1)

    def test_roll_from_notation(self):
        """Test rolling from notation string"""
        for _ in range(50):
            roll = self.roller.roll_from_notation("2d6+2")
            self.assertGreaterEqual(roll, 4)   # 2*1 + 2
            self.assertLessEqual(roll, 14)     # 2*6 + 2


class TestCombatResolver(unittest.TestCase):
    """Test THAC0 combat resolution"""

    def setUp(self):
        self.resolver = CombatResolver()

    def create_test_character(self, name="Fighter", ac=10, thac0=20, hp=10):
        """Helper to create test character"""
        char = Mock(spec=Character)
        char.name = name
        char.ac = ac
        char.thac0 = thac0
        char.hp_current = hp
        char.hp_max = hp
        char.is_alive = True
        return char

    def test_thac0_calculation_hit(self):
        """Test THAC0 hit calculation"""
        attacker = self.create_test_character("Attacker", thac0=18)
        defender = self.create_test_character("Defender", ac=5)

        # Need to roll >= (18 - 5) = 13 to hit
        # With roll of 13, should hit
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=13):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertTrue(result['hit'])

    def test_thac0_calculation_miss(self):
        """Test THAC0 miss calculation"""
        attacker = self.create_test_character("Attacker", thac0=18)
        defender = self.create_test_character("Defender", ac=5)

        # Need to roll >= 13 to hit
        # With roll of 12, should miss
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=12):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertFalse(result['hit'])

    def test_critical_hit_always_hits(self):
        """Test natural 20 always hits"""
        attacker = self.create_test_character("Attacker", thac0=20)
        defender = self.create_test_character("Defender", ac=-10)  # Very low AC

        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=20):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertTrue(result['hit'])
            self.assertTrue(result['critical'])

    def test_critical_miss_always_misses(self):
        """Test natural 1 always misses"""
        attacker = self.create_test_character("Attacker", thac0=1)
        defender = self.create_test_character("Defender", ac=10)  # Easy to hit

        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=1):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertFalse(result['hit'])
            self.assertTrue(result.get('fumble', False) or result['roll'] == 1)

    def test_negative_ac_harder_to_hit(self):
        """Test that negative AC is harder to hit"""
        attacker = self.create_test_character("Attacker", thac0=15)

        # Against AC 10, need roll >= 5
        defender_ac10 = self.create_test_character("Defender1", ac=10)
        # Against AC -5, need roll >= 20
        defender_ac_neg5 = self.create_test_character("Defender2", ac=-5)

        # Roll of 10 should hit AC 10 but miss AC -5
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=10):
            result1 = self.resolver.resolve_attack(attacker, defender_ac10)
            result2 = self.resolver.resolve_attack(attacker, defender_ac_neg5)

            self.assertTrue(result1['hit'])
            self.assertFalse(result2['hit'])

    def test_damage_roll(self):
        """Test damage is rolled on hit"""
        attacker = self.create_test_character("Attacker", thac0=10)
        defender = self.create_test_character("Defender", ac=10)

        # Mock weapon damage
        weapon = Mock(spec=Weapon)
        weapon.damage_sm = "1d8"
        weapon.damage_l = "1d8"
        attacker.equipment = Mock()
        attacker.equipment.get_equipped_weapon = Mock(return_value=weapon)

        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=15):
            with patch.object(self.resolver.dice_roller, 'roll_from_notation', return_value=5):
                result = self.resolver.resolve_attack(attacker, defender)

                self.assertTrue(result['hit'])
                self.assertEqual(result['damage'], 5)

    def test_no_damage_on_miss(self):
        """Test no damage dealt on miss"""
        attacker = self.create_test_character("Attacker", thac0=20)
        defender = self.create_test_character("Defender", ac=0)

        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=5):
            result = self.resolver.resolve_attack(attacker, defender)

            self.assertFalse(result['hit'])
            self.assertEqual(result.get('damage', 0), 0)

    def test_thac0_vs_very_high_ac(self):
        """Test hitting unarmored targets (AC 10)"""
        attacker = self.create_test_character("Attacker", thac0=20)
        defender = self.create_test_character("Defender", ac=10)

        # Need to roll >= (20 - 10) = 10
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=10):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertTrue(result['hit'])

    def test_thac0_vs_plate_armor(self):
        """Test hitting heavily armored targets (AC 0)"""
        attacker = self.create_test_character("Attacker", thac0=20)
        defender = self.create_test_character("Defender", ac=0)

        # Need to roll >= (20 - 0) = 20
        # Only critical hit will work
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=19):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertFalse(result['hit'])

        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=20):
            result = self.resolver.resolve_attack(attacker, defender)
            self.assertTrue(result['hit'])

    def test_improved_thac0_better_chance(self):
        """Test that better THAC0 improves hit chance"""
        defender = self.create_test_character("Defender", ac=5)

        # Fighter level 1 (THAC0 20) vs Fighter level 5 (THAC0 16)
        fighter_l1 = self.create_test_character("Fighter L1", thac0=20)
        fighter_l5 = self.create_test_character("Fighter L5", thac0=16)

        # Roll of 13
        # L1: need 15 (20-5), miss
        # L5: need 11 (16-5), hit
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=13):
            result_l1 = self.resolver.resolve_attack(fighter_l1, defender)
            result_l5 = self.resolver.resolve_attack(fighter_l5, defender)

            self.assertFalse(result_l1['hit'])
            self.assertTrue(result_l5['hit'])


class TestCombatIntegration(unittest.TestCase):
    """Integration tests for combat scenarios"""

    def setUp(self):
        self.resolver = CombatResolver()

    def test_full_combat_round(self):
        """Test complete combat round"""
        fighter = Mock(spec=Character)
        fighter.name = "Fighter"
        fighter.thac0 = 18
        fighter.hp_current = 20
        fighter.hp_max = 20
        fighter.is_alive = True

        orc = Mock(spec=Character)
        orc.name = "Orc"
        orc.ac = 6
        orc.thac0 = 19
        orc.hp_current = 15
        orc.hp_max = 15
        orc.is_alive = True

        # Simulate fighter attacking orc
        with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=15):
            result = self.resolver.resolve_attack(fighter, orc)
            self.assertTrue(result['hit'])
            self.assertIn('damage', result)

    def test_combat_until_death(self):
        """Test combat continues until death"""
        attacker = Mock(spec=Character)
        attacker.name = "Attacker"
        attacker.thac0 = 10

        defender = Mock(spec=Character)
        defender.name = "Defender"
        defender.ac = 5
        defender.hp_current = 10
        defender.is_alive = True

        rounds = 0
        max_rounds = 100  # Prevent infinite loop

        while defender.is_alive and rounds < max_rounds:
            with patch.object(self.resolver.dice_roller, 'roll_d20', return_value=20):
                with patch.object(self.resolver.dice_roller, 'roll_from_notation', return_value=5):
                    result = self.resolver.resolve_attack(attacker, defender)
                    if result['hit']:
                        defender.hp_current -= result['damage']
                        if defender.hp_current <= 0:
                            defender.is_alive = False
            rounds += 1

        self.assertFalse(defender.is_alive)
        self.assertLess(rounds, max_rounds)


if __name__ == '__main__':
    unittest.main()
