from typing import Generator, Any
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .. import models
from ..services.anthropic_service import anthropic_stream_response
from ..core.logging import logger
from ..pipelines.sentiment import SentimentClassificationOutput, Sentiment
from ..pipelines.next_action import ActionPick, Action

router = APIRouter()

def log_request(request: models.MeetingPart):
    logger.info("Received request: ")
    logger.info(f"Url:                    {request.url}")
    logger.info(f"Host ID:                {request.host_name}")
    logger.info(f"Transcript length:      {len(request.transcript)}")



def yield_one_message_annotation_of_each_type(transcript: models.Transcript) -> Generator[models.MessageAnnotations, Any, Any]:
    start = transcript[0]["words"][0]["start_timestamp"]
    end = transcript[-1]["words"][-1]["end_timestamp"]
    delta = end - start
    yield models.MessageAnnotations(
        sentiment=SentimentClassificationOutput(
            sentiment=Sentiment.CONFUSED,
            model_sentiment="confused",
            confidence=0.4,
            explanation="Because i picked it and I was confused.",
            usage={"input": 1000, "output": 100},
            duration=4.2,
        ),
        action=None,
        bot_message=None,
        timestamp=start + delta * 0.2
    ).model_dump_json()

    yield models.MessageAnnotations(
        sentiment=None,
        action=ActionPick(
            action=Action.LET_THE_CONVERSATION_CONTINUE,
            model_action="let_the_conversation_continue",
            confidence=1.0,
            explanation="I can't be bothered to do anything",
            usage={"input": 1000, "output": 20},
            duration=5,
        ),
        bot_message=None,
        timestamp=start + delta * 0.3,
    ).model_dump_json()


@router.post("/api/meeting")
async def handle_meeting(request: models.MeetingPart):
    log_request(request)
    response = StreamingResponse(yield_one_message_annotation_of_each_type(request.transcript), media_type="plain/text")
    return response