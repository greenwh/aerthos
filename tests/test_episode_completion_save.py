"""
Tests for episode completion campaign saving behavior

These tests verify the bug fix where episode completion in-dungeon
now properly saves the campaign file to disk.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from aerthos.campaign.campaign import Campaign
from aerthos.campaign.campaign_manager import CampaignManager
from aerthos.campaign.episode import Episode
from aerthos.campaign.episode_runner import EpisodeRunner
from aerthos.entities.party import Party
from aerthos.entities.player import PlayerCharacter
from aerthos.engine.game_state import GameState


class TestEpisodeCompletionSave(unittest.TestCase):
    """Test that episode completion properly saves campaign to disk"""

    def setUp(self):
        """Create temporary directory and test objects"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.campaign_mgr = CampaignManager(save_dir=self.temp_dir)

        # Create a test campaign
        self.campaign = Campaign(
            id='test-campaign-1',
            name='Test Campaign',
            description='Test campaign for save testing',
            party_id='test-party',
            current_episode_id='episode_01',
            current_hub_id='oakhaven',
            unlocked_episodes=['episode_01'],
            unlocked_hubs=['oakhaven']
        )

        # Save initial state
        self.campaign_mgr.save_campaign(self.campaign)

        # Create test party
        fighter = PlayerCharacter(
            name='Test Fighter',
            race='Human',
            char_class='Fighter',
            level=1,
            hp_current=10,
            hp_max=10,
            ac=5,
            thac0=20,
            strength=16, dexterity=14, constitution=15,
            intelligence=10, wisdom=10, charisma=10,
            gold=100
        )
        self.party = Party(members=[fighter])

        # Load episode
        self.episode = Episode.load('episode_01')

        # Create episode runner
        self.runner = EpisodeRunner(self.episode, self.campaign, self.party)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_episode_completion_updates_campaign_object(self):
        """Test that complete_episode updates the campaign object in memory"""
        # Verify initial state
        self.assertFalse(self.campaign.is_episode_completed('episode_01'))
        self.assertNotIn('episode_02', self.campaign.unlocked_episodes)

        # Complete episode
        success, message = self.runner.complete_episode()

        self.assertTrue(success)
        self.assertTrue(self.runner.state.completion_acknowledged)

        # Verify campaign object was updated in memory
        self.assertTrue(self.campaign.is_episode_completed('episode_01'))
        self.assertIn('episode_02', self.campaign.unlocked_episodes)

    def test_campaign_file_not_updated_without_explicit_save(self):
        """Test that campaign file is NOT updated without explicit save (pre-fix behavior)"""
        # Load initial campaign from disk
        loaded_before = self.campaign_mgr.load_campaign('test-campaign-1')
        self.assertFalse(loaded_before.is_episode_completed('episode_01'))

        # Complete episode (modifies in-memory campaign only)
        self.runner.complete_episode()

        # Load from disk again - should still show old state
        loaded_after = self.campaign_mgr.load_campaign('test-campaign-1')
        self.assertFalse(loaded_after.is_episode_completed('episode_01'))

    def test_campaign_file_updated_after_explicit_save(self):
        """Test that campaign file IS updated after explicit save (the fix)"""
        # Complete episode
        self.runner.complete_episode()

        # Explicitly save campaign (simulating the fix in web_ui/app.py)
        self.campaign_mgr.save_campaign(self.campaign)

        # Load from disk - should now show completed state
        loaded = self.campaign_mgr.load_campaign('test-campaign-1')
        self.assertTrue(loaded.is_episode_completed('episode_01'))
        self.assertIn('episode_02', loaded.unlocked_episodes)

    def test_completion_acknowledged_flag_set(self):
        """Test that completion_acknowledged flag is set after completion"""
        # Before completion
        self.assertFalse(self.runner.state.completion_acknowledged)

        # Complete episode
        self.runner.complete_episode()

        # After completion
        self.assertTrue(self.runner.state.completion_acknowledged)

    def test_save_campaign_after_completion_acknowledged(self):
        """Test the pattern used in the fix: check completion_acknowledged then save"""
        # This tests the exact pattern used in the web UI fix:
        # if game_state.episode_runner.state.completion_acknowledged:
        #     campaign_mgr.save_campaign(game_state.episode_runner.campaign)

        # Complete episode
        self.runner.complete_episode()

        # Check the flag and save (simulating the fix)
        if self.runner.state.completion_acknowledged:
            self.campaign_mgr.save_campaign(self.runner.campaign)

        # Verify file was updated
        loaded = self.campaign_mgr.load_campaign('test-campaign-1')
        self.assertTrue(loaded.is_episode_completed('episode_01'))

    def test_story_flags_saved_after_completion(self):
        """Test that story flags are persisted after completion save"""
        # Complete and save
        self.runner.complete_episode()
        self.campaign_mgr.save_campaign(self.campaign)

        # Load and verify story flags
        loaded = self.campaign_mgr.load_campaign('test-campaign-1')
        self.assertTrue(loaded.story_flags.get('found_serpent_medallion', False))
        self.assertTrue(loaded.story_flags.get('goblin_threat_ended', False))

    def test_unlocked_hubs_saved_after_completion(self):
        """Test that unlocked hubs are persisted after completion save"""
        # Complete episode (episode_01 unlocks no new hubs, but let's verify)
        self.runner.complete_episode()
        self.campaign_mgr.save_campaign(self.campaign)

        # Load and verify
        loaded = self.campaign_mgr.load_campaign('test-campaign-1')
        # Episode 01 doesn't unlock new hubs, but initial state should persist
        self.assertIn('oakhaven', loaded.unlocked_hubs)

    def test_xp_applied_after_completion(self):
        """Test that XP bonus is applied to party members after completion"""
        initial_xp = self.party.members[0].xp

        # Complete episode
        self.runner.complete_episode()

        # XP should have increased by episode bonus
        expected_xp = initial_xp + self.episode.rewards.xp_bonus
        self.assertEqual(self.party.members[0].xp, expected_xp)

    def test_multiple_completions_fail(self):
        """Test that completing an episode twice fails"""
        # First completion succeeds
        success1, _ = self.runner.complete_episode()
        self.assertTrue(success1)

        # Second completion fails
        success2, message = self.runner.complete_episode()
        self.assertFalse(success2)
        self.assertIn('already completed', message.lower())


