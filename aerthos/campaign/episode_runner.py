"""
Episode Runner - Manages episode flow from intro to completion

Connects campaign episodes with hand-crafted dungeons and GameState.
"""

from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from .episode import Episode
from .campaign import Campaign
from ..entities.party import Party
from ..entities.player import PlayerCharacter
from ..engine.game_state import GameState, GameData
from ..world.dungeon import Dungeon
from ..engine.parser import CommandParser, Command


@dataclass
class EpisodeState:
    """Current state of an episode playthrough"""
    episode_id: str
    campaign_id: str
    party_id: str
    phase: str  # 'intro', 'briefing', 'dungeon', 'completed'
    dungeon_entered: bool = False
    completion_acknowledged: bool = False


class EpisodeRunner:
    """Manages episode progression from intro to completion

    Handles:
    - Episode intro and briefing display
    - Hand-crafted dungeon loading
    - Integration with GameState for dungeon play
    - Completion criteria checking
    - Reward application
    """

    def __init__(self, episode: Episode, campaign: Campaign, party: Party):
        """Initialize episode runner

        Args:
            episode: Episode to run
            campaign: Current campaign state
            party: Party playing the episode
        """
        self.episode = episode
        self.campaign = campaign
        self.party = party
        self.game_state: Optional[GameState] = None
        self.dungeon: Optional[Dungeon] = None

        # Episode state
        self.state = EpisodeState(
            episode_id=episode.id,
            campaign_id=campaign.id,
            party_id=campaign.party_id,  # Use campaign's party_id
            phase='intro'
        )

    def get_intro_text(self) -> str:
        """Get formatted intro text

        Returns:
            Formatted intro narrative
        """
        lines = [
            "=" * 70,
            f"EPISODE {self.episode.act}: {self.episode.title.upper()}",
            "=" * 70,
            "",
            self.episode.intro_text,
            "",
            "=" * 70,
        ]
        return "\n".join(lines)

    def get_briefing_text(self) -> str:
        """Get formatted briefing text

        Returns:
            Formatted quest briefing
        """
        briefing = self.episode.briefing

        lines = [
            "=" * 70,
            "QUEST BRIEFING",
            "=" * 70,
            "",
            f"Location: {briefing.location}",
            f"Quest Giver: {briefing.quest_giver}",
            "",
            "─" * 70,
            "",
            briefing.dialogue,
            "",
        ]

        # Add rumors if present (from episode, not briefing)
        if self.episode.rumors:
            lines.extend([
                "─" * 70,
                "RUMORS HEARD IN TOWN:",
                ""
            ])
            for rumor in self.episode.rumors:
                lines.append(f"  • {rumor}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def load_dungeon(self, data_dir: str = "aerthos/data") -> Tuple[bool, str]:
        """Load the episode's dungeon

        Args:
            data_dir: Base data directory

        Returns:
            (success, message) tuple
        """
        if self.episode.dungeon_config.type != 'hand_crafted':
            return False, "Only hand-crafted dungeons are supported in campaign mode."

        # Build path to dungeon file
        dungeon_path = Path(data_dir) / self.episode.dungeon_config.file

        if not dungeon_path.exists():
            return False, f"Dungeon file not found: {dungeon_path}"

        try:
            self.dungeon = Dungeon.load_from_file(str(dungeon_path))
            self.state.dungeon_entered = True
            self.state.phase = 'dungeon'
            return True, f"Loaded dungeon: {self.dungeon.name}"
        except Exception as e:
            return False, f"Error loading dungeon: {e}"

    def create_game_state(self, active_character: PlayerCharacter) -> Tuple[bool, str]:
        """Create GameState for dungeon play

        Args:
            active_character: The character currently controlled by player

        Returns:
            (success, message) tuple
        """
        if self.dungeon is None:
            return False, "No dungeon loaded. Call load_dungeon() first."

        try:
            self.game_state = GameState(active_character, self.dungeon)
            self.game_state.load_game_data()
            return True, "Game state initialized."
        except Exception as e:
            return False, f"Error creating game state: {e}"

    def check_completion(self) -> bool:
        """Check if episode completion criteria are met

        Returns:
            True if episode is complete
        """
        if self.game_state is None:
            return False

        criteria = self.episode.completion_criteria

        if criteria.type == 'boss_defeated':
            # Check if target monster was defeated
            # For now, we'll check the dungeon state
            # More sophisticated tracking could be added
            target = criteria.target

            # Check if boss monster is no longer alive in any room
            # This is a simplified check - more robust tracking recommended
            if hasattr(self.game_state, 'defeated_monsters'):
                return target in self.game_state.defeated_monsters

            # Alternative: Check if player has left dungeon victorious
            # For MVP, we'll return False and require manual completion
            return False

        elif criteria.type == 'item_retrieved':
            # Check if player has the target item
            target = criteria.target
            return self.game_state.player.inventory.has_item(target)

        elif criteria.type == 'location_reached':
            # Check if player reached target room
            target = criteria.target
            return self.game_state.current_room.id == target

        elif criteria.type == 'custom':
            # Custom criteria would need specialized handler
            # For now, return False
            return False

        return False

    def complete_episode(self) -> Tuple[bool, str]:
        """Mark episode as complete and apply rewards

        Returns:
            (success, message) tuple with completion text
        """
        if self.state.completion_acknowledged:
            return False, "Episode already completed."

        # Mark episode complete in campaign
        rewards_data = {
            'unlocks': self.episode.rewards.unlocks,
            'story_flags': self.episode.rewards.story_flags,
            'unlocked_hubs': self.episode.rewards.unlocks_hubs
        }

        self.campaign.complete_episode(self.episode.id, rewards_data)

        # Apply XP bonus to all living party members
        if self.episode.rewards.xp_bonus > 0:
            for member in self.party.members:
                if member.is_alive:
                    member.xp += self.episode.rewards.xp_bonus

        # Apply gold bonus to party leader
        if self.episode.rewards.gold_bonus > 0:
            self.party.members[0].gold += self.episode.rewards.gold_bonus

        # Add items to party leader's inventory
        if self.episode.rewards.items and self.game_state:
            for item_id in self.episode.rewards.items:
                # Would need GameData to create actual items
                # For now, just track the item IDs
                pass

        self.state.phase = 'completed'
        self.state.completion_acknowledged = True

        # Build completion message
        lines = [
            "=" * 70,
            "EPISODE COMPLETE!",
            "=" * 70,
            "",
            self.episode.completion_text,
            "",
            "REWARDS:",
            f"  • XP Bonus: {self.episode.rewards.xp_bonus} (shared among party)",
            f"  • Gold: {self.episode.rewards.gold_bonus} gp",
        ]

        if self.episode.rewards.items:
            lines.append(f"  • Items: {', '.join(self.episode.rewards.items)}")

        if self.episode.rewards.unlocks:
            lines.append(f"  • Unlocked Episodes: {', '.join(self.episode.rewards.unlocks)}")

        if self.episode.rewards.story_flags:
            lines.append(f"  • Story Flags: {', '.join(self.episode.rewards.story_flags)}")

        lines.append("")
        lines.append("=" * 70)

        return True, "\n".join(lines)

    def get_current_phase(self) -> str:
        """Get current episode phase

        Returns:
            Phase name: 'intro', 'briefing', 'dungeon', 'completed'
        """
        return self.state.phase

    def advance_to_briefing(self) -> None:
        """Advance from intro to briefing phase"""
        if self.state.phase == 'intro':
            self.state.phase = 'briefing'

    def is_complete(self) -> bool:
        """Check if episode is in completed state

        Returns:
            True if episode is completed
        """
        return self.state.phase == 'completed'
