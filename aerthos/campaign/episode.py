"""
Episode classes for campaign progression
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


@dataclass
class EpisodeBriefing:
    """Quest briefing information"""
    quest_giver: str
    location: str
    dialogue: str


@dataclass
class DungeonReference:
    """Reference to a dungeon (hand-crafted or procedural)"""
    type: str  # 'hand_crafted' or 'procedural'
    file: Optional[str] = None  # Path to JSON file if hand_crafted
    name: Optional[str] = None
    theme: Optional[str] = None
    levels: int = 1
    boss: Optional[str] = None
    # For procedural generation
    num_rooms: Optional[int] = None
    seed: Optional[int] = None


@dataclass
class CompletionCriteria:
    """Defines how an episode is completed"""
    type: str  # 'boss_defeated', 'item_found', 'room_reached', 'all_cleared'
    target: str  # monster_id, item_id, room_id, or None


@dataclass
class EpisodeRewards:
    """Rewards granted upon episode completion"""
    xp_bonus: int = 0
    gold_bonus: int = 0
    items: List[str] = field(default_factory=list)  # item IDs
    unlocks: List[str] = field(default_factory=list)  # episode IDs
    story_flags: List[str] = field(default_factory=list)  # flags to set
    unlocks_hubs: List[str] = field(default_factory=list)  # hub IDs


@dataclass
class Episode:
    """Defines an episode's content and structure

    An episode is a single narrative unit in a campaign, typically
    involving a dungeon crawl with story context, objectives, and rewards.
    """

    id: str
    title: str
    act: int
    recommended_level: int
    hub_id: str
    intro_text: str
    briefing: EpisodeBriefing
    dungeon_config: DungeonReference
    completion_criteria: CompletionCriteria
    completion_text: str
    rewards: EpisodeRewards
    rumors: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)  # episode IDs

    @classmethod
    def load(cls, episode_id: str, data_dir: Optional[Path] = None) -> 'Episode':
        """Load an episode from JSON file

        Args:
            episode_id: Episode identifier (e.g., 'episode_01')
            data_dir: Optional custom data directory

        Returns:
            Episode instance

        Raises:
            FileNotFoundError: If episode file doesn't exist
            ValueError: If JSON is invalid
        """
        if data_dir is None:
            # Use default data directory from constants
            from ..constants import DATA_DIR
            data_dir = Path(DATA_DIR)

        episode_file = data_dir / 'episodes' / f'{episode_id}.json'

        if not episode_file.exists():
            raise FileNotFoundError(f"Episode file not found: {episode_file}")

        with open(episode_file, 'r') as f:
            data = json.load(f)

        return cls.from_json(data)

    @classmethod
    def from_json(cls, data: dict) -> 'Episode':
        """Deserialize episode from JSON dictionary

        Args:
            data: Dictionary from JSON file

        Returns:
            Episode instance
        """
        # Parse briefing
        briefing = EpisodeBriefing(
            quest_giver=data['briefing']['quest_giver'],
            location=data['briefing']['location'],
            dialogue=data['briefing']['dialogue']
        )

        # Parse dungeon config
        dungeon_data = data['dungeon']
        dungeon_config = DungeonReference(
            type=dungeon_data['type'],
            file=dungeon_data.get('file'),
            name=dungeon_data.get('name'),
            theme=dungeon_data.get('theme'),
            levels=dungeon_data.get('levels', 1),
            boss=dungeon_data.get('boss'),
            num_rooms=dungeon_data.get('num_rooms'),
            seed=dungeon_data.get('seed')
        )

        # Parse completion criteria
        criteria_data = data['completion_criteria']
        completion_criteria = CompletionCriteria(
            type=criteria_data['type'],
            target=criteria_data['target']
        )

        # Parse rewards
        rewards_data = data['rewards']
        rewards = EpisodeRewards(
            xp_bonus=rewards_data.get('xp_bonus', 0),
            gold_bonus=rewards_data.get('gold_bonus', 0),
            items=rewards_data.get('items', []),
            unlocks=rewards_data.get('unlocks', []),
            story_flags=rewards_data.get('story_flags', []),
            unlocks_hubs=rewards_data.get('unlocks_hubs', [])
        )

        return cls(
            id=data['id'],
            title=data['title'],
            act=data['act'],
            recommended_level=data['recommended_level'],
            hub_id=data['hub_id'],
            intro_text=data['intro_text'],
            briefing=briefing,
            dungeon_config=dungeon_config,
            completion_criteria=completion_criteria,
            completion_text=data['completion_text'],
            rewards=rewards,
            rumors=data.get('rumors', []),
            prerequisites=data.get('prerequisites', [])
        )

    def to_json(self) -> dict:
        """Serialize episode to JSON-compatible dictionary

        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            'id': self.id,
            'title': self.title,
            'act': self.act,
            'recommended_level': self.recommended_level,
            'hub_id': self.hub_id,
            'intro_text': self.intro_text,
            'briefing': {
                'quest_giver': self.briefing.quest_giver,
                'location': self.briefing.location,
                'dialogue': self.briefing.dialogue
            },
            'dungeon': {
                'type': self.dungeon_config.type,
                'file': self.dungeon_config.file,
                'name': self.dungeon_config.name,
                'theme': self.dungeon_config.theme,
                'levels': self.dungeon_config.levels,
                'boss': self.dungeon_config.boss,
                'num_rooms': self.dungeon_config.num_rooms,
                'seed': self.dungeon_config.seed
            },
            'completion_criteria': {
                'type': self.completion_criteria.type,
                'target': self.completion_criteria.target
            },
            'completion_text': self.completion_text,
            'rewards': {
                'xp_bonus': self.rewards.xp_bonus,
                'gold_bonus': self.rewards.gold_bonus,
                'items': self.rewards.items,
                'unlocks': self.rewards.unlocks,
                'story_flags': self.rewards.story_flags,
                'unlocks_hubs': self.rewards.unlocks_hubs
            },
            'rumors': self.rumors,
            'prerequisites': self.prerequisites
        }

    def check_prerequisites(self, campaign: 'Campaign') -> bool:
        """Check if all prerequisites are met

        Args:
            campaign: Current campaign state

        Returns:
            True if all prerequisites are met, False otherwise
        """
        for prereq_id in self.prerequisites:
            if not campaign.is_episode_completed(prereq_id):
                return False
        return True
