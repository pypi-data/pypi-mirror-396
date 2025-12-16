"""
Copyright © 2025 Omnissa, LLC.
"""

# Standard library imports
import os
from datetime import datetime
from typing import List

# Third-party imports
import click

# Local imports
import hcs_cli.service as hcs
from hcs_cli.cmds.advisor.config.advisor_config import CAPACITY_UTILIZATION_CUTOFF_DATE


def validate_and_fix_history_data(template_info: dict) -> dict:
    """
    Validate and fix data inconsistencies in template history data.

    Validation rules:
    1. provisionedVms >= poweredOnAssignedVms + poweredOnUnassignedVms
    2. poweredOnAssignedVms + poweredOnUnassignedVms >= utilized_capacity

    Args:
        template_info: Template information with usage data

    Returns:
        dict: Template info with corrected history data, or None if validation fails
    """
    try:
        if not template_info or "meta" not in template_info:
            click.echo("Warning: No template information or meta data found")
            return None

        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})

        if not history:
            click.echo("Warning: No history data found in template information")
            return None

        # Get template type and sessions per VM
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        is_multi_session = template_type == "MULTI_SESSION"
        sessions_per_vm = template.get("sessionsPerVm", 1) if is_multi_session else 1

        # Get data arrays
        provisioned_vms = history.get("provisionedVms", [])
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])
        consumed_sessions = history.get("consumedSessions", [])

        # Validate that all arrays have the same length
        max_length = max(len(provisioned_vms), len(powered_on_assigned), len(powered_on_unassigned), len(consumed_sessions))

        if max_length == 0:
            click.echo("Warning: No data points found in history")
            return None

        # Extend arrays to max_length if needed
        provisioned_vms = provisioned_vms + [0] * (max_length - len(provisioned_vms))
        powered_on_assigned = powered_on_assigned + [0] * (max_length - len(powered_on_assigned))
        powered_on_unassigned = powered_on_unassigned + [0] * (max_length - len(powered_on_unassigned))
        consumed_sessions = consumed_sessions + [0] * (max_length - len(consumed_sessions))

        # Create copies for modification
        corrected_provisioned_vms = provisioned_vms.copy()
        corrected_powered_on_assigned = powered_on_assigned.copy()
        corrected_powered_on_unassigned = powered_on_unassigned.copy()
        corrected_consumed_sessions = consumed_sessions.copy()

        issues_found = 0

        # Validate and fix data at each sampling point
        for i in range(max_length):
            original_provisioned = provisioned_vms[i]
            original_assigned = powered_on_assigned[i]
            original_unassigned = powered_on_unassigned[i]
            original_consumed = consumed_sessions[i]

            # Calculate powered-on VMs (assigned + unassigned)
            powered_on_total = original_assigned + original_unassigned

            # Calculate utilized capacity (convert sessions to VM-equivalent for MULTI_SESSION)
            if is_multi_session and sessions_per_vm > 0:
                utilized_capacity = original_consumed / sessions_per_vm
            else:
                utilized_capacity = original_consumed

            # Rule 1: provisionedVms >= poweredOnAssignedVms + poweredOnUnassignedVms
            if powered_on_total > original_provisioned:
                # Distribute the reduction proportionally between assigned and unassigned
                if powered_on_total > 0:
                    ratio_assigned = original_assigned / powered_on_total
                    ratio_unassigned = original_unassigned / powered_on_total
                    corrected_powered_on_assigned[i] = int(original_provisioned * ratio_assigned)
                    corrected_powered_on_unassigned[i] = int(original_provisioned * ratio_unassigned)
                    # Ensure the sum equals original_provisioned
                    corrected_powered_on_assigned[i] = original_provisioned - corrected_powered_on_unassigned[i]
                else:
                    corrected_powered_on_assigned[i] = 0
                    corrected_powered_on_unassigned[i] = original_provisioned
                issues_found += 1

            # Recalculate powered_on_total after potential correction
            corrected_powered_on_total = corrected_powered_on_assigned[i] + corrected_powered_on_unassigned[i]

            # Rule 2: poweredOnAssignedVms + poweredOnUnassignedVms >= utilized_capacity
            if utilized_capacity > corrected_powered_on_total:
                # For MULTI_SESSION, convert back to sessions
                if is_multi_session and sessions_per_vm > 0:
                    corrected_consumed_sessions[i] = int(corrected_powered_on_total * sessions_per_vm)
                else:
                    corrected_consumed_sessions[i] = int(corrected_powered_on_total)
                issues_found += 1

        if issues_found > 0:
            click.echo(f"Warning: Fixed {issues_found} data inconsistencies in template history")

            # Update the history data with corrected values
            corrected_history = history.copy()
            corrected_history["provisionedVms"] = corrected_provisioned_vms
            corrected_history["poweredOnAssignedVms"] = corrected_powered_on_assigned
            corrected_history["poweredOnUnassignedVms"] = corrected_powered_on_unassigned
            corrected_history["consumedSessions"] = corrected_consumed_sessions

            # Create corrected template_info
            corrected_template_info = template_info.copy()
            corrected_template_info["meta"] = meta_data.copy()
            corrected_template_info["meta"]["history"] = corrected_history

            return corrected_template_info
        else:
            # Debug info - not shown to user in CLI context
            return template_info

    except Exception as e:
        click.echo(f"Error: Error during data validation: {str(e)}")
        return None


