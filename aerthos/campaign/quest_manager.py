"""
Quest Manager for Aerthos Campaign

Manages side quest tracking, triggering, and completion across episodes.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from .side_quest import SideQuest, TriggerType, ObjectiveType


class QuestManager:
    """
    Manages side quests for the campaign

    Handles quest discovery, activation, tracking, and completion.
    """

    def __init__(self, quest_data_path: Optional[str] = None):
        """
        Initialize Quest Manager

        Args:
            quest_data_path: Path to side_quests.json (defaults to data/side_quests.json)
        """
        if quest_data_path is None:
            from ..constants import DATA_DIR
            quest_data_path = f"{DATA_DIR}/side_quests.json"

        self.quest_data_path = quest_data_path
        self.all_quests: Dict[str, SideQuest] = {}  # All quests by ID
        self.episode_quests: Dict[str, List[str]] = {}  # Quest IDs by episode

        self._load_quests()

    def _load_quests(self) -> None:
        """Load quest data from JSON file"""
        try:
            with open(self.quest_data_path, 'r') as f:
                quest_data = json.load(f)

            for quest_id, data in quest_data.items():
                quest = SideQuest.from_json_data(quest_id, data)
                self.all_quests[quest_id] = quest

                # Index by episode
                episode_id = quest.episode_id
                if episode_id not in self.episode_quests:
                    self.episode_quests[episode_id] = []
                self.episode_quests[episode_id].append(quest_id)

        except FileNotFoundError:
            # No quests defined yet - this is OK
            pass
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid quest data JSON: {e}")

    def get_quests_for_episode(self, episode_id: str) -> List[SideQuest]:
        """
        Get all quests for a specific episode

        Args:
            episode_id: Episode identifier

        Returns:
            List of SideQuests for that episode
        """
        quest_ids = self.episode_quests.get(episode_id, [])
        return [self.all_quests[qid] for qid in quest_ids]

    def get_active_quests(self) -> List[SideQuest]:
        """Get all currently active quests"""
        return [q for q in self.all_quests.values() if q.active]

    def get_completed_quests(self) -> List[SideQuest]:
        """Get all completed quests"""
        return [q for q in self.all_quests.values() if q.completed]

    def get_quest_by_id(self, quest_id: str) -> Optional[SideQuest]:
        """Get a specific quest by ID"""
        return self.all_quests.get(quest_id)

    def check_triggers(self, event_type: str, event_data: Dict[str, Any], episode_id: str) -> List[SideQuest]:
        """
        Check if any quests should be triggered by an event

        Args:
            event_type: Type of event (enter_room, find_item, etc.)
            event_data: Event-specific data
            episode_id: Current episode ID

        Returns:
            List of quests that were triggered
        """
        triggered = []

        # Only check quests for current episode
        for quest in self.get_quests_for_episode(episode_id):
            if quest.check_trigger(event_type, event_data):
                quest.activate()
                triggered.append(quest)

        return triggered

    def update_quest_objectives(self, objective_type: str, target: Optional[str] = None) -> List[tuple[SideQuest, List[str]]]:
        """
        Update objectives for all active quests

        Args:
            objective_type: Type of objective event (kill_monster, collect_item, etc.)
            target: Target of event (monster ID, item ID, etc.)

        Returns:
            List of (quest, updated_objective_ids) tuples
        """
        updated = []

        for quest in self.get_active_quests():
            objective_ids = quest.check_objective_event(objective_type, target)
            if objective_ids:
                updated.append((quest, objective_ids))

        return updated

    def check_completions(self) -> List[SideQuest]:
        """
        Check all active quests for completion

        Returns:
            List of quests that were just completed
        """
        completed = []

        for quest in self.get_active_quests():
            if quest.check_completion():
                completed.append(quest)

        return completed

    def get_quest_progress(self, quest_id: str) -> Optional[str]:
        """
        Get human-readable progress for a quest

        Args:
            quest_id: Quest identifier

        Returns:
            Progress text, or None if quest not found
        """
        quest = self.get_quest_by_id(quest_id)
        if quest:
            return quest.get_progress_text()
        return None

    def reset_episode_quests(self, episode_id: str) -> None:
        """
        Reset all quests for an episode (for retrying episode)

        Args:
            episode_id: Episode to reset quests for
        """
        for quest in self.get_quests_for_episode(episode_id):
            if not quest.repeatable and quest.completed:
                continue  # Don't reset non-repeatable completed quests

            quest.discovered = False
            quest.active = False
            quest.completed = False
            quest.failed = False

            for obj in quest.objectives:
                obj.current = 0
                obj.completed = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize quest state to dictionary for saving

        Returns:
            Dictionary of quest states
        """
        return {
            quest_id: quest.to_dict()
            for quest_id, quest in self.all_quests.items()
            if quest.discovered  # Only save quests that have been discovered
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load quest state from dictionary

        Args:
            data: Dictionary of quest states from save file
        """
        for quest_id, quest_data in data.items():
            if quest_id in self.all_quests:
                # Update existing quest with saved state
                saved_quest = SideQuest.from_dict(quest_data)

                # Copy state from saved quest
                quest = self.all_quests[quest_id]
                quest.discovered = saved_quest.discovered
                quest.active = saved_quest.active
                quest.completed = saved_quest.completed
                quest.failed = saved_quest.failed

                # Update objectives
                for saved_obj in saved_quest.objectives:
                    for obj in quest.objectives:
                        if obj.id == saved_obj.id:
                            obj.current = saved_obj.current
                            obj.completed = saved_obj.completed
                            break

    def get_summary_stats(self) -> Dict[str, int]:
        """
        Get summary statistics about quests

        Returns:
            Dictionary with quest stats
        """
        return {
            'total_quests': len(self.all_quests),
            'discovered': sum(1 for q in self.all_quests.values() if q.discovered),
            'active': sum(1 for q in self.all_quests.values() if q.active),
            'completed': sum(1 for q in self.all_quests.values() if q.completed),
            'failed': sum(1 for q in self.all_quests.values() if q.failed),
            'available': sum(1 for q in self.all_quests.values() if not q.discovered)
        }

    def get_total_rewards(self) -> Dict[str, Any]:
        """
        Calculate total rewards from completed quests

        Returns:
            Dictionary with total XP, gold, items, reputation
        """
        total_xp = 0
        total_gold = 0
        total_items = []
        total_reputation = 0

        for quest in self.get_completed_quests():
            total_xp += quest.rewards.xp
            total_gold += quest.rewards.gold
            total_items.extend(quest.rewards.items)
            total_reputation += quest.rewards.reputation

        return {
            'xp': total_xp,
            'gold': total_gold,
            'items': total_items,
            'reputation': total_reputation
        }
