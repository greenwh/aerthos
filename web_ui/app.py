"""
Flask web UI for Aerthos - Gold Box style interface

Run with: python3 web_ui/app.py
Then visit: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, session
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from aerthos.world.dungeon import Dungeon
from aerthos.engine.game_state import GameState, GameData
from aerthos.entities.player import PlayerCharacter
from aerthos.entities.party import Party
from aerthos.ui.party_creation import PartyCreator
from aerthos.ui.character_creation import CharacterCreator, ManualCharacterCreator
from aerthos.generator.dungeon_generator import DungeonGenerator
from aerthos.generator.config import DungeonConfig, STANDARD_DUNGEON
from aerthos.storage.character_roster import CharacterRoster
from aerthos.storage.party_manager import PartyManager
from aerthos.storage.scenario_library import ScenarioLibrary
from aerthos.storage.session_manager import SessionManager
from aerthos.campaign.campaign_manager import CampaignManager
from aerthos.campaign.campaign import Campaign
from aerthos.campaign.episode import Episode
from aerthos.campaign.episode_runner import EpisodeRunner
from aerthos.campaign.hub_menu import HubMenuSystem

app = Flask(__name__)
app.secret_key = 'aerthos_secret_key_change_in_production'

# Store active game sessions (in production, use proper session management)
active_games = {}


@app.route('/')
def index():
    """Main menu"""
    return render_template('index.html')


@app.route('/game')
def game():
    """Game interface"""
    return render_template('game.html')


@app.route('/character_creation')
def character_creation():
    """Character creation interface"""
    return render_template('character_creation.html')


@app.route('/character_roster')
def character_roster():
    """Character roster management"""
    return render_template('character_roster.html')


@app.route('/manual_import')
def manual_import():
    """Manual character import interface"""
    return render_template('manual_import.html')


@app.route('/party_manager')
def party_manager():
    """Party manager"""
    return render_template('party_builder.html')


@app.route('/scenario_library')
def scenario_library():
    """Scenario library"""
    return render_template('scenario_library.html')


@app.route('/session_manager')
def session_manager():
    """Session manager"""
    return render_template('session_manager.html')


@app.route('/campaign_manager')
def campaign_manager():
    """Campaign manager"""
    return render_template('campaign_manager.html')


@app.route('/campaign/<campaign_id>/hub')
def campaign_hub(campaign_id):
    """Campaign hub page"""
    return render_template('campaign_hub.html')


@app.route('/campaign/<campaign_id>/episodes')
def campaign_episodes(campaign_id):
    """Campaign episodes page"""
    return render_template('campaign_episodes.html')


# ============================================================================
# CAMPAIGN API ROUTES
# ============================================================================

@app.route('/api/campaigns/list', methods=['GET'])
def list_campaigns():
    """List all campaigns"""
    try:
        campaign_mgr = CampaignManager()
        campaigns = campaign_mgr.list_campaigns()

        # Convert Campaign objects to JSON-serializable dicts
        campaigns_data = []
        for camp in campaigns:
            campaigns_data.append({
                'id': camp.id,
                'name': camp.name,
                'description': camp.description,
                'party_id': camp.party_id,
                'current_hub_id': camp.current_hub_id,
                'current_episode_id': camp.current_episode_id,
                'completed_episodes': camp.completed_episodes,
                'unlocked_episodes': camp.unlocked_episodes,
                'unlocked_hubs': camp.unlocked_hubs,
                'story_flags': camp.story_flags,
                'reputation': camp.reputation
            })

        return jsonify({
            'success': True,
            'campaigns': campaigns_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/create', methods=['POST'])
def create_campaign():
    """Create a new campaign - IDENTICAL to CLI"""
    try:
        data = request.json
        template_id = data.get('template_id', 'serpents_shadow')
        party_id = data.get('party_id')

        if not party_id:
            return jsonify({
                'success': False,
                'error': 'Party ID required'
            }), 400

        # IDENTICAL call as CLI: campaign_mgr.create_campaign()
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.create_campaign(template_id, party_id)
        campaign_mgr.save_campaign(campaign)

        return jsonify({
            'success': True,
            'message': f"Campaign '{campaign.name}' created!",
            'campaign_id': campaign.id,
            'campaign': {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'current_hub_id': campaign.current_hub_id
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/load', methods=['GET'])
def load_campaign(campaign_id):
    """Load campaign details"""
    try:
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        if not campaign:
            return jsonify({
                'success': False,
                'error': 'Campaign not found'
            }), 404

        return jsonify({
            'success': True,
            'campaign': {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'party_id': campaign.party_id,
                'current_hub_id': campaign.current_hub_id,
                'current_episode_id': campaign.current_episode_id,
                'completed_episodes': campaign.completed_episodes,
                'unlocked_episodes': campaign.unlocked_episodes,
                'unlocked_hubs': campaign.unlocked_hubs,
                'story_flags': campaign.story_flags,
                'reputation': campaign.reputation
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/delete', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete a campaign"""
    try:
        campaign_mgr = CampaignManager()
        campaign_mgr.delete_campaign(campaign_id)

        return jsonify({
            'success': True,
            'message': 'Campaign deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/hub_menu', methods=['GET'])
def get_hub_menu(campaign_id):
    """Get hub menu for campaign - IDENTICAL to CLI"""
    try:
        # Load campaign
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        if not campaign:
            return jsonify({
                'success': False,
                'error': 'Campaign not found'
            }), 404

        # Load party
        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        if not party_data:
            return jsonify({
                'success': False,
                'error': 'Party not found'
            }), 404

        # Create Party object from party data
        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # IDENTICAL call as CLI: HubMenuSystem()
        hub_menu = HubMenuSystem(campaign, party)
        menu_text = hub_menu.display_hub_menu()
        options = hub_menu.get_menu_options()

        # Convert options to JSON
        options_data = []
        for i, opt in enumerate(options, 1):
            options_data.append({
                'number': i,
                'id': opt.id,
                'name': opt.name,
                'description': opt.description,
                'action': opt.action,
                'data': opt.data if opt.data else {}
            })

        return jsonify({
            'success': True,
            'menu_text': menu_text,
            'options': options_data,
            'campaign': {
                'id': campaign.id,
                'name': campaign.name,
                'current_hub_id': campaign.current_hub_id
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/episodes/list', methods=['GET'])
def list_episodes(campaign_id):
    """Get available episodes for campaign - IDENTICAL to CLI"""
    try:
        # Load campaign and party (same as CLI)
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # IDENTICAL call as CLI: hub_menu.get_travel_destinations()
        hub_menu = HubMenuSystem(campaign, party)
        destinations = hub_menu.get_travel_destinations()

        return jsonify({
            'success': True,
            'episodes': destinations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/episodes/<episode_id>/start', methods=['POST'])
def start_episode(campaign_id, episode_id):
    """Start an episode - IDENTICAL to CLI"""
    try:
        # Load campaign and party (same pattern as CLI)
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # IDENTICAL calls as CLI: Episode.load(), EpisodeRunner()
        episode = Episode.load(episode_id)
        runner = EpisodeRunner(episode, campaign, party)

        # Get intro and briefing
        intro_text = runner.get_intro_text()
        briefing_text = runner.get_briefing_text()

        # Load dungeon
        success, message = runner.load_dungeon()

        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 500

        return jsonify({
            'success': True,
            'episode': {
                'id': episode.id,
                'title': episode.title,
                'intro_text': intro_text,
                'briefing_text': briefing_text,
                'dungeon_name': runner.dungeon.name
            },
            'message': 'Episode ready to start'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/episodes/<episode_id>/complete', methods=['POST'])
def complete_episode(campaign_id, episode_id):
    """Complete an episode - IDENTICAL to CLI"""
    try:
        # Load campaign and party
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # IDENTICAL calls as CLI
        episode = Episode.load(episode_id)
        runner = EpisodeRunner(episode, campaign, party)

        # Complete episode
        success, completion_message = runner.complete_episode()

        if success:
            # Save campaign (same as CLI)
            campaign_mgr.save_campaign(campaign)

            return jsonify({
                'success': True,
                'message': completion_message,
                'campaign': {
                    'completed_episodes': campaign.completed_episodes,
                    'unlocked_episodes': campaign.unlocked_episodes
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': completion_message
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/episodes/<episode_id>/dungeon/init', methods=['POST'])
def init_episode_dungeon(campaign_id, episode_id):
    """Initialize dungeon game state for episode - IDENTICAL to CLI"""
    try:
        data = request.json
        session_id = data.get('session_id')
        character_index = data.get('character_index', 0)

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session_id provided'
            }), 400

        # Load campaign and party (same as CLI)
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # IDENTICAL calls as CLI: Episode.load(), EpisodeRunner()
        episode = Episode.load(episode_id)
        runner = EpisodeRunner(episode, campaign, party)

        # Load dungeon (same as CLI)
        success, message = runner.load_dungeon()
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 500

        # Select active character (same as CLI)
        if character_index < 0 or character_index >= len(party.members):
            character_index = 0

        active_character = party.members[character_index]

        if not active_character.is_alive:
            return jsonify({
                'success': False,
                'error': f'{active_character.name} is dead and cannot explore!'
            }), 400

        # IDENTICAL calls as CLI: create_game_state()
        success, msg = runner.create_game_state(active_character)
        if not success:
            return jsonify({
                'success': False,
                'error': msg
            }), 500

        # Store game state with campaign/episode metadata
        game_state = runner.game_state
        game_state.party = party
        game_state.campaign_id = campaign_id
        game_state.episode_id = episode_id
        game_state.episode_runner = runner

        active_games[session_id] = game_state

        return jsonify({
            'success': True,
            'message': f'Entering {runner.dungeon.name}...',
            'state': get_game_state_json(game_state),
            'active_character': character_index
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/episodes/<episode_id>/check_completion', methods=['POST'])
def check_episode_completion(campaign_id, episode_id):
    """Check if episode completion criteria are met"""
    try:
        data = request.json
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': 'No session_id provided'
            }), 400

        game_state = active_games.get(session_id)
        if not game_state:
            return jsonify({
                'success': False,
                'error': 'No active game'
            }), 400

        # Get episode runner from game state
        if not hasattr(game_state, 'episode_runner'):
            return jsonify({
                'success': False,
                'error': 'Not an episode game'
            }), 400

        runner = game_state.episode_runner

        # Check completion (same as CLI)
        is_complete = runner.check_completion()

        return jsonify({
            'success': True,
            'is_complete': is_complete,
            'episode_id': episode_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/inn/rest', methods=['POST'])
def inn_rest(campaign_id):
    """Rest party at inn - IDENTICAL to CLI"""
    try:
        # Get request data
        data = request.json
        nights = data.get('nights', 1)

        # Load campaign and party
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # Get inn config from hub
        from aerthos.campaign.city_hub import CityHub
        hub = CityHub.load(campaign.current_hub_id)
        inn_config = hub.inn

        if not inn_config:
            return jsonify({
                'success': False,
                'error': 'No inn available in this hub'
            }), 400

        # IDENTICAL calls as CLI
        from aerthos.campaign.hub_interfaces import InnInterface
        from aerthos.world.inn import Inn

        inn = Inn(name=inn_config.name, rate_per_night=inn_config.rate_per_night)
        inn_interface = InnInterface(inn, party, rate_per_night=inn_config.rate_per_night)

        success, message = inn_interface.rest(nights)

        if success:
            # Save campaign (same as CLI)
            campaign_mgr.save_campaign(campaign)

            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/shop/buy', methods=['POST'])
def shop_buy(campaign_id):
    """Buy item from shop - IDENTICAL to CLI"""
    try:
        # Get request data
        data = request.json
        item_id = data.get('item_id')
        shop_id = data.get('shop_id')
        character_index = data.get('character_index', 0)

        # Load campaign and party
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # Get shop config from hub
        from aerthos.campaign.city_hub import CityHub
        hub = CityHub.load(campaign.current_hub_id)

        shop_config = None
        for shop in hub.shops:
            if shop.id == shop_id:
                shop_config = shop
                break

        if not shop_config:
            return jsonify({
                'success': False,
                'error': 'Shop not found'
            }), 404

        # IDENTICAL calls as CLI
        from aerthos.campaign.hub_interfaces import ShopInterface
        from aerthos.world.shop import Shop

        # Build shop data dict from shop_config
        game_data = GameData.load_all()
        shop_data = {
            'name': shop_config.name,
            'type': shop_config.type,
            'description': shop_config.specialty,
            'items': []
        }

        # Add items from inventory with prices from game_data
        for item_id_in_inv in shop_config.inventory:
            if item_id_in_inv in game_data.items:
                item_data = game_data.items[item_id_in_inv]
                shop_data['items'].append({
                    'id': item_id_in_inv,
                    'price': item_data.get('cost', 10),
                    'stock': 10  # Default stock
                })

        shop = Shop(shop_config.id, shop_data)
        shop_interface = ShopInterface(shop, party,
                                      price_modifier=shop_config.price_modifier,
                                      buy_rate=shop_config.buy_rate)

        shop_interface.set_active_character(character_index)
        success, message = shop_interface.buy_item(item_id, game_data)

        if success:
            # Save campaign (same as CLI)
            campaign_mgr.save_campaign(campaign)

            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/shop/sell', methods=['POST'])
def shop_sell(campaign_id):
    """Sell item to shop - IDENTICAL to CLI"""
    try:
        # Get request data
        data = request.json
        item_id = data.get('item_id')
        shop_id = data.get('shop_id')
        character_index = data.get('character_index', 0)

        # Load campaign and party
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # Get shop config from hub
        from aerthos.campaign.city_hub import CityHub
        hub = CityHub.load(campaign.current_hub_id)

        shop_config = None
        for shop in hub.shops:
            if shop.id == shop_id:
                shop_config = shop
                break

        if not shop_config:
            return jsonify({
                'success': False,
                'error': 'Shop not found'
            }), 404

        # IDENTICAL calls as CLI
        from aerthos.campaign.hub_interfaces import ShopInterface
        from aerthos.world.shop import Shop

        # Build shop data dict from shop_config
        game_data = GameData.load_all()
        shop_data = {
            'name': shop_config.name,
            'type': shop_config.type,
            'description': shop_config.specialty,
            'items': []
        }

        # Add items from inventory with prices from game_data
        for item_id_in_inv in shop_config.inventory:
            if item_id_in_inv in game_data.items:
                item_data = game_data.items[item_id_in_inv]
                shop_data['items'].append({
                    'id': item_id_in_inv,
                    'price': item_data.get('cost', 10),
                    'stock': 10  # Default stock
                })

        shop = Shop(shop_config.id, shop_data)
        shop_interface = ShopInterface(shop, party,
                                      price_modifier=shop_config.price_modifier,
                                      buy_rate=shop_config.buy_rate)

        shop_interface.set_active_character(character_index)
        success, message = shop_interface.sell_item(item_id)

        if success:
            # Save campaign (same as CLI)
            campaign_mgr.save_campaign(campaign)

            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/campaigns/<campaign_id>/temple/service', methods=['POST'])
def temple_service(campaign_id):
    """Purchase temple service - IDENTICAL to CLI"""
    try:
        # Get request data
        data = request.json
        service_name = data.get('service_name')
        target_character_index = data.get('target_character_index')
        paid_amount = data.get('paid_amount')

        # Load campaign and party
        campaign_mgr = CampaignManager()
        campaign = campaign_mgr.load_campaign(campaign_id)

        party_mgr = PartyManager()
        party_data = party_mgr.load_party(campaign.party_id)

        roster = CharacterRoster()
        party_members = []
        for member_id in party_data['character_ids']:
            char_data = roster.load_character(member_id)
            if char_data:
                party_members.append(char_data)

        party = Party(members=party_members)

        # Get temple config from hub
        from aerthos.campaign.city_hub import CityHub
        hub = CityHub.load(campaign.current_hub_id)
        temple_config = hub.temple

        if not temple_config:
            return jsonify({
                'success': False,
                'error': 'No temple available in this hub'
            }), 400

        # IDENTICAL calls as CLI
        from aerthos.campaign.hub_interfaces import TempleInterface

        temple_interface = TempleInterface(
            party,
            available_services=temple_config.services,
            donation_based=False
        )

        success, message = temple_interface.purchase_service(
            service_name,
            target_character_index,
            paid_amount
        )

        if success:
            # Save campaign (same as CLI)
            campaign_mgr.save_campaign(campaign)

            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Start a new game"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        # For demo, create a simple party
        # In production, this would go through character creation
        game_data = GameData.load_all()

        # Create demo party
        from aerthos.ui.character_creation import CharacterCreator
        creator = CharacterCreator(game_data)

        # Quick character creation for demo
        player1 = creator.quick_create("Thorin", "Dwarf", "Fighter")
        player2 = creator.quick_create("Elara", "Elf", "Magic-User")
        player3 = creator.quick_create("Cedric", "Human", "Cleric")
        player4 = creator.quick_create("Shadow", "Halfling", "Thief")

        # Add Level 2 spells to Elara to demo nested menus
        from aerthos.entities.player import Spell
        # Add several Level 2 spells to test vertical expansion
        level_2_spells = ['web', 'invisibility', 'mirror_image', 'levitate', 'knock', 'detect_invisibility']
        for spell_id in level_2_spells:
            if spell_id in game_data.spells:
                spell_data = game_data.spells[spell_id]
                if 'Magic-User' in spell_data.get('class_availability', []):
                    spell = Spell(
                        name=spell_data['name'],
                        level=spell_data['level'],
                        school=spell_data['school'],
                        casting_time=spell_data['casting_time'],
                        range=spell_data['range'],
                        duration=spell_data['duration'],
                        area_of_effect=spell_data['area'],
                        saving_throw=spell_data['saving_throw'],
                        components=spell_data['components'],
                        description=spell_data['description'],
                        class_availability=spell_data['class_availability']
                    )
                    player2.spells_known.append(spell)

        party = Party(members=[player1, player2, player3, player4])

        # Generate dungeon
        generator = DungeonGenerator(game_data)
        config = STANDARD_DUNGEON
        dungeon_data = generator.generate(config)
        dungeon = Dungeon.load_from_generator(dungeon_data)

        # Create game state
        game_state = GameState(party.members[0], dungeon)  # Use first member as main
        game_state.party = party  # Add party to game state
        game_state.load_game_data()

        # Store in session
        active_games[session_id] = game_state

        # Return initial state
        return jsonify({
            'success': True,
            'message': f"Welcome to {dungeon.name}!",
            'state': get_game_state_json(game_state)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a game command"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        command_text = data.get('command', '')
        active_character_index = data.get('active_character', 0)

        game_state = active_games.get(session_id)
        if not game_state:
            return jsonify({'success': False, 'error': 'No active game'})

        # Switch to the active character if party exists
        if hasattr(game_state, 'party') and game_state.party:
            if 0 <= active_character_index < len(game_state.party.members):
                game_state.player = game_state.party.members[active_character_index]

        # Parse and execute command
        from aerthos.engine.parser import CommandParser
        parser = CommandParser()
        command = parser.parse(command_text)

        result = game_state.execute_command(command)

        return jsonify({
            'success': True,
            'message': result.get('message', ''),
            'state': get_game_state_json(game_state),
            'active_character': active_character_index
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/game_state', methods=['POST'])
def get_game_state():
    """Get current game state for an active session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')

        game_state = active_games.get(session_id)
        if not game_state:
            return jsonify({'success': False, 'error': 'No active game session found'})

        return jsonify({
            'success': True,
            'state': get_game_state_json(game_state)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


def get_game_state_json(game_state):
    """
    Convert game state to JSON for frontend

    ⚠️ WARNING - WEB UI DEPENDENCY:
    The web UI (game.html) depends on this JSON structure.
    When adding fields: Safe - web UI will ignore unknown fields
    When removing/renaming fields: DANGEROUS - will break web UI!
    If you change this, update game.html JavaScript accordingly.
    """

    party_data = []
    if hasattr(game_state, 'party'):
        for i, member in enumerate(game_state.party.members):
            # Get inventory items
            inventory_items = []
            if hasattr(member, 'inventory') and hasattr(member.inventory, 'items'):
                for item in member.inventory.items:
                    inventory_items.append({
                        'name': item.name,
                        'type': getattr(item, 'item_type', 'unknown'),
                        'weight': getattr(item, 'weight', 0)
                    })

            # Get equipped items
            equipped = {}
            if hasattr(member, 'equipment'):
                if member.equipment.weapon:
                    equipped['weapon'] = member.equipment.weapon.name
                if member.equipment.armor:
                    equipped['armor'] = member.equipment.armor.name
                if member.equipment.shield:
                    equipped['shield'] = member.equipment.shield.name
                if member.equipment.light_source:
                    equipped['light'] = member.equipment.light_source.name

            # PRIORITY 5: Get spell slots for spellcasters
            spell_slots = []
            if hasattr(member, 'spells_memorized'):
                for slot in member.spells_memorized:
                    spell_slot_data = {
                        'level': slot.level,
                        'is_used': slot.is_used,
                        'spell': None
                    }
                    if slot.spell:
                        spell_slot_data['spell'] = {
                            'name': slot.spell.name,
                            'level': slot.spell.level,
                            'school': getattr(slot.spell, 'school', 'unknown'),
                            'range': getattr(slot.spell, 'range', 'self'),
                            'description': getattr(slot.spell, 'description', '')
                        }
                    spell_slots.append(spell_slot_data)

            # Get spells_known for this character (spells available to memorize)
            spells_known = []
            if hasattr(member, 'spells_known'):
                for spell in member.spells_known:
                    spells_known.append({
                        'name': spell.name,
                        'level': spell.level,
                        'school': spell.school
                    })

            # Get money breakdown
            member_money = {
                'cp': getattr(member, 'copper_pieces', 0),
                'sp': getattr(member, 'silver_pieces', 0),
                'ep': getattr(member, 'electrum_pieces', 0),
                'gp': getattr(member, 'gold_pieces', 0),
                'pp': getattr(member, 'platinum_pieces', 0)
            }

            party_data.append({
                'name': member.name,
                'class': member.char_class,
                'race': member.race,
                'level': member.level,
                'hp': member.hp_current,
                'hp_max': member.hp_max,
                'ac': member.get_effective_ac(),
                'thac0': member.thac0,
                'xp': member.xp,
                'gold': member.gold,  # Deprecated - kept for backward compat
                'money': member_money,  # New money breakdown
                'is_alive': member.is_alive,
                'weight': member.inventory.current_weight,
                'weight_max': member.inventory.max_weight,
                'formation': game_state.party.formation[i] if i < len(game_state.party.formation) else 'front',
                'inventory': inventory_items,
                'equipped': equipped,
                'spell_slots': spell_slots,  # Memorized spells (for casting)
                'spells_known': spells_known  # Known spells (for memorizing)
            })

    # Get map data
    map_data = build_map_data(game_state)

    # PRIORITY 1: Context-aware action bar data
    # Get items in current room (for "take" actions)
    room_items = []
    if hasattr(game_state.current_room, 'items'):
        room_items = game_state.current_room.items

    # Get active monsters (for "attack" actions)
    active_monsters = []
    if game_state.in_combat and hasattr(game_state, 'active_monsters'):
        for monster in game_state.active_monsters:
            if monster.is_alive:
                active_monsters.append({
                    'name': monster.name,
                    'hp': monster.hp_current,
                    'hp_max': monster.hp_max,
                    'status': 'wounded' if monster.hp_current < monster.hp_max * 0.5 else 'healthy'
                })

    # Get available spells for active character (for "cast" actions)
    available_spells = []
    if hasattr(game_state, 'party') and len(game_state.party.members) > 0:
        # Use first living member as "active" for spell suggestions
        # (In real gameplay, frontend tracks which character is active)
        for member in game_state.party.members:
            if member.is_alive and hasattr(member, 'spells_memorized') and len(member.spells_memorized) > 0:
                for slot in member.spells_memorized:
                    if slot.spell and not slot.is_used:
                        available_spells.append({
                            'name': slot.spell.name,
                            'level': slot.spell.level,
                            'caster': member.name
                        })
                break  # Only get spells from first living caster with memorized spells

    # Get spells available to memorize (from spells_known but not yet memorized)
    available_spells_to_memorize = []
    if hasattr(game_state, 'party') and len(game_state.party.members) > 0:
        # Get spells for all spellcaster party members
        for member in game_state.party.members:
            if member.is_alive and hasattr(member, 'spells_known') and len(member.spells_known) > 0:
                for spell in member.spells_known:
                    available_spells_to_memorize.append({
                        'name': spell.name,
                        'level': spell.level,
                        'school': spell.school,
                        'caster': member.name
                    })
                break  # Only get spells from first living caster with spells

    return {
        'room': {
            'id': game_state.current_room.id,
            'title': game_state.current_room.title,
            'description': game_state.current_room.description,
            'exits': game_state.current_room.exits,
            'light_level': game_state.current_room.light_level,
            'items': room_items  # NEW: Items in room for context-aware actions
        },
        'party': party_data,
        'in_combat': game_state.in_combat,
        'active_monsters': active_monsters,  # NEW: Monsters for context-aware actions
        'available_spells': available_spells,  # NEW: Spells for context-aware actions
        'available_spells_to_memorize': available_spells_to_memorize,  # NEW: Spells for memorize menu
        'time': {
            'turns': game_state.time_tracker.turns_elapsed,
            'hours': game_state.time_tracker.total_hours
        },
        'map': map_data
    }


def build_map_data(game_state):
    """Build map data for 2D visualization with persistent coordinates"""

    # Build a graph of room connections with absolute positions
    # Always start from the dungeon start room for consistency
    explored = {}
    current_id = game_state.current_room.id
    start_room_id = game_state.dungeon.start_room_id

    room_positions = {}
    visited = set()

    def calculate_positions(room_id, x=0, y=0):
        """Recursively calculate room positions based on exits"""
        if room_id in visited or room_id not in game_state.dungeon.rooms:
            return

        visited.add(room_id)
        room = game_state.dungeon.rooms[room_id]

        # Store position for all rooms (explored or not)
        room_positions[room_id] = {'x': x, 'y': y, 'room': room}

        # Calculate neighbor positions based on cardinal directions
        direction_offsets = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
            'up': (0, -1),
            'down': (0, 1)
        }

        for direction, next_room_id in room.exits.items():
            if next_room_id not in visited:
                offset = direction_offsets.get(direction, (0, 0))
                calculate_positions(next_room_id, x + offset[0], y + offset[1])

    # Calculate positions starting from START room (for consistency)
    calculate_positions(start_room_id, 0, 0)

    # Collect explored rooms and unexplored adjacent rooms
    for room_id, pos_data in room_positions.items():
        if pos_data['room'].is_explored:
            explored[room_id] = {
                'id': room_id,
                'title': pos_data['room'].title,
                'x': pos_data['x'],
                'y': pos_data['y'],
                'exits': pos_data['room'].exits,
                'is_current': room_id == current_id,
                'is_explored': True
            }

    # Add unexplored but known rooms (exits from explored rooms)
    for room_id, room_data in list(explored.items()):
        room = game_state.dungeon.rooms[room_id]
        for direction, next_room_id in room.exits.items():
            # If the connected room exists but is not explored, add it as unknown
            if next_room_id in room_positions and next_room_id not in explored:
                pos_data = room_positions[next_room_id]
                explored[next_room_id] = {
                    'id': next_room_id,
                    'title': '???',  # Hide title until explored
                    'x': pos_data['x'],  # Use pre-calculated position
                    'y': pos_data['y'],  # Use pre-calculated position
                    'exits': {},  # Don't reveal exits until explored
                    'is_current': False,
                    'is_explored': False
                }

    return {
        'rooms': explored,
        'current_room_id': current_id
    }


# ============================================================================
# Character Roster API Endpoints
# ============================================================================

@app.route('/api/characters', methods=['GET'])
def get_characters():
    """Get all characters from roster"""
    try:
        roster = CharacterRoster()
        characters = roster.list_characters()
        return jsonify({'success': True, 'characters': characters})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/characters', methods=['POST'])
def create_character():
    """Create a new character"""
    try:
        data = request.json

        # Validate input
        name = data.get('name')
        race = data.get('race')
        char_class = data.get('char_class')

        if not name or not race or not char_class:
            return jsonify({'success': False, 'error': 'Name, race, and class are required'})

        # Validate race and class are implemented
        valid_races = ['Human', 'Elf', 'Dwarf', 'Halfling']
        valid_classes = ['Fighter', 'Cleric', 'Magic-User', 'Thief']

        if race not in valid_races:
            return jsonify({'success': False, 'error': f'Race "{race}" not implemented. Available: {", ".join(valid_races)}'})

        if char_class not in valid_classes:
            return jsonify({'success': False, 'error': f'Class "{char_class}" not implemented. Available: {", ".join(valid_classes)}'})

        game_data = GameData.load_all()
        creator = CharacterCreator(game_data)

        # Quick create character
        character = creator.quick_create(name, race, char_class)

        # Save to roster
        roster = CharacterRoster()
        char_id = roster.save_character(character)

        return jsonify({'success': True, 'character_id': char_id})
    except KeyError as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Missing game data for: {str(e)}'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/characters/<char_id>', methods=['GET'])
def get_character(char_id):
    """Get a specific character with full details"""
    try:
        roster = CharacterRoster()
        character = roster.load_character(char_id)

        if not character:
            return jsonify({'success': False, 'error': 'Character not found'})

        # Ability scores
        abilities = {
            'strength': character.strength,
            'dexterity': character.dexterity,
            'constitution': character.constitution,
            'intelligence': character.intelligence,
            'wisdom': character.wisdom,
            'charisma': character.charisma,
            'strength_percentile': character.strength_percentile
        }

        # Inventory items
        inventory_items = []
        for item in character.inventory.items:
            item_info = {
                'name': item.name,
                'type': item.item_type,
                'weight': item.weight
            }
            # Add weapon-specific info
            if hasattr(item, 'damage_sm'):
                item_info['damage_sm'] = item.damage_sm
                item_info['damage_l'] = item.damage_l
                if hasattr(item, 'magic_bonus') and item.magic_bonus > 0:
                    item_info['magic_bonus'] = item.magic_bonus
            # Add armor-specific info
            if hasattr(item, 'ac'):
                item_info['ac'] = item.ac
                if hasattr(item, 'magic_bonus') and item.magic_bonus > 0:
                    item_info['magic_bonus'] = item.magic_bonus
            inventory_items.append(item_info)

        # Equipped items
        equipment = {}
        if character.equipment.weapon:
            equipment['weapon'] = {
                'name': character.equipment.weapon.name,
                'damage_sm': character.equipment.weapon.damage_sm,
                'damage_l': character.equipment.weapon.damage_l,
                'magic_bonus': character.equipment.weapon.magic_bonus if hasattr(character.equipment.weapon, 'magic_bonus') else 0
            }
        if character.equipment.armor:
            equipment['armor'] = {
                'name': character.equipment.armor.name,
                'ac': character.equipment.armor.ac,
                'magic_bonus': character.equipment.armor.magic_bonus if hasattr(character.equipment.armor, 'magic_bonus') else 0
            }
        if character.equipment.shield:
            equipment['shield'] = {
                'name': character.equipment.shield.name,
                'ac_bonus': character.equipment.shield.ac_bonus,
                'magic_bonus': character.equipment.shield.magic_bonus if hasattr(character.equipment.shield, 'magic_bonus') else 0
            }
        if character.equipment.light_source:
            equipment['light_source'] = {
                'name': character.equipment.light_source.name,
                'turns_remaining': character.equipment.light_source.turns_remaining
            }

        # Spells
        spells_known = []
        for spell in character.spells_known:
            spells_known.append({
                'name': spell.name,
                'level': spell.level,
                'school': spell.school,
                'description': spell.description
            })

        spells_memorized = []
        for slot in character.spells_memorized:
            slot_info = {
                'level': slot.level,
                'is_used': slot.is_used
            }
            if slot.spell:
                slot_info['spell'] = {
                    'name': slot.spell.name,
                    'level': slot.spell.level
                }
            spells_memorized.append(slot_info)

        # Saving throws
        saving_throws = {
            'poison': character.save_poison,
            'rod_staff_wand': character.save_rod_staff_wand,
            'petrify_paralyze': character.save_petrify_paralyze,
            'breath': character.save_breath,
            'spell': character.save_spell
        }

        # Thief skills (if applicable)
        thief_skills = None
        if character.thief_skills:
            thief_skills = character.thief_skills

        # Money breakdown
        money = {
            'cp': getattr(character, 'copper_pieces', 0),
            'sp': getattr(character, 'silver_pieces', 0),
            'ep': getattr(character, 'electrum_pieces', 0),
            'gp': getattr(character, 'gold_pieces', 0),
            'pp': getattr(character, 'platinum_pieces', 0),
            'gold_old': character.gold  # Keep for backward compat
        }

        # Convert character to dict for JSON
        char_data = {
            'id': char_id,
            'name': character.name,
            'race': character.race,
            'char_class': character.char_class,
            'alignment': character.alignment,
            'level': character.level,
            'xp': character.xp,
            'xp_to_next_level': character.xp_to_next_level,
            'hp_current': character.hp_current,
            'hp_max': character.hp_max,
            'ac': character.get_effective_ac(),
            'thac0': character.thac0,
            'gold': character.gold,  # Deprecated but kept for backward compat
            'money': money,
            'weight': character.inventory.current_weight,
            'weight_max': character.inventory.max_weight,
            'abilities': abilities,
            'inventory': inventory_items,
            'equipment': equipment,
            'spells_known': spells_known,
            'spells_memorized': spells_memorized,
            'saving_throws': saving_throws,
            'thief_skills': thief_skills
        }

        return jsonify({'success': True, 'character': char_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/characters/<char_id>', methods=['DELETE'])
def delete_character(char_id):
    """Delete a character"""
    try:
        roster = CharacterRoster()
        success = roster.delete_character(char_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Character not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/get_races', methods=['POST'])
def get_available_races():
    """Get available races based on ability scores"""
    try:
        data = request.json
        stats = data.get('stats', {})

        game_data = GameData.load_all()
        from aerthos.ui.character_creation import CharacterCreator
        creator = CharacterCreator(game_data)

        races_info = []
        for race_name in ['Human', 'Elf', 'Dwarf', 'Halfling', 'Half-Elf', 'Half-Orc', 'Gnome']:
            if race_name not in game_data.races:
                continue

            race_data = game_data.races[race_name]
            is_available, reason = creator._check_race_requirements(
                race_name,
                stats.get('str', 0),
                stats.get('dex', 0),
                stats.get('con', 0),
                stats.get('int', 0),
                stats.get('wis', 0),
                stats.get('cha', 0)
            )

            mods = race_data.get('ability_modifiers', {})
            mod_str = creator._format_ability_modifiers(mods)

            races_info.append({
                'name': race_name,
                'description': race_data.get('description', ''),
                'modifiers': mod_str,
                'available': is_available,
                'reason': reason
            })

        return jsonify({'success': True, 'races': races_info})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/get_classes', methods=['POST'])
def get_available_classes():
    """Get available classes based on race and ability scores"""
    try:
        data = request.json
        stats = data.get('stats', {})
        race = data.get('race', 'Human')

        game_data = GameData.load_all()
        from aerthos.ui.character_creation import CharacterCreator
        creator = CharacterCreator(game_data)

        # Apply racial modifiers to stats
        race_data = game_data.races[race]
        modified_stats = stats.copy()
        for ability, modifier in race_data.get('ability_modifiers', {}).items():
            stat_key = ability[:3]  # str, dex, con, etc.
            if stat_key in modified_stats:
                modified_stats[stat_key] += modifier

        # Apply racial maximums
        maximums = race_data.get('ability_maximums', {})
        for ability, max_val in maximums.items():
            stat_key = ability[:3]
            if stat_key in modified_stats:
                modified_stats[stat_key] = min(modified_stats[stat_key], max_val)

        classes_info = []
        all_classes = ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard']

        for class_name in all_classes:
            if class_name not in game_data.classes:
                continue

            is_available, reason = creator._check_class_requirements(
                class_name,
                race,
                modified_stats.get('str', 0),
                modified_stats.get('dex', 0),
                modified_stats.get('con', 0),
                modified_stats.get('int', 0),
                modified_stats.get('wis', 0),
                modified_stats.get('cha', 0)
            )

            class_data = game_data.classes[class_name]
            classes_info.append({
                'name': class_name,
                'description': class_data.get('description', ''),
                'available': is_available,
                'reason': reason
            })

        return jsonify({
            'success': True,
            'classes': classes_info,
            'stats_after_race': modified_stats
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/get_alignments', methods=['POST'])
def get_available_alignments():
    """Get available alignments for a class"""
    try:
        data = request.json
        char_class = data.get('char_class')

        # Import alignments
        from aerthos.entities.character import ALIGNMENTS
        from aerthos.systems.alignment import get_allowed_alignments_for_class

        # If no class specified, return all alignments
        if not char_class:
            return jsonify({
                'success': True,
                'alignments': ALIGNMENTS
            })

        # Load class data
        game_data = load_game_data()
        class_data = game_data.classes.get(char_class)

        if not class_data:
            return jsonify({'success': False, 'error': 'Invalid class'})

        # Get allowed alignments for the specific class
        allowed_alignments = get_allowed_alignments_for_class(char_class, class_data)

        return jsonify({
            'success': True,
            'alignments': allowed_alignments
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/character/create', methods=['POST'])
def create_character_full():
    """Create a character with full stat rolling"""
    try:
        data = request.json
        name = data.get('name', 'Adventurer')
        race = data.get('race', 'Human')
        char_class = data.get('char_class', 'Fighter')
        alignment = data.get('alignment', 'True Neutral')
        base_stats = data.get('stats', {})

        game_data = GameData.load_all()
        from aerthos.ui.character_creation import CharacterCreator
        from aerthos.engine.combat import DiceRoller
        creator = CharacterCreator(game_data)

        # Get base stats
        strength = base_stats.get('str', 10)
        dexterity = base_stats.get('dex', 10)
        constitution = base_stats.get('con', 10)
        intelligence = base_stats.get('int', 10)
        wisdom = base_stats.get('wis', 10)
        charisma = base_stats.get('cha', 10)

        # Apply racial modifiers
        race_data = game_data.races[race]
        for ability, modifier in race_data.get('ability_modifiers', {}).items():
            if ability == 'strength':
                strength += modifier
            elif ability == 'dexterity':
                dexterity += modifier
            elif ability == 'constitution':
                constitution += modifier
            elif ability == 'intelligence':
                intelligence += modifier
            elif ability == 'wisdom':
                wisdom += modifier
            elif ability == 'charisma':
                charisma += modifier

        # Apply racial maximums
        maximums = race_data.get('ability_maximums', {})
        if 'strength' in maximums:
            strength = min(strength, maximums['strength'])
        if 'dexterity' in maximums:
            dexterity = min(dexterity, maximums['dexterity'])
        if 'constitution' in maximums:
            constitution = min(constitution, maximums['constitution'])
        if 'intelligence' in maximums:
            intelligence = min(intelligence, maximums['intelligence'])
        if 'wisdom' in maximums:
            wisdom = min(wisdom, maximums['wisdom'])
        if 'charisma' in maximums:
            charisma = min(charisma, maximums['charisma'])

        # Handle exceptional strength for Fighters
        strength_percentile = 0
        if char_class == 'Fighter' and strength == 18:
            import random
            strength_percentile = random.randint(1, 100)

        # Validate alignment for class
        class_data = game_data.classes[char_class]
        from aerthos.systems.alignment import validate_class_alignment
        if not validate_class_alignment(char_class, alignment, class_data):
            return jsonify({
                'success': False,
                'error': f'{alignment} is not a valid alignment for {char_class}'
            })

        # Roll HP
        hit_die = class_data['hit_die']
        hp = max(1, DiceRoller.roll(hit_die))

        # Apply CON bonus
        con_bonus = creator._get_con_bonus(constitution)
        hp = max(1, hp + con_bonus)

        # Get class-specific data
        saves = class_data['saves']
        thac0 = class_data['thac0_base']

        # Get XP needed for level 2
        from aerthos.entities.player import XP_TABLES
        xp_to_level_2 = XP_TABLES.get(char_class, [0, 2000])[1]

        # Create character
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            alignment=alignment,
            level=1,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp,
            ac=10,
            thac0=thac0,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            xp=0,
            xp_to_next_level=xp_to_level_2
        )

        # Add starting equipment
        creator._add_starting_equipment(player, char_class)

        # Add skills for skill-based classes
        if char_class in ['Thief', 'Assassin', 'Bard']:
            player.thief_skills = class_data.get('skills', {}).copy()

        # Add spell slots if spellcaster
        if char_class in ['Magic-User', 'Illusionist', 'Cleric', 'Druid', 'Ranger', 'Paladin', 'Bard']:
            spell_slots_key = 'spell_slots_level_1'
            if spell_slots_key in class_data:
                num_slots = class_data[spell_slots_key][0]
                if num_slots > 0:
                    for _ in range(num_slots):
                        player.add_spell_slot(1)

                    # Give starting spells (CRITICAL: must match CLI character_creation.py)
                    creator._add_starting_spells(player, char_class)

        # Save character
        roster = CharacterRoster()
        char_id = roster.save_character(player)

        return jsonify({'success': True, 'character_id': char_id, 'name': name})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Item Selection API Endpoints
# ============================================================================

@app.route('/api/items/weapons', methods=['GET'])
def get_weapons():
    """Get all available weapons"""
    try:
        import json
        from pathlib import Path

        weapons_path = Path("aerthos/data/weapons.json")
        with open(weapons_path) as f:
            weapons_data = json.load(f)

        weapons_list = []
        for weapon_id, weapon_info in weapons_data.items():
            weapons_list.append({
                'id': weapon_id,
                'name': weapon_info.get('name', weapon_id),
                'damage_sm': weapon_info.get('damage_sm', ''),
                'damage_l': weapon_info.get('damage_l', ''),
                'cost': weapon_info.get('cost_gp', weapon_info.get('cost_sp', 0))
            })

        return jsonify({'success': True, 'weapons': weapons_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/items/armor', methods=['GET'])
def get_armor():
    """Get all available armor"""
    try:
        import json
        from pathlib import Path

        armor_path = Path("aerthos/data/armor.json")
        with open(armor_path) as f:
            armor_data = json.load(f)

        armor_list = []
        for armor_id, armor_info in armor_data.get('armor', {}).items():
            armor_list.append({
                'id': armor_id,
                'name': armor_info.get('name', armor_id),
                'ac': armor_info.get('ac', 10),
                'cost': armor_info.get('cost_gp', 0)
            })

        return jsonify({'success': True, 'armor': armor_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/items/shields', methods=['GET'])
def get_shields():
    """Get all available shields"""
    try:
        import json
        from pathlib import Path

        armor_path = Path("aerthos/data/armor.json")
        with open(armor_path) as f:
            armor_data = json.load(f)

        shields_list = []
        for shield_id, shield_info in armor_data.get('shields', {}).items():
            shields_list.append({
                'id': shield_id,
                'name': shield_info.get('name', shield_id),
                'ac_bonus': shield_info.get('ac_bonus', 1),
                'cost': shield_info.get('cost_gp', 0)
            })

        return jsonify({'success': True, 'shields': shields_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/items/equipment', methods=['GET'])
def get_equipment():
    """Get all available equipment"""
    try:
        import json
        from pathlib import Path

        equipment_path = Path("aerthos/data/equipment.json")
        with open(equipment_path) as f:
            equipment_data = json.load(f)

        equipment_list = []
        for item_id, item_info in equipment_data.items():
            equipment_list.append({
                'id': item_id,
                'name': item_info.get('name', item_id),
                'cost': item_info.get('cost_gp', item_info.get('cost_sp', item_info.get('cost_cp', 0)))
            })

        return jsonify({'success': True, 'equipment': equipment_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/items/spells', methods=['POST'])
def get_spells():
    """Get available spells for a class"""
    try:
        data = request.json
        char_class = data.get('char_class', '')

        game_data = GameData.load_all()

        spells_list = []
        for spell_id, spell_info in game_data.spells.items():
            # Check if spell is available for this class
            spell_class = spell_info.get('class', '')
            if char_class and spell_class and char_class not in spell_class:
                continue

            spells_list.append({
                'id': spell_id,
                'name': spell_info.get('name', spell_id),
                'level': spell_info.get('level', 1),
                'class': spell_class,
                'school': spell_info.get('school', '')
            })

        return jsonify({'success': True, 'spells': spells_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/items/magic_items', methods=['GET'])
def get_magic_items():
    """Get all available magic items from magic_items.json"""
    try:
        import json
        from pathlib import Path

        magic_items_path = Path("aerthos/data/magic_items.json")
        with open(magic_items_path) as f:
            magic_data = json.load(f)

        magic_items_list = []

        # Add potions
        for potion in magic_data.get('potions', []):
            magic_items_list.append({
                'id': f"potion_{potion['name'].lower().replace(' ', '_')}",
                'name': f"Potion of {potion['name']}",
                'category': 'Potion',
                'xp': potion.get('xp', 0),
                'gp': potion.get('gp', 0)
            })

        # Add protection scrolls
        for scroll in magic_data.get('scrolls', {}).get('protection_scrolls', []):
            magic_items_list.append({
                'id': f"scroll_{scroll['name'].lower().replace(' ', '_').replace('protection_from_', 'prot_')}",
                'name': scroll['name'],
                'category': 'Scroll',
                'xp': scroll.get('xp', 0),
                'gp': scroll.get('gp', 0)
            })

        # Add magic weapons
        for weapon in magic_data.get('weapons', {}).get('swords', []):
            magic_items_list.append({
                'id': f"weapon_sword_{weapon['name'].lower().replace(' ', '_').replace(',', '').replace('+', 'plus')}",
                'name': weapon['name'],
                'category': 'Weapon (Sword)',
                'xp': weapon.get('xp', 0),
                'gp': weapon.get('gp', 0)
            })

        for weapon in magic_data.get('weapons', {}).get('misc_weapons', []):
            magic_items_list.append({
                'id': f"weapon_{weapon['name'].lower().replace(' ', '_').replace('+', 'plus').replace('(', '').replace(')', '')}",
                'name': weapon['name'],
                'category': 'Weapon',
                'xp': weapon.get('xp', 0),
                'gp': weapon.get('gp', 0)
            })

        # Add magic armor/shields
        for armor in magic_data.get('armor', []):
            magic_items_list.append({
                'id': f"armor_{armor['name'].lower().replace(' ', '_').replace('+', 'plus').replace(',', '')}",
                'name': armor['name'],
                'category': 'Armor/Shield',
                'xp': armor.get('xp', 0),
                'gp': armor.get('gp', 0)
            })

        # Add rings
        for ring in magic_data.get('rings', []):
            magic_items_list.append({
                'id': f"ring_{ring['name'].lower().replace(' ', '_').replace('+', 'plus').replace('(', '').replace(')', '')}",
                'name': ring['name'],
                'category': 'Ring',
                'xp': ring.get('xp', 0),
                'gp': ring.get('gp', 0)
            })

        # Add wands/staves/rods
        for item in magic_data.get('wands_staves_rods', []):
            category = item.get('type', 'wand').title()
            magic_items_list.append({
                'id': f"{item.get('type', 'wand')}_{item['name'].lower().replace(' ', '_')}",
                'name': item['name'],
                'category': category,
                'xp': item.get('xp', 0),
                'gp': item.get('gp', 0),
                'charges': item.get('charges', '')
            })

        # Add misc magic items
        for item in magic_data.get('misc_magic', []):
            magic_items_list.append({
                'id': f"misc_{item['name'].lower().replace(' ', '_')}",
                'name': item['name'],
                'category': 'Misc Magic',
                'xp': item.get('xp', 0),
                'gp': item.get('gp', 0)
            })

        return jsonify({'success': True, 'magic_items': magic_items_list})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# Party Manager API Endpoints
# ============================================================================

@app.route('/api/character/import_manual', methods=['POST'])
def import_manual_character():
    """
    Import a manually created character with custom stats
    Accepts comprehensive character data including abilities, level, XP, items, spells
    """
    try:
        data = request.json
        game_data = GameData.load_all()

        # Extract character data
        name = data.get('name', 'Adventurer')
        race = data.get('race', 'Human')
        char_class = data.get('char_class', 'Fighter')
        alignment = data.get('alignment', 'True Neutral')
        level = data.get('level', 1)
        xp = data.get('xp', 0)

        # Ability scores
        strength = data.get('strength', 10)
        dexterity = data.get('dexterity', 10)
        constitution = data.get('constitution', 10)
        intelligence = data.get('intelligence', 10)
        wisdom = data.get('wisdom', 10)
        charisma = data.get('charisma', 10)
        strength_percentile = data.get('strength_percentile', 0)

        # HP options: 'manual', 'max', 'auto'
        hp_option = data.get('hp_option', 'manual')
        hp_manual = data.get('hp_manual', 0)

        # Money
        money = data.get('money', {})
        copper_pieces = money.get('cp', 0)
        silver_pieces = money.get('sp', 0)
        electrum_pieces = money.get('ep', 0)
        gold_pieces = money.get('gp', 0)
        platinum_pieces = money.get('pp', 0)

        # Validate alignment for class
        class_data = game_data.classes[char_class]
        from aerthos.systems.alignment import validate_class_alignment
        if not validate_class_alignment(char_class, alignment, class_data):
            return jsonify({
                'success': False,
                'error': f'{alignment} is not a valid alignment for {char_class}'
            })

        # Calculate HP based on option
        from aerthos.engine.combat import DiceRoller
        from aerthos.ui.character_creation import CharacterCreator

        creator = CharacterCreator(game_data)
        con_bonus = creator._get_con_bonus(constitution)
        hit_die = class_data['hit_die']

        if hp_option == 'manual':
            hp = hp_manual
        elif hp_option == 'max':
            # Max possible for level
            die_size = int(hit_die.strip('d'))
            hp = (die_size + con_bonus) * level
        else:  # 'auto' - roll
            hp = 0
            for _ in range(level):
                roll = DiceRoller.roll(hit_die)
                hp += max(1, roll + con_bonus)

        hp = max(1, hp)

        # Calculate THAC0 and saves for level
        manual_creator = ManualCharacterCreator(game_data)
        thac0 = manual_creator._calculate_thac0(class_data, level)
        saves = manual_creator._calculate_saves(class_data, level)

        # Get XP requirements
        from aerthos.entities.player import XP_TABLES
        xp_table = XP_TABLES.get(char_class, [0] * 21)
        xp_to_next = xp_table[level] if level < len(xp_table) else xp_table[-1]

        # Create character
        player = PlayerCharacter(
            name=name,
            race=race,
            char_class=char_class,
            alignment=alignment,
            level=level,
            strength=strength,
            dexterity=dexterity,
            constitution=constitution,
            intelligence=intelligence,
            wisdom=wisdom,
            charisma=charisma,
            strength_percentile=strength_percentile,
            hp_current=hp,
            hp_max=hp,
            ac=10,  # Base AC, will be recalculated with equipment
            thac0=thac0,
            xp=xp,
            xp_to_next_level=xp_to_next,
            save_poison=saves['poison'],
            save_rod_staff_wand=saves['rod_staff_wand'],
            save_petrify_paralyze=saves['petrify_paralyze'],
            save_breath=saves['breath'],
            save_spell=saves['spell'],
            copper_pieces=copper_pieces,
            silver_pieces=silver_pieces,
            electrum_pieces=electrum_pieces,
            gold_pieces=gold_pieces,
            platinum_pieces=platinum_pieces
        )

        # Add starting equipment from data
        equipment_ids = data.get('equipment', [])
        print(f"DEBUG: Equipment IDs from request: {equipment_ids}")

        if equipment_ids:
            # User provided specific equipment
            for item_id in equipment_ids:
                print(f"DEBUG: Processing item_id: '{item_id}'")
                # Try to find item in separate databases (weapons, armor, shields, equipment)
                item_data = None
                item = None

                # Check weapons
                if item_id in manual_creator.weapons:
                    print(f"DEBUG: Found '{item_id}' in weapons")
                    item_data = manual_creator.weapons[item_id]
                    item = manual_creator._create_weapon_from_data(item_id, item_data)
                    if item:
                        player.inventory.add_item(item)
                        # Equip first weapon
                        if not player.equipment.weapon:
                            player.equip_weapon(item)
                            print(f"DEBUG: Equipped weapon: {item.name}")

                # Check armor
                elif item_id in manual_creator.armor:
                    print(f"DEBUG: Found '{item_id}' in armor")
                    item_data = manual_creator.armor[item_id]
                    item = manual_creator._create_armor_from_data(item_id, item_data)
                    if item:
                        player.inventory.add_item(item)
                        # Equip first armor
                        if not player.equipment.armor:
                            player.equipment.armor = item
                            print(f"DEBUG: Equipped armor: {item.name}")

                # Check shields
                elif item_id in manual_creator.shields:
                    print(f"DEBUG: Found '{item_id}' in shields")
                    item_data = manual_creator.shields[item_id]
                    item = manual_creator._create_shield_from_data(item_id, item_data)
                    if item:
                        player.inventory.add_item(item)
                        # Equip first shield
                        if not player.equipment.shield:
                            player.equipment.shield = item
                            print(f"DEBUG: Equipped shield: {item.name}")

                # Check equipment
                elif item_id in manual_creator.equipment:
                    print(f"DEBUG: Found '{item_id}' in equipment")
                    item_data = manual_creator.equipment[item_id]
                    item = manual_creator._create_item_from_data(item_id, item_data)
                    if item:
                        player.inventory.add_item(item)
                else:
                    print(f"DEBUG: Item '{item_id}' not found in any database")

                if item:
                    print(f"DEBUG: Added to inventory: {item.name}")
                    print(f"DEBUG: Inventory count: {len(player.inventory.items)}")
        else:
            # Auto-generate starting equipment based on class
            print(f"DEBUG: Auto-generating equipment for {char_class}")

            # Save user's money values before auto-equipment overwrites them
            saved_cp = player.copper_pieces
            saved_sp = player.silver_pieces
            saved_ep = player.electrum_pieces
            saved_gp = player.gold_pieces
            saved_pp = player.platinum_pieces

            creator._add_starting_equipment(player, char_class)

            # Restore user's money values if they were set (non-zero)
            if saved_cp > 0 or saved_sp > 0 or saved_ep > 0 or saved_gp > 0 or saved_pp > 0:
                player.copper_pieces = saved_cp
                player.silver_pieces = saved_sp
                player.electrum_pieces = saved_ep
                player.gold_pieces = saved_gp
                player.platinum_pieces = saved_pp
                player.gold = 0  # Clear the old gold field

            print(f"DEBUG: After auto-gen, inventory count: {len(player.inventory.items)}")

        # Add spells for casters
        spell_ids = data.get('spells', [])
        if spell_ids:
            # User provided specific spells
            for spell_id in spell_ids:
                if spell_id in game_data.spells:
                    spell = manual_creator._create_spell_from_data(game_data.spells[spell_id])
                    player.spells_known.append(spell)
        else:
            # Auto-assign spells for caster classes
            manual_creator._auto_assign_spells(player, char_class, level)

        # Add magic items
        magic_item_ids = data.get('magic_items', [])
        if magic_item_ids:
            import json
            from pathlib import Path
            from aerthos.entities.player import Item, Weapon, Armor

            magic_items_path = Path("aerthos/data/magic_items.json")
            with open(magic_items_path) as f:
                magic_data = json.load(f)

            for magic_id in magic_item_ids:
                # Parse magic item ID to find in correct category
                # Format: "category_name" (e.g., "potion_healing", "weapon_sword_plus1")
                magic_item = None
                item_name = ""

                # Potions
                if magic_id.startswith('potion_'):
                    for potion in magic_data.get('potions', []):
                        potion_id = f"potion_{potion['name'].lower().replace(' ', '_')}"
                        if potion_id == magic_id:
                            item_name = f"Potion of {potion['name']}"
                            magic_item = Item(name=item_name, item_type='potion', weight=0.1)
                            break

                # Scrolls
                elif magic_id.startswith('scroll_'):
                    for scroll in magic_data.get('scrolls', {}).get('protection_scrolls', []):
                        scroll_id = f"scroll_{scroll['name'].lower().replace(' ', '_').replace('protection_from_', 'prot_')}"
                        if scroll_id == magic_id:
                            item_name = scroll['name']
                            magic_item = Item(name=item_name, item_type='scroll', weight=0.1)
                            break

                # Rings
                elif magic_id.startswith('ring_'):
                    for ring in magic_data.get('rings', []):
                        ring_id = f"ring_{ring['name'].lower().replace(' ', '_').replace('+', 'plus').replace('(', '').replace(')', '')}"
                        if ring_id == magic_id:
                            item_name = ring['name']
                            magic_item = Item(name=item_name, item_type='ring', weight=0.1)
                            break

                # Wands/Staves/Rods
                elif magic_id.startswith('wand_') or magic_id.startswith('staff_') or magic_id.startswith('rod_'):
                    for item in magic_data.get('wands_staves_rods', []):
                        item_id = f"{item.get('type', 'wand')}_{item['name'].lower().replace(' ', '_')}"
                        if item_id == magic_id:
                            item_name = item['name']
                            magic_item = Item(name=item_name, item_type=item.get('type', 'wand'), weight=1.0)
                            break

                # Misc magic items
                elif magic_id.startswith('misc_'):
                    for item in magic_data.get('misc_magic', []):
                        item_id = f"misc_{item['name'].lower().replace(' ', '_')}"
                        if item_id == magic_id:
                            item_name = item['name']
                            magic_item = Item(name=item_name, item_type='misc_magic', weight=1.0)
                            break

                # Magic weapons and armor are more complex - add as generic magic items for now
                # In a full implementation, these would be created as Weapon/Armor with magic_bonus
                elif magic_id.startswith('weapon_') or magic_id.startswith('armor_'):
                    # Extract name from ID (simplified)
                    item_name = magic_id.replace('_', ' ').replace('plus', '+').title()
                    magic_item = Item(name=item_name, item_type='magic_item', weight=1.0)

                if magic_item:
                    player.inventory.add_item(magic_item)
                    print(f"DEBUG: Added magic item to inventory: {magic_item.name}")

        # Add thief skills if thief
        if 'Thief' in char_class or char_class in ['Assassin', 'Acrobat']:
            player.thief_skills = data.get('thief_skills', creator._get_thief_skills(level))

        # Save to roster
        print(f"DEBUG: Before saving - inventory count: {len(player.inventory.items)}")
        print(f"DEBUG: Before saving - spells known: {len(player.spells_known)}")
        roster = CharacterRoster()
        char_id = roster.save_character(player)
        print(f"DEBUG: Character saved with ID: {char_id}")

        # Verify saved character has items
        loaded_char = roster.load_character(char_id)
        print(f"DEBUG: After loading - inventory count: {len(loaded_char.inventory.items)}")
        print(f"DEBUG: After loading - spells known: {len(loaded_char.spells_known)}")

        # Return character data
        char_data = {
            'id': char_id,
            'name': player.name,
            'race': player.race,
            'char_class': player.char_class,
            'alignment': player.alignment,
            'level': player.level,
            'hp_current': player.hp_current,
            'hp_max': player.hp_max,
            'ac': player.get_effective_ac(),
            'thac0': player.thac0,
            'xp': player.xp,
            'strength': player.strength,
            'dexterity': player.dexterity,
            'constitution': player.constitution,
            'intelligence': player.intelligence,
            'wisdom': player.wisdom,
            'charisma': player.charisma,
            'strength_percentile': player.strength_percentile
        }

        return jsonify({'success': True, 'character': char_data})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/parties', methods=['GET'])
def get_parties():
    """Get all parties"""
    try:
        party_mgr = PartyManager()
        parties = party_mgr.list_parties()
        return jsonify({'success': True, 'parties': parties})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/parties', methods=['POST'])
def create_party():
    """Create a new party"""
    try:
        data = request.json
        party_mgr = PartyManager()

        character_ids = data.get('character_ids', [])

        # Create default formation if not provided (2 rows)
        formation = data.get('formation')
        if not formation:
            # Default: put half in front row, half in back row
            mid = len(character_ids) // 2
            formation = ['front'] * mid + ['back'] * (len(character_ids) - mid)

        party_id = party_mgr.save_party(
            data.get('name'),
            character_ids,
            formation
        )

        return jsonify({'success': True, 'party_id': party_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/parties/<party_id>', methods=['DELETE'])
def delete_party(party_id):
    """Delete a party"""
    try:
        party_mgr = PartyManager()
        success = party_mgr.delete_party(party_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Party not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Scenario Library API Endpoints
# ============================================================================

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """Get all scenarios"""
    try:
        library = ScenarioLibrary()
        scenarios = library.list_scenarios()
        return jsonify({'success': True, 'scenarios': scenarios})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/scenarios', methods=['POST'])
def create_scenario():
    """
    Generate and save a new scenario

    Expected JSON parameters:
    - dungeon_type: '1' (fixed - not saveable), '2' (easy), '3' (standard), '4' (hard), '5' (custom)
    - party_level: Required for types 2-4 (default 1)
    - name: Scenario name
    - description: Scenario description

    For custom (type 5):
    - num_rooms: Rooms per level (5-30, default 12)
    - layout_type: 'linear', 'branching', 'network' (default 'branching')
    - num_levels: Number of levels (1-5, default 1)
    - dungeon_theme: 'mine', 'crypt', 'cave', 'ruins', 'sewer' (default 'mine')
    - seed: Optional seed for reproducibility
    - party_aware: Interview results dict with apl, party_size, composition, magic_level
    """
    try:
        data = request.json
        game_data = GameData.load_all()

        dungeon_type = data.get('dungeon_type', '3')  # Default to standard

        # Type 1 (fixed) cannot be saved
        if dungeon_type == '1':
            return jsonify({'success': False, 'error': 'Cannot save fixed starter dungeon'})

        generator = DungeonGenerator(game_data)
        config = None
        dungeon = None
        difficulty = 'medium'

        # Types 2-4: Preset dungeons (Easy/Standard/Hard)
        if dungeon_type in ['2', '3', '4']:
            from aerthos.generator.config import EASY_DUNGEON, STANDARD_DUNGEON, HARD_DUNGEON

            party_level = data.get('party_level', 1)

            if dungeon_type == '2':
                config = EASY_DUNGEON
                difficulty = 'easy'
            elif dungeon_type == '3':
                config = STANDARD_DUNGEON
                difficulty = 'medium'
            else:  # '4'
                config = HARD_DUNGEON
                difficulty = 'hard'

            # Update config with party level
            config.party_level = party_level

            # Generate single-level dungeon
            dungeon_data = generator.generate(config)
            dungeon = Dungeon.load_from_generator(dungeon_data)

        # Type 5: Custom (includes multi-level and party-aware)
        elif dungeon_type == '5':
            # Get custom parameters
            num_rooms = data.get('num_rooms', 12)
            layout_type = data.get('layout_type', 'branching')
            num_levels = data.get('num_levels', 1)
            dungeon_theme = data.get('dungeon_theme', 'mine')
            seed = data.get('seed', None)

            # Party-aware interview results
            party_aware = data.get('party_aware', {})
            apl = party_aware.get('apl', 1)
            party_size = party_aware.get('party_size', 4)
            composition = party_aware.get('composition', 'balanced')
            magic_level = party_aware.get('magic_level', 'low')

            # Create config from interview results
            interview_results = {
                'apl': apl,
                'party_size': party_size,
                'composition': composition,
                'magic_level': magic_level
            }
            config = DungeonConfig.from_interview(interview_results)

            # Apply custom settings
            config.seed = seed
            config.num_rooms = num_rooms
            config.layout_type = layout_type
            config.dungeon_theme = dungeon_theme

            # Generate dungeon name
            if num_levels > 1:
                dungeon_name = f"The {dungeon_theme.capitalize()} Depths"
            else:
                dungeon_name = f"The Abandoned {dungeon_theme.capitalize()}"

            # Multi-level or single-level?
            if num_levels > 1:
                from aerthos.generator.multilevel_generator import MultiLevelGenerator

                ml_generator = MultiLevelGenerator()
                dungeon = ml_generator.generate(
                    num_levels=num_levels,
                    rooms_per_level=config.num_rooms,
                    dungeon_name=dungeon_name
                )
                difficulty = 'multilevel_custom'
            else:
                dungeon_data = generator.generate(config)
                dungeon = Dungeon.load_from_generator(dungeon_data)
                difficulty = 'custom'

        # Save scenario
        library = ScenarioLibrary()
        scenario_name = data.get('name', dungeon.name)
        description = data.get('description', '')

        scenario_id = library.save_scenario(dungeon, scenario_name, description, difficulty)

        return jsonify({'success': True, 'scenario_id': scenario_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/scenarios/<scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id):
    """Delete a scenario"""
    try:
        library = ScenarioLibrary()
        success = library.delete_scenario(scenario_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Scenario not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


# ============================================================================
# Session Manager API Endpoints
# ============================================================================

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions"""
    try:
        session_mgr = SessionManager()
        sessions = session_mgr.list_sessions()
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.json
        session_mgr = SessionManager()

        session_id = session_mgr.create_session(
            party_id=data.get('party_id'),
            scenario_id=data.get('scenario_id'),
            session_name=data.get('name')
        )

        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions/solo', methods=['POST'])
def create_solo_session():
    """Create a solo character session (auto-creates party)"""
    try:
        data = request.json
        session_mgr = SessionManager()
        roster = CharacterRoster()

        character_id = data.get('character_id')
        scenario_id = data.get('scenario_id')
        session_name = data.get('name')

        if not character_id:
            return jsonify({'success': False, 'error': 'Character ID required'})
        if not scenario_id:
            return jsonify({'success': False, 'error': 'Scenario ID required'})

        # Load character to get name
        character = roster.load_character(character_id=character_id)
        if not character:
            return jsonify({'success': False, 'error': 'Character not found'})

        # Create a solo party automatically
        solo_party_name = f"Solo: {character.name}"
        party_id = session_mgr.party_manager.save_party(
            solo_party_name,
            [character_id],
            ['front']
        )

        # Generate session name if not provided
        if not session_name:
            scenario_data = session_mgr.scenario_library.load_scenario(scenario_id)
            scenario_name = scenario_data['name'] if scenario_data else 'Unknown'
            session_name = f"{character.name} - {scenario_name}"

        # Create session
        session_id = session_mgr.create_session(
            party_id=party_id,
            scenario_id=scenario_id,
            session_name=session_name
        )

        return jsonify({'success': True, 'session_id': session_id})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    try:
        session_mgr = SessionManager()
        success = session_mgr.delete_session(session_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Session not found'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/sessions/<session_id>/load', methods=['POST'])
def load_session(session_id):
    """Load a game session for playing"""
    try:
        session_mgr = SessionManager()
        party_mgr = PartyManager()
        library = ScenarioLibrary()

        # Load session data
        session_data = session_mgr.load_session(session_id)
        if not session_data:
            return jsonify({'success': False, 'error': 'Session not found'})

        # Load party (returns dict with 'party' key containing Party object)
        party_data = party_mgr.load_party(party_id=session_data['party_id'])
        if not party_data:
            return jsonify({'success': False, 'error': 'Party not found'})
        party = party_data['party']

        # Load scenario
        scenario_data = library.load_scenario(session_data['scenario_id'])
        if not scenario_data:
            return jsonify({'success': False, 'error': 'Scenario not found'})

        # Create dungeon from scenario
        dungeon = library.create_dungeon_from_scenario(scenario_data)

        # Create game state
        game_state = GameState(party.members[0], dungeon)
        game_state.party = party
        game_state.load_game_data()

        # Restore session state if it exists
        if session_data.get('current_room_id'):
            game_state.current_room = dungeon.rooms.get(session_data['current_room_id'])

        # Store in active games
        web_session_id = 'session_' + session_id
        active_games[web_session_id] = game_state

        # Update session last played time (save_session_state expects game_state object)
        session_mgr.save_session_state(session_id, game_state)

        return jsonify({
            'success': True,
            'message': f"Resuming {session_data['name']}...",
            'state': get_game_state_json(game_state),
            'web_session_id': web_session_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("=" * 70)
    print("AERTHOS - Web Interface")
    print("=" * 70)
    print()
    print("Starting Flask server...")
    print("Visit: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