def get_template_info(template_id: str, org_id: str) -> dict:
    """Get template information using hcs scm template command."""
    try:
        usage = hcs.scm.template_usage(org_id, template_id)
        if not usage:
            click.echo(f"Warning: No usage data available for template (ID: {template_id})")
            usage = {}
        template = hcs.template.get(org_id=org_id, id=template_id)
        if not template:
            click.echo("Warning: Could not fetch template details")
            template = {}

        template_info = {"meta": usage, "template": template}

        # Validate and fix data inconsistencies
        validated_template_info = validate_and_fix_history_data(template_info)
        if validated_template_info is None:
            click.echo("Warning: Data validation failed, returning original data")
            return template_info

        return validated_template_info
    except Exception as e:
        click.echo(f"Warning: Could not fetch template information: {str(e)}")
        return {}


def create_report_file(prefix: str, id: str, extension: str = "pdf") -> str:
    """
    Create a report file path in the hcs-reports directory.

    Args:
        prefix: Prefix for the report file (e.g., 'pool_advisor', 'org_advisor')
        id: Identifier for the report (e.g., pool_id, org_id)
        extension: File extension (e.g., 'pdf', 'html')

    Returns:
        str: Full path to the report file
    """
    reports_dir = os.path.expanduser("~/hcs-reports")
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(reports_dir, f"{prefix}_{id}_{timestamp}.{extension}")


def calculate_cutoff_index(start_timestamp: int, timeslot_ms: int, cutoff_date_str: str = CAPACITY_UTILIZATION_CUTOFF_DATE) -> int:
    """
    Calculate the index from which to start processing data based on a cutoff date.

    Args:
        start_timestamp: Start timestamp in milliseconds
        timeslot_ms: Time interval between values in milliseconds
        cutoff_date_str: Cutoff date string in format "YYYY-MM-DD HH:MM:SS"

    Returns:
        int: Index from which to start processing data (0-based)
    """
    try:
        # Parse the cutoff date
        cutoff_datetime = datetime.strptime(cutoff_date_str, "%Y-%m-%d %H:%M:%S")
        cutoff_timestamp = int(cutoff_datetime.timestamp() * 1000)

        # If cutoff is before start timestamp, return 0 (use all data)
        if cutoff_timestamp <= start_timestamp:
            return 0

        # Calculate how many time slots have passed since start
        time_diff_ms = cutoff_timestamp - start_timestamp
        cutoff_index = int(time_diff_ms / timeslot_ms)

        # Ensure we don't return a negative index
        return max(0, cutoff_index)
    except Exception:
        # If there's any error parsing the date, return 0 (use all data)
        return 0


def calculate_duration_from_history(
    history_values: List[int], timeslot_ms: int, is_multi_session: bool = False, sessions_per_vm: int = 1, start_index: int = 0
) -> float:
    """
    Calculate total history duration hours from a list of history values and timeslot in milliseconds.

    Args:
        history_values: List of values from history
        timeslot_ms: Time interval between values in milliseconds
        is_multi_session: Whether this is a MULTI_SESSION template calculation
        sessions_per_vm: Number of sessions per VM for MULTI_SESSION templates
        start_index: Index from which to start processing data (0-based)

    Returns:
        float: Total hours calculated from the values starting from start_index
    """
    if not history_values or not timeslot_ms:
        return 0.0

    # Filter values starting from start_index
    filtered_values = history_values[start_index:] if start_index < len(history_values) else []

    if not filtered_values:
        return 0.0

    # Convert timeslot from milliseconds to hours
    timeslot_hours = timeslot_ms / (1000 * 60 * 60)

    # Calculate total hours
    if is_multi_session and sessions_per_vm > 0:
        # For MULTI_SESSION templates, divide each value by sessions_per_vm before summing
        adjusted_values = [value / sessions_per_vm for value in filtered_values]
        total_hours = sum(adjusted_values) * timeslot_hours
    else:
        # For non-MULTI_SESSION templates, use existing logic
        total_hours = sum(filtered_values) * timeslot_hours

    return round(total_hours, 2)


