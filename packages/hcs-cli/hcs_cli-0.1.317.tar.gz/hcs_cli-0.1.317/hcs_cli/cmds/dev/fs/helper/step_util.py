import functools

import click

import hcs_cli.cmds.dev.util.log as log

_deployment_config = None
_step_name_stack = []


def disable(deployment_config: list[str]):
    global _deployment_config
    _deployment_config = deployment_config


def is_enabled(name: str) -> bool:
    if _deployment_config is None:
        return True
    return name not in _deployment_config


def step(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        try:
            _step_name_stack.append(func_name)
            _step_name = ".".join(_step_name_stack)
            if not is_enabled(_step_name):
                click.echo(f"📦 {_step_name} <DISABLED>")
                return
            click.echo(f"📦 {_step_name}")
            return func(*args, **kwargs)
        except Exception as e:
            print()
            log.fail(f"'{_step_name}' failed", e)
            raise
        finally:
            _step_name_stack.pop()

    return wrapper
