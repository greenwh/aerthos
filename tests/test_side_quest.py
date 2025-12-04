"""
Tests for Side Quest System

Tests the SideQuest data model including:
- Quest data structure
- Trigger conditions
- Objective tracking
- Completion detection
- Reward distribution
- Serialization/deserialization
"""

import unittest
from aerthos.campaign.side_quest import (
    TriggerType, ObjectiveType, QuestObjective, QuestRewards, SideQuest
)


class TestQuestObjective(unittest.TestCase):
    """Test quest objective data model"""

    def test_objective_creation(self):
        """Test creating a quest objective"""
        obj = QuestObjective(
            id="test_obj",
            description="Test objective",
            objective_type=ObjectiveType.KILL_MONSTER,
            target="goblin",
            count=3
        )

        self.assertEqual(obj.id, "test_obj")
        self.assertEqual(obj.description, "Test objective")
        self.assertEqual(obj.objective_type, ObjectiveType.KILL_MONSTER)
        self.assertEqual(obj.target, "goblin")
        self.assertEqual(obj.count, 3)
        self.assertEqual(obj.current, 0)
        self.assertFalse(obj.completed)

    def test_objective_progress_tracking(self):
        """Test objective progress tracking"""
        obj = QuestObjective(
            id="kill_orcs",
            description="Kill 5 orcs",
            objective_type=ObjectiveType.KILL_MONSTER,
            target="orc",
            count=5
        )

        # Initially incomplete
        self.assertFalse(obj.completed)
        self.assertEqual(obj.current, 0)

        # Update progress
        obj.update_progress(2)
        self.assertEqual(obj.current, 2)
        self.assertFalse(obj.completed)

        # Complete objective
        newly_completed = obj.update_progress(3)
        self.assertEqual(obj.current, 5)
        self.assertTrue(obj.completed)
        self.assertTrue(newly_completed)

        # Additional progress doesn't exceed count
        obj.update_progress(2)
        self.assertEqual(obj.current, 5)

    def test_objective_serialization(self):
        """Test objective to/from dict"""
        obj = QuestObjective(
            id="collect_items",
            description="Collect 3 keys",
            objective_type=ObjectiveType.COLLECT_ITEM,
            target="key",
            count=3
        )
        obj.update_progress(2)

        # Serialize
        data = obj.to_dict()
        self.assertEqual(data['id'], "collect_items")
        self.assertEqual(data['current'], 2)
        self.assertFalse(data['completed'])

        # Deserialize
        obj2 = QuestObjective.from_dict(data)
        self.assertEqual(obj2.id, obj.id)
        self.assertEqual(obj2.current, obj.current)
        self.assertEqual(obj2.completed, obj.completed)


class TestQuestRewards(unittest.TestCase):
    """Test quest reward data model"""

    def test_reward_creation(self):
        """Test creating quest rewards"""
        rewards = QuestRewards(
            xp=500,
            gold=100,
            items=["ring_protection_1", "potion_healing"],
            reputation=10
        )

        self.assertEqual(rewards.xp, 500)
        self.assertEqual(rewards.gold, 100)
        self.assertEqual(len(rewards.items), 2)
        self.assertEqual(rewards.reputation, 10)

    def test_reward_defaults(self):
        """Test reward default values"""
        rewards = QuestRewards()

        self.assertEqual(rewards.xp, 0)
        self.assertEqual(rewards.gold, 0)
        self.assertEqual(rewards.items, [])
        self.assertEqual(rewards.reputation, 0)

    def test_reward_serialization(self):
        """Test reward to/from dict"""
        rewards = QuestRewards(
            xp=1000,
            gold=250,
            items=["sword_plus_1"],
            reputation=25
        )

        data = rewards.to_dict()
        self.assertEqual(data['xp'], 1000)
        self.assertEqual(data['items'], ["sword_plus_1"])

        rewards2 = QuestRewards.from_dict(data)
        self.assertEqual(rewards2.xp, rewards.xp)
        self.assertEqual(rewards2.gold, rewards.gold)
        self.assertEqual(rewards2.reputation, rewards.reputation)


