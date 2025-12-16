import logging
import sys

import click
from hcs_core.sglib import cli_options as cli
from hcs_ext_hst.base import common_op
from hcs_ext_hst.base.helper import exit_on_error, panic, print_data, reduce_log

log = logging.getLogger(__name__)


@click.group()
def report():
    """Commands for report"""


@report.command("del")
@click.option("--search", type=str, help="Specify search criteria. Either search criteria or IDs must be specified, but not both.")
@click.argument("id", nargs=-1, type=str)
def report_del(search: str, id: list):
    """Delete reports"""
    reduce_log()

    if not search and not id:
        panic("Either search criteria or ID must be specified.")
    if search and id:
        panic("Search criteria and ID must not be specified together.")

    error_occured = False

    def _delete(report):
        if isinstance(report, str):
            report_id = report
            click.echo(f"Deleting report: {report_id}")
        else:
            report_id = report.id
            click.echo(f"Deleting report: {report_id}, outpost={report.outpostId}, probe_id={report.probeId}")

        try:
            common_op.reports.delete(report_id)
        except Exception as e:
            click.secho(e, fg="bright_red")
            nonlocal error_occured
            error_occured = True

    if id:  # delete by IDs
        click.echo("Reports to delete: %d" % len(id))
        for i in id:
            _delete(i)
    else:  # delete by search
        items = common_op.reports.list(search)
        click.echo("Reports to delete: %d" % len(items))
        for p in items:
            _delete(p)

    if error_occured:
        sys.exit(1)


@report.command("get")
@click.argument("id", nargs=1, type=str)
def report_get(id: str):
    """Get a report."""
    reduce_log()

    def fn():
        o = common_op.reports.get(id)
        print_data(o)

    exit_on_error(fn)


@report.command("list")
@click.option("--search", type=str, required=False, help="The search string. E.g. 'name $eq alice")
@click.option("--sort", type=str, required=False, multiple=True, help="Example: createdAt,desc")
@click.option(
    "--first/--all",
    type=bool,
    required=False,
    default=False,
    help="Return the first element if any, instead of the full list.",
)
@cli.ids
@click.option(
    "--output",
    type=click.Choice(["json", "plain", "table"], case_sensitive=False),
    default="json",
    help="Specify the output format",
)
def report_list(search: str, sort: list, first: bool, ids: bool, output: str):
    """List reports."""
    reduce_log()

    if first:
        ret = common_op.reports.first(search, sort)
        if not ret:
            return
        if ids:
            ret = ret.id
    else:
        ret = common_op.reports.list(search, sort)
        if ret and ids:
            ret = list(map(lambda o: o.id, ret))

    print_data(ret, output)
