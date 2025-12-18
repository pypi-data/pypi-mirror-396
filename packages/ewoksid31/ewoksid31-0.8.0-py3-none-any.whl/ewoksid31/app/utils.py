from collections import defaultdict
from typing import Any

FLATFIELD_DEFAULT_DIR = "/data/id31/inhouse/P3/"
NEWFLAT_FILENAME = "flats.mat"
OLDFLAT_FILENAME = "flats_old.mat"


def print_inputs(inputs: list[dict[str, Any]]) -> None:
    """Pretty print a list of ewoks task inputs"""
    tasks_args = defaultdict(list)
    for input in inputs:
        task_key = input.get("task_identifier", "")
        task_id = input.get("id")
        if task_id:
            task_key += f" <id={task_id}"
        task_label = input.get("label")
        if task_label:
            task_key += f' "{task_label}"'
        tasks_args[task_key].append((input["name"], input["value"]))

    for task_key in sorted(tasks_args.keys()):
        print(f"{task_key}:")
        for name, value in tasks_args[task_key]:
            print(f"- {name}: {value}")
        print("")
