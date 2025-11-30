"""
Tests for HubMenuSystem
"""

import unittest
from aerthos.campaign.hub_menu import HubMenuSystem, HubMenuResult
from aerthos.campaign.campaign import Campaign
from aerthos.campaign.city_hub import CityHub
from aerthos.entities.party import Party
from aerthos.entities.player import PlayerCharacter


class TestHubMenuSystem(unittest.TestCase):
    """Test HubMenuSystem functionality"""

    def setUp(self):
        """Create test campaign and party"""
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

        # Create menu system
        self.menu = HubMenuSystem(self.campaign, self.party)

    def test_menu_system_initialization(self):
        """Test menu system initializes correctly"""
        self.assertIsNotNone(self.menu)
        self.assertEqual(self.menu.campaign, self.campaign)
        self.assertEqual(self.menu.party, self.party)
        self.assertIsNotNone(self.menu.current_hub)
        self.assertEqual(self.menu.current_hub.id, 'oakhaven')

    def test_display_hub_menu(self):
        """Test menu display generation"""
        menu_text = self.menu.display_hub_menu()

        self.assertIsInstance(menu_text, str)
        self.assertIn('OAKHAVEN', menu_text.upper())
        self.assertIn('CAMPAIGN:', menu_text.upper())
        self.assertIn('Save & Exit', menu_text)

    def test_get_menu_options(self):
        """Test menu options generation"""
        options = self.menu.get_menu_options()

        self.assertIsInstance(options, list)
        self.assertGreater(len(options), 0)

        # Should have inn, shop, temple, etc.
        option_ids = [opt.id for opt in options]
        self.assertIn('inn', option_ids)
        self.assertIn('temple', option_ids)

        # Should have travel and party management
        actions = [opt.action for opt in options]
        self.assertIn('travel_menu', actions)
        self.assertIn('manage_party', actions)

    def test_handle_exit_choice(self):
        """Test exit (choice 0) handling"""
        result = self.menu.handle_choice(0)

        self.assertIsInstance(result, HubMenuResult)
        self.assertTrue(result.success)
        self.assertEqual(result.next_state, 'save_and_exit')

    def test_handle_invalid_choice(self):
        """Test invalid choice handling"""
        result = self.menu.handle_choice(999)

        self.assertIsInstance(result, HubMenuResult)
        self.assertFalse(result.success)
        self.assertEqual(result.next_state, 'hub')

    def test_handle_valid_choice(self):
        """Test valid menu choice"""
        options = self.menu.get_menu_options()

        # Try first option (whatever it is)
        result = self.menu.handle_choice(1)

        self.assertIsInstance(result, HubMenuResult)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.next_state)

    def test_travel_option_exists(self):
        """Test travel menu option is available"""
        options = self.menu.get_menu_options()

        travel_options = [opt for opt in options if opt.action == 'travel_menu']
        self.assertEqual(len(travel_options), 1)

        travel_option = travel_options[0]
        self.assertIn('episode_01', travel_option.data.get('available_episodes', []))

    def test_get_travel_destinations(self):
        """Test travel destination listing"""
        destinations = self.menu.get_travel_destinations()

        self.assertIsInstance(destinations, list)
        self.assertGreater(len(destinations), 0)

        # Check first destination structure
        dest = destinations[0]
        self.assertIn('episode_id', dest)
        self.assertIn('title', dest)
        self.assertIn('status', dest)

    def test_completed_episode_status(self):
        """Test completed episodes show correct status"""
        # Complete episode 01
        self.campaign.complete_episode('episode_01', {'unlocks': ['episode_02']})

        # Reload menu
        self.menu = HubMenuSystem(self.campaign, self.party)

        destinations = self.menu.get_travel_destinations()

        # Find episode 01
        ep01 = next((d for d in destinations if d['episode_id'] == 'episode_01'), None)
        self.assertIsNotNone(ep01)
        self.assertEqual(ep01['status'], 'COMPLETED')


if __name__ == '__main__':
    unittest.main()
