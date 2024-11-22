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

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


ACTION_DESCRIPTIONS = {
    "refocus": "",
    "elaborate": "",
    "summarize": "",
    "invite_someone_else": "",
    "help_to_answer_question": "",
    "prompt_host_for_missing_topic": "",
}


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


def load_action_examples(
    csv_path: str,
) -> Dict[str, Dict[str, Union[str, List[str]]]]:
    """The examples in this spreadsheet need to be examples of what behaviour
    the participant should have BEFORE the action is performed"""
    df = pd.read_csv(csv_path)
    examples = {}

    for action in df["action"].unique():
        examples[action] = {
            "explanation": ACTION_DESCRIPTIONS[action],
            "examples": df[df["action"] == action]["example"].tolist(),
        }

    return examples

def format_action_into_prompt(examples: Dict):
    example_str = ""
    for action, data in examples.items():
        example_separator = "- \n"
        example_str += f"""{action.capitalize()}: {data['explanation']}
Examples:
- {example_separator.join(data['examples'])}
"""
    return example_str

class ActionPicker:
    def __init__(self, action_csv_path: str):
        self.examples = load_action_examples(action_csv_path)

        self.system_prompt = """
        You are helping to moderate a conversation about personal finance and ethical investing. The participants have agreed on the following goals and ways to interact for the conversation:
        <goals_of_conversation>
        {goals_of_conversation}
        </goals_of_conversation>
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
        self.tools = [
            {
                "name": self.tool_name,
                "description": "A tool that will help you steer the conversation in the direction that we have agreed upon",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "explanation": {
                            "type": "string",
                            "description": "brief explanation of the action that was made and highlight the key reason why it was chosen",
                        },
                        # TODO make an array
                        "action": {
                            "type": "string",
                            "description": format_action_into_prompt(
                                self.examples
                            ),
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence in the action chosen, 0.0-1.0 (inclusive)",
                        },
                    },
                    "required": ["explanation", "action", "confidence"],
                },
            }
        ]

    def pick_action_from_transcript(
        self, transcript: str,
    ) -> ActionPick:
        """
        Classify the action of a single text.

        Args:
            text (str): The text to analyze

        Returns:
            dict: Dictionary containing action types, confidence score, and explanation
        """
        messages = [
            {
                "role": "user",
                "content": self.user_prompt_format.format(
                    transcript=transcript, message=message
                ),
            }
        ]
        start = time.time()
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            temperature=0.5,
            system=self.system_prompt,
            messages=messages,
            tools=self.tools,
            tool_choice={"type": "tool", "name": self.tool_name},
        )

        assert response.content
        assert response.content[0].type == "tool_use"
        assert response.content[0].name == "action_tracker"
        tool_input = response.content[0].input
        raw_action = str(tool_input["action"]).lower()
        try:
            action = Action[raw_action.upper()]
        except KeyError:
            action = None
        return ActionPick(
            **{
                "action": action,
                "model_action": raw_action,
                "explanation": str(tool_input["explanation"]),
                "confidence": float(tool_input["confidence"]),
                "api_usage": response.usage.to_json(),
                "duration": time.time() - start,
            }
        )
