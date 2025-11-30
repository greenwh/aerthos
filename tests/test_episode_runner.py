"""
Tests for EpisodeRunner system
"""

import unittest
from aerthos.campaign.episode_runner import EpisodeRunner, EpisodeState
from aerthos.campaign.episode import Episode
from aerthos.campaign.campaign import Campaign
from aerthos.entities.party import Party
from aerthos.entities.player import PlayerCharacter


class TestEpisodeRunner(unittest.TestCase):
    """Test EpisodeRunner functionality"""

    def setUp(self):
        """Create test episode, campaign, and party"""
        # Load test episode
        self.episode = Episode.load('episode_01')

        # Create test campaign
        self.campaign = Campaign(
            id='test-campaign',
            name='Test Campaign',
            description='Test',
            party_id='test-party',
            current_episode_id='episode_01',
            current_hub_id='oakhaven',
            unlocked_episodes=['episode_01'],
            unlocked_hubs=['oakhaven']
        )

        # Create test party
        fighter = PlayerCharacter(
            name="Test Fighter",
            char_class="Fighter",
            race="Human",
            level=1,
            strength=16,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10,
            hp_current=10,
            hp_max=10,
            ac=5,
            thac0=19,
            gold=100
        )

        self.party = Party(members=[fighter])

        # Create episode runner
        self.runner = EpisodeRunner(self.episode, self.campaign, self.party)

    def test_initialization(self):
        """Test episode runner initializes correctly"""
        self.assertIsNotNone(self.runner)
        self.assertEqual(self.runner.episode, self.episode)
        self.assertEqual(self.runner.campaign, self.campaign)
        self.assertEqual(self.runner.party, self.party)
        self.assertEqual(self.runner.state.phase, 'intro')
        self.assertFalse(self.runner.state.dungeon_entered)

    def test_get_intro_text(self):
        """Test intro text generation"""
        intro = self.runner.get_intro_text()

        self.assertIsInstance(intro, str)
        self.assertIn('EPISODE', intro.upper())
        self.assertIn(self.episode.title.upper(), intro.upper())
        self.assertIn(self.episode.intro_text, intro)

    def test_get_briefing_text(self):
        """Test briefing text generation"""
        briefing = self.runner.get_briefing_text()

        self.assertIsInstance(briefing, str)
        self.assertIn('QUEST BRIEFING', briefing.upper())
        self.assertIn(self.episode.briefing.location, briefing)
        self.assertIn(self.episode.briefing.quest_giver, briefing)
        self.assertIn(self.episode.briefing.dialogue, briefing)

    def test_advance_to_briefing(self):
        """Test advancing from intro to briefing"""
        self.assertEqual(self.runner.state.phase, 'intro')

        self.runner.advance_to_briefing()

        self.assertEqual(self.runner.state.phase, 'briefing')

    def test_load_dungeon_success(self):
        """Test loading hand-crafted dungeon"""
        success, message = self.runner.load_dungeon()

        self.assertTrue(success, message)
        self.assertIsNotNone(self.runner.dungeon)
        self.assertEqual(self.runner.dungeon.name, "Keep of Kaldor")
        self.assertTrue(self.runner.state.dungeon_entered)
        self.assertEqual(self.runner.state.phase, 'dungeon')

    def test_load_dungeon_file_not_found(self):
        """Test loading nonexistent dungeon"""
        # Modify episode to point to nonexistent file
        self.episode.dungeon_config.file = "dungeons/nonexistent.json"

        success, message = self.runner.load_dungeon()

        self.assertFalse(success)
        self.assertIn("not found", message.lower())

    def test_create_game_state_without_dungeon(self):
        """Test creating game state before loading dungeon fails"""
        fighter = self.party.members[0]

        success, message = self.runner.create_game_state(fighter)

        self.assertFalse(success)
        self.assertIn("No dungeon loaded", message)

    def test_create_game_state_with_dungeon(self):
        """Test creating game state after loading dungeon"""
        # Load dungeon first
        self.runner.load_dungeon()
        fighter = self.party.members[0]

        success, message = self.runner.create_game_state(fighter)

        self.assertTrue(success, message)
        self.assertIsNotNone(self.runner.game_state)
        self.assertEqual(self.runner.game_state.player, fighter)
        self.assertEqual(self.runner.game_state.dungeon, self.runner.dungeon)

    def test_check_completion_no_game_state(self):
        """Test completion check without game state"""
        is_complete = self.runner.check_completion()

        self.assertFalse(is_complete)

    def test_check_completion_item_retrieved(self):
        """Test completion criteria: item retrieved"""
        # Modify episode to use item retrieval completion
        self.episode.completion_criteria.type = 'item_retrieved'
        self.episode.completion_criteria.target = 'serpent_medallion'

        # Load dungeon and create game state
        self.runner.load_dungeon()
        fighter = self.party.members[0]
        self.runner.create_game_state(fighter)

        # Should not be complete yet
        self.assertFalse(self.runner.check_completion())

        # Add the item to inventory
        # (Would need actual item creation, but test structure is here)

    def test_check_completion_location_reached(self):
        """Test completion criteria: location reached"""
        # Modify episode to use location completion
        self.episode.completion_criteria.type = 'location_reached'
        self.episode.completion_criteria.target = 'throne_room'

        # Load dungeon and create game state
        self.runner.load_dungeon()
        fighter = self.party.members[0]
        self.runner.create_game_state(fighter)

        # Should not be complete (starting at entrance)
        self.assertFalse(self.runner.check_completion())

        # Move to throne room (if we could navigate there)
        # For now, manually set current room
        throne_room = self.runner.dungeon.get_room('throne_room')
        if throne_room:
            self.runner.game_state.current_room = throne_room
            self.assertTrue(self.runner.check_completion())

    def test_complete_episode(self):
        """Test episode completion and reward application"""
        # Complete the episode
        success, message = self.runner.complete_episode()

        self.assertTrue(success)
        self.assertIn("EPISODE COMPLETE", message)
        self.assertIn(self.episode.completion_text, message)
        self.assertTrue(self.runner.state.completion_acknowledged)
        self.assertEqual(self.runner.state.phase, 'completed')

        # Check campaign was updated
        self.assertTrue(self.campaign.is_episode_completed('episode_01'))

        # Check rewards were applied
        fighter = self.party.members[0]
        self.assertGreater(fighter.xp, 0)  # XP bonus applied

        # Check episode 02 was unlocked
        self.assertIn('episode_02', self.campaign.unlocked_episodes)

        # Check story flag was set
        self.assertTrue(self.campaign.story_flags.get('found_serpent_medallion', False))

    def test_complete_episode_twice(self):
        """Test completing episode twice fails"""
        # Complete once
        self.runner.complete_episode()

        # Try to complete again
        success, message = self.runner.complete_episode()

        self.assertFalse(success)
        self.assertIn("already completed", message.lower())

    def test_get_current_phase(self):
        """Test phase tracking"""
        self.assertEqual(self.runner.get_current_phase(), 'intro')

        self.runner.advance_to_briefing()
        self.assertEqual(self.runner.get_current_phase(), 'briefing')

        self.runner.load_dungeon()
        self.assertEqual(self.runner.get_current_phase(), 'dungeon')

        self.runner.complete_episode()
        self.assertEqual(self.runner.get_current_phase(), 'completed')

    def test_is_complete(self):
        """Test completion status check"""
        self.assertFalse(self.runner.is_complete())

        self.runner.complete_episode()

        self.assertTrue(self.runner.is_complete())

    def test_full_episode_flow(self):
        """Test complete episode flow from intro to completion"""
        # 1. Start with intro
        self.assertEqual(self.runner.state.phase, 'intro')
        intro = self.runner.get_intro_text()
        self.assertIn(self.episode.title.upper(), intro.upper())

        # 2. Advance to briefing
        self.runner.advance_to_briefing()
        self.assertEqual(self.runner.state.phase, 'briefing')
        briefing = self.runner.get_briefing_text()
        self.assertIn(self.episode.briefing.dialogue, briefing)

        # 3. Load dungeon
        success, msg = self.runner.load_dungeon()
        self.assertTrue(success, msg)
        self.assertEqual(self.runner.state.phase, 'dungeon')
        self.assertIsNotNone(self.runner.dungeon)

        # 4. Create game state
        fighter = self.party.members[0]
        success, msg = self.runner.create_game_state(fighter)
        self.assertTrue(success, msg)
        self.assertIsNotNone(self.runner.game_state)

        # 5. Complete episode
        success, msg = self.runner.complete_episode()
        self.assertTrue(success, msg)
        self.assertTrue(self.runner.is_complete())
        self.assertEqual(self.runner.state.phase, 'completed')

        # 6. Verify campaign state
        self.assertTrue(self.campaign.is_episode_completed('episode_01'))
        self.assertIn('episode_02', self.campaign.unlocked_episodes)


if __name__ == '__main__':
    unittest.main()
