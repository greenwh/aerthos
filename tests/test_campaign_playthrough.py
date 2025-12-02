"""
Automated Campaign Playthrough Tests

These tests verify that all 10 episodes can be completed end-to-end without
"monster not found" or "item not found" errors. This automates the playthrough
testing described in SESSION_ROADMAP.md Task 4.

Tests check:
1. All episodes load correctly
2. All dungeons load successfully
3. All referenced monsters exist in monsters.json
4. All reward items exist in item data files
5. Episode completion flow works for each episode
"""

import unittest
import json
from pathlib import Path
from aerthos.campaign.episode import Episode
from aerthos.campaign.campaign import Campaign
from aerthos.campaign.episode_runner import EpisodeRunner
from aerthos.entities.party import Party
from aerthos.entities.player import PlayerCharacter
from aerthos.engine.game_state import GameData


class TestCampaignPlaythrough(unittest.TestCase):
    """Test complete campaign playthrough for all 10 episodes"""

    @classmethod
    def setUpClass(cls):
        """Load game data once for all tests"""
        cls.game_data = GameData.load_all()
        cls.all_episodes = [
            'episode_01', 'episode_02', 'episode_03', 'episode_04', 'episode_05',
            'episode_06', 'episode_07', 'episode_08', 'episode_09', 'episode_10'
        ]

    def setUp(self):
        """Create test party for each test"""
        # Create balanced party (Fighter, Cleric, Magic-User, Thief)
        self.fighter = PlayerCharacter(
            name="Test Fighter",
            char_class="Fighter",
            race="Human",
            level=3,
            strength=16,
            dexterity=12,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10,
            hp_current=24,
            hp_max=24,
            ac=3,
            thac0=18,
            gold=500
        )

        self.cleric = PlayerCharacter(
            name="Test Cleric",
            char_class="Cleric",
            race="Human",
            level=3,
            strength=14,
            dexterity=10,
            constitution=12,
            intelligence=10,
            wisdom=16,
            charisma=12,
            hp_current=18,
            hp_max=18,
            ac=4,
            thac0=18,
            gold=500
        )

        self.magic_user = PlayerCharacter(
            name="Test Magic-User",
            char_class="Magic-User",
            race="Elf",
            level=3,
            strength=10,
            dexterity=14,
            constitution=12,
            intelligence=16,
            wisdom=12,
            charisma=10,
            hp_current=12,
            hp_max=12,
            ac=6,
            thac0=19,
            gold=500
        )

        self.thief = PlayerCharacter(
            name="Test Thief",
            char_class="Thief",
            race="Halfling",
            level=3,
            strength=12,
            dexterity=16,
            constitution=12,
            intelligence=12,
            wisdom=10,
            charisma=10,
            hp_current=15,
            hp_max=15,
            ac=5,
            thac0=19,
            gold=500
        )

        self.party = Party(members=[self.fighter, self.cleric, self.magic_user, self.thief])

    def test_all_episodes_load(self):
        """Test that all 10 episodes load without errors"""
        for episode_id in self.all_episodes:
            with self.subTest(episode=episode_id):
                episode = Episode.load(episode_id)
                self.assertIsNotNone(episode, f"{episode_id} failed to load")
                self.assertEqual(episode.id, episode_id)
                self.assertIsNotNone(episode.title)
                self.assertIsNotNone(episode.intro_text)
                self.assertIsNotNone(episode.dungeon_config)

    def test_all_dungeons_load(self):
        """Test that all episode dungeons load successfully"""
        for episode_id in self.all_episodes:
            with self.subTest(episode=episode_id):
                episode = Episode.load(episode_id)

                # Create minimal campaign and runner
                campaign = Campaign(
                    id='test',
                    name='Test',
                    description='Test',
                    party_id='test',
                    current_episode_id=episode_id,
                    current_hub_id=episode.hub_id,
                    unlocked_episodes=[episode_id],
                    unlocked_hubs=[episode.hub_id]
                )

                runner = EpisodeRunner(episode, campaign, self.party)
                success, message = runner.load_dungeon()

                self.assertTrue(success, f"{episode_id} dungeon failed to load: {message}")
                self.assertIsNotNone(runner.dungeon)

    def test_all_monsters_exist(self):
        """Test that all monsters referenced in episodes exist in monsters.json"""
        missing_monsters = set()
        monster_references = {}  # Track which episode references which monster

        for episode_id in self.all_episodes:
            episode = Episode.load(episode_id)

            # Create runner to load dungeon
            campaign = Campaign(
                id='test',
                name='Test',
                description='Test',
                party_id='test',
                current_episode_id=episode_id,
                current_hub_id=episode.hub_id
            )

            runner = EpisodeRunner(episode, campaign, self.party)
            success, _ = runner.load_dungeon()

            if success and runner.dungeon:
                # Check all monsters in all rooms
                for room_id, room in runner.dungeon.rooms.items():
                    if hasattr(room, 'encounters'):
                        for encounter in room.encounters:
                            if encounter.get('type') == 'combat' and 'monsters' in encounter:
                                for monster_id in encounter['monsters']:
                                    # Check if monster exists in game data
                                    if monster_id not in self.game_data.monsters:
                                        missing_monsters.add(monster_id)
                                        if episode_id not in monster_references:
                                            monster_references[episode_id] = []
                                        monster_references[episode_id].append(
                                            f"{monster_id} (room: {room_id})"
                                        )

        # Report any missing monsters
        if missing_monsters:
            error_msg = f"\n\nMissing monsters found:\n"
            for episode_id, monsters in sorted(monster_references.items()):
                error_msg += f"\n{episode_id}:\n"
                for monster in monsters:
                    error_msg += f"  - {monster}\n"

            self.fail(error_msg)

    def test_all_reward_items_exist(self):
        """Test that all reward items exist in item data files"""
        missing_items = set()
        item_references = {}  # Track which episode rewards which item

        for episode_id in self.all_episodes:
            episode = Episode.load(episode_id)

            if hasattr(episode.rewards, 'items') and episode.rewards.items:
                for item_id in episode.rewards.items:
                    # Check if item exists (try to create it)
                    try:
                        # Items are loaded from MagicItemFactory
                        from aerthos.systems.magic_item_factory import MagicItemFactory
                        factory = MagicItemFactory()

                        # Check if item exists in base items
                        if item_id not in factory.base_items:
                            missing_items.add(item_id)
                            if episode_id not in item_references:
                                item_references[episode_id] = []
                            item_references[episode_id].append(item_id)

                    except Exception as e:
                        missing_items.add(item_id)
                        if episode_id not in item_references:
                            item_references[episode_id] = []
                        item_references[episode_id].append(f"{item_id} (error: {e})")

        # Report any missing items
        if missing_items:
            error_msg = f"\n\nMissing reward items found:\n"
            for episode_id, items in sorted(item_references.items()):
                error_msg += f"\n{episode_id}:\n"
                for item in items:
                    error_msg += f"  - {item}\n"

            self.fail(error_msg)

    def test_episode_01_playthrough(self):
        """Test Episode 1: The Goblin Refugees - complete flow"""
        self._test_episode_playthrough('episode_01', 'oakhaven')

    def test_episode_02_playthrough(self):
        """Test Episode 2: Oakhaven Sewers - complete flow"""
        self._test_episode_playthrough('episode_02', 'oakhaven')

    def test_episode_03_playthrough(self):
        """Test Episode 3: Silas's Warehouse - complete flow"""
        self._test_episode_playthrough('episode_03', 'oakhaven')

    def test_episode_04_playthrough(self):
        """Test Episode 4: Duergar Hold - complete flow"""
        self._test_episode_playthrough('episode_04', 'oakhaven')

    def test_episode_05_playthrough(self):
        """Test Episode 5: Sunken Temple - complete flow"""
        self._test_episode_playthrough('episode_05', 'ironfast_outpost')

    def test_episode_06_playthrough(self):
        """Test Episode 6: Scorched Fortress - complete flow"""
        self._test_episode_playthrough('episode_06', 'mires_edge')

    def test_episode_07_playthrough(self):
        """Test Episode 7: Drowned Ruins - complete flow (waterbreathing required)"""
        self._test_episode_playthrough('episode_07', 'coastal_haven')

    def test_episode_08_playthrough(self):
        """Test Episode 8: Eldoria Catacombs - complete flow"""
        self._test_episode_playthrough('episode_08', 'eldoria')

    def test_episode_09_playthrough(self):
        """Test Episode 9: Elemental Chaos - complete flow"""
        self._test_episode_playthrough('episode_09', 'eldoria')

    def test_episode_10_playthrough(self):
        """Test Episode 10: Serpent Temple - final boss"""
        self._test_episode_playthrough('episode_10', 'eldoria')

    def _test_episode_playthrough(self, episode_id, hub_id):
        """Helper method to test complete episode flow"""
        # Load episode
        episode = Episode.load(episode_id)
        self.assertIsNotNone(episode, f"{episode_id} failed to load")

        # Create campaign with this episode unlocked
        campaign = Campaign(
            id=f'test-{episode_id}',
            name=f'Test Campaign - {episode_id}',
            description='Test',
            party_id='test-party',
            current_episode_id=episode_id,
            current_hub_id=hub_id,
            unlocked_episodes=[episode_id],
            unlocked_hubs=[hub_id]
        )

        # Create episode runner
        runner = EpisodeRunner(episode, campaign, self.party)

        # 1. Check intro phase
        self.assertEqual(runner.state.phase, 'intro')
        intro = runner.get_intro_text()
        self.assertIn(episode.title.upper(), intro.upper())

        # 2. Advance to briefing
        runner.advance_to_briefing()
        self.assertEqual(runner.state.phase, 'briefing')
        briefing = runner.get_briefing_text()
        self.assertIn(episode.briefing.dialogue, briefing)

        # 3. Load dungeon
        success, msg = runner.load_dungeon()
        self.assertTrue(success, f"{episode_id} dungeon load failed: {msg}")
        self.assertEqual(runner.state.phase, 'dungeon')
        self.assertIsNotNone(runner.dungeon)

        # 4. Create game state
        success, msg = runner.create_game_state(self.fighter)
        self.assertTrue(success, f"{episode_id} game state creation failed: {msg}")
        self.assertIsNotNone(runner.game_state)

        # 5. Complete episode (simulate completion)
        # Note: We're not actually playing through combat, just testing the flow
        success, msg = runner.complete_episode()
        self.assertTrue(success, f"{episode_id} completion failed: {msg}")
        self.assertTrue(runner.is_complete())
        self.assertEqual(runner.state.phase, 'completed')

        # 6. Verify campaign state updated
        self.assertTrue(campaign.is_episode_completed(episode_id))

        # 7. Verify XP/gold rewards applied
        # Party leader should have received XP bonus
        if episode.rewards.xp_bonus > 0:
            self.assertGreater(self.fighter.xp, 0, f"{episode_id} XP reward not applied")

    def test_campaign_progression(self):
        """Test that episodes unlock correctly in sequence"""
        # Start with Episode 1
        campaign = Campaign(
            id='progression-test',
            name='Progression Test',
            description='Test',
            party_id='test',
            current_episode_id='episode_01',
            current_hub_id='oakhaven',
            unlocked_episodes=['episode_01'],
            unlocked_hubs=['oakhaven']
        )

        # Verify only Episode 1 is unlocked
        self.assertTrue(campaign.is_episode_unlocked('episode_01'))
        self.assertFalse(campaign.is_episode_unlocked('episode_02'))

        # Complete Episode 1
        episode_01 = Episode.load('episode_01')
        runner = EpisodeRunner(episode_01, campaign, self.party)
        runner.load_dungeon()
        runner.create_game_state(self.fighter)
        runner.complete_episode()

        # Verify Episode 2 is now unlocked
        self.assertTrue(campaign.is_episode_unlocked('episode_02'))
        self.assertTrue(campaign.is_episode_completed('episode_01'))

        # Verify story flags are set
        self.assertTrue(campaign.get_story_flag('found_serpent_medallion'))
        self.assertTrue(campaign.get_story_flag('goblin_threat_ended'))


if __name__ == '__main__':
    unittest.main()
