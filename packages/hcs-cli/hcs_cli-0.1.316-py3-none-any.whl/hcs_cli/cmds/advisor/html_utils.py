"""
Copyright © 2025 Omnissa, LLC.
"""

import json
from datetime import datetime, timedelta

import yumako

from hcs_cli.cmds.advisor.advisor_utils import calculate_usage_metrics
from hcs_cli.cmds.advisor.recommendation_engine import generate_recommendations
from hcs_cli.service.org_service import details

# Chart type switch: "line" or "area"
CHART_TYPE = "area"


def create_pool_html_report(org_id: str, resource_id: str, resource_type: str, template_info: dict = None, filename: str = None):
    """Create an HTML report for advisor insights (pool)."""
    try:
        org_details = details.get(org_id)
        org_name = org_details.get("orgName", "Unknown Organization") if org_details else "Unknown Organization"

        # Get usage metrics
        usage_data = calculate_usage_metrics(template_info) if template_info else []

        # Prepare chart data for VM Utilization
        chart_data = prepare_vm_utilization_chart_data(template_info)

        # Get recommendations (matching pdf_utils.py logic)
        try:
            recommendations = generate_recommendations(org_id, resource_id, resource_type, template_info)
        except Exception as e:
            print(f"Warning: Could not generate recommendations: {str(e)}")
            recommendations = {"recommendations": []}

        # Generate HTML content
        formatted_resource_type = _format_resource_type_with_template(resource_type, template_info)
        html_content = _get_pool_html_template(
            org_name=org_name,
            resource_type=formatted_resource_type,
            resource_id=resource_id,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            template_info=template_info,
            usage_data=usage_data,
            chart_data=chart_data,
            recommendations=recommendations,
        )

        # Write HTML file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return filename

    except Exception as e:
        raise Exception(f"Failed to create HTML report: {str(e)}")


def create_org_html_report(org_details: dict, all_recommendations: list, filename: str = None):
    """Generate an HTML report for an organization with recommendations for all templates."""
    try:
        org_name = org_details.get("orgName", "Unknown Organization")

        # Generate HTML content
        html_content = _get_org_html_template(
            org_name=org_name,
            generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            all_recommendations=all_recommendations,
        )

        # Write HTML file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return filename

    except Exception as e:
        raise Exception(f"Failed to create HTML report: {str(e)}")


def prepare_vm_utilization_chart_data(template_info: dict) -> dict:
    """Prepare chart data for VM Utilization chart."""

    # Extract real data from template_info if available
    meta_data = template_info.get("meta", {})
    history = meta_data.get("history", {})

    # Generate proper date labels using startTimestamp and timeslot
    start_timestamp = history.get("startTimestamp")
    timeslot_ms = meta_data.get("timeslotMs", 0)
    provisioned_vms = history.get("provisionedVms", [])

    if start_timestamp and timeslot_ms and provisioned_vms:
        # Get full data arrays first (no sampling)
        data_length = len(provisioned_vms)

        # Calculate Powered-on VMs from assigned + unassigned
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])
        powered_on_vms = []

        # Combine the two arrays, handling different lengths
        max_length = max(len(powered_on_assigned), len(powered_on_unassigned), data_length)
        for i in range(max_length):
            assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
            unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
            powered_on_vms.append(assigned_val + unassigned_val)

        # Get Utilized Capacity data
        utilized_capacity = history.get("consumedSessions", [])

        # Handle MULTI_SESSION templates by converting sessions to VM-equivalent
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        sessions_per_vm = 1
        if template_type == "MULTI_SESSION":
            sessions_per_vm = template.get("sessionsPerVm", 1)
            # Convert sessions to VM-equivalent capacity
            if sessions_per_vm > 0:
                utilized_capacity = [sessions / sessions_per_vm for sessions in utilized_capacity]

        # Ensure all data arrays have the same length
        powered_on_vms = powered_on_vms[:data_length]
        utilized_capacity = utilized_capacity[:data_length]

        # Pad shorter arrays with zeros if needed
        while len(powered_on_vms) < data_length:
            powered_on_vms.append(0)
        while len(utilized_capacity) < data_length:
            utilized_capacity.append(0)

        start_date = datetime.fromtimestamp(start_timestamp / 1000)
        x_axis = [start_date + timedelta(minutes=(timeslot_ms / (1000 * 60)) * i) for i in range(data_length)]

        # Convert datetime objects to formatted strings for ECharts
        x_axis = [dt.strftime("%Y-%m-%d %H:%M") for dt in x_axis]
    else:
        x_axis = []
        provisioned_vms = []
        powered_on_vms = []
        utilized_capacity = []

    return {
        "x_axis": x_axis,
        "provisioned_vms": provisioned_vms,
        "powered_on_vms": powered_on_vms,
        "utilized_capacity": utilized_capacity,
    }


