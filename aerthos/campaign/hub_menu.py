"""
Hub Menu System for menu-driven city navigation in campaign mode
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

from .campaign import Campaign
from .city_hub import CityHub, MenuOption
from .episode import Episode
from ..entities.party import Party


@dataclass
class HubMenuResult:
    """Result of a menu action"""
    success: bool
    message: str
    next_state: Optional[str] = None  # 'hub', 'dungeon', 'save_and_exit', etc.
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class HubMenuSystem:
    """Handles the menu-driven city hub interface

    Provides a text-based menu for navigating city services,
    managing party, and selecting episodes/dungeons.
    """

    def __init__(self, campaign: Campaign, party: Party):
        """Initialize hub menu system

        Args:
            campaign: Current campaign state
            party: Party in the campaign
        """
        self.campaign = campaign
        self.party = party
        self.current_hub: Optional[CityHub] = None
        self._load_current_hub()

    def _load_current_hub(self):
        """Load the current hub based on campaign state"""
        try:
            self.current_hub = CityHub.load(self.campaign.current_hub_id)
        except FileNotFoundError:
            print(f"Warning: Could not load hub {self.campaign.current_hub_id}")
            self.current_hub = None

    def display_hub_menu(self) -> str:
        """Generate the hub menu display

        Returns:
            Formatted menu string
        """
        if self.current_hub is None:
            return "Error: No hub loaded."

        lines = [
            f"╔{'═' * 68}╗",
            f"║  CAMPAIGN: {self.campaign.name:<55}║",
            f"║  {self._get_episode_display():<66}║",
            f"╠{'═' * 68}╣",
            f"║                                                                    ║",
            f"║  {self.current_hub.name.upper()} - {self.current_hub.theme:<43}║",
            f"║  {'─' * 64}  ║",
            f"║                                                                    ║",
        ]

        # Add menu options
        options = self.get_menu_options()
        for i, option in enumerate(options, 1):
            # Main option line
            option_text = f"{i}. {option.name}"
            lines.append(f"║  {option_text:<66}║")

            # Description line (if present)
            if option.description:
                desc_text = f"   • {option.description}"
                lines.append(f"║  {desc_text:<66}║")

            # Spacing
            lines.append(f"║  {'':<66}║")

        # Footer
        lines.extend([
            f"║  s. Save Campaign Progress{'':<40}║",
            f"║  0. Save & Exit Campaign{'':<42}║",
            f"║  {'':<66}║",
            f"╚{'═' * 68}╝",
        ])

        return '\n'.join(lines)

    def _get_episode_display(self) -> str:
        """Get current episode status for header

        Returns:
            Episode status string
        """
        if not self.campaign.current_episode_id:
            return "No active episode"

        try:
            episode = Episode.load(self.campaign.current_episode_id)
            if self.campaign.is_episode_completed(episode.id):
                return f"Episode {episode.act}: {episode.title} [COMPLETED]"
            else:
                return f"Episode {episode.act}: {episode.title} [IN PROGRESS]"
        except:
            return f"Episode: {self.campaign.current_episode_id}"

    def get_menu_options(self) -> List[MenuOption]:
        """Build menu options based on hub and campaign state

        Returns:
            List of available menu options
        """
        if self.current_hub is None:
            return []

        options = []

        # Add inn if available
        if self.current_hub.inn:
            options.append(MenuOption(
                id='inn',
                name=self.current_hub.inn.name,
                description=f"Rest and recover ({self.current_hub.inn.rate_per_night}gp/person/night)",
                action='enter_inn'
            ))

        # Add shops
        for shop_config in self.current_hub.shops:
            options.append(MenuOption(
                id=f'shop_{shop_config.id}',
                name=shop_config.name,
                description=shop_config.specialty,
                action='enter_shop',
                data={'shop_id': shop_config.id, 'shop_config': shop_config}
            ))

        # Add temple if available
        if self.current_hub.temple:
            options.append(MenuOption(
                id='temple',
                name=self.current_hub.temple.name,
                description="Healing and divine services",
                action='enter_temple'
            ))

        # Add guild if available
        if self.current_hub.guild:
            options.append(MenuOption(
                id='guild',
                name=self.current_hub.guild.name,
                description=f"{self.current_hub.guild.guild_type.capitalize()} guild services",
                action='enter_guild'
            ))

        # Add travel/dungeon options
        travel_option = self._build_travel_option()
        if travel_option:
            options.append(travel_option)

        # Add party management
        options.append(MenuOption(
            id='party',
            name='Party Management',
            description='View party status and manage equipment',
            action='manage_party'
        ))

        # Add journal
        options.append(MenuOption(
            id='journal',
            name='Campaign Journal',
            description='View completed episodes and story progress',
            action='view_journal'
        ))

        return options

    def _build_travel_option(self) -> Optional[MenuOption]:
        """Build the travel/dungeon option with available destinations

        Returns:
            MenuOption for travel, or None if no destinations available
        """
        if self.current_hub is None:
            return None

        available_episodes = self.current_hub.get_available_episodes(self.campaign)
        if not available_episodes:
            return None

        # Count episode statuses
        completed = sum(1 for ep_id in available_episodes
                       if self.campaign.is_episode_completed(ep_id))
        in_progress = 1 if self.campaign.current_episode_id in available_episodes else 0
        available_count = len(available_episodes) - completed

        desc_parts = []
        if available_count > 0:
            desc_parts.append(f"{available_count} quest(s) available")
        if completed > 0:
            desc_parts.append(f"{completed} completed")

        description = ", ".join(desc_parts) if desc_parts else "No quests available"

        return MenuOption(
            id='travel',
            name='Town Gate / Travel',
            description=description,
            action='travel_menu',
            data={
                'available_episodes': available_episodes,
                'completed': [ep_id for ep_id in available_episodes
                            if self.campaign.is_episode_completed(ep_id)]
            }
        )

    def handle_choice(self, choice: int) -> HubMenuResult:
        """Process menu choice

        Args:
            choice: Menu option number (0 = exit)

        Returns:
            HubMenuResult with outcome
        """
        # Handle exit
        if choice == 0:
            return HubMenuResult(
                success=True,
                message="Saving campaign...",
                next_state='save_and_exit'
            )

        # Validate choice
        options = self.get_menu_options()
        if choice < 1 or choice > len(options):
            return HubMenuResult(
                success=False,
                message="Invalid choice.",
                next_state='hub'
            )

        # Execute action
        option = options[choice - 1]
        return self._execute_action(option)

    def _execute_action(self, option: MenuOption) -> HubMenuResult:
        """Execute the selected menu action

        Args:
            option: Selected menu option

        Returns:
            HubMenuResult
        """
        action = option.action

        if action == 'enter_inn':
            return HubMenuResult(
                success=True,
                message=f"Entering {self.current_hub.inn.name}...",
                next_state='inn',
                data={'inn_config': self.current_hub.inn}
            )

        elif action == 'enter_shop':
            shop_config = option.data.get('shop_config')
            return HubMenuResult(
                success=True,
                message=f"Entering {shop_config.name}...",
                next_state='shop',
                data={'shop_config': shop_config}
            )

        elif action == 'enter_temple':
            return HubMenuResult(
                success=True,
                message=f"Entering {self.current_hub.temple.name}...",
                next_state='temple',
                data={'temple_config': self.current_hub.temple}
            )

        elif action == 'enter_guild':
            return HubMenuResult(
                success=True,
                message=f"Entering {self.current_hub.guild.name}...",
                next_state='guild',
                data={'guild_config': self.current_hub.guild}
            )

        elif action == 'travel_menu':
            return HubMenuResult(
                success=True,
                message="Opening travel menu...",
                next_state='travel',
                data=option.data
            )

        elif action == 'manage_party':
            return HubMenuResult(
                success=True,
                message="Party management...",
                next_state='party_management'
            )

        elif action == 'view_journal':
            return HubMenuResult(
                success=True,
                message="Campaign journal...",
                next_state='journal'
            )

        else:
            return HubMenuResult(
                success=False,
                message=f"Unknown action: {action}",
                next_state='hub'
            )

    def get_travel_destinations(self) -> List[Dict[str, Any]]:
        """Get list of travel destinations with status

        Returns:
            List of destination dictionaries
        """
        if self.current_hub is None:
            return []

        destinations = []
        available_episodes = self.current_hub.get_available_episodes(self.campaign)

        for ep_id in available_episodes:
            try:
                episode = Episode.load(ep_id)

                # Determine status
                if self.campaign.is_episode_completed(ep_id):
                    status = 'COMPLETED'
                elif ep_id == self.campaign.current_episode_id:
                    status = 'CURRENT'
                else:
                    status = 'AVAILABLE'

                destinations.append({
                    'episode_id': ep_id,
                    'title': episode.title,
                    'dungeon_name': episode.dungeon_config.name,
                    'recommended_level': episode.recommended_level,
                    'status': status
                })
            except:
                continue

        return destinations
