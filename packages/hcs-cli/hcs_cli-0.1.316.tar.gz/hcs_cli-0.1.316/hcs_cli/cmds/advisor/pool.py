"""
Copyright © 2025 Omnissa, LLC.
"""

import urllib.parse
import urllib.request
import webbrowser

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import recent

from hcs_cli.cmds.advisor.advisor_utils import create_report_file, get_template_info, prompt_for_report_options
from hcs_cli.cmds.advisor.html_utils import create_pool_html_report
from hcs_cli.cmds.advisor.pdf_utils import create_pool_pdf_report
from hcs_cli.service.org_service import details


@click.group()
def pool():
    """Advisor commands for desktop pools."""
    pass


@pool.command()
@click.argument("id", type=str, required=False)
@cli.org_id
@click.option("--pdf-report", is_flag=True, help="Generate PDF report")
@click.option("--html-report", is_flag=True, help="Generate HTML report")
def get(id: str, org: str, pdf_report: bool, html_report: bool):
    """Get advisor information about a desktop pool."""
    id = recent.require("pool", id)
    org_id = cli.get_org_id(org)
    org_details = details.get(org_id)

    # Handle case where org_details is None
    if org_details is None:
        org_name = "Unknown Organization"
        click.echo(f"Warning: Could not retrieve organization details for org_id: {org_id}")
    else:
        org_name = org_details.get("orgName", "Unknown Organization")

    click.echo(f"Getting advisor information for pool: {id} in organization: {org_name}")

    # Check if any report options are specified
    if not pdf_report and not html_report:
        pdf_report, html_report = prompt_for_report_options()
        if not pdf_report and not html_report:
            click.echo("No reports will be generated.")
            return

    # Get template information with usage data
    template_info = get_template_info(id, org_id)

    # Generate PDF report if requested
    if pdf_report:
        pdf_file = create_report_file("pool_advisor", id, "pdf")
        create_pool_pdf_report(org_id, id, "Pool", template_info, filename=pdf_file)
        click.echo(f"PDF report generated: {pdf_file}")

        # Open the PDF file in the default browser
        try:
            file_url = urllib.parse.urljoin("file:", urllib.request.pathname2url(pdf_file))
            webbrowser.open(file_url)
            click.echo("Opening PDF report in your default browser...")
        except Exception as e:
            click.echo(f"Warning: Could not open PDF automatically: {str(e)}")
            click.echo("Please open the PDF file manually from the location shown above.")

    # Generate HTML report if requested
    if html_report:
        html_file = create_report_file("pool_advisor", id, "html")
        create_pool_html_report(org_id, id, "Pool", template_info, filename=html_file)
        click.echo(f"HTML report generated: {html_file}")

        # Open the HTML file in the default browser
        try:
            file_url = urllib.parse.urljoin("file:", urllib.request.pathname2url(html_file))
            webbrowser.open(file_url)
            click.echo("Opening HTML report in your default browser...")
        except Exception as e:
            click.echo(f"Warning: Could not open HTML automatically: {str(e)}")
            click.echo("Please open the HTML file manually from the location shown above.")
