"""
Copyright © 2025 Omnissa, LLC.
"""

# Standard library imports
import json
import urllib.parse
import urllib.request
import webbrowser

# Third-party imports
import click

# Local imports
from hcs_core.ctxp import recent

from hcs_cli.cmds.advisor.advisor_utils import create_report_file, get_template_info, prompt_for_report_options
from hcs_cli.cmds.advisor.html_utils import create_org_html_report
from hcs_cli.cmds.advisor.pdf_utils import create_org_pdf_report
from hcs_cli.cmds.advisor.recommendation_engine import generate_recommendations
from hcs_cli.service.org_service import details
from hcs_cli.support.exec_util import exec


@click.group()
def org():
    """Advisor commands for organizations."""
    pass


@org.command()
@click.argument("id", type=str, required=False)
@click.option("--pdf-report", is_flag=True, help="Generate PDF report")
@click.option("--html-report", is_flag=True, help="Generate HTML report")
def get(id, pdf_report, html_report):
    """Get organization advisor information and recommendations."""
    try:
        org_id = recent.require("org", id)
        org_details = details.get(org_id)
        org_name = org_details.get("orgName", "Unknown Organization")
        click.echo(f"Getting advisor information for organization: {org_name}")

        # Check if any report options are specified
        if not pdf_report and not html_report:
            pdf_report, html_report = prompt_for_report_options()
            if not pdf_report and not html_report:
                click.echo("No reports will be generated.")
                return

        # Get all templates in the organization
        result = exec(f"hcs template list --org {org_id}")
        templates = json.loads(result.stdout)
        click.echo(f"Total templates: {len(templates)}")
        click.echo(f"Template types: {set(template.get('templateType') for template in templates)}")

        if not templates:
            click.echo("No templates found in the organization")
            return

        # Collect recommendations for each template
        all_recommendations = []
        for template in templates:
            template_id = template.get("id")
            template_name = template.get("name", "Unknown Template")
            template_type = template.get("templateType", "Unknown Template Type")

            # Get template info with usage data
            template_info = get_template_info(template_id, org_id)

            # Get recommendations for this template
            recommendations_data = generate_recommendations(org_id, template_id, "pool", template_info)
            if recommendations_data and recommendations_data.get("recommendations"):
                all_recommendations.append(
                    {
                        "template_id": template_id,
                        "template_name": template_name,
                        "template_type": template_type,
                        "recommendations": recommendations_data["recommendations"],
                    }
                )

        # Generate PDF report if requested
        if pdf_report:
            pdf_file = create_report_file("org_advisor", org_id, "pdf")
            create_org_pdf_report(org_details, all_recommendations, filename=pdf_file)
            click.echo(f"Organization advisor PDF report generated: {pdf_file}")

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
            html_file = create_report_file("org_advisor", org_id, "html")
            create_org_html_report(org_details, all_recommendations, filename=html_file)
            click.echo(f"Organization advisor HTML report generated: {html_file}")

            # Open the HTML file in the default browser
            try:
                file_url = urllib.parse.urljoin("file:", urllib.request.pathname2url(html_file))
                webbrowser.open(file_url)
                click.echo("Opening HTML report in your default browser...")
            except Exception as e:
                click.echo(f"Warning: Could not open HTML automatically: {str(e)}")
                click.echo("Please open the HTML file manually from the location shown above.")

    except Exception as e:
        click.echo(f"Error: {str(e)}")
        raise click.Abort()
