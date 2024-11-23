"""
File which decides the next action to be taken the LLM

This uses anthropic tool use to choose what the most appropriate actions is


"""
from typing import List, Dict, Union, TypedDict
import pandas as pd
import time
from enum import Enum
import anthropic
import os
from pathlib import Path
from ..task_data.task_loader import discover_tasks

# Existing Action enum
class Action(Enum):
    REFOCUS = "refocus"
    ELABORATE = "elaborate"
    SUMMARIZE = "summarize"
    INVITE_SOMEONE_ELSE = "invite_someone_else"
    LET_THE_CONVERSATION_CONTINUE = "let_the_conversation_continue"

class ActionPick(TypedDict):
    action: Action | None
    model_action: str
    confidence: float
    explanation: str
    usage: Dict[str, Union[int, float]]
    duration: float


class ActionPicker:
    def __init__(self):
        """Initialize ActionPicker with dynamically loaded tasks."""
        self.tasks = discover_tasks()
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        self.system_prompt = """
        You are helping to moderate a conversation about personal finance and ethical investing.
        You will be given part of the transcript and you will need to decide if
        you need to intervene to re-align the conversation with the goals outlined above.
        """

        self.user_prompt_format = """
        Here is a conversation transcript, use it as context for what the action should be taken:
        <transcript>
        {transcript}
        </transcript>
        """

        self.tool_name = "action_picker"
        self.model = "claude-3-5-haiku-20241022"

        # Build tool description from discovered tasks
        self.tools = [self._build_tool_schema()]

    def _build_tool_schema(self) -> Dict:
        """Build the tool schema using the discovered tasks."""
        task_descriptions = []
        for task in self.tasks:
            task_descriptions.append(task.get_task_trigger())

        action_descriptions = "\n\n".join(task_descriptions)

        return {
            "name": self.tool_name,
            "description": "A tool that will help you steer the conversation in the direction agreed upon",
            "input_schema": {
                "type": "object",
                "properties": {
                    "explanation": {
                        "type": "string",
                        "description": "brief explanation of the action chosen and why",
                    },
                    "action": {
                        "type": "string",
                        "description": action_descriptions,
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence in the action chosen, 0.0-1.0 (inclusive)",
                    },
                },
                "required": ["explanation", "action", "confidence"],
            },
        }

    def pick_action_from_transcript(
        self, transcript: str,
    ) -> ActionPick:
        """Classify the action based on the transcript."""
        messages = [
            {
                "role": "user",
                "content": self.user_prompt_format.format(transcript=transcript),
            }
        ]

        start = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.5,
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_choice={"type": "tool", "name": self.tool_name},
        )

        assert response.content
        assert response.content[0].type == "tool_use"
        assert response.content[0].name == "action_picker"
        tool_input = response.content[0].input
        raw_action = str(tool_input["action"]).lower()

        try:
            action = Action[raw_action.upper()]
        except KeyError:
            action = None

        return ActionPick(
            action=action,
            model_action=raw_action,
            explanation=str(tool_input["explanation"]),
            confidence=float(tool_input["confidence"]),
            usage=response.usage.to_json(),
            duration=time.time() - start,
        )