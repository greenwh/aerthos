"""
Campaign class for tracking campaign playthrough state
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json


@dataclass
class Campaign:
    """Represents a campaign playthrough state

    A campaign tracks the player's progress through a series of episodes,
    their current location in the world, completed objectives, story flags,
    and faction relationships.
    """

    id: str
    name: str
    description: str
    party_id: str                           # Reference to saved party
    current_episode_id: str
    current_hub_id: str
    completed_episodes: List[str] = field(default_factory=list)
    unlocked_episodes: List[str] = field(default_factory=list)
    unlocked_hubs: List[str] = field(default_factory=list)
    story_flags: Dict[str, bool] = field(default_factory=dict)
    reputation: Dict[str, int] = field(default_factory=dict)  # Faction reputation scores
    active_session_id: Optional[str] = None  # ID of the active dungeon session (if any)
    play_time_minutes: int = 0
    created_at: Optional[datetime] = None
    last_played: Optional[datetime] = None

    def __post_init__(self):
        """Initialize timestamps if not set"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_played is None:
            self.last_played = datetime.now()

    def is_episode_unlocked(self, episode_id: str) -> bool:
        """Check if an episode is unlocked and available to play

        Args:
            episode_id: Episode identifier to check

        Returns:
            True if episode is unlocked, False otherwise
        """
        return episode_id in self.unlocked_episodes

    def is_episode_completed(self, episode_id: str) -> bool:
        """Check if an episode has been completed

        Args:
            episode_id: Episode identifier to check

        Returns:
            True if episode is completed, False otherwise
        """
        return episode_id in self.completed_episodes

    def is_hub_unlocked(self, hub_id: str) -> bool:
        """Check if a city hub is unlocked and accessible

        Args:
            hub_id: City hub identifier to check

        Returns:
            True if hub is unlocked, False otherwise
        """
        return hub_id in self.unlocked_hubs

    def complete_episode(self, episode_id: str, rewards: dict) -> None:
        """Mark an episode as completed and apply rewards

        Args:
            episode_id: Episode to mark as completed
            rewards: Rewards dictionary containing:
                - unlocks: List of episode IDs to unlock
                - story_flags: List of flags to set
                - (XP and gold handled by party/characters directly)
        """
        # Mark as completed
        if episode_id not in self.completed_episodes:
            self.completed_episodes.append(episode_id)

        # Unlock new episodes
        if 'unlocks' in rewards:
            for unlock_id in rewards['unlocks']:
                if unlock_id not in self.unlocked_episodes:
                    self.unlocked_episodes.append(unlock_id)

        # Set story flags
        if 'story_flags' in rewards:
            for flag in rewards['story_flags']:
                self.story_flags[flag] = True

        # Unlock new hubs if specified
        if 'unlocks_hubs' in rewards:
            for hub_id in rewards['unlocks_hubs']:
                if hub_id not in self.unlocked_hubs:
                    self.unlocked_hubs.append(hub_id)

        # Update last played time
        self.last_played = datetime.now()

    def set_story_flag(self, flag: str, value: bool = True) -> None:
        """Set a story flag

        Args:
            flag: Flag name
            value: Flag value (default True)
        """
        self.story_flags[flag] = value

    def get_story_flag(self, flag: str, default: bool = False) -> bool:
        """Get a story flag value

        Args:
            flag: Flag name
            default: Default value if flag not set

        Returns:
            Flag value or default
        """
        return self.story_flags.get(flag, default)

    def modify_reputation(self, faction: str, delta: int) -> None:
        """Modify reputation with a faction

        Args:
            faction: Faction identifier
            delta: Amount to add (positive) or subtract (negative)
        """
        current = self.reputation.get(faction, 0)
        self.reputation[faction] = current + delta

    def get_reputation(self, faction: str) -> int:
        """Get current reputation with a faction

        Args:
            faction: Faction identifier

        Returns:
            Reputation score (default 0)
        """
        return self.reputation.get(faction, 0)

    def update_play_time(self, minutes: int) -> None:
        """Add to total play time

        Args:
            minutes: Minutes to add to play time
        """
        self.play_time_minutes += minutes
        self.last_played = datetime.now()

    def to_json(self) -> dict:
        """Serialize campaign to JSON-compatible dictionary

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'party_id': self.party_id,
            'current_episode_id': self.current_episode_id,
            'current_hub_id': self.current_hub_id,
            'completed_episodes': self.completed_episodes,
            'unlocked_episodes': self.unlocked_episodes,
            'unlocked_hubs': self.unlocked_hubs,
            'story_flags': self.story_flags,
            'reputation': self.reputation,
            'active_session_id': self.active_session_id,
            'play_time_minutes': self.play_time_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_played': self.last_played.isoformat() if self.last_played else None,
        }

    @classmethod
    def from_json(cls, data: dict) -> 'Campaign':
        """Deserialize campaign from JSON dictionary

        Args:
            data: Dictionary from JSON file

        Returns:
            Campaign instance
        """
        # Parse timestamps
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])

        last_played = None
        if data.get('last_played'):
            last_played = datetime.fromisoformat(data['last_played'])

        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            party_id=data['party_id'],
            current_episode_id=data['current_episode_id'],
            current_hub_id=data['current_hub_id'],
            completed_episodes=data.get('completed_episodes', []),
            unlocked_episodes=data.get('unlocked_episodes', []),
            unlocked_hubs=data.get('unlocked_hubs', []),
            story_flags=data.get('story_flags', {}),
            reputation=data.get('reputation', {}),
            active_session_id=data.get('active_session_id'),
            play_time_minutes=data.get('play_time_minutes', 0),
            created_at=created_at,
            last_played=last_played,
        )
