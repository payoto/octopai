from typing import TypedDict, Optional, List
import argparse
import dataclasses
from pprint import pprint
from pathlib import Path

from ..pipelines.transcript_processing import format_transcript_for_llm, load_transcript, merge_into_user_messages

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
    "triggers.txt"
]


@dataclasses.dataclass
class TaskBuilder:
    name: str
    version: Optional[str] = None
    description: str = ""
    answer_format: str = ""
    good_responses: List[str] = dataclasses.field(default_factory=list)
    bad_responses: List[str] = dataclasses.field(default_factory=list)
    triggers: List[str] = dataclasses.field(default_factory=list)

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
            raise ValueError(f"Missing required files in {folder}: {', '.join(missing_files)}")

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
                [line.strip() for line in content.split("\n") if line.strip()]
            )

    def get_task_trigger(self) -> str:
        """Assembles the description of the task using the first line of the description and
        up to 2 trigger examples."""
        first_line = self.description.split("\n")[0].strip()
        selected_triggers = self.triggers[:2]

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
            **kwargs
        )

        formatted_user = user_prompt.format(
            description=self.description,
            good_responses=self.good_responses,
            bad_responses=self.bad_responses,
            triggers=self.triggers,
            answer_format=self.answer_format,
            **kwargs
        )

        return {
            "system": formatted_system,
            "user": formatted_user,
            "tools": {}
        }

def discover_tasks() -> List[TaskBuilder]:
    """Discover all tasks in the task_data directory."""
    tasks_dir = Path(__file__).parent / "task_data"
    tasks = []

    # Get all subdirectories that contain the required task files
    for task_dir in tasks_dir.iterdir():
        if task_dir.is_dir() and not task_dir.name.startswith('.'):
            required_files = REQUIRED_FILES

            # Check if all required files exist
            if all((task_dir / file).exists() for file in required_files):
                tasks.append(TaskBuilder(task_dir.name))

    return tasks

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
    pprint(description)
    pprint(task_output)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
