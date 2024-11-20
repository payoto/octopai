from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pipelines.hyde_pipeline import HydePipeline
from models.request_models import AnthropicRequest
from core.logging import logger


router = APIRouter()

def log_request(request: AnthropicRequest):
    logger.info(f"Received request: ")
    logger.info(f"Model:            {request.model}")
    logger.info(f"Max tokens:       {request.max_tokens}")
    logger.info(f"Temperature:      {request.temperature}")
    logger.info(f"Top P:            {request.top_p}")
    logger.info(f"Top K:            {request.top_k}")
    logger.info(f"System message:   {request.system_message}")
    logger.info(f"Image type:       {request.image_type}")
    logger.info(f"Messages count:   {len(request.messages)}")
    logger.info(f"Last message:     {request.messages[-1].content}")


@router.post("/api/hyde")
async def process_chat(
    request: AnthropicRequest,
    hyde_pipeline: HydePipeline = Depends(),
):
    log_request(request)
    return StreamingResponse(hyde_pipeline.process_query(request), media_type="plain/text")
