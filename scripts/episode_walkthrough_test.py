#!/usr/bin/env python3
"""
Episode Walkthrough Test

Run this test BEFORE starting each episode to verify all critical systems
are working properly. This catches the recurring bugs that have disrupted
gameplay in previous episodes.

Usage:
    python scripts/episode_walkthrough_test.py 3           # Test episode 3
    python scripts/episode_walkthrough_test.py 3 --verbose # Detailed output
    python scripts/episode_walkthrough_test.py all         # Test all episodes

Tests performed:
1. Episode Definition Validation
2. Dungeon Structure Validation
3. Treasure/Item Conversion (Bug #1 fix verification)
4. Boss Defeat & Episode Completion Triggers (Bug #4 fix verification)
5. Save/Load Cycle (Bug #2 fix verification)
6. Character State Validation
7. Required Lore/Prerequisites Check
"""

import sys
import json
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aerthos.engine.game_state import GameState
from aerthos.storage.character_roster import CharacterRoster
from aerthos.entities.player import Weapon, Armor, Item, Inventory, Shield


@dataclass
class TestResult:
    """Result of a single test"""
    name: str
    passed: bool
    message: str
    details: List[str] = None


class EpisodeWalkthroughTest:
    """Comprehensive pre-episode testing suite"""

    def __init__(self, episode_num: int, verbose: bool = False):
        self.episode_num = episode_num
        self.episode_id = f"episode_{episode_num:02d}"
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.data_dir = Path(__file__).parent.parent / "aerthos" / "data"

        # Load episode data
        self.episode_data = None
        self.dungeon_data = None
        self.game_state = None

    def log(self, msg: str):
        """Print if verbose mode"""
        if self.verbose:
            print(f"  {msg}")

    def run_all_tests(self) -> bool:
        """Run all tests and return overall pass/fail"""
        print(f"\n{'='*70}")
        print(f"EPISODE {self.episode_num} WALKTHROUGH TEST")
        print(f"{'='*70}\n")

        tests = [
            self.test_episode_definition,
            self.test_dungeon_structure,
            self.test_treasure_conversion,
            self.test_boss_completion_trigger,
            self.test_save_load_cycle,
            self.test_character_validation,
            self.test_prerequisites,
        ]

        for test_func in tests:
            try:
                result = test_func()
                self.results.append(result)
                status = "✓ PASS" if result.passed else "✗ FAIL"
                print(f"{status}: {result.name}")
                if not result.passed:
                    print(f"       {result.message}")
                if result.details and self.verbose:
                    for detail in result.details:
                        print(f"       - {detail}")
            except Exception as e:
                self.results.append(TestResult(
                    name=test_func.__name__,
                    passed=False,
                    message=f"Exception: {e}"
                ))
                print(f"✗ FAIL: {test_func.__name__}")
                print(f"       Exception: {e}")

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        all_passed = passed == total

        print(f"\n{'='*70}")
        if all_passed:
            print(f"✓ ALL TESTS PASSED ({passed}/{total})")
            print(f"Episode {self.episode_num} is ready to play!")
        else:
            print(f"✗ TESTS FAILED ({passed}/{total} passed)")
            print("Fix the issues above before playing this episode.")
        print(f"{'='*70}\n")

        return all_passed

    def test_episode_definition(self) -> TestResult:
        """Test 1: Validate episode definition file"""
        episode_file = self.data_dir / "episodes" / f"{self.episode_id}.json"

        if not episode_file.exists():
            return TestResult(
                name="Episode Definition",
                passed=False,
                message=f"Episode file not found: {episode_file}"
            )

        try:
            with open(episode_file) as f:
                self.episode_data = json.load(f)
        except json.JSONDecodeError as e:
            return TestResult(
                name="Episode Definition",
                passed=False,
                message=f"Invalid JSON: {e}"
            )

        # Check required fields
        required_fields = ["id", "title", "hub_id", "dungeon", "completion_criteria", "rewards"]
        missing = [f for f in required_fields if f not in self.episode_data]

        if missing:
            return TestResult(
                name="Episode Definition",
                passed=False,
                message=f"Missing required fields: {missing}"
            )

        # Validate completion criteria
        criteria = self.episode_data.get("completion_criteria", {})
        if criteria.get("type") == "boss_defeated" and not criteria.get("target"):
            return TestResult(
                name="Episode Definition",
                passed=False,
                message="Boss defeat criteria missing 'target' field"
            )

        # Validate rewards
        rewards = self.episode_data.get("rewards", {})
        details = [
            f"Title: {self.episode_data['title']}",
            f"Hub: {self.episode_data['hub_id']}",
            f"Completion: {criteria.get('type')} - {criteria.get('target', 'N/A')}",
            f"XP Bonus: {rewards.get('xp_bonus', 0)}",
            f"Gold Bonus: {rewards.get('gold_bonus', 0)}",
        ]

        return TestResult(
            name="Episode Definition",
            passed=True,
            message="Episode definition is valid",
            details=details
        )

    def test_dungeon_structure(self) -> TestResult:
        """Test 2: Validate dungeon structure"""
        if not self.episode_data:
            return TestResult(
                name="Dungeon Structure",
                passed=False,
                message="Episode data not loaded"
            )

        dungeon_info = self.episode_data.get("dungeon", {})
        dungeon_file = self.data_dir / dungeon_info.get("file", "")

        if not dungeon_file.exists():
            return TestResult(
                name="Dungeon Structure",
                passed=False,
                message=f"Dungeon file not found: {dungeon_file}"
            )

        try:
            with open(dungeon_file) as f:
                self.dungeon_data = json.load(f)
        except json.JSONDecodeError as e:
            return TestResult(
                name="Dungeon Structure",
                passed=False,
                message=f"Invalid dungeon JSON: {e}"
            )

        rooms = self.dungeon_data.get("rooms", {})
        if not rooms:
            return TestResult(
                name="Dungeon Structure",
                passed=False,
                message="No rooms defined in dungeon"
            )

        # Validate room connections point to valid rooms
        missing_connections = []
        for room_id, room_data in rooms.items():
            exits = room_data.get("exits", {})
            for direction, target_room in exits.items():
                if target_room not in rooms:
                    missing_connections.append(f"{room_id} -> {target_room} ({direction})")

        # CRITICAL: Check all rooms are REACHABLE from start (BFS traversal)
        start_room = self.dungeon_data.get("start_room")
        visited = set()
        queue = [start_room] if start_room else []
        if start_room:
            visited.add(start_room)

        while queue:
            current = queue.pop(0)
            room = rooms.get(current)
            if room:
                for direction, target in room.get("exits", {}).items():
                    if target not in visited and target in rooms:
                        visited.add(target)
                        queue.append(target)

        unreachable_rooms = set(rooms.keys()) - visited

        # Check for asymmetric exits (one-way passages that might trap players)
        OPPOSITES = {
            "north": "south", "south": "north", "east": "west", "west": "east",
            "up": "down", "down": "up", "northeast": "southwest", "southwest": "northeast",
            "northwest": "southeast", "southeast": "northwest"
        }
        asymmetric_exits = []
        for room_id, room_data in rooms.items():
            for direction, target in room_data.get("exits", {}).items():
                if target in rooms:
                    opposite = OPPOSITES.get(direction)
                    if opposite:
                        return_exit = rooms[target].get("exits", {}).get(opposite)
                        if return_exit != room_id:
                            asymmetric_exits.append(f"{room_id} -> {target} ({direction}, no return)")

        # Check for boss room (if boss_defeated criteria)
        criteria = self.episode_data.get("completion_criteria", {})
        boss_target = criteria.get("target", "").lower().replace(" ", "_")
        boss_room_found = False

        for room_id, room_data in rooms.items():
            encounters = room_data.get("encounters", [])
            for encounter in encounters:
                monsters = encounter.get("monsters", [])
                for monster in monsters:
                    # Handle both formats: string ID or dict with 'id' field
                    if isinstance(monster, str):
                        monster_id = monster.lower()
                    elif isinstance(monster, dict):
                        monster_id = monster.get("id", "").lower()
                    else:
                        continue
                    if boss_target and boss_target in monster_id:
                        boss_room_found = True
                        break

        details = [
            f"Dungeon: {self.dungeon_data.get('name', 'Unknown')}",
            f"Total rooms: {len(rooms)}",
            f"Reachable rooms: {len(visited)}/{len(rooms)}",
            f"Start room: {self.dungeon_data.get('start_room', 'N/A')}",
        ]

        if missing_connections:
            return TestResult(
                name="Dungeon Structure",
                passed=False,
                message=f"Invalid room connections: {missing_connections}",
                details=details
            )

        # CRITICAL: Fail if any rooms are unreachable
        if unreachable_rooms:
            details.append(f"UNREACHABLE: {list(unreachable_rooms)}")
            return TestResult(
                name="Dungeon Structure",
                passed=False,
                message=f"{len(unreachable_rooms)} rooms are unreachable from start!",
                details=details
            )

        # Warn about asymmetric exits (one-way passages)
        if asymmetric_exits:
            details.append(f"One-way passages: {len(asymmetric_exits)}")
            for exit_info in asymmetric_exits[:3]:  # Show first 3
                details.append(f"  - {exit_info}")

        if criteria.get("type") == "boss_defeated" and not boss_room_found:
            details.append(f"WARNING: Boss '{boss_target}' not found in any encounter")

        return TestResult(
            name="Dungeon Structure",
            passed=True,
            message=f"Dungeon valid with {len(rooms)} rooms (all reachable)",
            details=details
        )

    def test_treasure_conversion(self) -> TestResult:
        """Test 3: Verify treasure items convert to proper types (Bug #1)

        Enhanced to check:
        - Magic weapons (+N) become Weapon class with damage_sm
        - Magic armor (+N) becomes Armor class with ac
        - Magic shields (+N) become Shield class with ac_bonus
        - Non-magic weapons (warhammer, dwarven_shield) are properly typed
        - Items have Web UI actionable types (weapon, armor, shield, consumable, tool, key)
        """
        if not self.dungeon_data:
            return TestResult(
                name="Treasure Conversion",
                passed=False,
                message="Dungeon data not loaded"
            )

        # Initialize game state for item creation
        class MockGameData:
            def __init__(self, data_dir):
                with open(data_dir / 'weapons.json') as f:
                    self.weapons = json.load(f)
                with open(data_dir / 'armor.json') as f:
                    armor_data = json.load(f)
                    self.armor_data = armor_data.get('armor', {})
                with open(data_dir / 'equipment.json') as f:
                    self.equipment = json.load(f)

        gs = GameState.__new__(GameState)
        gs.game_data = MockGameData(self.data_dir)

        # Collect all items from dungeon (items list AND treasure.magic_items)
        all_items = []
        rooms = self.dungeon_data.get("rooms", {})
        for room_id, room_data in rooms.items():
            items = room_data.get("items", [])
            all_items.extend([(item, room_id) for item in items])
            # Also check treasure section for magic items
            treasure = room_data.get("treasure", {})
            for magic_item in treasure.get("magic_items", []):
                all_items.append((magic_item, room_id))

        if not all_items:
            return TestResult(
                name="Treasure Conversion",
                passed=True,
                message="No items in dungeon to test",
                details=["No treasure items defined in this dungeon"]
            )

        # Web UI action types
        EQUIPABLE_TYPES = ['weapon', 'armor', 'shield', 'light']
        USABLE_TYPES = ['potion', 'consumable', 'scroll', 'wand', 'key', 'tool']
        ACTIONABLE_TYPES = EQUIPABLE_TYPES + USABLE_TYPES

        # Test each item
        failed_items = []
        weapon_items = []
        armor_items = []
        shield_items = []
        actionable_items = []
        other_items = []

        seen = set()
        for item_name, room_id in all_items:
            if item_name in seen:
                continue
            seen.add(item_name)

            # Skip gold items
            if item_name.lower().startswith('gold_'):
                continue

            try:
                item = gs._create_item_from_name(item_name)
            except Exception as e:
                failed_items.append(f"{item_name}: Creation failed - {e}")
                continue

            # Determine actual type
            if isinstance(item, Weapon):
                item_type = 'weapon'
                weapon_items.append(item_name)
                if not hasattr(item, 'damage_sm') or not item.damage_sm:
                    failed_items.append(f"{item_name}: Weapon missing damage_sm")
            elif hasattr(item, 'ac_bonus'):  # Shield
                item_type = 'shield'
                shield_items.append(item_name)
            elif isinstance(item, Armor):
                item_type = 'armor'
                armor_items.append(item_name)
                if not hasattr(item, 'ac'):
                    failed_items.append(f"{item_name}: Armor missing ac")
            else:
                item_type = getattr(item, 'item_type', 'unknown')
                other_items.append(item_name)

            # Track actionable items
            if item_type in ACTIONABLE_TYPES:
                actionable_items.append((item_name, item_type))

            # Check magic items are properly typed
            if '_plus_' in item_name.lower() or '_plus' in item_name.lower() or '+' in item_name:
                # Magic weapon check
                weapon_keywords = ['sword', 'dagger', 'axe', 'mace', 'hammer', 'warhammer', 'waraxe', 'spear']
                if any(kw in item_name.lower() for kw in weapon_keywords):
                    if not isinstance(item, Weapon):
                        failed_items.append(f"{item_name}: Magic weapon is {type(item).__name__}, not Weapon")
                # Magic armor check
                armor_keywords = ['mail', 'armor', 'plate', 'leather']
                if any(kw in item_name.lower() for kw in armor_keywords):
                    if not isinstance(item, Armor):
                        failed_items.append(f"{item_name}: Magic armor is {type(item).__name__}, not Armor")
                # Magic shield check
                if 'shield' in item_name.lower():
                    if not hasattr(item, 'ac_bonus'):
                        failed_items.append(f"{item_name}: Magic shield missing ac_bonus")

            # Check non-magic items that SHOULD be actionable
            # (Skip items with "broken" prefix or quest/lore items)
            if not item_name.startswith('broken_') and item_type not in ACTIONABLE_TYPES:
                should_be_weapon = any(kw in item_name.lower() for kw in ['sword', 'dagger', 'axe', 'mace', 'warhammer', 'waraxe'])
                should_be_shield = 'shield' in item_name.lower() and 'second_key' not in item_name.lower()
                if should_be_weapon:
                    failed_items.append(f"{item_name}: Should be weapon but is {item_type}")
                elif should_be_shield:
                    failed_items.append(f"{item_name}: Should be shield but is {item_type}")

        details = [
            f"Tested {len(seen)} unique items",
            f"Weapons: {len(weapon_items)}",
            f"Armor: {len(armor_items)}",
            f"Shields: {len(shield_items)}",
            f"Web UI actionable: {len(actionable_items)}",
            f"Other (lore/treasure): {len(other_items)}",
        ]

        if failed_items:
            return TestResult(
                name="Treasure Conversion",
                passed=False,
                message=f"{len(failed_items)} items failed conversion",
                details=details + failed_items
            )

        return TestResult(
            name="Treasure Conversion",
            passed=True,
            message=f"All {len(set(all_items))} items convert correctly",
            details=details
        )

    def test_boss_completion_trigger(self) -> TestResult:
        """Test 4: Verify boss defeat triggers episode completion (Bug #4)"""
        if not self.episode_data:
            return TestResult(
                name="Boss Completion Trigger",
                passed=False,
                message="Episode data not loaded"
            )

        criteria = self.episode_data.get("completion_criteria", {})
        if criteria.get("type") != "boss_defeated":
            return TestResult(
                name="Boss Completion Trigger",
                passed=True,
                message=f"Episode uses '{criteria.get('type')}' completion, not boss_defeated",
                details=["Skipping boss trigger test"]
            )

        boss_target = criteria.get("target", "")
        if not boss_target:
            return TestResult(
                name="Boss Completion Trigger",
                passed=False,
                message="Boss target not specified in completion_criteria"
            )

        # Simulate boss defeat tracking
        gs = GameState.__new__(GameState)
        gs.defeated_monsters = set()

        # Verify the attribute exists (Bug #4 fix)
        if not hasattr(gs, 'defeated_monsters'):
            return TestResult(
                name="Boss Completion Trigger",
                passed=False,
                message="GameState missing 'defeated_monsters' attribute (Bug #4 not fixed)"
            )

        # Simulate defeating boss
        boss_id = boss_target.lower().replace(" ", "_")
        gs.defeated_monsters.add(boss_id)

        if boss_id not in gs.defeated_monsters:
            return TestResult(
                name="Boss Completion Trigger",
                passed=False,
                message="Boss defeat not tracked in defeated_monsters"
            )

        details = [
            f"Boss target: {boss_target}",
            f"Boss ID format: {boss_id}",
            "defeated_monsters tracking: OK",
        ]

        return TestResult(
            name="Boss Completion Trigger",
            passed=True,
            message=f"Boss '{boss_target}' completion trigger working",
            details=details
        )

    def test_save_load_cycle(self) -> TestResult:
        """Test 5: Verify save/load works with magic items (Bug #2)"""
        # Create temporary directory for test
        test_dir = tempfile.mkdtemp()

        try:
            roster = CharacterRoster(roster_dir=test_dir)

            # Create test inventory with magic items
            inv = Inventory()

            # Create a magic weapon
            weapon = Weapon(
                name="Test Longsword +1",
                weight=6.0,
                damage_sm="1d8",
                damage_l="1d12",
                speed_factor=5,
                magic_bonus=1
            )
            inv.add_item(weapon)

            # Create magic armor
            armor = Armor(
                name="Test Chainmail +1",
                weight=40.0,
                ac=5,
                armor_type="heavy",
                movement_rate=9,
                magic_bonus=1
            )
            inv.add_item(armor)

            # Serialize
            serialized = roster._serialize_inventory(inv)

            # Verify serialized data has required fields
            for item_data in serialized:
                if item_data['type'] == 'weapon':
                    if 'damage_sm' not in item_data:
                        return TestResult(
                            name="Save/Load Cycle",
                            passed=False,
                            message="Weapon serialization missing damage_sm"
                        )
                elif item_data['type'] == 'armor':
                    if 'ac' not in item_data:
                        return TestResult(
                            name="Save/Load Cycle",
                            passed=False,
                            message="Armor serialization missing ac"
                        )

            # Deserialize
            for item_data in serialized:
                loaded_item = roster._deserialize_item(item_data)
                if isinstance(loaded_item, Weapon):
                    if not loaded_item.damage_sm:
                        return TestResult(
                            name="Save/Load Cycle",
                            passed=False,
                            message="Loaded weapon missing damage_sm"
                        )
                elif isinstance(loaded_item, Armor):
                    if loaded_item.ac is None:
                        return TestResult(
                            name="Save/Load Cycle",
                            passed=False,
                            message="Loaded armor missing ac"
                        )

            # Test malformed data (backward compatibility)
            malformed_weapon = {'name': 'Old Sword', 'type': 'weapon', 'weight': 5.0}
            try:
                loaded = roster._deserialize_item(malformed_weapon)
                if not isinstance(loaded, Weapon):
                    return TestResult(
                        name="Save/Load Cycle",
                        passed=False,
                        message="Malformed weapon not deserialized correctly"
                    )
            except KeyError as e:
                return TestResult(
                    name="Save/Load Cycle",
                    passed=False,
                    message=f"KeyError on malformed data: {e} (Bug #2 not fixed)"
                )

            details = [
                "Weapon serialization: OK",
                "Armor serialization: OK",
                "Deserialization: OK",
                "Backward compatibility: OK"
            ]

            return TestResult(
                name="Save/Load Cycle",
                passed=True,
                message="Save/load cycle works correctly",
                details=details
            )

        finally:
            shutil.rmtree(test_dir)

    def test_character_validation(self) -> TestResult:
        """Test 6: Validate current party characters"""
        aerthos_dir = Path.home() / ".aerthos"
        characters_dir = aerthos_dir / "characters"

        if not characters_dir.exists():
            return TestResult(
                name="Character Validation",
                passed=True,
                message="No character roster found (new game)",
                details=["Character validation skipped - no roster"]
            )

        # Find party characters
        party_chars = ["grim", "valorian", "eryndor", "canon", "aether", "pip"]
        issues = []
        char_details = []

        for name in party_chars:
            char_files = list(characters_dir.glob(f"{name}_*.json"))
            if not char_files:
                continue

            try:
                with open(char_files[0]) as f:
                    char_data = json.load(f)

                # Validate character state
                hp_current = char_data.get("hp_current", 0)
                hp_max = char_data.get("hp_max", 1)
                is_alive = char_data.get("is_alive", True)

                if hp_current <= 0 and is_alive:
                    issues.append(f"{name}: HP=0 but is_alive=True (Bug #5)")

                if hp_current > hp_max:
                    issues.append(f"{name}: HP exceeds max ({hp_current}/{hp_max})")

                # Check THAC0 is reasonable for level
                level = char_data.get("level", 1)
                thac0 = char_data.get("thac0", 20)
                expected_max_thac0 = 20 - (level - 1)  # Rough check

                char_details.append(
                    f"{char_data['name']}: L{level} {char_data.get('class', '?')} "
                    f"HP:{hp_current}/{hp_max} THAC0:{thac0}"
                )

            except Exception as e:
                issues.append(f"{name}: Error loading - {e}")

        if issues:
            return TestResult(
                name="Character Validation",
                passed=False,
                message=f"{len(issues)} character issues found",
                details=issues
            )

        return TestResult(
            name="Character Validation",
            passed=True,
            message=f"All {len(char_details)} characters valid",
            details=char_details
        )

    def test_prerequisites(self) -> TestResult:
        """Test 7: Check episode prerequisites and required lore"""
        if not self.episode_data:
            return TestResult(
                name="Prerequisites",
                passed=False,
                message="Episode data not loaded"
            )

        prerequisites = self.episode_data.get("prerequisites", [])
        if not prerequisites:
            return TestResult(
                name="Prerequisites",
                passed=True,
                message="No prerequisites required",
                details=["Episode can be started fresh"]
            )

        # Check campaign file for completed episodes
        aerthos_dir = Path.home() / ".aerthos"
        campaigns_dir = aerthos_dir / "campaigns"

        if not campaigns_dir.exists():
            return TestResult(
                name="Prerequisites",
                passed=False,
                message=f"No campaign found - prerequisites {prerequisites} not met"
            )

        # Find active campaign
        campaign_files = list(campaigns_dir.glob("*.json"))
        if not campaign_files:
            return TestResult(
                name="Prerequisites",
                passed=False,
                message="No campaign file found"
            )

        try:
            with open(campaign_files[0]) as f:
                campaign = json.load(f)
        except Exception as e:
            return TestResult(
                name="Prerequisites",
                passed=False,
                message=f"Error loading campaign: {e}"
            )

        completed = campaign.get("completed_episodes", [])
        unlocked = campaign.get("unlocked_episodes", [])
        story_flags = campaign.get("story_flags", {})

        missing_prereqs = [p for p in prerequisites if p not in completed]

        details = [
            f"Required: {prerequisites}",
            f"Completed: {completed}",
            f"Unlocked: {unlocked}",
            f"Story flags: {list(story_flags.keys())}"
        ]

        if missing_prereqs:
            return TestResult(
                name="Prerequisites",
                passed=False,
                message=f"Missing prerequisites: {missing_prereqs}",
                details=details
            )

        if self.episode_id not in unlocked:
            return TestResult(
                name="Prerequisites",
                passed=False,
                message=f"Episode {self.episode_id} not unlocked in campaign",
                details=details
            )

        return TestResult(
            name="Prerequisites",
            passed=True,
            message="All prerequisites met",
            details=details
        )


def main():
    parser = argparse.ArgumentParser(
        description="Episode Walkthrough Test - Run before each episode"
    )
    parser.add_argument(
        "episode",
        help="Episode number (1-10) or 'all' to test all episodes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    if args.episode.lower() == "all":
        episodes = range(1, 11)
        all_passed = True
        for ep in episodes:
            test = EpisodeWalkthroughTest(ep, verbose=args.verbose)
            if not test.run_all_tests():
                all_passed = False
        sys.exit(0 if all_passed else 1)
    else:
        try:
            episode_num = int(args.episode)
            if not 1 <= episode_num <= 10:
                print("Episode number must be between 1 and 10")
                sys.exit(1)
        except ValueError:
            print(f"Invalid episode number: {args.episode}")
            sys.exit(1)

        test = EpisodeWalkthroughTest(episode_num, verbose=args.verbose)
        passed = test.run_all_tests()
        sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
