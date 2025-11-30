"""
Tests for CityHub class
"""

import unittest
from pathlib import Path
from aerthos.campaign.city_hub import CityHub
from aerthos.campaign.campaign import Campaign


class TestCityHub(unittest.TestCase):
    """Test CityHub loading and functionality"""

    def test_hub_loading(self):
        """Test loading city hub from JSON"""
        hub = CityHub.load('oakhaven')

        self.assertEqual(hub.id, 'oakhaven')
        self.assertEqual(hub.name, 'Oakhaven')
        self.assertEqual(hub.theme, 'Frontier Town')
        self.assertEqual(hub.region, 'Verdant Heartlands')

    def test_hub_shops(self):
        """Test shop configuration"""
        hub = CityHub.load('oakhaven')

        self.assertEqual(len(hub.shops), 1)

        shop = hub.shops[0]
        self.assertEqual(shop.id, 'silas_shop')
        self.assertEqual(shop.name, "Silas's Equipment Emporium")
        self.assertEqual(shop.type, 'general')
        self.assertEqual(shop.buy_rate, 0.4)
        self.assertEqual(shop.price_modifier, 1.5)
        self.assertIn('longsword', shop.inventory)

    def test_hub_inn(self):
        """Test inn configuration"""
        hub = CityHub.load('oakhaven')

        self.assertIsNotNone(hub.inn)
        self.assertEqual(hub.inn.id, 'dirty_mug')
        self.assertEqual(hub.inn.name, 'The Dirty Mug')
        self.assertEqual(hub.inn.rate_per_night, 10)
        self.assertIn('rest', hub.inn.services)
        self.assertIn('episode_01', hub.inn.rumors_by_episode)

    def test_hub_temple(self):
        """Test temple configuration"""
        hub = CityHub.load('oakhaven')

        self.assertIsNotNone(hub.temple)
        self.assertEqual(hub.temple.id, 'temple_of_light')
        self.assertEqual(hub.temple.name, 'Temple of Light')
        self.assertEqual(hub.temple.alignment, 'Lawful Good')
        self.assertIn('cure_light', hub.temple.services)

    def test_hub_npcs(self):
        """Test NPC configuration"""
        hub = CityHub.load('oakhaven')

        self.assertIn('silas', hub.npcs)
        self.assertIn('the_guide', hub.npcs)

        silas = hub.npcs['silas']
        self.assertEqual(silas.name, 'Silas')
        self.assertEqual(silas.role, 'Merchant')
        self.assertEqual(silas.alignment, 'Lawful Evil')
        self.assertIn('greeting', silas.dialogue)

    def test_hub_special_rules(self):
        """Test special rules"""
        hub = CityHub.load('oakhaven')

        self.assertEqual(hub.special_rules['gate_toll'], 5)
        self.assertEqual(hub.special_rules['currency_exchange_rate'], 0.9)
        self.assertEqual(hub.special_rules['inflation_multiplier'], 1.5)

    def test_hub_available_episodes(self):
        """Test available episodes filtering"""
        hub = CityHub.load('oakhaven')

        # Create campaign with some unlocked episodes
        campaign = Campaign(
            id='test',
            name='Test',
            description='Test',
            party_id='test',
            current_episode_id='episode_01',
            current_hub_id='oakhaven',
            unlocked_episodes=['episode_01', 'episode_02']
        )

        available = hub.get_available_episodes(campaign)

        # Should only return unlocked episodes that are in available_quests
        self.assertIn('episode_01', available)
        self.assertIn('episode_02', available)
        self.assertNotIn('episode_03', available)  # Not unlocked

    def test_hub_serialization(self):
        """Test hub serialization"""
        hub = CityHub.load('oakhaven')

        # Serialize
        data = hub.to_json()

        # Deserialize
        restored = CityHub.from_json(data)

        # Verify
        self.assertEqual(restored.id, hub.id)
        self.assertEqual(restored.name, hub.name)
        self.assertEqual(len(restored.shops), len(hub.shops))
        self.assertEqual(restored.inn.name, hub.inn.name)


if __name__ == '__main__':
    unittest.main()
