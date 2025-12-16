from enum import IntEnum, StrEnum

class EventLevel(IntEnum):
    """Defines event levels for the event emitter module."""
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

class EventType(StrEnum):
    """Defines event types for the event emitter module."""
    ACTIVITY = 'activity'
    CODE = 'code'
    REFERENCE = 'reference'
    RESPONSE = 'response'
    STATUS = 'status'
    THINKING = 'thinking'

class EventTypeSuffix(StrEnum):
    """Defines suffixes for block based event types."""
    START = '_start'
    END = '_end'

class DefaultChunkMetadata:
    """Defines constants for default chunk metadata keys."""
    CHUNK_ID: str
    PREV_CHUNK_ID: str
    NEXT_CHUNK_ID: str

class LogMode(StrEnum):
    """Defines supported log modes for the SDK logging system."""
    TEXT = 'text'
    SIMPLE = 'simple'
    JSON = 'json'
