from typing import TypedDict
import argparse
import dataclasses
import os
import random
from pathlib import Path
from pipelines.transcript_processing import format_transcript_for_llm, load_transcript, merge_into_user_messages

current_folder = Path(__file__).resolve().parent
backend_root = current_folder.parents[1]


class TaskPrompt(TypedDict):
    system: str
    user: str
    tools: dict


@dataclasses.dataclass
class TaskBuilder:
    name: str
    description: str = ""
    answer_format: str = ""
    good_responses: list[str] = dataclasses.field(default_factory=list)
    bad_responses: list[str] = dataclasses.field(default_factory=list)
    triggers: list[str] = dataclasses.field(default_factory=list)

    def __post__init__(self):
        folder = Path(self.name)
        # Read each file and assign to the corresponding attribute
        self.name = folder.name
        for file in ["answer_format", "description"]:
            file_path = folder / f"{file}.txt"
            if file_path.exists():
                setattr(self, file, file_path.read_text().strip())

        for file in ["good_responses", "bad_responses", "triggers"]:
            file_path = folder / f"{file}.txt"
            if file_path.exists():
                setattr(
                    self,
                    file,
                    [
                        line.strip()
                        for line in file_path.read_text().strip().split("\n")
                        if line.strip()
                    ],
                )

    def get_task_trigger(self) -> str:
        """Assembles the description of the task using the first line of the description and
        up to 2 trigger examples.
        """
        # Get first line of description
        first_line = self.description.split("\n")[0].strip()
        print(self)
        # Select up to 2 random triggers
        # selected_triggers = random.sample(self.triggers, min(2, len(self.triggers)))
        selected_triggers = self.triggers[:2]

        # Combine into final trigger
        trigger_text = f"{self.name}: {first_line}\n\nExample messages that indicate this action should be used:\n"
        trigger_text += "\n".join(f"- {trigger}" for trigger in selected_triggers)

        return trigger_text

    def get_task_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> TaskPrompt:
        """Creates a TaskPrompt by formatting the provided system and user prompts with
        the task's attributes.
        """
        # Format system prompt with all available attributes
        formatted_system = system_prompt.format(
            description=self.description,
            good_responses=self.good_responses,
            bad_responses=self.bad_responses,
            triggers=self.triggers,
            answer_format=self.answer_format,
            **kwargs
        )

        # Format user prompt
        formatted_user = user_prompt.format(
            description=self.description,
            good_responses=self.good_responses,
            bad_responses=self.bad_responses,
            triggers=self.triggers,
            answer_format=self.answer_format,
            **kwargs
        )

        return TaskPrompt(
            system=formatted_system,
            user=formatted_user,
            tools={},  # Empty dict as per TaskPrompt definition
        )


def get_parser() -> argparse.ArgumentParser:
    """Argument parser should collect a task which have the same name as the
    subfolders in this directory.
    """
    parser = argparse.ArgumentParser(description="Task prompt builder")

    # Get list of tasks by looking at subdirectories in current directory
    tasks = [
        d.name
        for d in Path(__file__).resolve().parent.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    parser.add_argument(
        "task",
        choices=tasks,
        help="Task name corresponding to a subfolder containing required txt files",
    )
    parser.add_argument(
        "--transcript",
        default=str(backend_root / "logs/transcripts/transcript_3.json"),
        type=str,
        help="Provide a transcript",
    )

    return parser


def main(args: argparse.Namespace):
    # Initialize TaskBuilder with the specified task folder
    task_builder = TaskBuilder(args.task)
    transcript = format_transcript_for_llm(merge_into_user_messages(load_transcript(args.transcript)))
    # Example system and user prompts - these could be loaded from files as well
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
    # Generate task prompt
    print()
    description = task_builder.get_task_trigger()
    task_output = task_builder.get_task_prompt(system_prompt, user_prompt, transcript=transcript)
    print(description)
    print(task_output)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
