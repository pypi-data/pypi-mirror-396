import json
import os
import os.path as path
import sys


def load(name: str, as_json: bool = False) -> str:
    file_name = path.join(path.dirname(__file__), f"../payload/{name}")
    file_name = path.abspath(file_name)

    if path.exists(file_name):
        with open(file_name, "rt") as f:
            if as_json:
                return json.load(f)
            return f.read()

    # payload file not found.
    print("Available payloads:", file=sys.stderr)
    parent_dir = path.dirname(file_name)
    items = []
    for root, _, files in os.walk(parent_dir):
        for file in files:
            if file == "__init__.py":
                continue
            if file.endswith(".json"):
                file = file[:-5]
            items.append(file)
    items.sort()
    for file in items:
        print("    " + file, file=sys.stderr)

    raise FileNotFoundError(f"Payload file '{file_name}' does not exist.")
