"""
Tests for CampaignManager class
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from aerthos.campaign.campaign_manager import CampaignManager, Campaign


class TestCampaignManager(unittest.TestCase):
    """Test CampaignManager persistence"""

    def setUp(self):
        """Create temporary directory for testing"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = CampaignManager(save_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_create_campaign(self):
        """Test campaign creation from template"""
        campaign = self.manager.create_campaign(
            campaign_template_id='serpents_shadow',
            party_id='test-party-1'
        )

        self.assertIsNotNone(campaign.id)
        self.assertEqual(campaign.name, "The Serpent's Shadow")
        self.assertEqual(campaign.party_id, 'test-party-1')
        self.assertEqual(campaign.current_hub_id, 'oakhaven')
        self.assertEqual(campaign.current_episode_id, 'episode_01')
        self.assertIn('episode_01', campaign.unlocked_episodes)
        self.assertIn('oakhaven', campaign.unlocked_hubs)

    def test_save_campaign(self):
        """Test saving a campaign"""
        campaign = Campaign(
            id='test-campaign-1',
            name='Test Campaign',
            description='Test',
            party_id='test-party',
            current_episode_id='episode_01',
            current_hub_id='oakhaven'
        )

        campaign_id = self.manager.save_campaign(campaign)

        self.assertEqual(campaign_id, 'test-campaign-1')

        # Verify file exists
        filepath = self.temp_dir / f'{campaign_id}.json'
        self.assertTrue(filepath.exists())

    def test_load_campaign(self):
        """Test loading a campaign"""
        # Create and save
        original = Campaign(
            id='test-campaign-1',
            name='Test Campaign',
            description='Test',
            party_id='test-party',
            current_episode_id='episode_01',
            current_hub_id='oakhaven'
        )
        original.complete_episode('episode_01', {'unlocks': ['episode_02']})

        self.manager.save_campaign(original)

        # Load
        loaded = self.manager.load_campaign('test-campaign-1')

        # Verify
        self.assertEqual(loaded.id, original.id)
        self.assertEqual(loaded.name, original.name)
        self.assertTrue(loaded.is_episode_completed('episode_01'))
        self.assertTrue(loaded.is_episode_unlocked('episode_02'))

    def test_list_campaigns(self):
        """Test listing campaigns"""
        # Create multiple campaigns
        for i in range(3):
            campaign = Campaign(
                id=f'test-campaign-{i}',
                name=f'Campaign {i}',
                description='Test',
                party_id='test-party',
                current_episode_id='episode_01',
                current_hub_id='oakhaven'
            )
            self.manager.save_campaign(campaign)

        # List
        campaigns = self.manager.list_campaigns()

        self.assertEqual(len(campaigns), 3)
        self.assertTrue(all(hasattr(c, 'id') for c in campaigns))
        self.assertTrue(all(hasattr(c, 'name') for c in campaigns))

    def test_delete_campaign(self):
        """Test deleting a campaign"""
        # Create and save
        campaign = Campaign(
            id='test-campaign-1',
            name='Test Campaign',
            description='Test',
            party_id='test-party',
            current_episode_id='episode_01',
            current_hub_id='oakhaven'
        )
        self.manager.save_campaign(campaign)

        # Verify exists
        self.assertTrue(self.manager.campaign_exists('test-campaign-1'))

        # Delete
        result = self.manager.delete_campaign('test-campaign-1')

        self.assertTrue(result)
        self.assertFalse(self.manager.campaign_exists('test-campaign-1'))

    def test_campaign_exists(self):
        """Test checking campaign existence"""
        self.assertFalse(self.manager.campaign_exists('nonexistent'))

        # Create campaign
        campaign = Campaign(
            id='test-campaign-1',
            name='Test Campaign',
            description='Test',
            party_id='test-party',
            current_episode_id='episode_01',
            current_hub_id='oakhaven'
        )
        self.manager.save_campaign(campaign)

        self.assertTrue(self.manager.campaign_exists('test-campaign-1'))


if __name__ == '__main__':
    unittest.main()
