"""
Side Quest System for Aerthos Campaign

Provides optional content and objectives within episodes for enhanced
gameplay depth, replayability, and additional rewards.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class TriggerType(Enum):
    """Types of quest triggers"""
    ENTER_ROOM = "enter_room"           # Triggered when entering specific room
    FIND_ITEM = "find_item"             # Triggered when picking up specific item
    KILL_MONSTER = "kill_monster"       # Triggered when defeating specific monster
    SEARCH_ROOM = "search_room"         # Triggered when searching specific room
    AUTO_START = "auto_start"           # Triggered at episode start
    DIALOGUE = "dialogue"               # Triggered by NPC dialogue
    EPISODE_PROGRESS = "episode_progress"  # Triggered at certain episode milestones


class ObjectiveType(Enum):
    """Types of quest objectives"""
    KILL_MONSTER = "kill_monster"       # Defeat X monsters of type Y
    COLLECT_ITEM = "collect_item"       # Collect X items
    VISIT_ROOM = "visit_room"           # Visit specific room(s)
    SEARCH_ROOM = "search_room"         # Search specific room(s)
    ESCORT_NPC = "escort_npc"           # Escort NPC to safe location
    SOLVE_PUZZLE = "solve_puzzle"       # Solve a puzzle or riddle
    SURVIVE = "survive"                 # Survive X turns in dangerous area


@dataclass
class QuestObjective:
    """A single objective within a quest"""
    id: str
    description: str
    objective_type: ObjectiveType
    target: Optional[str] = None        # Monster ID, item ID, room ID, etc.
    count: int = 1                      # How many required
    current: int = 0                    # Current progress
    completed: bool = False

    def update_progress(self, increment: int = 1) -> bool:
        """
        Update progress toward objective

        Args:
            increment: Amount to increase progress

        Returns:
            True if objective completed by this update
        """
        was_complete = self.completed
        self.current = min(self.current + increment, self.count)
        self.completed = (self.current >= self.count)
        return self.completed and not was_complete

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for saving"""
        return {
            'id': self.id,
            'description': self.description,
            'type': self.objective_type.value,
            'target': self.target,
            'count': self.count,
            'current': self.current,
            'completed': self.completed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestObjective':
        """Deserialize from dictionary"""
        return cls(
            id=data['id'],
            description=data['description'],
            objective_type=ObjectiveType(data['type']),
            target=data.get('target'),
            count=data.get('count', 1),
            current=data.get('current', 0),
            completed=data.get('completed', False)
        )


@dataclass
class QuestRewards:
    """Rewards granted upon quest completion"""
    xp: int = 0
    gold: int = 0
    items: List[str] = field(default_factory=list)  # Item IDs
    reputation: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'xp': self.xp,
            'gold': self.gold,
            'items': self.items,
            'reputation': self.reputation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestRewards':
        """Deserialize from dictionary"""
        return cls(
            xp=data.get('xp', 0),
            gold=data.get('gold', 0),
            items=data.get('items', []),
            reputation=data.get('reputation', 0)
        )


@dataclass
class SideQuest:
    """
    A side quest with objectives and rewards

    Side quests are optional content within episodes that provide
    additional challenges, story, and rewards.
    """
    id: str
    title: str
    description: str
    episode_id: str
    trigger_type: TriggerType
    trigger_conditions: Dict[str, Any]
    objectives: List[QuestObjective]
    rewards: QuestRewards
    completion_flag: str                # Story flag set when complete
    optional: bool = True               # Whether quest is optional
    hidden: bool = False                # Whether quest is hidden until triggered
    repeatable: bool = False            # Whether quest can be repeated

    # State tracking
    discovered: bool = False            # Whether quest has been discovered
    active: bool = False                # Whether quest is currently active
    completed: bool = False             # Whether quest has been completed
    failed: bool = False                # Whether quest has failed

    def check_trigger(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """
        Check if quest should be triggered by an event

        Args:
            event_type: Type of event (enter_room, find_item, etc.)
            event_data: Event-specific data

        Returns:
            True if quest should be triggered
        """
        if self.active or self.completed or self.failed:
            return False

        if event_type != self.trigger_type.value:
            return False

        # Check trigger conditions
        for key, value in self.trigger_conditions.items():
            if key not in event_data or event_data[key] != value:
                return False

        return True

    def activate(self) -> None:
        """Activate the quest"""
        self.discovered = True
        self.active = True

    def update_objective(self, objective_id: str, increment: int = 1) -> bool:
        """
        Update progress on a specific objective

        Args:
            objective_id: ID of objective to update
            increment: Amount to increment progress

        Returns:
            True if objective was completed by this update
        """
        for obj in self.objectives:
            if obj.id == objective_id:
                return obj.update_progress(increment)
        return False

    def check_objective_event(self, objective_type: str, target: Optional[str] = None) -> List[str]:
        """
        Check if an event completes any objectives

        Args:
            objective_type: Type of objective event
            target: Target of the event (monster ID, item ID, etc.)

        Returns:
            List of objective IDs that were updated
        """
        if not self.active or self.completed:
            return []

        updated = []
        for obj in self.objectives:
            if obj.completed:
                continue

            # Check if objective type matches
            if obj.objective_type.value != objective_type:
                continue

            # Check if target matches (if applicable)
            if obj.target and obj.target != target:
                continue

            # Update objective
            if obj.update_progress():
                updated.append(obj.id)

        return updated

    def check_completion(self) -> bool:
        """
        Check if all objectives are complete

        Returns:
            True if quest is now complete
        """
        if self.completed or self.failed:
            return False

        all_complete = all(obj.completed for obj in self.objectives)
        if all_complete:
            self.completed = True
            self.active = False

        return all_complete

    def fail_quest(self) -> None:
        """Mark quest as failed"""
        self.failed = True
        self.active = False

    def get_progress_text(self) -> str:
        """Get human-readable progress text"""
        lines = [f"Quest: {self.title}"]
        for obj in self.objectives:
            status = "✓" if obj.completed else " "
            lines.append(f"  [{status}] {obj.description} ({obj.current}/{obj.count})")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for saving"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'episode_id': self.episode_id,
            'trigger_type': self.trigger_type.value,
            'trigger_conditions': self.trigger_conditions,
            'objectives': [obj.to_dict() for obj in self.objectives],
            'rewards': self.rewards.to_dict(),
            'completion_flag': self.completion_flag,
            'optional': self.optional,
            'hidden': self.hidden,
            'repeatable': self.repeatable,
            'discovered': self.discovered,
            'active': self.active,
            'completed': self.completed,
            'failed': self.failed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SideQuest':
        """Deserialize from dictionary"""
        objectives = [QuestObjective.from_dict(obj) for obj in data.get('objectives', [])]
        rewards = QuestRewards.from_dict(data.get('rewards', {}))

        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            episode_id=data['episode_id'],
            trigger_type=TriggerType(data['trigger_type']),
            trigger_conditions=data.get('trigger_conditions', {}),
            objectives=objectives,
            rewards=rewards,
            completion_flag=data.get('completion_flag', ''),
            optional=data.get('optional', True),
            hidden=data.get('hidden', False),
            repeatable=data.get('repeatable', False),
            discovered=data.get('discovered', False),
            active=data.get('active', False),
            completed=data.get('completed', False),
            failed=data.get('failed', False)
        )

    @classmethod
    def from_json_data(cls, quest_id: str, json_data: Dict[str, Any]) -> 'SideQuest':
        """
        Create SideQuest from JSON file format

        Args:
            quest_id: Unique quest identifier
            json_data: Quest data from side_quests.json

        Returns:
            SideQuest instance
        """
        # Parse objectives
        objectives = []
        for obj_data in json_data.get('objectives', []):
            objectives.append(QuestObjective(
                id=obj_data['id'],
                description=obj_data['description'],
                objective_type=ObjectiveType(obj_data['type']),
                target=obj_data.get('target'),
                count=obj_data.get('count', 1)
            ))

        # Parse rewards
        rewards_data = json_data.get('rewards', {})
        rewards = QuestRewards(
            xp=rewards_data.get('xp', 0),
            gold=rewards_data.get('gold', 0),
            items=rewards_data.get('items', []),
            reputation=rewards_data.get('reputation', 0)
        )

        return cls(
            id=quest_id,
            title=json_data['title'],
            description=json_data['description'],
            episode_id=json_data['episode_id'],
            trigger_type=TriggerType(json_data['trigger_type']),
            trigger_conditions=json_data.get('trigger_conditions', {}),
            objectives=objectives,
            rewards=rewards,
            completion_flag=json_data.get('completion_flag', f'quest_{quest_id}_complete'),
            optional=json_data.get('optional', True),
            hidden=json_data.get('hidden', False),
            repeatable=json_data.get('repeatable', False)
        )
