
from typing import TypedDict, List, Optional, Union, Dict



class Word(TypedDict):
    text: str
    start_timestamp: float
    end_timestamp: float
    language: Optional[str]
    confidence: Optional[float]


class TranscriptSegment(TypedDict):
    words: List[Word]
    speaker: str
    speaker_id: int
    language: str


Transcript = List[TranscriptSegment]


class Message:
    text: str
    speaker: str
    speaker_id: int
    start_timestamp: float
    end_timestamp: float

class MessageAnnotations:
    sentiment: Dict | None
    action: Dict | None
    bot_message: Dict | None
    timestamp: float


class Meeting:
    """Internal representation"""
    url: str
    host_name: str
    conversation: List[Message]
    annotations: List[MessageAnnotations]

class MeetingPart:
    """Input from the frontend"""
    url: str
    host_name: str
    transcript: Transcript
