"""
Test suite for Waterbreathing Mechanic (Campaign Episode 7)
Tests the underwater room system and drowning damage mechanics
"""

import unittest
from unittest.mock import Mock, patch
from aerthos.entities.character import Character
from aerthos.entities.player import PlayerCharacter, Inventory, Item
from aerthos.world.room import Room


class TestCharacterWaterbreathing(unittest.TestCase):
    """Test Character.has_waterbreathing property"""

    def test_character_no_waterbreathing_by_default(self):
        """Test that characters don't have waterbreathing by default"""
        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=10,
            hp_max=10
        )
        self.assertFalse(char.has_waterbreathing)

    def test_character_with_waterbreathing_condition(self):
        """Test that waterbreathing condition grants waterbreathing"""
        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=10,
            hp_max=10,
            conditions=['waterbreathing']
        )
        self.assertTrue(char.has_waterbreathing)

    def test_character_waterbreathing_added_dynamically(self):
        """Test that adding waterbreathing condition grants waterbreathing"""
        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=10,
            hp_max=10
        )
        self.assertFalse(char.has_waterbreathing)
        char.add_condition('waterbreathing')
        self.assertTrue(char.has_waterbreathing)


class TestPlayerCharacterWaterbreathing(unittest.TestCase):
    """Test PlayerCharacter.has_waterbreathing property with inventory"""

    def test_player_no_waterbreathing_by_default(self):
        """Test that player characters don't have waterbreathing by default"""
        player = PlayerCharacter(
            name="Test Cleric",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=14,
            dexterity=12,
            constitution=15,
            intelligence=10,
            wisdom=16,
            charisma=14,
            hp_current=10,
            hp_max=10
        )
        self.assertFalse(player.has_waterbreathing)

    def test_player_with_waterbreathing_condition(self):
        """Test that waterbreathing spell/condition grants waterbreathing"""
        player = PlayerCharacter(
            name="Test Cleric",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=14,
            dexterity=12,
            constitution=15,
            intelligence=10,
            wisdom=16,
            charisma=14,
            hp_current=10,
            hp_max=10,
            conditions=['waterbreathing']
        )
        self.assertTrue(player.has_waterbreathing)

    def test_player_with_amulet_of_waterbreathing(self):
        """Test that Amulet of Waterbreathing grants waterbreathing"""
        player = PlayerCharacter(
            name="Test Cleric",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=14,
            dexterity=12,
            constitution=15,
            intelligence=10,
            wisdom=16,
            charisma=14,
            hp_current=10,
            hp_max=10
        )

        # Create amulet with grants_waterbreathing property
        amulet = Mock(spec=Item)
        amulet.name = "Amulet of Waterbreathing"
        amulet.grants_waterbreathing = True
        amulet.properties = {'grants_waterbreathing': True}

        # Add to inventory
        player.inventory.items.append(amulet)

        self.assertTrue(player.has_waterbreathing)

    def test_player_without_waterbreathing_item(self):
        """Test that regular items don't grant waterbreathing"""
        player = PlayerCharacter(
            name="Test Cleric",
            race="Human",
            char_class="Cleric",
            level=1,
            strength=14,
            dexterity=12,
            constitution=15,
            intelligence=10,
            wisdom=16,
            charisma=14,
            hp_current=10,
            hp_max=10
        )

        # Create regular item without waterbreathing
        rope = Mock(spec=Item)
        rope.name = "Rope"
        rope.grants_waterbreathing = False

        # Add to inventory
        player.inventory.items.append(rope)

        self.assertFalse(player.has_waterbreathing)