def calculate_usage_metrics(template_info: dict) -> List[List[str]]:
    """
    Calculate usage metrics from template_info data.

    Args:
        template_info: Dictionary containing template information and usage data

    Returns:
        List[List[str]]: List of [metric, value] for usage data table
    """
    if not template_info or "meta" not in template_info:
        return [
            ["Metric", "Value"],
            ["Allocated VMs Hours", "N/A"],
            ["Powered-on VMs Hours", "N/A"],
            ["Utilized Capacity Hours", "N/A"],
            ["Idle Capacity Hours", "N/A"],
            ["Capacity Utilization", "N/A"],
        ]

    meta_data = template_info["meta"]
    history = meta_data.get("history", {})
    timeslot_ms = meta_data.get("timeslotMs", 0)
    start_timestamp = history.get("startTimestamp")

    # Check if this is a MULTI_SESSION template
    template = template_info.get("template", {})
    template_type = template.get("templateType", "")
    is_multi_session = template_type == "MULTI_SESSION"

    # Get sessions_per_vm for MULTI_SESSION templates
    sessions_per_vm = 1
    if is_multi_session:
        sessions_per_vm = template.get("sessionsPerVm", 1)

    # Calculate cutoff index for Capacity Utilization (only use data after cutoff date)
    cutoff_index = 0
    if start_timestamp and timeslot_ms:
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, CAPACITY_UTILIZATION_CUTOFF_DATE)

    # Calculate metrics using new data sources with cutoff for Capacity Utilization
    allocated_hours = calculate_duration_from_history(
        history.get("provisionedVms", []), timeslot_ms, is_multi_session=False, sessions_per_vm=1, start_index=cutoff_index
    )

    # Calculate Powered-on VMs from assigned + unassigned
    powered_on_assigned = history.get("poweredOnAssignedVms", [])
    powered_on_unassigned = history.get("poweredOnUnassignedVms", [])
    powered_on_vms = []

    # Combine the two arrays, handling different lengths
    max_length = max(len(powered_on_assigned), len(powered_on_unassigned))
    for i in range(max_length):
        assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
        unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
        powered_on_vms.append(assigned_val + unassigned_val)

    powered_on_hours = calculate_duration_from_history(
        powered_on_vms, timeslot_ms, is_multi_session=False, sessions_per_vm=1, start_index=cutoff_index
    )

    # Calculate Utilized Capacity with MULTI_SESSION logic
    utilized_hours = calculate_duration_from_history(
        history.get("consumedSessions", []),
        timeslot_ms,
        is_multi_session=is_multi_session,
        sessions_per_vm=sessions_per_vm,
        start_index=cutoff_index,
    )

    # Calculate Idle Capacity as Powered-on VMs - Utilized Capacity
    idle_hours = powered_on_hours - utilized_hours
    if idle_hours < 0:
        idle_hours = 0  # Ensure non-negative values

    # Calculate resource utilization
    utilization = 0.0
    if allocated_hours > 0:
        utilization = (utilized_hours / allocated_hours) * 100

    # Format the metrics for display
    metrics = [
        ["Metric", "Value"],
        [
            "Allocated VMs Hours",
            f"{allocated_hours:,.0f}",
        ],
        [
            "Powered-on VMs Hours",
            f"{powered_on_hours:,.0f}",
        ],
        [
            "Utilized Capacity Hours",
            f"{utilized_hours:,.0f}",
        ],
        ["Idle Capacity Hours", f"{idle_hours:,.0f}"],
        [
            "Capacity Utilization",
            f"{utilization:.1f}%",
        ],
    ]

    return metrics


def prompt_for_report_options() -> tuple[bool, bool]:
    """Prompt user to select report generation options when none are specified.

    Returns:
        tuple[bool, bool]: (generate_pdf, generate_html)
    """
    click.echo("No report type specified. Please choose:")
    click.echo("1. Generate PDF report")
    click.echo("2. Generate HTML report")
    click.echo("3. Generate both PDF and HTML reports")
    click.echo("4. No reports (exit)")

    while True:
        choice = click.prompt("Enter your choice (1-4)", type=int)
        if choice == 1:
            return True, False
        elif choice == 2:
            return False, True
        elif choice == 3:
            return True, True
        elif choice == 4:
            return False, False
        else:
            click.echo("Invalid choice. Please enter 1, 2, 3, or 4.")
