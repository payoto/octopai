
from typing import  List, Optional, Union, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from utils.prompt import ClientMessage


class AnthropicRequest(BaseModel):
    messages:       List[ClientMessage]
    system_message: str = Field(default="You are a helpful assistant.")
    model:          str = Field(default="claude-3-haiku-20240307")
    max_tokens:     int = Field(default=1000)
    temperature:    float = Field(default=0.0)
    top_p:          float = Field(default=0.0)
    top_k:          int = Field(default=0)
    image:          Optional[str] = None
    image_type:     Optional[str] = None


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

class MessageAnnotations(BaseModel):
    sentiment: Dict | Any | None
    action: Dict | Any | None
    bot_message: Dict | Any | None
    timestamp: float


class Meeting:
    """Internal representation"""
    url: str
    host_name: str
    conversation: List[Message]
    annotations: List[MessageAnnotations]

class MeetingPart(BaseModel):
    """Input from the frontend"""
    url: str
    host_name: str
    transcript: Transcript