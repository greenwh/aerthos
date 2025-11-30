"""
City Hub classes for menu-driven navigation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


@dataclass
class ShopConfig:
    """Configuration for a shop in a city hub"""
    id: str
    name: str
    type: str  # 'general', 'weapons_armor', 'magic', etc.
    specialty: str
    buy_rate: float = 0.4  # How much shop pays for items (40% default)
    inventory: List[str] = field(default_factory=list)  # item IDs
    price_modifier: float = 1.0  # Price multiplier (1.5 = 50% more expensive)
    quality_bonus: Optional[str] = None  # e.g., "+1 durability"


@dataclass
class InnConfig:
    """Configuration for an inn/tavern"""
    id: str
    name: str
    description: str
    rate_per_night: int  # Gold per person per night
    services: List[str] = field(default_factory=list)  # 'rest', 'rumors', 'hirelings'
    rumors_by_episode: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class TempleConfig:
    """Configuration for a temple"""
    id: str
    name: str
    deity: str
    alignment: str
    services: List[str] = field(default_factory=list)  # Service IDs
    donation_suggested: bool = True


@dataclass
class GuildConfig:
    """Configuration for a guild"""
    id: str
    name: str
    guild_type: str  # 'fighters', 'mages', 'thieves', etc.
    services: List[str] = field(default_factory=list)


@dataclass
class NPC:
    """Non-player character"""
    name: str
    role: str
    alignment: str
    description: str
    dialogue: Dict[str, str] = field(default_factory=dict)  # context -> dialogue


@dataclass
class MenuOption:
    """A menu option in the city hub"""
    id: str
    name: str
    description: Optional[str]
    action: str  # Action identifier
    data: Dict[str, Any] = field(default_factory=dict)  # Additional data


@dataclass
class CityHub:
    """Represents a city/town the party can visit

    A city hub is the main navigation point for campaign mode,
    providing access to shops, inns, temples, and dungeons.
    """

    id: str
    name: str
    description: str
    theme: str
    region: str

    # Services (references to existing systems)
    shops: List[ShopConfig] = field(default_factory=list)
    inn: Optional[InnConfig] = None
    temple: Optional[TempleConfig] = None
    guild: Optional[GuildConfig] = None

    # NPCs and content
    npcs: Dict[str, NPC] = field(default_factory=dict)
    available_quests: List[str] = field(default_factory=list)  # Episode IDs
    special_rules: Dict[str, Any] = field(default_factory=dict)  # Gate tolls, restrictions

    @classmethod
    def load(cls, hub_id: str, data_dir: Optional[Path] = None) -> 'CityHub':
        """Load a city hub from JSON file

        Args:
            hub_id: Hub identifier (e.g., 'oakhaven')
            data_dir: Optional custom data directory

        Returns:
            CityHub instance

        Raises:
            FileNotFoundError: If hub file doesn't exist
            ValueError: If JSON is invalid
        """
        if data_dir is None:
            # Use default data directory from constants
            from ..constants import DATA_DIR
            data_dir = Path(DATA_DIR)

        hub_file = data_dir / 'cities' / f'{hub_id}.json'

        if not hub_file.exists():
            raise FileNotFoundError(f"City hub file not found: {hub_file}")

        with open(hub_file, 'r') as f:
            data = json.load(f)

        return cls.from_json(data)

    @classmethod
    def from_json(cls, data: dict) -> 'CityHub':
        """Deserialize city hub from JSON dictionary

        Args:
            data: Dictionary from JSON file

        Returns:
            CityHub instance
        """
        # Parse shops
        shops = []
        for shop_data in data.get('shops', []):
            shop = ShopConfig(
                id=shop_data['id'],
                name=shop_data['name'],
                type=shop_data['type'],
                specialty=shop_data['specialty'],
                buy_rate=shop_data.get('buy_rate', 0.4),
                inventory=shop_data.get('inventory', []),
                price_modifier=shop_data.get('price_modifier', 1.0),
                quality_bonus=shop_data.get('quality_bonus')
            )
            shops.append(shop)

        # Parse inn
        inn = None
        if data.get('inn'):
            inn_data = data['inn']
            inn = InnConfig(
                id=inn_data['id'],
                name=inn_data['name'],
                description=inn_data['description'],
                rate_per_night=inn_data['rate_per_night'],
                services=inn_data.get('services', []),
                rumors_by_episode=inn_data.get('rumors_by_episode', {})
            )

        # Parse temple
        temple = None
        if data.get('temple'):
            temple_data = data['temple']
            temple = TempleConfig(
                id=temple_data['id'],
                name=temple_data['name'],
                deity=temple_data['deity'],
                alignment=temple_data['alignment'],
                services=temple_data.get('services', []),
                donation_suggested=temple_data.get('donation_suggested', True)
            )

        # Parse guild
        guild = None
        if data.get('guild'):
            guild_data = data['guild']
            guild = GuildConfig(
                id=guild_data['id'],
                name=guild_data['name'],
                guild_type=guild_data['guild_type'],
                services=guild_data.get('services', [])
            )

        # Parse NPCs
        npcs = {}
        for npc_id, npc_data in data.get('npcs', {}).items():
            npc = NPC(
                name=npc_data['name'],
                role=npc_data['role'],
                alignment=npc_data['alignment'],
                description=npc_data['description'],
                dialogue=npc_data.get('dialogue', {})
            )
            npcs[npc_id] = npc

        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            theme=data['theme'],
            region=data['region'],
            shops=shops,
            inn=inn,
            temple=temple,
            guild=guild,
            npcs=npcs,
            available_quests=data.get('available_quests', []),
            special_rules=data.get('special_rules', {})
        )

    def to_json(self) -> dict:
        """Serialize city hub to JSON-compatible dictionary

        Returns:
            Dictionary suitable for JSON serialization
        """
        # Serialize shops
        shops_data = []
        for shop in self.shops:
            shops_data.append({
                'id': shop.id,
                'name': shop.name,
                'type': shop.type,
                'specialty': shop.specialty,
                'buy_rate': shop.buy_rate,
                'inventory': shop.inventory,
                'price_modifier': shop.price_modifier,
                'quality_bonus': shop.quality_bonus
            })

        # Serialize inn
        inn_data = None
        if self.inn:
            inn_data = {
                'id': self.inn.id,
                'name': self.inn.name,
                'description': self.inn.description,
                'rate_per_night': self.inn.rate_per_night,
                'services': self.inn.services,
                'rumors_by_episode': self.inn.rumors_by_episode
            }

        # Serialize temple
        temple_data = None
        if self.temple:
            temple_data = {
                'id': self.temple.id,
                'name': self.temple.name,
                'deity': self.temple.deity,
                'alignment': self.temple.alignment,
                'services': self.temple.services,
                'donation_suggested': self.temple.donation_suggested
            }

        # Serialize guild
        guild_data = None
        if self.guild:
            guild_data = {
                'id': self.guild.id,
                'name': self.guild.name,
                'guild_type': self.guild.guild_type,
                'services': self.guild.services
            }

        # Serialize NPCs
        npcs_data = {}
        for npc_id, npc in self.npcs.items():
            npcs_data[npc_id] = {
                'name': npc.name,
                'role': npc.role,
                'alignment': npc.alignment,
                'description': npc.description,
                'dialogue': npc.dialogue
            }

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'theme': self.theme,
            'region': self.region,
            'shops': shops_data,
            'inn': inn_data,
            'temple': temple_data,
            'guild': guild_data,
            'npcs': npcs_data,
            'available_quests': self.available_quests,
            'special_rules': self.special_rules
        }

    def get_available_episodes(self, campaign: 'Campaign') -> List[str]:
        """Get list of episode IDs available from this hub

        Args:
            campaign: Current campaign state

        Returns:
            List of unlocked episode IDs available from this hub
        """
        available = []
        for episode_id in self.available_quests:
            if campaign.is_episode_unlocked(episode_id):
                available.append(episode_id)
        return available