class TestRoomUnderwaterProperty(unittest.TestCase):
    """Test Room.is_underwater property"""

    def test_room_not_underwater_by_default(self):
        """Test that rooms without tags are not underwater"""
        room = Room(
            id="test_room",
            title="Test Room",
            description="A normal room"
        )
        self.assertFalse(room.is_underwater)

    def test_room_with_underwater_tag(self):
        """Test that room with underwater tag is underwater"""
        room = Room(
            id="underwater_room",
            title="Underwater Room",
            description="A flooded chamber",
            tags=['underwater']
        )
        self.assertTrue(room.is_underwater)

    def test_room_with_multiple_tags_including_underwater(self):
        """Test that room with multiple tags including underwater is underwater"""
        room = Room(
            id="cold_underwater_room",
            title="Frozen Depths",
            description="A cold, flooded chamber",
            tags=['underwater', 'cold', 'dark']
        )
        self.assertTrue(room.is_underwater)

    def test_room_with_other_tags_not_underwater(self):
        """Test that room with other tags but not underwater is not underwater"""
        room = Room(
            id="hot_room",
            title="Lava Chamber",
            description="A very hot room",
            tags=['hot', 'dangerous']
        )
        self.assertFalse(room.is_underwater)


class TestRoomDrowningMechanic(unittest.TestCase):
    """Test Room.check_drowning() method"""

    def test_drowning_in_regular_room_no_damage(self):
        """Test that regular rooms don't cause drowning"""
        room = Room(
            id="regular_room",
            title="Regular Room",
            description="A normal room"
        )

        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=10,
            hp_max=10
        )

        result = room.check_drowning(char)

        self.assertEqual(result, "")
        self.assertEqual(char.hp_current, 10)
        self.assertTrue(char.is_alive)

    def test_drowning_underwater_without_waterbreathing(self):
        """Test that underwater rooms cause drowning without waterbreathing"""
        room = Room(
            id="underwater_room",
            title="Underwater Room",
            description="A flooded chamber",
            tags=['underwater']
        )

        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=10,
            hp_max=10
        )

        # Patch random to control damage
        with patch('random.randint', return_value=3):
            result = room.check_drowning(char)

        self.assertIn("DROWNING", result)
        self.assertIn("Test Fighter", result)
        self.assertIn("3 damage", result)
        self.assertEqual(char.hp_current, 7)
        self.assertTrue(char.is_alive)

    def test_drowning_underwater_with_waterbreathing_condition(self):
        """Test that waterbreathing condition prevents drowning"""
        room = Room(
            id="underwater_room",
            title="Underwater Room",
            description="A flooded chamber",
            tags=['underwater']
        )

        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=10,
            hp_max=10,
            conditions=['waterbreathing']
        )

        result = room.check_drowning(char)

        self.assertEqual(result, "")
        self.assertEqual(char.hp_current, 10)
        self.assertTrue(char.is_alive)

    def test_drowning_causes_death_at_zero_hp(self):
        """Test that drowning can kill character"""
        room = Room(
            id="underwater_room",
            title="Underwater Room",
            description="A flooded chamber",
            tags=['underwater']
        )

        char = Character(
            name="Test Fighter",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=16,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=12,
            charisma=10,
            hp_current=3,
            hp_max=10
        )

        # Patch random to deal 6 damage (more than current HP)
        with patch('random.randint', return_value=6):
            result = room.check_drowning(char)

        self.assertIn("DROWNING", result)
        self.assertIn("drowned", result)
        self.assertEqual(char.hp_current, -3)
        self.assertFalse(char.is_alive)

    def test_drowning_damage_range(self):
        """Test that drowning deals 1-6 damage (1d6)"""
        room = Room(
            id="underwater_room",
            title="Underwater Room",
            description="A flooded chamber",
            tags=['underwater']
        )

        # Test multiple damage rolls to verify range
        for expected_damage in [1, 2, 3, 4, 5, 6]:
            char = Character(
                name="Test Fighter",
                race="Human",
                char_class="Fighter",
                level=1,
                strength=16,
                dexterity=14,
                constitution=15,
                intelligence=10,
                wisdom=12,
                charisma=10,
                hp_current=20,
                hp_max=20
            )

            with patch('random.randint', return_value=expected_damage):
                result = room.check_drowning(char)

            self.assertIn(f"{expected_damage} damage", result)
            self.assertEqual(char.hp_current, 20 - expected_damage)


if __name__ == '__main__':
    unittest.main()