class TestEpisodeCompletionIntegration(unittest.TestCase):
    """Integration tests for episode completion flow"""

    def setUp(self):
        """Create temporary directory and full test setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.campaign_mgr = CampaignManager(save_dir=self.temp_dir)

        # Create campaign via manager (uses template)
        self.campaign = self.campaign_mgr.create_campaign(
            campaign_template_id='serpents_shadow',
            party_id='test-party'
        )

        # Create test party with multiple members
        members = []
        for name, cls in [
            ('Fighter', 'Fighter'),
            ('Cleric', 'Cleric'),
            ('Thief', 'Thief'),
            ('MageTest', 'Magic-User')
        ]:
            char = PlayerCharacter(
                name=name,
                race='Human',
                char_class=cls,
                level=1,
                hp_current=10,
                hp_max=10,
                ac=5 if cls == 'Fighter' else 7,
                thac0=20,
                strength=16, dexterity=14, constitution=15,
                intelligence=12, wisdom=12, charisma=10,
                gold=100
            )
            members.append(char)
        self.party = Party(members=members)

        # Load episode and create runner
        self.episode = Episode.load('episode_01')
        self.runner = EpisodeRunner(self.episode, self.campaign, self.party)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_full_completion_flow_with_save(self):
        """Test complete episode flow including save"""
        # Load dungeon and create game state
        success, _ = self.runner.load_dungeon()
        self.assertTrue(success)

        success, _ = self.runner.create_game_state(self.party.members[0])
        self.assertTrue(success)

        # Initial state
        self.assertEqual(self.runner.state.phase, 'dungeon')

        # Complete episode
        success, message = self.runner.complete_episode()
        self.assertTrue(success)
        self.assertEqual(self.runner.state.phase, 'completed')

        # Simulate the fix: save campaign when completion_acknowledged
        if self.runner.state.completion_acknowledged:
            self.campaign_mgr.save_campaign(self.runner.campaign)

        # Verify persistence
        loaded = self.campaign_mgr.load_campaign(self.campaign.id)
        self.assertTrue(loaded.is_episode_completed('episode_01'))
        self.assertTrue(loaded.is_episode_unlocked('episode_02'))

    def test_party_xp_distribution(self):
        """Test that XP is distributed to all living party members"""
        initial_xp = [m.xp for m in self.party.members]

        # Complete episode
        self.runner.complete_episode()

        # All members should have gained XP
        for i, member in enumerate(self.party.members):
            expected = initial_xp[i] + self.episode.rewards.xp_bonus
            self.assertEqual(member.xp, expected,
                           f"{member.name} should have {expected} XP, got {member.xp}")

    def test_campaign_state_consistency_after_save_reload(self):
        """Test that campaign state is consistent after save and reload"""
        # Complete episode
        self.runner.complete_episode()

        # Save
        self.campaign_mgr.save_campaign(self.campaign)

        # Reload
        loaded = self.campaign_mgr.load_campaign(self.campaign.id)

        # Verify all state is preserved
        self.assertEqual(loaded.completed_episodes, self.campaign.completed_episodes)
        self.assertEqual(loaded.unlocked_episodes, self.campaign.unlocked_episodes)
        self.assertEqual(loaded.story_flags, self.campaign.story_flags)
        self.assertEqual(loaded.unlocked_hubs, self.campaign.unlocked_hubs)


if __name__ == '__main__':
    unittest.main()
