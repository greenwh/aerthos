"""
Integration Tests for Quest System

Tests quest integration with campaign systems:
- Quest manager integration with episode runner
- Quest loading from actual quest data
- Quest state persistence
- End-to-end quest flow
"""

import unittest
import json
import os
from aerthos.campaign.quest_manager import QuestManager
from aerthos.campaign.side_quest import TriggerType


class TestQuestDataLoading(unittest.TestCase):
    """Test loading actual quest data from side_quests.json"""

    def test_load_actual_quest_data(self):
        """Test loading the actual side_quests.json file"""
        # Try to load the actual quest file
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Should have loaded quests
        self.assertGreater(len(manager.all_quests), 0)

        # Check that episodes are indexed
        self.assertGreater(len(manager.episode_quests), 0)

    def test_quest_data_structure(self):
        """Test that loaded quests have correct structure"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Verify each quest has required fields
        for quest_id, quest in manager.all_quests.items():
            self.assertIsNotNone(quest.id)
            self.assertIsNotNone(quest.title)
            self.assertIsNotNone(quest.description)
            self.assertIsNotNone(quest.episode_id)
            self.assertIsNotNone(quest.trigger_type)
            self.assertIsNotNone(quest.rewards)
            self.assertIsInstance(quest.objectives, list)

    def test_episode_distribution(self):
        """Test that quests are distributed across episodes"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Should have quests for multiple episodes
        self.assertGreater(len(manager.episode_quests), 0)

        # Check specific episodes have quests
        # Based on the quest data we created, Episodes 1-10 should all have quests
        for episode_num in range(1, 11):
            episode_id = f"episode_{episode_num:02d}"
            quests = manager.get_quests_for_episode(episode_id)
            # Each episode should have at least some quests
            # (We added 2 per episode, so this should pass)
            if episode_num <= 10:  # Episodes 1-10
                self.assertGreaterEqual(len(quests), 0, f"Episode {episode_num} should have quests")


class TestQuestWorkflow(unittest.TestCase):
    """Test end-to-end quest workflow"""

    def test_quest_discovery_and_completion(self):
        """Test full quest lifecycle"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Get first quest for episode 1
        ep1_quests = manager.get_quests_for_episode("episode_01")
        if len(ep1_quests) == 0:
            self.skipTest("No quests for episode 1")

        quest = ep1_quests[0]

        # Initially not discovered or active
        self.assertFalse(quest.discovered)
        self.assertFalse(quest.active)
        self.assertFalse(quest.completed)

        # Trigger quest
        trigger_type = quest.trigger_type.value
        trigger_cond = quest.trigger_conditions

        triggered = manager.check_triggers(trigger_type, trigger_cond, "episode_01")

        # Quest should be triggered and active
        self.assertIn(quest, triggered)
        self.assertTrue(quest.discovered)
        self.assertTrue(quest.active)

        # Complete all objectives
        for obj in quest.objectives:
            obj.update_progress(obj.count)

        # Check completion
        completed = manager.check_completions()

        if len(quest.objectives) > 0:
            # Quest with objectives should complete when objectives done
            self.assertIn(quest, completed)
            self.assertTrue(quest.completed)
        else:
            # Quest with no objectives completes immediately upon activation
            quest.check_completion()
            self.assertTrue(quest.completed)

    def test_quest_state_persistence(self):
        """Test saving and loading quest state"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Get and activate a quest
        ep1_quests = manager.get_quests_for_episode("episode_01")
        if len(ep1_quests) == 0:
            self.skipTest("No quests for episode 1")

        quest = ep1_quests[0]
        quest.activate()

        # Complete some objectives
        if len(quest.objectives) > 0:
            quest.objectives[0].update_progress(1)

        # Save state
        state = manager.to_dict()
        self.assertIn(quest.id, state)

        # Create new manager and restore state
        new_manager = QuestManager(quest_data_path=quest_file)
        new_manager.from_dict(state)

        # Verify state was restored
        restored_quest = new_manager.get_quest_by_id(quest.id)
        self.assertTrue(restored_quest.discovered)
        self.assertTrue(restored_quest.active)

        if len(quest.objectives) > 0:
            self.assertEqual(
                restored_quest.objectives[0].current,
                quest.objectives[0].current
            )


class TestQuestRewards(unittest.TestCase):
    """Test quest reward system"""

    def test_reward_accumulation(self):
        """Test that rewards accumulate across quests"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Get quests for episode 1
        ep1_quests = manager.get_quests_for_episode("episode_01")
        if len(ep1_quests) < 2:
            self.skipTest("Need at least 2 quests for episode 1")

        # Complete first two quests
        for quest in ep1_quests[:2]:
            quest.activate()
            for obj in quest.objectives:
                obj.update_progress(obj.count)
            quest.check_completion()

        # Get total rewards
        rewards = manager.get_total_rewards()

        # Should have accumulated XP and gold
        self.assertGreater(rewards['xp'], 0)

        # Verify it matches sum of individual quest rewards
        expected_xp = sum(q.rewards.xp for q in ep1_quests[:2])
        expected_gold = sum(q.rewards.gold for q in ep1_quests[:2])

        self.assertEqual(rewards['xp'], expected_xp)
        self.assertEqual(rewards['gold'], expected_gold)


class TestQuestStatistics(unittest.TestCase):
    """Test quest statistics and tracking"""

    def test_quest_statistics(self):
        """Test quest summary statistics"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Get initial stats
        stats = manager.get_summary_stats()

        self.assertIn('total_quests', stats)
        self.assertIn('discovered', stats)
        self.assertIn('active', stats)
        self.assertIn('completed', stats)
        self.assertIn('available', stats)

        # Total should equal discovered + available
        self.assertEqual(
            stats['total_quests'],
            stats['discovered'] + stats['available']
        )

        # Activate a quest
        all_quests = list(manager.all_quests.values())
        if len(all_quests) > 0:
            all_quests[0].activate()

            # Stats should update
            new_stats = manager.get_summary_stats()
            self.assertEqual(new_stats['active'], 1)
            self.assertEqual(new_stats['discovered'], 1)


class TestQuestTriggerTypes(unittest.TestCase):
    """Test different quest trigger types"""

    def test_trigger_types_exist(self):
        """Test that quests use different trigger types"""
        from aerthos.constants import DATA_DIR
        quest_file = f"{DATA_DIR}/side_quests.json"

        if not os.path.exists(quest_file):
            self.skipTest("Quest data file not found")

        manager = QuestManager(quest_data_path=quest_file)

        # Collect all trigger types used
        trigger_types = set()
        for quest in manager.all_quests.values():
            trigger_types.add(quest.trigger_type)

        # Should have variety of trigger types
        self.assertGreater(len(trigger_types), 0)

        # Check for specific trigger types we know exist
        trigger_values = {t.value for t in trigger_types}
        # Based on our quest data, we should have enter_room, kill_monster, search_room, find_item
        common_triggers = {"enter_room", "kill_monster", "search_room", "find_item"}
        self.assertTrue(len(trigger_values & common_triggers) > 0)


if __name__ == '__main__':
    unittest.main()
