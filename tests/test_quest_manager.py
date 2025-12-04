"""
Tests for Quest Manager

Tests the QuestManager system including:
- Quest loading from JSON
- Episode-based quest filtering
- Quest triggering
- Objective updates
- Quest completion tracking
- Save/load state
- Statistics and rewards
"""

import unittest
import json
import tempfile
import os
from aerthos.campaign.quest_manager import QuestManager
from aerthos.campaign.side_quest import TriggerType, ObjectiveType


class TestQuestManagerLoading(unittest.TestCase):
    """Test quest manager loading and initialization"""

    def setUp(self):
        """Create temporary quest data file for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.quest_file = os.path.join(self.temp_dir, "test_quests.json")

        # Create test quest data
        test_quests = {
            "test_quest_1": {
                "title": "Test Quest 1",
                "description": "First test quest",
                "episode_id": "episode_01",
                "trigger_type": "enter_room",
                "trigger_conditions": {"room_id": "room_1"},
                "objectives": [
                    {
                        "id": "obj_1",
                        "description": "Kill goblin",
                        "type": "kill_monster",
                        "target": "goblin",
                        "count": 1
                    }
                ],
                "rewards": {"xp": 100, "gold": 50, "items": [], "reputation": 5},
                "completion_flag": "quest1_done",
                "optional": True,
                "hidden": False
            },
            "test_quest_2": {
                "title": "Test Quest 2",
                "description": "Second test quest",
                "episode_id": "episode_01",
                "trigger_type": "kill_monster",
                "trigger_conditions": {"monster_id": "orc"},
                "objectives": [
                    {
                        "id": "obj_2",
                        "description": "Collect keys",
                        "type": "collect_item",
                        "target": "key",
                        "count": 3
                    }
                ],
                "rewards": {"xp": 200, "gold": 100, "items": ["sword"], "reputation": 10},
                "completion_flag": "quest2_done",
                "optional": True,
                "hidden": True
            },
            "test_quest_3": {
                "title": "Test Quest 3",
                "description": "Episode 2 quest",
                "episode_id": "episode_02",
                "trigger_type": "enter_room",
                "trigger_conditions": {"room_id": "room_2"},
                "objectives": [],
                "rewards": {"xp": 300, "gold": 0, "items": [], "reputation": 15},
                "completion_flag": "quest3_done",
                "optional": True,
                "hidden": False
            }
        }

        with open(self.quest_file, 'w') as f:
            json.dump(test_quests, f)

    def tearDown(self):
        """Clean up temporary files"""
        if os.path.exists(self.quest_file):
            os.remove(self.quest_file)
        os.rmdir(self.temp_dir)

    def test_quest_manager_initialization(self):
        """Test creating quest manager"""
        manager = QuestManager(quest_data_path=self.quest_file)

        self.assertEqual(len(manager.all_quests), 3)
        self.assertIn("test_quest_1", manager.all_quests)
        self.assertIn("test_quest_2", manager.all_quests)
        self.assertIn("test_quest_3", manager.all_quests)

    def test_get_quests_for_episode(self):
        """Test filtering quests by episode"""
        manager = QuestManager(quest_data_path=self.quest_file)

        # Episode 1 should have 2 quests
        ep1_quests = manager.get_quests_for_episode("episode_01")
        self.assertEqual(len(ep1_quests), 2)

        # Episode 2 should have 1 quest
        ep2_quests = manager.get_quests_for_episode("episode_02")
        self.assertEqual(len(ep2_quests), 1)
        self.assertEqual(ep2_quests[0].id, "test_quest_3")

        # Non-existent episode should return empty list
        ep3_quests = manager.get_quests_for_episode("episode_99")
        self.assertEqual(len(ep3_quests), 0)

    def test_get_quest_by_id(self):
        """Test getting specific quest by ID"""
        manager = QuestManager(quest_data_path=self.quest_file)

        quest = manager.get_quest_by_id("test_quest_1")
        self.assertIsNotNone(quest)
        self.assertEqual(quest.title, "Test Quest 1")

        nonexistent = manager.get_quest_by_id("fake_quest")
        self.assertIsNone(nonexistent)


class TestQuestManagerTriggers(unittest.TestCase):
    """Test quest triggering system"""

    def setUp(self):
        """Create temporary quest data"""
        self.temp_dir = tempfile.mkdtemp()
        self.quest_file = os.path.join(self.temp_dir, "test_quests.json")

        test_quests = {
            "room_quest": {
                "title": "Room Quest",
                "description": "Triggered by room",
                "episode_id": "episode_01",
                "trigger_type": "enter_room",
                "trigger_conditions": {"room_id": "secret_room"},
                "objectives": [],
                "rewards": {"xp": 100, "gold": 0, "items": [], "reputation": 0},
                "completion_flag": "room_done",
                "optional": True,
                "hidden": False
            },
            "monster_quest": {
                "title": "Monster Quest",
                "description": "Triggered by monster",
                "episode_id": "episode_01",
                "trigger_type": "kill_monster",
                "trigger_conditions": {"monster_id": "dragon"},
                "objectives": [],
                "rewards": {"xp": 500, "gold": 0, "items": [], "reputation": 0},
                "completion_flag": "dragon_done",
                "optional": True,
                "hidden": False
            }
        }

        with open(self.quest_file, 'w') as f:
            json.dump(test_quests, f)

        self.manager = QuestManager(quest_data_path=self.quest_file)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.quest_file):
            os.remove(self.quest_file)
        os.rmdir(self.temp_dir)

    def test_check_triggers_room(self):
        """Test room trigger"""
        triggered = self.manager.check_triggers(
            "enter_room",
            {"room_id": "secret_room"},
            "episode_01"
        )

        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].id, "room_quest")
        self.assertTrue(triggered[0].active)

    def test_check_triggers_monster(self):
        """Test monster trigger"""
        triggered = self.manager.check_triggers(
            "kill_monster",
            {"monster_id": "dragon"},
            "episode_01"
        )

        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].id, "monster_quest")

    def test_check_triggers_wrong_episode(self):
        """Test that triggers only work for current episode"""
        triggered = self.manager.check_triggers(
            "enter_room",
            {"room_id": "secret_room"},
            "episode_02"  # Wrong episode
        )

        self.assertEqual(len(triggered), 0)

    def test_check_triggers_no_match(self):
        """Test trigger with no matching quests"""
        triggered = self.manager.check_triggers(
            "enter_room",
            {"room_id": "nonexistent_room"},
            "episode_01"
        )

        self.assertEqual(len(triggered), 0)


class TestQuestManagerObjectives(unittest.TestCase):
    """Test quest objective tracking"""

    def setUp(self):
        """Create test quests with objectives"""
        self.temp_dir = tempfile.mkdtemp()
        self.quest_file = os.path.join(self.temp_dir, "test_quests.json")

        test_quests = {
            "kill_quest": {
                "title": "Kill Quest",
                "description": "Kill monsters",
                "episode_id": "episode_01",
                "trigger_type": "auto_start",
                "trigger_conditions": {},
                "objectives": [
                    {
                        "id": "kill_goblins",
                        "description": "Kill 3 goblins",
                        "type": "kill_monster",
                        "target": "goblin",
                        "count": 3
                    }
                ],
                "rewards": {"xp": 300, "gold": 0, "items": [], "reputation": 0},
                "completion_flag": "kill_done",
                "optional": True,
                "hidden": False
            }
        }

        with open(self.quest_file, 'w') as f:
            json.dump(test_quests, f)

        self.manager = QuestManager(quest_data_path=self.quest_file)

        # Activate the quest
        quest = self.manager.get_quest_by_id("kill_quest")
        quest.activate()

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.quest_file):
            os.remove(self.quest_file)
        os.rmdir(self.temp_dir)

    def test_update_quest_objectives(self):
        """Test updating quest objectives"""
        quest = self.manager.get_quest_by_id("kill_quest")
        self.assertFalse(quest.completed)

        # Update objective progress
        quest.objectives[0].update_progress(3)

        # Check completion
        completed = self.manager.check_completions()
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].id, "kill_quest")
        self.assertTrue(quest.completed)


class TestQuestManagerState(unittest.TestCase):
    """Test quest manager state management"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.quest_file = os.path.join(self.temp_dir, "test_quests.json")

        test_quests = {
            "quest_1": {
                "title": "Quest 1",
                "description": "Test quest",
                "episode_id": "episode_01",
                "trigger_type": "auto_start",
                "trigger_conditions": {},
                "objectives": [],
                "rewards": {"xp": 100, "gold": 50, "items": ["sword"], "reputation": 5},
                "completion_flag": "q1_done",
                "optional": True,
                "hidden": False
            },
            "quest_2": {
                "title": "Quest 2",
                "description": "Another quest",
                "episode_id": "episode_01",
                "trigger_type": "auto_start",
                "trigger_conditions": {},
                "objectives": [],
                "rewards": {"xp": 200, "gold": 100, "items": [], "reputation": 10},
                "completion_flag": "q2_done",
                "optional": True,
                "hidden": False
            }
        }

        with open(self.quest_file, 'w') as f:
            json.dump(test_quests, f)

        self.manager = QuestManager(quest_data_path=self.quest_file)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.quest_file):
            os.remove(self.quest_file)
        os.rmdir(self.temp_dir)

    def test_get_active_quests(self):
        """Test getting active quests"""
        # Initially no active quests
        active = self.manager.get_active_quests()
        self.assertEqual(len(active), 0)

        # Activate one quest
        quest1 = self.manager.get_quest_by_id("quest_1")
        quest1.activate()

        active = self.manager.get_active_quests()
        self.assertEqual(len(active), 1)

    def test_get_completed_quests(self):
        """Test getting completed quests"""
        # Initially no completed quests
        completed = self.manager.get_completed_quests()
        self.assertEqual(len(completed), 0)

        # Complete a quest
        quest1 = self.manager.get_quest_by_id("quest_1")
        quest1.activate()
        quest1.check_completion()  # No objectives, completes immediately

        completed = self.manager.get_completed_quests()
        self.assertEqual(len(completed), 1)

    def test_get_summary_stats(self):
        """Test getting quest statistics"""
        stats = self.manager.get_summary_stats()

        self.assertEqual(stats['total_quests'], 2)
        self.assertEqual(stats['discovered'], 0)
        self.assertEqual(stats['active'], 0)
        self.assertEqual(stats['completed'], 0)
        self.assertEqual(stats['available'], 2)

        # Activate and complete one quest
        quest1 = self.manager.get_quest_by_id("quest_1")
        quest1.activate()
        quest1.check_completion()

        stats = self.manager.get_summary_stats()
        self.assertEqual(stats['discovered'], 1)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['available'], 1)

    def test_get_total_rewards(self):
        """Test calculating total rewards"""
        # Initially no rewards
        rewards = self.manager.get_total_rewards()
        self.assertEqual(rewards['xp'], 0)
        self.assertEqual(rewards['gold'], 0)

        # Complete quests
        quest1 = self.manager.get_quest_by_id("quest_1")
        quest1.activate()
        quest1.check_completion()

        quest2 = self.manager.get_quest_by_id("quest_2")
        quest2.activate()
        quest2.check_completion()

        # Check total rewards
        rewards = self.manager.get_total_rewards()
        self.assertEqual(rewards['xp'], 300)  # 100 + 200
        self.assertEqual(rewards['gold'], 150)  # 50 + 100
        self.assertEqual(len(rewards['items']), 1)  # sword
        self.assertEqual(rewards['reputation'], 15)  # 5 + 10

    def test_save_load_state(self):
        """Test saving and loading quest state"""
        # Activate one quest (but don't complete it)
        quest1 = self.manager.get_quest_by_id("quest_1")
        quest1.activate()
        # Don't call check_completion - keep it active

        # Save state
        state = self.manager.to_dict()
        self.assertIn("quest_1", state)
        self.assertTrue(state["quest_1"]["discovered"])
        self.assertTrue(state["quest_1"]["active"])

        # Create new manager and load state
        new_manager = QuestManager(quest_data_path=self.quest_file)
        new_manager.from_dict(state)

        # Verify state was restored
        restored_quest = new_manager.get_quest_by_id("quest_1")
        self.assertTrue(restored_quest.discovered)
        self.assertTrue(restored_quest.active)
        self.assertFalse(restored_quest.completed)  # Not completed yet


class TestQuestManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_missing_quest_file(self):
        """Test handling missing quest file"""
        # Should not crash, just create empty manager
        manager = QuestManager(quest_data_path="/nonexistent/path.json")
        self.assertEqual(len(manager.all_quests), 0)

    def test_invalid_json(self):
        """Test handling invalid JSON"""
        temp_dir = tempfile.mkdtemp()
        quest_file = os.path.join(temp_dir, "bad_quests.json")

        # Write invalid JSON
        with open(quest_file, 'w') as f:
            f.write("{invalid json")

        # Should raise error
        with self.assertRaises(ValueError):
            QuestManager(quest_data_path=quest_file)

        os.remove(quest_file)
        os.rmdir(temp_dir)


if __name__ == '__main__':
    unittest.main()
