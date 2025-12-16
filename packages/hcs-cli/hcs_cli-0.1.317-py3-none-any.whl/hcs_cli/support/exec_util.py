import json
import os
import shlex
import subprocess
from typing import Any, List, Tuple, Union

import click


def _split_command(cmd: Union[str, List[str]]) -> Tuple[List[str], str]:
    if isinstance(cmd, str):
        return shlex.split(cmd), cmd

    if isinstance(cmd, list):
        return cmd, shlex.join(cmd)

    raise TypeError("cmd must be a string or a list of strings")


def exec(
    cmd,
    log_error=True,
    raise_on_error=True,
    inherit_output=False,
    cwd=None,
    input: Union[str, dict[Any, Any], list[Any]] = None,
    show_command: bool = True,
    env: dict = None,
):
    commands, cmd_text = _split_command(cmd)
    text = f"RUNNING: {cmd_text}"
    if input:
        text += " <input-redacted>"
        if isinstance(input, dict) or isinstance(input, list):
            input = json.dumps(input)

    if show_command:
        click.echo(click.style(text, fg="bright_black"))

    if inherit_output:
        result = subprocess.run(commands, env=env, cwd=cwd, input=input, text=True, capture_output=False)
    else:
        result = subprocess.run(commands, env=env, cwd=cwd, input=input, text=True, capture_output=True)

    if result.returncode != 0:
        if log_error:
            click.echo(f"  RETURN: {result.returncode}")
            if not inherit_output:
                stdout = result.stdout.strip()
                stderr = result.stderr.strip()
                if stdout:
                    click.echo(f"  STDOUT:      {stdout}")
                if stderr:
                    click.echo(f"  STDERR:      {stderr}")
        if raise_on_error:
            raise click.ClickException(f"Command '{cmd_text}' failed with return code {result.returncode}.")
    return result


def run_cli(
    cmd: str,
    output_json=False,
    raise_on_error=True,
    inherit_output: Union[bool, None] = None,
    input: Union[str, dict[Any, Any], list[Any]] = None,
    show_command: bool = True,
    log_error: bool = True,
    env: dict = None,
):
    eventual_env = os.environ.copy()
    eventual_env["HCS_CLI_CHECK_UPGRADE"] = "false"
    if env:
        eventual_env.update(env)
    if output_json:
        if inherit_output is None:
            inherit_output = False
        output = exec(
            cmd,
            log_error=log_error,
            raise_on_error=raise_on_error,
            inherit_output=inherit_output,
            env=eventual_env,
            input=input,
            show_command=show_command,
        ).stdout
        if not output:
            return None
        try:
            return json.loads(output)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON output from command '{cmd}': {e}\nOutput: {output}"
            raise click.ClickException(msg)
    else:
        if inherit_output is None:
            inherit_output = True
        return exec(
            cmd,
            log_error=log_error,
            raise_on_error=raise_on_error,
            inherit_output=inherit_output,
            env=eventual_env,
            input=input,
            show_command=show_command,
        )
