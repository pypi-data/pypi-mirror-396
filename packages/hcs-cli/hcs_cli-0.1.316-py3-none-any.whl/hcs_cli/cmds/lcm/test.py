import click
from hcs_core.ctxp import profile

from hcs_cli.service.lcm import health as health
from hcs_cli.support.exec_util import run_cli


def _safe_check():
    url = profile.current().hcs.url
    if url.find(".fs.devframe.cp.horizon.omnissa.com") == -1:
        raise click.UsageError("This command is only available on feature stack development environments. Current URL: " + url)


def _clear():
    lcm_template_ids = run_cli("hcs lcm template list --ids", output_json=True)
    for tid in lcm_template_ids:
        run_cli("hcs lcm template delete -y --force " + tid)
    for tid in lcm_template_ids:
        run_cli("hcs lcm template delete -y --force --wait 5m " + tid)


@click.command(hidden=True)
def test():
    _safe_check()
    _clear()
    run_cli("hcs lcm template create -p zero-new -w2m")
    run_cli("hcs lcm template get")
    _clear()


@click.command(hidden=True)
def clear():
    _safe_check()
    _clear()
