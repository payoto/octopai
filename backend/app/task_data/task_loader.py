from typing import TypedDict, Dict, List, Type, Optional, TYPE_CHECKING
import argparse
import dataclasses
from pprint import pprint
from pathlib import Path
from enum import Enum
from ..models import BotMessage
from ..pipelines.transcript_processing import (
    format_transcript_for_llm,
    load_transcript,
    merge_into_user_messages,
)

from ..pipelines.hyde_pipeline import client, log_response_messages, HydePipeline

current_folder = Path(__file__).resolve().parent
backend_root = current_folder.parents[1]


class TaskPrompt(TypedDict):
    system: str
    user: str
    tools: dict


REQUIRED_FILES = [
    "answer_format.txt",
    "description.txt",
    "good_responses.txt",
    "bad_responses.txt",
    "triggers.txt",
]


@dataclasses.dataclass
class TaskBuilder:
    name: str
    version: Optional[str] = None
    description: str = ""
    answer_format: str = ""
    good_responses: list[str] = dataclasses.field(default_factory=list)
    bad_responses: list[str] = dataclasses.field(default_factory=list)
    triggers: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        # Determine the correct folder based on version
        if self.version:
            folder = Path(__file__).resolve().parent / self.version
        else:
            folder = Path(__file__).resolve().parent / self.name

        if not folder.exists():
            raise ValueError(f"Task folder {folder} does not exist")

        # Verify all required files exist
        missing_files = [f for f in REQUIRED_FILES if not (folder / f).exists()]
        if missing_files:
            raise ValueError(
                f"Missing required files in {folder}: {', '.join(missing_files)}"
            )

        self.name = self.name  # Keep original name even when using version

        # Read each file and assign to the corresponding attribute
        self.description = (folder / "description.txt").read_text().strip()
        self.answer_format = (folder / "answer_format.txt").read_text().strip()

        # Read list files
        for file_name in ["good_responses", "bad_responses", "triggers"]:
            content = (folder / f"{file_name}.txt").read_text().strip()
            setattr(
                self,
                file_name,
                [line.strip() for line in content.split("\n") if line.strip()],
            )

    def get_task_trigger(self) -> str:
        """Assembles the description of the task using the first line of the description and
        up to 2 trigger examples.
        """
        # Get first line of description
        first_line = self.description.split("\n")[0].strip()
        # Select up to 2 triggers
        selected_triggers = self.triggers[:2]

        # Combine into final trigger
        trigger_text = f"{self.name}: {first_line}\n\nExample messages that indicate this action should be used:\n"
        trigger_text += "\n".join(f"- {trigger}" for trigger in selected_triggers)

        return trigger_text

    def get_task_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> dict:
        """Creates a TaskPrompt by formatting the provided system and user prompts with
        the task's attributes."""
        formatted_system = system_prompt.format(
            description=self.description,
            good_responses="\n".join(f"- {r}" for r in self.good_responses),
            bad_responses="\n".join(f"- {r}" for r in self.bad_responses),
            triggers="\n".join(f"- {t}" for t in self.triggers),
            answer_format=self.answer_format,
            **kwargs,
        )

        formatted_user = user_prompt.format(
            description=self.description,
            good_responses=self.good_responses,
            bad_responses=self.bad_responses,
            triggers=self.triggers,
            answer_format=self.answer_format,
            **kwargs,
        )

        return {"system": formatted_system, "user": formatted_user, "tools": {}}

    def run_task(self, transcript: str) -> "BotMessage":
        """Run the task on the provided transcript."""
        print(f"Running task {self.name}")
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
        task_output = self.get_task_prompt(
            system_prompt, user_prompt, transcript=transcript
        )
        claude_response = self.call_claude(task_output["system"], task_output["user"], task_output["tools"])
        return {"role": self.name, "content": claude_response}

    def call_claude(self, system, user, tools):
        messages = [{
            "role": "user",
            "content": user
        }]
        stream = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=messages,
            system=system,
            stream=True,
        )
        output = ""
        for chunk in stream:
            if chunk.type == "content_block_delta":
                output += chunk.delta.text
        messages.insert(0, {
            "role": "system",
            "content": system
        })
        messages.append({
            "role": "assistant",
            "content": output
        })
        log_response_messages(messages)
        return output


