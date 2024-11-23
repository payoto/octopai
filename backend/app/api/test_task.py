# app/api/task.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from ..task_data.task_loader import TaskBuilder
from ..services.anthropic_service import anthropic_stream_response
from ..models import AnthropicRequest, ClientMessage

router = APIRouter()

class TestTaskRequest(BaseModel):
    task_version: str
    transcript: str

@router.post("/api/test_task")
async def test_task(request: TestTaskRequest):
    # Load task
    task_name = request.task_version.split('_v')[0]
    task_builder = TaskBuilder(task_name)

    # Get task prompt
    system_prompt = """
    You will receive a transcript from a conversation, based on the conversation complete the following task:
    {description}

    Some bad examples of what your answer might look like are:
    {bad_responses}

    Some good examples of what your answer might look like are:
    {good_responses}

    {answer_format}
    You will now receive a transcript
    """

    user_prompt = """This is a transcript of the conversation:
    <transcript>
    {transcript}
    </transcript>
    {description}
    """

    task_prompt = task_builder.get_task_prompt(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        transcript=request.transcript
    )

    # Create Anthropic request
    anthropic_request = AnthropicRequest(
        messages=[ClientMessage(role="user", content=task_prompt.user)],
        system_message=task_prompt.system,
        model="claude-3-5-haiku-20241022",
        max_tokens=1024,
        temperature=0.7
    )

    # Stream response
    return StreamingResponse(
        anthropic_stream_response(anthropic_request),
        media_type="text/plain"
    )