"""
Web API Schema Validation Tests

These tests verify the JSON structure returned by the web API endpoints.
If these tests fail, the web UI may be broken and needs updating.

CRITICAL: If you modify get_game_state_json() or any API response format,
         update these tests AND update the web UI JavaScript accordingly.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.world.dungeon import Dungeon
from aerthos.world.room import Room
from aerthos.engine.game_state import GameState, GameData

# Check if Flask is available
try:
    import flask
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed - web UI tests skipped")
class TestWebAPISchema(unittest.TestCase):
    """Test web API JSON response schemas"""

    def setUp(self):
        """Create minimal game state for testing"""
        # Create a simple character
        self.character = PlayerCharacter(
            name="TestHero",
            race="Human",
            char_class="Fighter",
            level=1,
            strength=15, dexterity=14, constitution=13, intelligence=12, wisdom=11, charisma=10,
            hp_current=10,
            hp_max=10
        )

        # Create simple dungeon with one room
        room = Room(
            id="room_001",
            title="Test Room",
            description="A test room for validation",
            exits={},
            light_level="bright"
        )

        self.dungeon = Dungeon(
            name="Test Dungeon",
            start_room_id="room_001",
            rooms={"room_001": room}
        )

        # Set position for map rendering (normally done by dungeon generator)
        room.x = 0
        room.y = 0

        # Create game state
        self.game_state = GameState(self.character, self.dungeon)
        self.game_state.game_data = GameData()
        self.game_state.game_data.load_all()

    def test_game_state_has_required_fields(self):
        """Test that game state JSON has all required fields for web UI"""
        # Import here to avoid circular dependencies
        from web_ui.app import get_game_state_json

        state = get_game_state_json(self.game_state)

        # CRITICAL FIELDS - Web UI depends on these existing
        # ⚠️ WARNING: If you add/remove/rename these fields, update game.html JavaScript!
        required_fields = [
            'room',         # Current room data
            'party',        # Party/character data
            'time',         # Game time tracking
            'map'           # Map data for 2D view
        ]

        for field in required_fields:
            self.assertIn(field, state,
                f"Missing required field '{field}' in game state JSON. "
                f"Web UI (game.html) expects this field!")

    def test_room_schema(self):
        """Test room data structure"""
        from web_ui.app import get_game_state_json

        state = get_game_state_json(self.game_state)
        room = state['room']

        # Fields that web UI uses
        required_room_fields = ['title', 'description', 'id', 'exits']

        for field in required_room_fields:
            self.assertIn(field, room,
                f"Missing '{field}' in room data. "
                f"Check updateDisplay() in game.html")

    def test_party_schema(self):
        """Test party/character data structure"""
        from web_ui.app import get_game_state_json

        state = get_game_state_json(self.game_state)
        party = state['party']

        self.assertIsInstance(party, list, "Party should be a list")
        self.assertGreater(len(party), 0, "Party should have at least one member")

        # Test first character structure
        char = party[0]
        required_char_fields = [
            'name', 'race', 'class', 'level',
            'hp', 'hp_max', 'ac', 'thac0',
            'is_alive', 'formation', 'gold',
            'weight', 'weight_max', 'xp'
        ]

        for field in required_char_fields:
            self.assertIn(field, char,
                f"Missing '{field}' in character data. "
                f"Check updatePartyDisplay() in game.html")

    def test_time_schema(self):
        """Test time data structure"""
        from web_ui.app import get_game_state_json

        state = get_game_state_json(self.game_state)
        time = state['time']

        required_time_fields = ['turns', 'hours']

        for field in required_time_fields:
            self.assertIn(field, time,
                f"Missing '{field}' in time data. "
                f"Check time-info display in game.html")

    def test_map_schema(self):
        """Test map data structure"""
        from web_ui.app import get_game_state_json

        state = get_game_state_json(self.game_state)
        map_data = state['map']

        self.assertIn('rooms', map_data,
            "Map data must have 'rooms' field. "
            "Check render2DMap() in game.html")

        # Test room map structure
        if map_data['rooms']:
            room_id = list(map_data['rooms'].keys())[0]
            room = map_data['rooms'][room_id]

            required_map_room_fields = ['x', 'y', 'title', 'is_explored', 'is_current']

            for field in required_map_room_fields:
                self.assertIn(field, room,
                    f"Missing '{field}' in map room data. "
                    f"Check render2DMap() in game.html")

    def test_character_inventory_schema(self):
        """Test character inventory structure"""
        from web_ui.app import get_game_state_json

        state = get_game_state_json(self.game_state)
        char = state['party'][0]

        # Inventory fields used by web UI
        self.assertIn('inventory', char,
            "Character must have 'inventory' field. "
            "Check updateInventoryPanel() in game.html")

        self.assertIn('equipped', char,
            "Character must have 'equipped' field. "
            "Check updateInventoryPanel() in game.html")

    def test_party_mode_game_state(self):
        """Test game state with full party (not solo character)"""
        # Create a party
        party = Party()

        # Create multiple characters
        for i in range(4):
            char = PlayerCharacter(
                name=f"Hero{i}",
                race="Human",
                char_class="Fighter",
                level=1,
                strength=15, dexterity=14, constitution=13, intelligence=12, wisdom=11, charisma=10,
                hp_current=10,
                hp_max=10
            )
            party.add_member(char)

        # Create game state with party
        game_state = GameState(party.members[0], self.dungeon)
        game_state.party = party
        game_state.game_data = GameData()
        game_state.game_data.load_all()

        from web_ui.app import get_game_state_json

        state = get_game_state_json(game_state)

        # Should have multiple party members
        self.assertEqual(len(state['party']), 4,
            "Party mode should return all party members")

        # Each should have formation
        for member in state['party']:
            self.assertIn('formation', member,
                "Each party member must have 'formation' field")
            self.assertIn(member['formation'], ['front', 'back'],
                "Formation must be 'front' or 'back'")


class TestCommandParsingCompatibility(unittest.TestCase):
    """
    Test that UI-generated commands will be parsed correctly

    IMPORTANT: These tests verify that button-generated commands
               match what the parser expects.
    """

    def setUp(self):
        """Set up command parser"""
        from aerthos.engine.parser import CommandParser
        self.parser = CommandParser()

    def test_attack_command_format(self):
        """Test attack commands generated by UI buttons"""
        # UI generates: `attack ${enemy.name}`
        test_commands = [
            "attack goblin",
            "attack orc warrior",
            "attack skeleton #1"
        ]

        for cmd in test_commands:
            result = self.parser.parse(cmd)
            self.assertIsNotNone(result,
                f"Parser failed to parse UI-generated command: '{cmd}'")
            self.assertEqual(result.action, 'attack',
                f"Command '{cmd}' not parsed as attack")

    def test_cast_spell_command_format(self):
        """Test cast spell commands generated by UI"""
        # UI generates: `cast ${spell.name}` or `cast ${spell.name} on ${target}`
        test_commands = [
            "cast magic missile",
            "cast cure light wounds",
            "cast magic missile on goblin",
            "cast cure light wounds on thorin"
        ]

        for cmd in test_commands:
            result = self.parser.parse(cmd)
            self.assertIsNotNone(result,
                f"Parser failed to parse UI-generated command: '{cmd}'")
            self.assertEqual(result.action, 'cast',
                f"Command '{cmd}' not parsed as cast")

    def test_take_item_command_format(self):
        """Test take commands generated by UI"""
        # UI generates: `take ${item}`
        test_commands = [
            "take sword",
            "take health potion",
            "take iron key"
        ]

        for cmd in test_commands:
            result = self.parser.parse(cmd)
            self.assertIsNotNone(result,
                f"Parser failed to parse UI-generated command: '{cmd}'")
            self.assertEqual(result.action, 'take',
                f"Command '{cmd}' not parsed as take")

    def test_movement_commands(self):
        """Test movement commands from keyboard shortcuts"""
        # Keyboard shortcuts generate: 'north', 'south', 'east', 'west'
        directions = ['north', 'south', 'east', 'west']

        for direction in directions:
            result = self.parser.parse(direction)
            self.assertIsNotNone(result,
                f"Parser failed to parse direction: '{direction}'")
            self.assertEqual(result.action, 'move',
                f"Direction '{direction}' not parsed as movement")


if __name__ == '__main__':
    unittest.main()
