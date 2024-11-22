""" Given
"""
from typing import TypedDict
import argparse
import dataclasses

class TaskPrompt(TypedDict):
    system: str
    user: str
    tools: dict

@dataclasses.dataclass
class TaskBuilder:
    description: str
    good_responses: list[str]
    bad_responses: list[str]
    triggers: list[str]
    def __init__(self, folder):
        # read-in the txt files named the same as the attributes and assign them
        # to the appropriate attribute.
        ...

    def get_task_trigger(self) -> str:
        """Assembles the description of the task using the first line of the description and
        up to 2 trigger examples.
        """
        ...

    def get_task_prompt(self, system_prompt: str, user_prompt: str) -> TaskPrompt:
        system_prompt.format(
            # Attributes passed as key word arguments
        )
        # Same for user_prompt







def get_parser():
    """ Argument parser should collect:

    - A task which have the same name as the subfolders in this directory
    """
    parser = argparse.ArgumentParser()
    ...
    return parser

def main(args: argparse.Namespace):
    ...
    print(task_output)

if "__main__" == __name__:
    parser = get_parser()
    args = parser.parse_args()
    main(args)
