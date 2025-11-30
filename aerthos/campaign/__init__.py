"""
Campaign system for Aerthos

This module provides menu-driven campaign functionality with:
- Episode progression
- City hub navigation
- Story flag tracking
- Faction reputation
"""

from .campaign import Campaign
from .episode import Episode, EpisodeBriefing, DungeonReference, CompletionCriteria, EpisodeRewards
from .city_hub import CityHub, MenuOption, ShopConfig, InnConfig, TempleConfig, GuildConfig, NPC
from .campaign_manager import CampaignManager, CampaignSummary

__all__ = [
    'Campaign',
    'Episode',
    'EpisodeBriefing',
    'DungeonReference',
    'CompletionCriteria',
    'EpisodeRewards',
    'CityHub',
    'MenuOption',
    'ShopConfig',
    'InnConfig',
    'TempleConfig',
    'GuildConfig',
    'NPC',
    'CampaignManager',
    'CampaignSummary',
]
