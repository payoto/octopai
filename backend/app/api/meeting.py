from typing import Generator, Any
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import models
from services.anthropic_service import anthropic_stream_response
from core.logging import logger
from pipelines.sentiment import SentimentClassificationOutput, Sentiment

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
        timestamp=delta * 0.2
    ).model_dump_json()

@router.post("/api/meeting")
async def handle_meeting(request: models.MeetingPart) -> models.MessageAnnotations:
    log_request(request)
    response = StreamingResponse(yield_one_message_annotation_of_each_type(request.transcript), media_type="plain/text")
    return response