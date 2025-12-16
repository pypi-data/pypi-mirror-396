"""
Contains helper functions.
"""

import json
import os


def load_from_json_file(path):
    with open(path, mode="r", encoding="utf-8") as file:
        json_str_input = file.read()
    return json.loads(json_str_input)


def save_to_json_file(data, filepath: str, sort_keys=False):
    json_str = json.dumps(data, indent=4, sort_keys=sort_keys)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode="w", encoding="utf-8") as text_file:
        text_file.write(json_str)
