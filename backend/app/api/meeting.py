from typing import Generator, Any
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .. import models
from ..services.anthropic_service import anthropic_stream_response
from ..core.logging import logger
from ..pipelines.sentiment import SentimentClassificationOutput, Sentiment
from ..pipelines.transcript_processing import format_transcript_for_llm, merge_into_user_messages, extract_last_minutes
from ..pipelines.next_action import ActionPick, Action, ActionPicker
from ..task_data.task_loader import Action, discover_tasks, get_task_by_action

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

    yield models.MessageAnnotations(
        sentiment=None,
        action=None,
        bot_message=models.BotMessage(
            role="assistant",
            content="I'm a bot message",
        ),
        timestamp=start + delta * 0.4,
    ).model_dump_json()


def real_meeting_processing(transcript: models.Transcript):
    # Pick the action that needs doing
    formatted_transcript = format_transcript_for_llm(merge_into_user_messages(extract_last_minutes(transcript, 180)))
    picker = ActionPicker()
    print("Picking action")
    picked_action = picker.pick_action_from_transcript(formatted_transcript)
    if transcript:
        step_time = transcript[-1]["words"][-1]["end_timestamp"]
        print(f"Picked action {picked_action}")
        yield models.MessageAnnotations(
            sentiment=None,
            action=picked_action,
            bot_message=None,
            timestamp=step_time,
        ).model_dump_json()

        # Run the action

        if picked_action["action"] is not None:
            print(f"Running action {picked_action['action']}")
            if picked_action["action"] != Action.CONTINUE_CONVERSATION:
                task_builder = get_task_by_action(picked_action["action"])
                task_output = task_builder.run_task(formatted_transcript)
            else:
                task_output = {"role": "let_it_flow", "content": ""}
            print("Completed action!")
            yield models.MessageAnnotations(
                sentiment=None,
                action=None,
                bot_message=task_output,
                timestamp=step_time + 0.1,
            ).model_dump_json()


@router.post("/api/meeting")
async def handle_meeting(request: models.MeetingPart):
    log_request(request)

    if request.fake:
        return StreamingResponse(yield_one_message_annotation_of_each_type(request.transcript), media_type="plain/text")
    else:
        return StreamingResponse(real_meeting_processing(request.transcript), media_type="plain/text")