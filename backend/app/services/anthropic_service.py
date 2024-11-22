from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY
from models.request_models import AnthropicRequest
from core.context import log_response_messages


client = Anthropic(api_key=ANTHROPIC_API_KEY)

def create_message(request: AnthropicRequest):
    if request.image and request.image_type:
        return [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": request.image_type,
                        "data": request.image
                    }
                },
                {
                    "type": "text",
                    "text": request.messages[0].content
                }
            ]
        }]
    return request.messages

def anthropic_stream_response(request: AnthropicRequest):

    messages = create_message(request)
    stream = client.messages.create(
        model=request.model,
        system=request.system_message,
        max_tokens=request.max_tokens,
        messages=messages,
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        stream=True,
    )
    output += ""
    for chunk in stream:
        if chunk.type == "content_block_delta":
            output += chunk.delta.text
            yield chunk.delta.text
    if True:
        messages.append({
            "role": "assistant",
            "content": output
        })
        log_response_messages(messages)