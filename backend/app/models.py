
from typing import  List, Optional, Union, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from enum import Enum

from .utils.prompt import ClientMessage

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


class Sentiment(Enum):
    DISCONNECTED = "disconnected"
    CONFUSED = "confused"
    POSITIVE = "positive"
    NERVOUS = "nervous"
    CONNECTED = "connected"
    CONFLICTUAL = "conflictual"
    NEUTRAL = "neutral"


class SentimentClassificationOutput(TypedDict):
    sentiment: Sentiment | None
    model_sentiment: str
    confidence: float
    explanation: str
    usage: Dict[str, Union[int, float]]
    duration: float

class BotMessage(TypedDict):
    role: str
    content: str

class Message:
    text: str
    speaker: str
    speaker_id: int
    start_timestamp: float
    end_timestamp: float

class MessageAnnotations(BaseModel):
    sentiment: SentimentClassificationOutput | None
    action: Dict | Any | None
    bot_message: BotMessage | Any | None
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
