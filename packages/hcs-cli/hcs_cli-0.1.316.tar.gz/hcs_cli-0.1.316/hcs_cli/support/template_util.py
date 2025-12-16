import os
import re
import tempfile
from typing import Callable


def with_template_file(
    name: str, substitutions: dict, fn: Callable, base_path: str = None, use_temp_file: bool = False, delete_after: bool = False
):

    if base_path:
        if os.path.isfile(base_path):
            base_path = os.path.dirname(os.path.realpath(base_path))
        template_path = os.path.join(base_path, name)
    else:
        template_path = name

    with open(template_path, "r") as f:
        template_content = f.read()

    if substitutions:
        for key, value in substitutions.items():
            template_content = re.sub(key, value, template_content)

    _, suffix = os.path.splitext(name)
    if not suffix:
        suffix = ".yaml"  # Default to .yaml if no suffix

    try:
        if use_temp_file:
            with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=suffix) as temp_file:
                temp_file.write(template_content)
                temp_file_path = temp_file.name
        else:
            temp_file_path = os.path.basename(template_path)
            with open(temp_file_path, "w") as out_file:
                out_file.write(template_content)

        return fn(temp_file_path)
    except Exception as e:
        print("----- Start of temp file dump -----")
        print(template_content)
        print("----- End of temp file dump -----")
        raise e
    finally:
        if delete_after and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