class RagTaskBuilder(TaskBuilder):
    def run_task(self, transcript: str) -> BotMessage:
        print("Running RAG task")
        question = super().run_task(transcript)
        pipeline = HydePipeline()
        hyde_output = ""
        for o in pipeline.process_query(question["content"]):
            hyde_output += o
        return {"role": self.name, "content": hyde_output}

CUSTOM_TASK_CLASS_REGISTRATIONS = {
    "generate_query": RagTaskBuilder,
}

def discover_tasks() -> List[TaskBuilder]:
    """Discover all tasks in the task_data directory."""
    tasks_dir = current_folder
    tasks = []

    # Get all subdirectories that contain the required task files
    for task_dir in tasks_dir.iterdir():
        if task_dir.is_dir() and not task_dir.name.startswith("."):
            # Check if all required files exist
            if all((task_dir / file).exists() for file in REQUIRED_FILES):
                task_class = CUSTOM_TASK_CLASS_REGISTRATIONS.get(task_dir.name, TaskBuilder)
                tasks.append(task_class(task_dir.name))

    return tasks


def create_action_enum() -> Type[Enum]:
    """Dynamically create an Action enum from discovered tasks."""
    tasks = discover_tasks()

    # Create enum members dict
    # Convert task names to uppercase and replace spaces/hyphens with underscores
    enum_members = {
        task.name.upper().replace("-", "_").replace(" ", "_"): task.name.lower()
        for task in tasks
    }

    # Always add a default "let the conversation continue" action
    enum_members["LET_THE_CONVERSATION_CONTINUE"] = "let_the_conversation_continue"

    # Create the enum dynamically
    return Enum("Action", enum_members)


# Create the Action enum when module is imported
if TYPE_CHECKING:
    # Existing Action enum
    class Action(Enum):
        REFOCUS = "refocus"
        ELABORATE = "elaborate"
        SUMMARIZE = "summarize"
        INVITE_SOMEONE_ELSE = "invite_someone_else"
        LET_THE_CONVERSATION_CONTINUE = "let_the_conversation_continue"
else:
    Action = create_action_enum()


def get_task_by_action(action: "Action", version=None) -> TaskBuilder | None:
    """Get the TaskBuilder instance corresponding to an Action enum value."""
    tasks = discover_tasks()
    for task in tasks:
        if task.name.lower() == action.value:
            return task
    return None


def get_parser() -> argparse.ArgumentParser:
    """Argument parser should collect a task which have the same name as the
    subfolders in this directory.
    """
    parser = argparse.ArgumentParser(description="Task prompt builder")

    # Get list of tasks by looking at subdirectories in current directory
    tasks = [d.name for d in discover_tasks()]

    parser.add_argument(
        "task",
        choices=tasks,
        help="Task name corresponding to a subfolder containing required txt files",
    )
    parser.add_argument(
        "--transcript",
        default=str(backend_root / "logs/transcripts/transcript_better.json"),
        type=str,
        help="Provide a transcript",
    )

    return parser


def main(args: argparse.Namespace):
    # Initialize TaskBuilder with the specified task folder
    task_builder = get_task_by_action(Action[args.task.upper()])
    transcript = format_transcript_for_llm(
        merge_into_user_messages(load_transcript(args.transcript))
    )
    # Example system and user prompts - these could be loaded from files as well
    # Generate task prompt
    print()
    description = task_builder.get_task_trigger()
    print("Task Trigger:")
    pprint(description)
    print("Task Result:")
    task_output = task_builder.run_task(transcript)
    print(task_output["content"])


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    # Print out discovered tasks and generated enum for debugging
    print("\nDiscovered Tasks:")
    for task in discover_tasks():
        print(f"- {task.name}")

    print("\nGenerated Action Enum Members:")
    for action in Action:
        print(f"- {action.name}: {action.value}")
    main(args)
