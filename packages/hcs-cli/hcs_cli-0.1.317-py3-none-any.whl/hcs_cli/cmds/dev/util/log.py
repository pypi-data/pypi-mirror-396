import click
from hcs_core.ctxp.util import CtxpException, print_error


def good(msg):
    click.secho("✅", fg="green", nl=False)
    click.echo(" " + msg)


def warn(msg):
    click.secho("⚠️", fg="yellow", nl=False)
    click.echo(" " + msg)


def info(msg):
    click.secho("ℹ️ " + msg)


# icons = ["💡", "✅", "⚠️", "ℹ️", "❌", "🚀", "🔔", "🔍", "📝", "📦"]


def trivial(msg):
    click.secho(click.style(msg, fg="bright_black"))


def fail(msg, e: Exception = None):
    if e:
        print_error(e)
    click.secho("❌", fg="red", nl=False)
    click.echo(" " + msg)
    raise CtxpException()
