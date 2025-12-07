from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from common_utils.datetime_utils import to_iso_format

from api_specs.memory_models import MemoryType


class RawDataType(Enum):
    """Types of content that can be processed."""

    CONVERSATION = "Conversation"

    @classmethod
    def from_string(cls, type_str: Optional[str]) -> Optional['RawDataType']:
        """
        Convert string type to RawDataType enum

        Args:
            type_str: Type string, such as "Conversation", "Email", etc.

        Returns:
            RawDataType enum value, returns None if conversion fails
        """
        if not type_str:
            return None

        try:
            # Convert string to enum name format (e.g., "Conversation" -> "CONVERSATION")
            enum_name = type_str.upper()
            return getattr(cls, enum_name)

        except AttributeError:
            # If no matching enum is found, return None
            from core.observation.logger import get_logger

            logger = get_logger(__name__)
            logger.error(f"No matching RawDataType found: {type_str}, returning None")
            return None
        except Exception as e:
            from core.observation.logger import get_logger

            logger = get_logger(__name__)
            logger.warning(f"Failed to convert type field: {type_str}, error: {e}")
            return None


@dataclass
class MemCell:
    """
    Boundary detection result following the specified schema.

    This class represents the result of boundary detection analysis
    and contains all the required fields for memory storage.
    """

    event_id: str
    user_id_list: List[str]
    # For downstream consumers we store normalized dicts extracted from RawData
    original_data: List[Dict[str, Any]]
    timestamp: datetime
    summary: str

    # Optional fields
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    participants: Optional[List[str]] = None
    type: Optional[RawDataType] = None
    keywords: Optional[List[str]] = None
    subject: Optional[str] = None
    linked_entities: Optional[List[str]] = None
    episode: Optional[str] = None  # episodic memory content

    # Prospective association prediction field
    foresights: Optional[List['ForesightItem']] = (
        None  # list of prospective associations
    )
    # Event Log field
    event_log: Optional[Any] = None  # Event Log object
    # extend fields, can be used to store any additional information
    extend: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the result after initialization."""
        if not self.event_id:
            raise ValueError("event_id is required")
        if not self.original_data:
            raise ValueError("original_data is required")
        if not self.summary:
            raise ValueError("summary is required")

    def __repr__(self) -> str:
        return f"MemCell(event_id={self.event_id}, original_data={self.original_data}, timestamp={self.timestamp}, summary={self.summary})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "user_id_list": self.user_id_list,
            "original_data": self.original_data,
            "timestamp": to_iso_format(self.timestamp),  # convert to ISO format string
            "summary": self.summary,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "participants": self.participants,
            "type": str(self.type.value) if self.type else None,
            "keywords": self.keywords,
            "linked_entities": self.linked_entities,
            "subject": self.subject,
            "episode": self.episode,
            "foresights": (
                [item.to_dict() for item in self.foresights]
                if self.foresights
                else None
            ),
            "event_log": (
                (
                    self.event_log.to_dict()
                    if hasattr(self.event_log, 'to_dict')
                    else self.event_log
                )
                if self.event_log
                else None
            ),
            "extend": self.extend,
        }


@dataclass
class Memory:
    """
    Simple result class for memory extraction.

    Contains the essential information for extracted memories.
    """

    memory_type: MemoryType
    user_id: str
    timestamp: datetime
    ori_event_id_list: List[str]

    subject: Optional[str] = None
    summary: Optional[str] = None
    episode: Optional[str] = None

    group_id: Optional[str] = None
    group_name: Optional[str] = None
    participants: Optional[List[str]] = None
    type: Optional[RawDataType] = None
    keywords: Optional[List[str]] = None
    linked_entities: Optional[List[str]] = None

    memcell_event_id_list: Optional[List[str]] = None
    user_name: Optional[str] = None
    # Prospective association prediction field
    foresights: Optional[List['ForesightItem']] = (
        None  # list of prospective associations
    )
    extend: Optional[Dict[str, Any]] = None

    # vector and model
    vector_model: Optional[str] = None
    vector: Optional[List[float]] = None

    def __post_init__(self):
        pass

    def to_dict(self) -> Dict[str, Any]:
        # Safely handle timestamp (could be datetime, str, or None)
        timestamp_str = None
        if self.timestamp:
            if isinstance(self.timestamp, str):
                timestamp_str = self.timestamp if self.timestamp else None
            else:
                try:
                    timestamp_str = to_iso_format(self.timestamp)
                except Exception:
                    timestamp_str = str(self.timestamp) if self.timestamp else None

        return {
            "memory_type": self.memory_type.value if self.memory_type else None,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "timestamp": timestamp_str,
            "ori_event_id_list": self.ori_event_id_list,
            "subject": self.subject,
            "summary": self.summary,
            "episode": self.episode,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "participants": self.participants,
            "type": self.type.value if self.type else None,
            "keywords": self.keywords,
            "linked_entities": self.linked_entities,
            "foresights": (
                [item.to_dict() for item in self.foresights]
                if self.foresights
                else None
            ),
            "extend": self.extend,
        }


@dataclass
class Foresight:
    """
    Prospective data model

    Used to store prospective knowledge extracted from episodic memories
    """

    user_id: str
    content: str
    knowledge_type: str = "knowledge"
    source_episodes: List[str] = None
    created_at: datetime = None
    group_id: Optional[str] = None
    participants: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        from common_utils.datetime_utils import get_now_with_timezone

        if self.source_episodes is None:
            self.source_episodes = []
        if self.created_at is None:
            self.created_at = get_now_with_timezone()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "content": self.content,
            "knowledge_type": self.knowledge_type,
            "source_episodes": self.source_episodes,
            "created_at": to_iso_format(self.created_at),
            "group_id": self.group_id,
            "participants": self.participants,
            "metadata": self.metadata,
        }


@dataclass
class ForesightItem:
    """
    Prospective association item

    Contains time-informed prospective association predictions
    """

    content: str
    evidence: Optional[str] = (
        None  # original evidence, specific facts supporting this association prediction (no more than 30 characters)
    )
    start_time: Optional[str] = None  # event start time, format: YYYY-MM-DD
    end_time: Optional[str] = None  # event end time, format: YYYY-MM-DD
    duration_days: Optional[int] = None  # duration in days
    source_episode_id: Optional[str] = None  # source event ID
    vector: Optional[List[float]] = None
    vector_model: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "evidence": self.evidence,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_days": self.duration_days,
            "source_episode_id": self.source_episode_id,
            "vector": self.vector,
            "vector_model": self.vector_model,
        }
