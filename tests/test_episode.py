"""
Tests for Episode class
"""

import unittest
from pathlib import Path
from aerthos.campaign.episode import Episode
from aerthos.campaign.campaign import Campaign


class TestEpisode(unittest.TestCase):
    """Test Episode loading and functionality"""

    def test_episode_loading(self):
        """Test loading episode from JSON"""
        episode = Episode.load('episode_01')

        self.assertEqual(episode.id, 'episode_01')
        self.assertEqual(episode.title, 'The Goblin Refugees')
        self.assertEqual(episode.act, 1)
        self.assertEqual(episode.recommended_level, 1)
        self.assertEqual(episode.hub_id, 'oakhaven')

    def test_episode_briefing(self):
        """Test episode briefing data"""
        episode = Episode.load('episode_01')

        self.assertEqual(episode.briefing.quest_giver, 'The Guide')
        self.assertEqual(episode.briefing.location, 'The Dirty Mug tavern')
        self.assertIn('goblins', episode.briefing.dialogue.lower())

    def test_episode_dungeon_config(self):
        """Test dungeon configuration"""
        episode = Episode.load('episode_01')

        self.assertEqual(episode.dungeon_config.type, 'hand_crafted')
        self.assertEqual(episode.dungeon_config.file, 'dungeons/keep_of_kaldor.json')
        self.assertEqual(episode.dungeon_config.name, 'The Ruined Keep of Kaldor')
        self.assertEqual(episode.dungeon_config.theme, 'ruins')
        self.assertEqual(episode.dungeon_config.levels, 2)

    def test_episode_completion_criteria(self):
        """Test completion criteria"""
        episode = Episode.load('episode_01')

        self.assertEqual(episode.completion_criteria.type, 'boss_defeated')
        self.assertEqual(episode.completion_criteria.target, 'grukk_hobgoblin_chief')

    def test_episode_rewards(self):
        """Test rewards structure"""
        episode = Episode.load('episode_01')

        self.assertEqual(episode.rewards.xp_bonus, 2500)  # Updated for 5x XP multiplier
        self.assertEqual(episode.rewards.gold_bonus, 100)
        self.assertIn('dagger_plus_1', episode.rewards.items)
        self.assertIn('episode_02', episode.rewards.unlocks)
        self.assertIn('found_serpent_medallion', episode.rewards.story_flags)
        self.assertIn('goblin_threat_ended', episode.rewards.story_flags)

    def test_episode_rumors(self):
        """Test rumors list"""
        episode = Episode.load('episode_01')

        self.assertEqual(len(episode.rumors), 3)
        self.assertIn('High Pass', episode.rumors[0])

    def test_episode_prerequisites(self):
        """Test prerequisites checking"""
        episode = Episode.load('episode_01')

        # Episode 1 has no prerequisites
        self.assertEqual(len(episode.prerequisites), 0)

        # Create campaign and check
        campaign = Campaign(
            id='test',
            name='Test',
            description='Test',
            party_id='test',
            current_episode_id='episode_01',
            current_hub_id='oakhaven'
        )

        self.assertTrue(episode.check_prerequisites(campaign))

    def test_episode_serialization(self):
        """Test episode serialization"""
        episode = Episode.load('episode_01')

        # Serialize
        data = episode.to_json()

        # Deserialize
        restored = Episode.from_json(data)

        # Verify
        self.assertEqual(restored.id, episode.id)
        self.assertEqual(restored.title, episode.title)
        self.assertEqual(restored.rewards.xp_bonus, episode.rewards.xp_bonus)


if __name__ == '__main__':
    unittest.main()