def _format_resource_type_with_template(resource_type: str, template_info: dict = None) -> str:
    """
    Format resource type to include template type for pools.

    Args:
        resource_type: Original resource type (e.g., "pool", "edge", "uag")
        template_info: Template information containing template type

    Returns:
        str: Formatted resource type (e.g., "Pool(MULTI_SESSION)", "Pool(FLOATING)")
    """
    if not template_info or resource_type.lower() != "pool":
        return resource_type.title()

    template = template_info.get("template", {})
    template_type = template.get("templateType", "")

    if template_type:
        return f"Pool({template_type})"
    else:
        return "Pool"


def _format_json_to_text(json_data, indent=2):
    """Format JSON data to readable text (matching pdf_utils.py function)."""
    if not json_data:
        return "N/A"
    try:
        return json.dumps(json_data, indent=indent)
    except:
        return str(json_data)


def _get_pool_html_template(
    org_name: str,
    resource_type: str,
    resource_id: str,
    generation_date: str,
    template_info: dict,
    usage_data: list,
    chart_data: dict,
    recommendations: dict,
) -> str:
    """Generate HTML template for pool advisor report."""

    # Format usage data table
    usage_table_html = ""
    for row in usage_data:
        cells = [f"<td>{cell}</td>" for cell in row]
        usage_table_html += f"<tr>{''.join(cells)}</tr>"

    # Format summary information from meta data
    summary_html = ""
    if template_info and "meta" in template_info:
        meta_data = template_info["meta"]
        history = meta_data.get("history", {})

        # Calculate summary information (matching pdf_utils.py logic)
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if start_timestamp and "provisionedVms" in history:
            start_date = datetime.fromtimestamp(start_timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

            # Calculate end timestamp from data length (matching pdf_utils.py logic)
            len_history = len(history["provisionedVms"])
            end_timestamp = start_timestamp + (len_history * timeslot_ms)
            end_date = datetime.fromtimestamp(end_timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

            # Calculate duration (fixed calculation)
            duration_seconds = (end_timestamp - start_timestamp) / 1000
            duration_days = duration_seconds / (24 * 60 * 60)

            # Format timeslot
            timeslot_minutes = timeslot_ms / (1000 * 60)

            summary_html = f"""
            <tr><td><strong>History Start</strong></td><td>{start_date}</td></tr>
            <tr><td><strong>History End</strong></td><td>{end_date}</td></tr>
            <tr><td><strong>History Duration</strong></td><td>{duration_days:.0f} days</td></tr>
            <tr><td><strong>Time Slot</strong></td><td>{timeslot_minutes:.1f} minutes</td></tr>
            """
        else:
            # Fallback when required data is not available
            timeslot_minutes = timeslot_ms / (1000 * 60)
            summary_html = f"""
            <tr><td><strong>History Start</strong></td><td>Not available</td></tr>
            <tr><td><strong>History End</strong></td><td>Not available</td></tr>
            <tr><td><strong>History Duration</strong></td><td>Not available</td></tr>
            <tr><td><strong>Time Slot</strong></td><td>{timeslot_minutes:.1f} minutes</td></tr>
            """
    else:
        # Fallback when no meta data is available
        summary_html = """
        <tr><td><strong>History Start</strong></td><td>No data available</td></tr>
        <tr><td><strong>History End</strong></td><td>No data available</td></tr>
        <tr><td><strong>History Duration</strong></td><td>No data available</td></tr>
        <tr><td><strong>Time Slot</strong></td><td>No data available</td></tr>
        """

    # Format recommendations table
    recommendations_html = ""
    if recommendations and recommendations.get("recommendations"):
        for rec in recommendations["recommendations"]:
            current_settings = _format_json_to_text(rec.get("current_settings", {}))
            recommended_settings = _format_json_to_text(rec.get("recommended_settings", {}))
            recommendations_html += f"""
            <tr>
                <td>{rec.get("action", "N/A")}</td>
                <td>{rec.get("justification", "N/A")}</td>
                <td><pre>{current_settings}</pre></td>
                <td><pre>{recommended_settings}</pre></td>
            </tr>
            """
    else:
        recommendations_html = """
        <tr>
            <td colspan="4" style="text-align: center; color: #666;">No recommendations available for this resource.</td>
        </tr>
        """

    # Generate chart series configuration based on CHART_TYPE
    if CHART_TYPE == "area":
        chart_series = f"""
            {{
                name: 'Allocated VMs',
                type: 'line',
                areaStyle: {{
                    color: '#007acc',
                    opacity: 0.3
                }},
                lineStyle: {{
                    width: 2,
                    color: '#007acc'
                }},
                itemStyle: {{
                    color: '#007acc'
                 }},
                data: {chart_data['provisioned_vms']}
            }},
            {{
                name: 'Powered-on VMs',
                type: 'line',
                areaStyle: {{
                    color: '#dc3545',
                    opacity: 0.3
                }},
                lineStyle: {{
                    width: 2,
                    color: '#dc3545'
                }},
                itemStyle: {{
                    color: '#dc3545'
                }},
                data: {chart_data['powered_on_vms']}
            }},
            {{
                name: 'Utilized Capacity',
                type: 'line',
                areaStyle: {{
                    color: '#28a745',
                    opacity: 0.3
                }},
                lineStyle: {{
                    width: 2,
                    color: '#28a745'
                }},
                itemStyle: {{
                    color: '#28a745'
                }},
                data: {chart_data['utilized_capacity']}
            }}
        """
    else:  # line chart
        chart_series = f"""
            {{
                name: 'Allocated VMs',
                type: 'line',
                lineStyle: {{ width: 2 }},
                emphasis: {{
                    focus: 'series'
                }},
                color: '#007acc',
                data: {chart_data['provisioned_vms']}
            }},
            {{
                name: 'Powered-on VMs',
                type: 'line',
                lineStyle: {{ width: 2 }},
                emphasis: {{
                    focus: 'series'
                }},
                color: '#dc3545',
                data: {chart_data['powered_on_vms']}
            }},
            {{
                name: 'Utilized Capacity',
                type: 'line',
                lineStyle: {{ width: 2 }},
                emphasis: {{
                    focus: 'series'
                }},
                color: '#28a745',
                data: {chart_data['utilized_capacity']}
            }}
        """

    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horizon Cloud Next-gen Advisor Report</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007acc;
            margin: 0;
            font-size: 28px;
        }
        .metadata {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metadata p {
            margin: 5px 0;
            color: #555;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #007acc;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        .section h3 {
            color: #007acc;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #007acc;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        pre {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            font-size: 12px;
        }
        .chart-container {
            width: 100%;
            height: 400px;
            margin: 20px 0;
        }
        #vm-utilization-chart {
            width: 100%;
            height: 400px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Horizon Cloud Next-gen Advisor Report</h1>
        </div>

        <div class="metadata">
            <p><strong>Generated on:</strong> {{generation_date}}</p>
            <p><strong>Organization:</strong> {{org_name}}</p>
            <p><strong>Resource Type:</strong> {{resource_type}}</p>
            <p><strong>Resource ID:</strong> {{resource_id}}</p>
        </div>

        <div class="section">
            <h2>Part 1: Horizon Cloud Next-gen Usage Insights</h2>

            <h3>Summary Information</h3>
            <table>
                <tr>
                    <th>Field</th>
                    <th>Value</th>
                </tr>
                {{summary_html}}
            </table>

            <h3>Usage Metrics</h3>
            <table>
                {{usage_table_html}}
            </table>
        </div>

        <div class="section">
            <h2>VM Utilization</h2>
            <div id="vm-utilization-chart" class="chart-container"></div>
        </div>

        <div class="section">
            <h2>Part 2: Recommendation Actions</h2>
            <table>
                <tr>
                    <th>Action</th>
                    <th>Justification</th>
                    <th>Current Settings</th>
                    <th>Recommended Settings</th>
                </tr>
                {{recommendations_html}}
            </table>
        </div>
    </div>

    <script>
        window.addEventListener('DOMContentLoaded', function () {
            var chartDom = document.getElementById('vm-utilization-chart');
            chartDom.style.width = '100%';
            chartDom.style.height = '400px';
            var myChart = echarts.init(chartDom);
            var option = {
                title: { text: 'VM Utilization Over Time' },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross',
                        label: { backgroundColor: '#6a7985' }
                    }
                },
                legend: { data: ['Allocated VMs', 'Powered-on VMs', 'Utilized Capacity'] },
                toolbox: { feature: { saveAsImage: {} } },
                grid: { left: '7%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: [{
                    type: 'category',
                    boundaryGap: true,
                    data: {{x_axis_data}},
                    axisLine: { show: true },
                    axisLabel: { show: true },
                    splitLine: { show: true }
                }],
                yAxis: [{
                    type: 'value',
                    min: 0,
                    max: 'dataMax',
                    name: 'Capacity Count',
                    nameLocation: 'middle',
                    nameGap: 50,
                    nameTextStyle: {
                        fontSize: 14,
                        fontWeight: 'bold',
                        color: '#333'
                    },
                    axisLine: { show: true },
                    axisLabel: { show: true },
                    splitLine: { show: true },
                    axisTick: { show: true }
                }],
                series: [
                    {{chart_series_data}}
                ]
            };
            myChart.setOption(option);
            window.addEventListener('resize', () => myChart.resize());
        });
    </script>