class TestSideQuest(unittest.TestCase):
    """Test side quest data model"""

    def test_quest_creation(self):
        """Test creating a side quest"""
        quest = SideQuest(
            id="test_quest",
            title="Test Quest",
            description="A test quest",
            episode_id="episode_01",
            trigger_type=TriggerType.ENTER_ROOM,
            trigger_conditions={"room_id": "test_room"},
            objectives=[
                QuestObjective(
                    id="obj_1",
                    description="Defeat goblins",
                    objective_type=ObjectiveType.KILL_MONSTER,
                    target="goblin",
                    count=3
                )
            ],
            rewards=QuestRewards(xp=300, gold=50),
            completion_flag="test_complete",
            optional=True,
            hidden=False
        )

        self.assertEqual(quest.id, "test_quest")
        self.assertEqual(quest.title, "Test Quest")
        self.assertEqual(quest.episode_id, "episode_01")
        self.assertFalse(quest.active)
        self.assertFalse(quest.completed)
        self.assertEqual(len(quest.objectives), 1)

    def test_quest_trigger_matching(self):
        """Test quest trigger condition matching"""
        quest = SideQuest(
            id="room_quest",
            title="Room Quest",
            description="Triggered by entering room",
            episode_id="episode_01",
            trigger_type=TriggerType.ENTER_ROOM,
            trigger_conditions={"room_id": "secret_room"},
            objectives=[],
            rewards=QuestRewards(),
            completion_flag="quest_done"
        )

        # Check if trigger conditions match
        self.assertTrue(quest.check_trigger("enter_room", {"room_id": "secret_room"}))
        self.assertFalse(quest.check_trigger("enter_room", {"room_id": "other_room"}))
        self.assertFalse(quest.check_trigger("kill_monster", {"monster_id": "orc"}))

    def test_quest_activation(self):
        """Test quest activation"""
        quest = SideQuest(
            id="test_quest",
            title="Test Quest",
            description="Test",
            episode_id="episode_01",
            trigger_type=TriggerType.ENTER_ROOM,
            trigger_conditions={"room_id": "test_room"},
            objectives=[],
            rewards=QuestRewards(),
            completion_flag="test_done"
        )

        self.assertFalse(quest.discovered)
        self.assertFalse(quest.active)

        quest.activate()

        self.assertTrue(quest.discovered)
        self.assertTrue(quest.active)

    def test_quest_completion_detection(self):
        """Test quest completion detection"""
        quest = SideQuest(
            id="simple_quest",
            title="Simple Quest",
            description="Single objective",
            episode_id="episode_01",
            trigger_type=TriggerType.ENTER_ROOM,
            trigger_conditions={"room_id": "start"},
            objectives=[
                QuestObjective(
                    id="defeat_boss",
                    description="Defeat the boss",
                    objective_type=ObjectiveType.KILL_MONSTER,
                    target="boss",
                    count=1
                )
            ],
            rewards=QuestRewards(xp=1000, items=["sword_plus_2"]),
            completion_flag="boss_defeated"
        )

        quest.activate()
        self.assertFalse(quest.completed)

        # Complete objective
        quest.objectives[0].update_progress(1)

        # Check completion
        is_complete = quest.check_completion()
        self.assertTrue(is_complete)
        self.assertTrue(quest.completed)

    def test_quest_serialization(self):
        """Test quest to/from dict"""
        quest = SideQuest(
            id="serialize_test",
            title="Serialize Test",
            description="Test serialization",
            episode_id="episode_03",
            trigger_type=TriggerType.KILL_MONSTER,
            trigger_conditions={"monster_id": "dragon"},
            objectives=[
                QuestObjective(
                    id="obj_1",
                    description="Test obj",
                    objective_type=ObjectiveType.KILL_MONSTER,
                    target="dragon",
                    count=1
                )
            ],
            rewards=QuestRewards(xp=2000, gold=500),
            completion_flag="dragon_slain",
            optional=True,
            hidden=True
        )

        quest.activate()
        quest.objectives[0].update_progress(1)
        quest.check_completion()

        # Serialize
        data = quest.to_dict()
        self.assertEqual(data['id'], "serialize_test")
        self.assertFalse(data['active'])  # Quest becomes inactive when completed
        self.assertTrue(data['completed'])

        # Deserialize
        quest2 = SideQuest.from_dict(data)
        self.assertEqual(quest2.id, quest.id)
        self.assertFalse(quest2.active)  # Completed quests are inactive
        self.assertTrue(quest2.completed)
        self.assertEqual(len(quest2.objectives), len(quest.objectives))

    def test_quest_from_json_data(self):
        """Test loading quest from JSON-style dict"""
        json_data = {
            "title": "The Forgotten Cistern",
            "description": "An ancient cistern holds a terrible secret",
            "episode_id": "episode_02",
            "trigger_type": "enter_room",
            "trigger_conditions": {
                "room_id": "old_cistern"
            },
            "objectives": [
                {
                    "id": "defeat_otyugh",
                    "description": "Defeat the Otyugh",
                    "type": "kill_monster",
                    "target": "otyugh",
                    "count": 1
                }
            ],
            "rewards": {
                "xp": 500,
                "gold": 100,
                "items": ["ring_protection_1"],
                "reputation": 10
            },
            "completion_flag": "cistern_explored",
            "optional": True,
            "hidden": False
        }

        quest = SideQuest.from_json_data("forgotten_cistern", json_data)

        self.assertEqual(quest.id, "forgotten_cistern")
        self.assertEqual(quest.title, "The Forgotten Cistern")
        self.assertEqual(quest.episode_id, "episode_02")
        self.assertEqual(quest.trigger_type, TriggerType.ENTER_ROOM)
        self.assertEqual(len(quest.objectives), 1)
        self.assertEqual(quest.rewards.xp, 500)
        self.assertEqual(quest.rewards.items, ["ring_protection_1"])


class TestQuestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_quest_with_no_objectives(self):
        """Test quest with no objectives"""
        quest = SideQuest(
            id="no_obj_quest",
            title="No Objectives",
            description="Quest with no objectives",
            episode_id="episode_01",
            trigger_type=TriggerType.AUTO_START,
            trigger_conditions={},
            objectives=[],
            rewards=QuestRewards(xp=100),
            completion_flag="instant_complete"
        )

        quest.activate()
        # Quest with no objectives should be complete immediately
        is_complete = quest.check_completion()
        self.assertTrue(is_complete)
        self.assertTrue(quest.completed)

    def test_multi_objective_progress(self):
        """Test quest with multiple objectives"""
        quest = SideQuest(
            id="multi_obj",
            title="Multi Objective",
            description="Multiple objectives",
            episode_id="episode_02",
            trigger_type=TriggerType.ENTER_ROOM,
            trigger_conditions={"room_id": "start"},
            objectives=[
                QuestObjective(
                    id="kill_goblins",
                    description="Kill 3 goblins",
                    objective_type=ObjectiveType.KILL_MONSTER,
                    target="goblin",
                    count=3
                ),
                QuestObjective(
                    id="find_key",
                    description="Find the key",
                    objective_type=ObjectiveType.COLLECT_ITEM,
                    target="key",
                    count=1
                )
            ],
            rewards=QuestRewards(xp=500),
            completion_flag="multi_done"
        )

        quest.activate()

        # Complete first objective
        quest.objectives[0].update_progress(3)
        is_complete = quest.check_completion()
        self.assertFalse(is_complete)  # Second objective not done

        # Complete second objective
        quest.objectives[1].update_progress(1)
        is_complete = quest.check_completion()
        self.assertTrue(is_complete)
        self.assertTrue(quest.completed)


if __name__ == '__main__':
    unittest.main()
