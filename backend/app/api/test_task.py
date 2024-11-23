# app/api/task.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
from ..task_data.task_loader import TaskBuilder, get_task_by_action, Action
from ..services.anthropic_service import anthropic_stream_response
from ..models import AnthropicRequest, ClientMessage
from ..core.logging import logger


router = APIRouter()

class TestTaskRequest(BaseModel):
    task_version: str
    transcript: str

@router.post("/api/test_task")
async def test_task(request: TestTaskRequest):
    # Extract task name and handle temp versions
    if "_temp-" in request.task_version:
        task_name = request.task_version.split('_temp-')[0]
    else:
        task_name = request.task_version.split('_v')[0]

    logger.info(f"Testing task {task_name} with version {request.task_version}")

    # Initialize TaskBuilder with specific version
    task_builder = get_task_by_action(Action[task_name.upper()], request.task_version)

    # Stream response
    return task_builder.run_task(request.transcript)['content']