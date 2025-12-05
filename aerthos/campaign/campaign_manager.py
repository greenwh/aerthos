"""
Campaign persistence manager
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json
import uuid

from .campaign import Campaign
from .episode import Episode


@dataclass
class CampaignSummary:
    """Summary of a saved campaign for list display"""
    id: str
    name: str
    description: str
    current_episode: str
    current_hub_id: str
    completed_episodes: List[str]
    unlocked_episodes: List[str]
    play_time: str  # Formatted string
    last_played: str  # Formatted string


class CampaignManager:
    """Handles campaign persistence

    Campaigns are saved to ~/.aerthos/campaigns/ as JSON files.
    """

    def __init__(self, save_dir: Optional[Path] = None):
        """Initialize campaign manager

        Args:
            save_dir: Optional custom save directory
        """
        if save_dir is None:
            # FIX: Use constants for consistency
            from ..constants import _AERTHOS_HOME
            self.save_dir = _AERTHOS_HOME / 'campaigns'
        else:
            self.save_dir = Path(save_dir)

        # Ensure directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def create_campaign(self, campaign_template_id: str, party_id: str,
                       data_dir: Optional[Path] = None) -> Campaign:
        """Create a new campaign from a template

        Args:
            campaign_template_id: Template identifier (e.g., 'serpents_shadow')
            party_id: ID of the party to use
            data_dir: Optional custom data directory

        Returns:
            New Campaign instance

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        # Load campaign template
        if data_dir is None:
            from ..constants import DATA_DIR
            data_dir = Path(DATA_DIR)

        template_file = data_dir / 'campaigns' / f'{campaign_template_id}.json'

        if not template_file.exists():
            raise FileNotFoundError(f"Campaign template not found: {template_file}")

        with open(template_file, 'r') as f:
            template = json.load(f)

        # Create campaign instance
        campaign = Campaign(
            id=str(uuid.uuid4()),
            name=template['name'],
            description=template['description'],
            party_id=party_id,
            current_episode_id=template['starting_episode'],
            current_hub_id=template['starting_hub'],
            completed_episodes=[],
            unlocked_episodes=[template['starting_episode']],  # Unlock first episode
            unlocked_hubs=[template['starting_hub']],  # Unlock starting hub
            story_flags={},
            reputation={faction_id: faction['starting_reputation']
                       for faction_id, faction in template.get('factions', {}).items()},
            play_time_minutes=0,
            created_at=datetime.now(),
            last_played=datetime.now()
        )

        # Save immediately
        self.save_campaign(campaign)

        return campaign

    def save_campaign(self, campaign: Campaign) -> str:
        """Save a campaign to disk

        Args:
            campaign: Campaign to save

        Returns:
            Campaign ID
        """
        # Update last played time
        campaign.last_played = datetime.now()

        # Serialize to JSON
        data = campaign.to_json()

        # Save to file
        filename = f"{campaign.id}.json"
        filepath = self.save_dir / filename

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return campaign.id

    def load_campaign(self, campaign_id: str) -> Campaign:
        """Load a campaign from disk

        Args:
            campaign_id: Campaign ID to load

        Returns:
            Campaign instance

        Raises:
            FileNotFoundError: If campaign doesn't exist
        """
        filename = f"{campaign_id}.json"
        filepath = self.save_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Campaign not found: {campaign_id}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        return Campaign.from_json(data)

    def list_campaigns(self) -> List[CampaignSummary]:
        """List all saved campaigns

        Returns:
            List of campaign summaries
        """
        summaries = []

        # Find all campaign JSON files
        for filepath in self.save_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                # Format play time
                hours = data.get('play_time_minutes', 0) // 60
                minutes = data.get('play_time_minutes', 0) % 60
                play_time = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

                # Format last played
                last_played_str = "Never"
                if data.get('last_played'):
                    last_played = datetime.fromisoformat(data['last_played'])
                    last_played_str = last_played.strftime('%Y-%m-%d %H:%M')

                summary = CampaignSummary(
                    id=data['id'],
                    name=data['name'],
                    description=data.get('description', ''),
                    current_episode=data.get('current_episode_id', ''),
                    current_hub_id=data.get('current_hub_id', ''),
                    completed_episodes=data.get('completed_episodes', []),
                    unlocked_episodes=data.get('unlocked_episodes', []),
                    play_time=play_time,
                    last_played=last_played_str
                )

                summaries.append(summary)

            except (json.JSONDecodeError, KeyError) as e:
                # Skip invalid files
                print(f"Warning: Skipping invalid campaign file {filepath}: {e}")
                continue

        # Sort by last played (most recent first)
        summaries.sort(key=lambda s: s.last_played, reverse=True)

        return summaries

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign

        Args:
            campaign_id: Campaign ID to delete

        Returns:
            True if deleted, False if not found
        """
        filename = f"{campaign_id}.json"
        filepath = self.save_dir / filename

        if filepath.exists():
            filepath.unlink()
            return True

        return False

    def campaign_exists(self, campaign_id: str) -> bool:
        """Check if a campaign exists

        Args:
            campaign_id: Campaign ID to check

        Returns:
            True if campaign exists, False otherwise
        """
        filename = f"{campaign_id}.json"
        filepath = self.save_dir / filename
        return filepath.exists()