</body>
</html>
"""

    return yumako.template.replace(
        template,
        {
            "org_name": org_name,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "generation_date": generation_date,
            "summary_html": summary_html,
            "usage_table_html": usage_table_html,
            "recommendations_html": recommendations_html,
            "x_axis_data": chart_data["x_axis"],
            "chart_series_data": chart_series,
        },
    )


def _get_org_html_template(org_name: str, generation_date: str, all_recommendations: list) -> str:
    """Generate HTML template for organization advisor report."""

    # Format recommendations for display
    recommendations_html = ""
    for template_data in all_recommendations:
        template_name = template_data["template_name"]
        template_type = template_data["template_type"]
        recommendations = template_data["recommendations"]

        recommendations_html += f"""
        <div class="template-section">
            <h3>Template: {template_name} ({template_type})</h3>
            <table>
                <tr>
                    <th>Action</th>
                    <th>Justification</th>
                    <th>Current Settings</th>
                    <th>Recommended Settings</th>
                </tr>
        """

        for rec in recommendations:
            current_settings = json.dumps(rec["current_settings"], indent=2)
            recommended_settings = json.dumps(rec["recommended_settings"], indent=2)
            recommendations_html += f"""
                <tr>
                    <td>{rec['action']}</td>
                    <td>{rec['justification']}</td>
                    <td><pre>{current_settings}</pre></td>
                    <td><pre>{recommended_settings}</pre></td>
                </tr>
            """

        recommendations_html += "</table></div>"

    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horizon Cloud Next-gen Organization Advisor Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007acc;
            margin: 0;
            font-size: 28px;
        }
        .metadata {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metadata p {
            margin: 5px 0;
            color: #555;
        }
        .template-section {
            margin-bottom: 30px;
        }
        .template-section h3 {
            color: #007acc;
            border-bottom: 1px solid #ddd;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: #007acc;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        pre {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Horizon Cloud Next-gen Organization Advisor Report</h1>
        </div>

        <div class="metadata">
            <p><strong>Generated on:</strong> {{generation_date}}</p>
            <p><strong>Organization:</strong> {{org_name}}</p>
        </div>

        <div class="recommendations">
            {{recommendations_html}}
        </div>
    </div>
</body>
</html>
"""

    return yumako.template.replace(
        template,
        {"org_name": org_name, "generation_date": generation_date, "recommendations_html": recommendations_html},
    )
