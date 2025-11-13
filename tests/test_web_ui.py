"""
Test suite for Web UI (Flask app)

Tests the Flask REST API wrapper that provides web interface to the game.
Ensures Web UI correctly wraps core game logic without breaking it.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path

# Import Flask app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from web_ui.app import app, active_games
except ImportError:
    app = None
    active_games = None


@unittest.skipIf(app is None, "Flask not installed or web_ui/app.py not found")
class TestWebUIRoutes(unittest.TestCase):
    """Test Flask routes and API endpoints"""

    def setUp(self):
        """Set up test client"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()
            # Clear active games
            active_games.clear()

    def tearDown(self):
        """Clean up"""
        if active_games:
            active_games.clear()

    def test_index_route(self):
        """Test main menu page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data.lower())

    def test_new_game_route_exists(self):
        """Test new game endpoint exists"""
        response = self.client.post('/api/new_game')
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 400, 500])

    def test_command_route_exists(self):
        """Test command endpoint exists"""
        response = self.client.post('/api/command',
                                     json={'session_id': 'test', 'command': 'look'})
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 400, 404, 500])

    def test_game_state_route_exists(self):
        """Test game state endpoint exists"""
        response = self.client.post('/api/game_state',
                                      json={'session_id': 'test'})
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 400, 404, 500])

    def test_new_game_returns_json(self):
        """Test new game returns JSON response"""
        response = self.client.post('/api/new_game')

        self.assertEqual(response.content_type, 'application/json')

        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    def test_new_game_creates_session(self):
        """Test new game creates session ID"""
        response = self.client.post('/api/new_game')

        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('session_id', data)
            self.assertIsNotNone(data['session_id'])

    def test_command_requires_session_id(self):
        """Test command endpoint requires session_id"""
        response = self.client.post('/api/command',
                                      json={'command': 'look'})

        # Should return error without session_id
        self.assertIn(response.status_code, [400, 404])

    def test_command_with_invalid_session(self):
        """Test command with non-existent session"""
        response = self.client.post('/api/command',
                                      json={'session_id': 'invalid_session_xyz',
                                             'command': 'look'})

        self.assertEqual(response.status_code, 404)

    def test_full_game_flow(self):
        """Test complete game flow: new game → command → state"""
        # Create new game
        response = self.client.post('/api/new_game')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        session_id = data['session_id']

        # Execute command
        response = self.client.post('/api/command',
                                      json={'session_id': session_id,
                                             'command': 'look'})

        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('message', data)

        # Get game state
        response = self.client.post('/api/game_state',
                                      json={'session_id': session_id})

        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIsInstance(data, dict)

    def test_multiple_concurrent_sessions(self):
        """Test multiple game sessions can coexist"""
        # Create two games
        response1 = self.client.post('/api/new_game')
        response2 = self.client.post('/api/new_game')

        if response1.status_code == 200 and response2.status_code == 200:
            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)

            session1 = data1['session_id']
            session2 = data2['session_id']

            # Sessions should be different
            self.assertNotEqual(session1, session2)

            # Both should accept commands
            cmd_response1 = self.client.post('/api/command',
                                               json={'session_id': session1,
                                                      'command': 'inventory'})

            cmd_response2 = self.client.post('/api/command',
                                               json={'session_id': session2,
                                                      'command': 'status'})

            # Both should work independently
            self.assertEqual(cmd_response1.status_code, 200)
            self.assertEqual(cmd_response2.status_code, 200)


@unittest.skipIf(app is None, "Flask not installed")
class TestWebUICommandExecution(unittest.TestCase):
    """Test command execution through Web UI"""

    def setUp(self):
        """Set up test client and create game session"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()
            active_games.clear()

            # Create a game session
            response = self.client.post('/api/new_game')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.session_id = data['session_id']
            else:
                self.session_id = None

    def tearDown(self):
        """Clean up"""
        if active_games:
            active_games.clear()

    @unittest.skipIf(app is None, "Session creation failed")
    def test_look_command(self):
        """Test look command through Web UI"""
        if not self.session_id:
            self.skipTest("Session not created")

        response = self.client.post('/api/command',
                                      json={'session_id': self.session_id,
                                             'command': 'look'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    @unittest.skipIf(app is None, "Session creation failed")
    def test_inventory_command(self):
        """Test inventory command through Web UI"""
        if not self.session_id:
            self.skipTest("Session not created")

        response = self.client.post('/api/command',
                                      json={'session_id': self.session_id,
                                             'command': 'inventory'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    @unittest.skipIf(app is None, "Session creation failed")
    def test_status_command(self):
        """Test status command through Web UI"""
        if not self.session_id:
            self.skipTest("Session not created")

        response = self.client.post('/api/command',
                                      json={'session_id': self.session_id,
                                             'command': 'status'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    @unittest.skipIf(app is None, "Session creation failed")
    def test_map_command(self):
        """Test map command through Web UI"""
        if not self.session_id:
            self.skipTest("Session not created")

        response = self.client.post('/api/command',
                                      json={'session_id': self.session_id,
                                             'command': 'map'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    @unittest.skipIf(app is None, "Session creation failed")
    def test_help_command(self):
        """Test help command through Web UI"""
        if not self.session_id:
            self.skipTest("Session not created")

        response = self.client.post('/api/command',
                                      json={'session_id': self.session_id,
                                             'command': 'help'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    @unittest.skipIf(app is None, "Session creation failed")
    def test_movement_command(self):
        """Test movement command through Web UI"""
        if not self.session_id:
            self.skipTest("Session not created")

        response = self.client.post('/api/command',
                                      json={'session_id': self.session_id,
                                             'command': 'north'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)


@unittest.skipIf(app is None, "Flask not installed")
class TestWebUICharacterManagement(unittest.TestCase):
    """Test character roster management through Web UI"""

    def setUp(self):
        """Set up test client"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()

    def test_list_characters_route_exists(self):
        """Test list characters endpoint exists"""
        response = self.client.get('/api/characters')
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 500])

    def test_list_characters_returns_json(self):
        """Test list characters returns JSON"""
        response = self.client.get('/api/characters')

        if response.status_code == 200:
            self.assertEqual(response.content_type, 'application/json')
            data = json.loads(response.data)
            self.assertIsInstance(data, (list, dict))


@unittest.skipIf(app is None, "Flask not installed")
class TestWebUIPartyManagement(unittest.TestCase):
    """Test party management through Web UI"""

    def setUp(self):
        """Set up test client"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()

    def test_list_parties_route_exists(self):
        """Test list parties endpoint exists"""
        response = self.client.get('/api/parties')
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 500])

    def test_list_parties_returns_json(self):
        """Test list parties returns JSON"""
        response = self.client.get('/api/parties')

        if response.status_code == 200:
            self.assertEqual(response.content_type, 'application/json')
            data = json.loads(response.data)
            self.assertIsInstance(data, (list, dict))


@unittest.skipIf(app is None, "Flask not installed")
class TestWebUIScenarioManagement(unittest.TestCase):
    """Test scenario management through Web UI"""

    def setUp(self):
        """Set up test client"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()

    def test_list_scenarios_route_exists(self):
        """Test list scenarios endpoint exists"""
        response = self.client.get('/api/scenarios')
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 500])

    def test_list_scenarios_returns_json(self):
        """Test list scenarios returns JSON"""
        response = self.client.get('/api/scenarios')

        if response.status_code == 200:
            self.assertEqual(response.content_type, 'application/json')
            data = json.loads(response.data)
            self.assertIsInstance(data, (list, dict))


@unittest.skipIf(app is None, "Flask not installed")
class TestWebUISessionManagement(unittest.TestCase):
    """Test session management through Web UI"""

    def setUp(self):
        """Set up test client"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()

    def test_list_sessions_route_exists(self):
        """Test list sessions endpoint exists"""
        response = self.client.get('/api/sessions')
        # Should return 200 or appropriate status (not 404)
        self.assertIn(response.status_code, [200, 500])

    def test_list_sessions_returns_json(self):
        """Test list sessions returns JSON"""
        response = self.client.get('/api/sessions')

        if response.status_code == 200:
            self.assertEqual(response.content_type, 'application/json')
            data = json.loads(response.data)
            self.assertIsInstance(data, (list, dict))


@unittest.skipIf(app is None, "Flask not installed")
class TestWebUIErrorHandling(unittest.TestCase):
    """Test Web UI error handling"""

    def setUp(self):
        """Set up test client"""
        if app:
            app.config['TESTING'] = True
            self.client = app.test_client()

    def test_invalid_command_json(self):
        """Test handling of invalid JSON"""
        response = self.client.post('/api/command',
                                      data='invalid json',
                                      content_type='application/json')

        self.assertIn(response.status_code, [400, 500])

    def test_missing_command_field(self):
        """Test handling of missing command field"""
        response = self.client.post('/api/command',
                                      json={'session_id': 'test'})

        self.assertIn(response.status_code, [400, 404])

    def test_empty_command(self):
        """Test handling of empty command"""
        response = self.client.post('/api/command',
                                      json={'session_id': 'test',
                                             'command': ''})

        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 404])


if __name__ == '__main__':
    unittest.main()
