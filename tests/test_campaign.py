"""
Tests for Campaign class
"""

import unittest
from datetime import datetime
from aerthos.campaign.campaign import Campaign


class TestCampaign(unittest.TestCase):
    """Test Campaign state management"""

    def setUp(self):
        """Create a test campaign"""
        self.campaign = Campaign(
            id='test-campaign-1',
            name='Test Campaign',
            description='A test campaign',
            party_id='test-party-1',
            current_episode_id='episode_01',
            current_hub_id='oakhaven',
            unlocked_episodes=['episode_01'],
            unlocked_hubs=['oakhaven']
        )

    def test_campaign_creation(self):
        """Test campaign is created correctly"""
        self.assertEqual(self.campaign.id, 'test-campaign-1')
        self.assertEqual(self.campaign.name, 'Test Campaign')
        self.assertEqual(self.campaign.party_id, 'test-party-1')
        self.assertEqual(self.campaign.current_episode_id, 'episode_01')
        self.assertEqual(self.campaign.current_hub_id, 'oakhaven')
        self.assertEqual(self.campaign.play_time_minutes, 0)
        self.assertIsInstance(self.campaign.created_at, datetime)
        self.assertIsInstance(self.campaign.last_played, datetime)

    def test_is_episode_unlocked(self):
        """Test episode unlock checking"""
        self.assertTrue(self.campaign.is_episode_unlocked('episode_01'))
        self.assertFalse(self.campaign.is_episode_unlocked('episode_02'))

    def test_is_episode_completed(self):
        """Test episode completion checking"""
        self.assertFalse(self.campaign.is_episode_completed('episode_01'))

        # Complete episode
        self.campaign.complete_episode('episode_01', {})

        self.assertTrue(self.campaign.is_episode_completed('episode_01'))

    def test_is_hub_unlocked(self):
        """Test hub unlock checking"""
        self.assertTrue(self.campaign.is_hub_unlocked('oakhaven'))
        self.assertFalse(self.campaign.is_hub_unlocked('eldoria'))

    def test_complete_episode(self):
        """Test episode completion with rewards"""
        rewards = {
            'unlocks': ['episode_02', 'episode_03'],
            'story_flags': ['goblin_threat_ended', 'found_serpent_medallion'],
            'unlocks_hubs': ['ironfast_outpost']
        }

        self.campaign.complete_episode('episode_01', rewards)

        # Check completion
        self.assertTrue(self.campaign.is_episode_completed('episode_01'))

        # Check unlocks
        self.assertTrue(self.campaign.is_episode_unlocked('episode_02'))
        self.assertTrue(self.campaign.is_episode_unlocked('episode_03'))

        # Check story flags
        self.assertTrue(self.campaign.get_story_flag('goblin_threat_ended'))
        self.assertTrue(self.campaign.get_story_flag('found_serpent_medallion'))

        # Check hub unlocks
        self.assertTrue(self.campaign.is_hub_unlocked('ironfast_outpost'))

    def test_story_flags(self):
        """Test story flag management"""
        # Initially no flags
        self.assertFalse(self.campaign.get_story_flag('test_flag'))

        # Set flag
        self.campaign.set_story_flag('test_flag', True)
        self.assertTrue(self.campaign.get_story_flag('test_flag'))

        # Clear flag
        self.campaign.set_story_flag('test_flag', False)
        self.assertFalse(self.campaign.get_story_flag('test_flag'))

    def test_reputation(self):
        """Test faction reputation tracking"""
        # Initially neutral
        self.assertEqual(self.campaign.get_reputation('dwarves'), 0)

        # Gain reputation
        self.campaign.modify_reputation('dwarves', 10)
        self.assertEqual(self.campaign.get_reputation('dwarves'), 10)

        # Lose reputation
        self.campaign.modify_reputation('dwarves', -5)
        self.assertEqual(self.campaign.get_reputation('dwarves'), 5)

    def test_play_time(self):
        """Test play time tracking"""
        self.assertEqual(self.campaign.play_time_minutes, 0)

        self.campaign.update_play_time(30)
        self.assertEqual(self.campaign.play_time_minutes, 30)

        self.campaign.update_play_time(45)
        self.assertEqual(self.campaign.play_time_minutes, 75)

    def test_serialization(self):
        """Test campaign serialization/deserialization"""
        # Add some state
        self.campaign.complete_episode('episode_01', {
            'unlocks': ['episode_02'],
            'story_flags': ['test_flag']
        })
        self.campaign.modify_reputation('dwarves', 10)
        self.campaign.update_play_time(60)

        # Serialize
        data = self.campaign.to_json()

        # Deserialize
        restored = Campaign.from_json(data)

        # Verify state
        self.assertEqual(restored.id, self.campaign.id)
        self.assertEqual(restored.name, self.campaign.name)
        self.assertEqual(restored.party_id, self.campaign.party_id)
        self.assertTrue(restored.is_episode_completed('episode_01'))
        self.assertTrue(restored.is_episode_unlocked('episode_02'))
        self.assertTrue(restored.get_story_flag('test_flag'))
        self.assertEqual(restored.get_reputation('dwarves'), 10)
        self.assertEqual(restored.play_time_minutes, 60)


if __name__ == '__main__':
    unittest.main()
