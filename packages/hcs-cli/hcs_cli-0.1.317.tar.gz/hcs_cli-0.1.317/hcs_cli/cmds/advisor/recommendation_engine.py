"""
Copyright © 2025 Omnissa, LLC.
"""

"""
Recommendation engine for generating recommendations for advisor reports.
"""

import datetime
import math

import hcs_cli.cmds.advisor.config.advisor_config as config
from hcs_cli.cmds.advisor.advisor_utils import calculate_cutoff_index, calculate_duration_from_history, calculate_usage_metrics


def has_usage_data(template_info: dict) -> bool:
    """
    Check if template_info has usage data available.

    Args:
        template_info: Template information

    Returns:
        bool: True if meta data is not empty and key metrics are not all zero, False otherwise
    """
    # Check if meta data exists
    meta_data = template_info.get("meta", {})
    if not meta_data:
        return False

    try:
        # Get usage metrics
        usage_metrics = calculate_usage_metrics(template_info)

        # Extract the three key metrics
        allocated_hours = 0.0
        powered_on_hours = 0.0
        utilized_hours = 0.0

        for metric in usage_metrics:
            metric_name = metric[0]
            metric_value = metric[1]

            if metric_name == "Allocated VMs Hours":
                try:
                    allocated_hours = float(metric_value.replace(",", ""))
                except (ValueError, AttributeError):
                    allocated_hours = 0.0
            elif metric_name == "Powered-on VMs Hours":
                try:
                    powered_on_hours = float(metric_value.replace(",", ""))
                except (ValueError, AttributeError):
                    powered_on_hours = 0.0
            elif metric_name == "Utilized Capacity Hours":
                try:
                    utilized_hours = float(metric_value.replace(",", ""))
                except (ValueError, AttributeError):
                    utilized_hours = 0.0

        # Return False if all three metrics are zero
        if allocated_hours == 0.0 or powered_on_hours == 0.0 or utilized_hours == 0.0:
            return False

        return True

    except Exception:
        # Conservative approach: return False if any error occurs
        return False


def get_vm_cost_per_hour(template_info: dict) -> float:
    """
    Get VM cost per hour from template information.

    Args:
        template_info: Template information containing VM SKU details

    Returns:
        float: Cost per hour in USD
    """
    try:
        # Try to get VM SKU from template
        template = template_info.get("template", {})
        infrastructure = template.get("infrastructure", {})
        vm_sku = infrastructure.get("vmSku", "Standard_D4ads_v5")

        # Get cost from configuration
        return config.AZURE_VM_COSTS.get(vm_sku, config.AZURE_VM_COSTS["DEFAULT"])
    except Exception:
        return config.AZURE_VM_COSTS["DEFAULT"]


def get_disk_cost_per_hour(template_info: dict, disk_type: str) -> float:
    """
    Get disk cost per hour for a specific disk type.

    Args:
        template_info: Template information
        disk_type: Disk type (e.g., "Premium_LRS", "Standard_LRS")

    Returns:
        float: Cost per hour in USD
    """
    return config.AZURE_DISK_COSTS.get(disk_type, config.AZURE_DISK_COSTS["DEFAULT"])


def calculate_observation_period_days(template_info: dict) -> float:
    """
    Calculate actual observation period in days from cutoff date to end of data.

    Args:
        template_info: Template information with usage data

    Returns:
        float: Observation period in days
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms:
            return 30.0  # Default to 30 days

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get data length after cutoff
        consumed_sessions = history.get("consumedSessions", [])
        data_length_after_cutoff = len(consumed_sessions) - cutoff_index

        if data_length_after_cutoff <= 0:
            return 30.0  # Default to 30 days

        # Calculate observation period in days
        observation_hours = (data_length_after_cutoff * timeslot_ms) / (1000 * 60 * 60)
        observation_days = observation_hours / 24

        return max(1.0, observation_days)  # Minimum 1 day
    except Exception:
        return 30.0  # Default to 30 days


def calculate_actual_hours_per_month(historical_hours: float, template_info: dict) -> float:
    """
    Calculate actual hours per month from historical data using 30-day scaling.

    Args:
        historical_hours: Hours from historical data
        template_info: Template information for observation period calculation

    Returns:
        float: Hours per month (30-day scaled)
    """
    try:
        observation_days = calculate_observation_period_days(template_info)

        # Scale to 30 days: (historical_hours / observation_days) * 30
        hours_per_month = (historical_hours / observation_days) * 30

        return max(0.0, hours_per_month)
    except Exception:
        return historical_hours  # Fallback to original value


def calculate_filtered_hours(template_info: dict, data_type: str) -> float:
    """
    Calculate hours from data after cutoff date with fallback to default values.

    Args:
        template_info: Template information with usage data
        data_type: Type of data to calculate ("allocated", "powered_on", "utilized")

    Returns:
        float: Hours from filtered data
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        timeslot_ms = meta_data.get("timeslotMs", 0)
        start_timestamp = history.get("startTimestamp")
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        is_multi_session = False
        sessions_per_vm = 1

        if not start_timestamp or not timeslot_ms:
            return 0.0

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        if data_type == "allocated":
            data_array = history.get("provisionedVms", [])
        elif data_type == "powered_on":
            # Combine assigned and unassigned
            assigned = history.get("poweredOnAssignedVms", [])
            unassigned = history.get("poweredOnUnassignedVms", [])
            data_array = []
            max_length = max(len(assigned), len(unassigned))
            for i in range(max_length):
                assigned_val = assigned[i] if i < len(assigned) else 0
                unassigned_val = unassigned[i] if i < len(unassigned) else 0
                data_array.append(assigned_val + unassigned_val)
        elif data_type == "utilized":
            data_array = history.get("consumedSessions", [])
            if template_type == "MULTI_SESSION":
                is_multi_session = True
                sessions_per_vm = template.get("sessionsPerVm", 1)
            else:
                is_multi_session = False
                sessions_per_vm = 1
        else:
            return 0.0

        # Calculate hours from filtered data
        hours = calculate_duration_from_history(data_array, timeslot_ms, is_multi_session, sessions_per_vm, start_index=cutoff_index)

        return hours
    except Exception:
        return 0.0


def calculate_peak_utilized_capacity(template_info: dict) -> int:
    """
    Calculate peak utilized capacity (max session count) during observation window.
    For MULTI_SESSION templates, converts session count to VM-equivalent capacity.

    Args:
        template_info: Template information with usage data

    Returns:
        int: Peak utilized capacity (VM-equivalent for MULTI_SESSION)
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        consumed_sessions = history.get("consumedSessions", [])

        if not consumed_sessions:
            return 0

        # Get template type and sessions per VM
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        is_multi_session = template_type == "MULTI_SESSION"

        sessions_per_vm = 1
        if is_multi_session:
            sessions_per_vm = template.get("sessionsPerVm", 1)

        # Calculate peak capacity
        peak_sessions = max(consumed_sessions)

        # For MULTI_SESSION, convert to VM-equivalent capacity
        if is_multi_session and sessions_per_vm > 1:
            peak_capacity = math.ceil(peak_sessions / sessions_per_vm)
        else:
            peak_capacity = peak_sessions

        return peak_capacity
    except Exception:
        return 0


def calculate_powered_off_ratio(template_info: dict) -> float:
    """
    Calculate powered-off ratio for auto scale disk type recommendation.

    Args:
        template_info: Template information with usage data

    Returns:
        float: Powered-off ratio (0.0 to 1.0)
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        timeslot_ms = meta_data.get("timeslotMs", 0)
        start_timestamp = history.get("startTimestamp")

        # Calculate cutoff index for Capacity Utilization (only use data after cutoff date)
        cutoff_index = 0
        if start_timestamp and timeslot_ms:
            cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Calculate allocated VM hours
        allocated_hours = calculate_duration_from_history(
            history.get("provisionedVms", []), timeslot_ms, is_multi_session=False, sessions_per_vm=1, start_index=cutoff_index
        )

        # Calculate powered-on VM hours
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])
        powered_on_vms = []

        # Combine the two arrays
        max_length = max(len(powered_on_assigned), len(powered_on_unassigned))
        for i in range(max_length):
            assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
            unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
            powered_on_vms.append(assigned_val + unassigned_val)

        powered_on_hours = calculate_duration_from_history(
            powered_on_vms, timeslot_ms, is_multi_session=False, sessions_per_vm=1, start_index=cutoff_index
        )

        # Calculate powered-off ratio
        if allocated_hours > 0:
            return (allocated_hours - powered_on_hours) / allocated_hours
        return 0.0
    except Exception:
        return 0.0


def calculate_gradient_based_decrease(peak_utilized: int, max_vms: int, utilization: float) -> int:
    """
    Calculate new maximum VMs using gradient-based decrease formula.

    Args:
        peak_utilized: Peak utilized capacity
        max_vms: Current maximum VMs
        utilization: Resource utilization percentage

    Returns:
        int: New recommended maximum VMs
    """
    try:
        # Calculate scaling factor
        scaling_factor = (config.MAX_UTILIZATION_THRESHOLD - utilization) / (
            config.MAX_UTILIZATION_THRESHOLD - config.MIN_UTILIZATION_THRESHOLD
        )
        scaling_factor = max(0.0, min(1.0, scaling_factor))  # Clamp between 0 and 1

        # Calculate denominator
        denominator = config.MAX_REDUCTION_FACTOR + scaling_factor * config.MAX_REDUCTION_FACTOR

        # Calculate new maximum VMs
        new_max_vms = math.ceil(peak_utilized / denominator)

        # Ensure new max is not greater than current max
        return min(new_max_vms, max_vms)
    except Exception:
        return max_vms


def estimate_cost_savings_max_vms_reduction(old_max_vms: int, new_max_vms: int, template_info: dict) -> float:
    """
    Estimate cost savings for maximum VMs reduction.

    Args:
        old_max_vms: Current maximum VMs
        new_max_vms: New maximum VMs
        template_info: Template information

    Returns:
        float: Estimated monthly savings in USD
    """
    try:
        template = template_info.get("template", {})
        power_policy = template.get("powerPolicy", {})
        min_ratio = power_policy.get("min", 0.5)  # Default to 50%

        vm_cost_per_hour = get_vm_cost_per_hour(template_info)
        disk_cost_per_hour = get_disk_cost_per_hour(template_info, "Premium_LRS")  # Default to Premium_LRS

        # Calculate VM cost savings
        delta_vms = old_max_vms - new_max_vms
        vm_savings = (delta_vms * min_ratio * config.HOURS_PER_MONTH) * vm_cost_per_hour

        # Calculate disk cost savings
        # delta_total_pool_hours_per_month = (Old_Max_VMs - New_Max_VMs) × hours_per_month
        delta_total_pool_hours_per_month = delta_vms * config.HOURS_PER_MONTH
        disk_savings = delta_total_pool_hours_per_month * disk_cost_per_hour

        # Total savings = VM savings + disk savings
        total_savings = vm_savings + disk_savings

        return round(total_savings, 2)
    except Exception:
        return 0.0


def estimate_cost_savings_auto_scale_disk(powered_off_hours_per_month: float, template_info: dict) -> float:
    """
    Estimate cost savings for auto scale disk type.

    Args:
        powered_off_hours_per_month: Estimated powered-off hours per month
        template_info: Template information

    Returns:
        float: Estimated monthly savings in USD
    """
    try:
        template = template_info.get("template", {})
        infrastructure = template.get("infrastructure", {})
        disk_skus = infrastructure.get("diskSkus", [])

        if not disk_skus:
            return 0.0

        disk_data = disk_skus[0].get("data", {})
        current_disk_type = disk_data.get("diskSkuOnPowerOff", "Premium_LRS")

        # Get costs
        original_disk_cost = get_disk_cost_per_hour(template_info, current_disk_type)
        standard_lrs_cost = get_disk_cost_per_hour(template_info, "Standard_LRS")

        # Calculate actual powered-off hours from filtered data
        allocated_hours = calculate_filtered_hours(template_info, "allocated")
        powered_on_hours = calculate_filtered_hours(template_info, "powered_on")
        actual_powered_off_hours = allocated_hours - powered_on_hours

        # Scale to monthly hours
        powered_off_hours_per_month = calculate_actual_hours_per_month(actual_powered_off_hours, template_info)

        # Calculate savings
        savings = powered_off_hours_per_month * (original_disk_cost - standard_lrs_cost)
        return round(savings, 2)
    except Exception:
        return 0.0


def calculate_scheduled_powered_on_hours(template_info: dict, power_schedules: list) -> float:
    """
    Calculate total powered-on VM hours during scheduled periods.

    Args:
        template_info: Template information with usage data
        power_schedules: List of power schedules

    Returns:
        float: Total powered-on hours during scheduled periods
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms or not power_schedules:
            return 0.0

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get powered-on data after cutoff
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])

        if cutoff_index >= len(powered_on_assigned) or cutoff_index >= len(powered_on_unassigned):
            return 0.0

        # Filter data to scheduled periods only
        scheduled_powered_on = []

        # Process each data point
        for i in range(cutoff_index, min(len(powered_on_assigned), len(powered_on_unassigned))):
            # Calculate timestamp for this data point
            point_timestamp = start_timestamp + (i * timeslot_ms)
            point_datetime = datetime.datetime.fromtimestamp(point_timestamp / 1000, tz=datetime.timezone.utc)

            # Check if this point falls within any scheduled period
            if _is_within_scheduled_period(point_datetime, power_schedules):
                assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
                unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
                scheduled_powered_on.append(assigned_val + unassigned_val)

        # Calculate hours from scheduled data
        if not scheduled_powered_on:
            return 0.0

        # Convert timeslot to hours
        timeslot_hours = timeslot_ms / (1000 * 60 * 60)

        # Calculate total powered-on hours during scheduled periods
        total_scheduled_hours = sum(scheduled_powered_on) * timeslot_hours

        return total_scheduled_hours

    except Exception as e:
        print(f"Warning: Error calculating scheduled powered-on hours: {str(e)}")
        return 0.0


def calculate_schedule_duration_30day_month(power_schedules: list) -> float:
    """
    Calculate total schedule duration in hours for a 30-day month.

    Args:
        power_schedules: List of power schedules

    Returns:
        float: Total schedule duration in hours for 30-day month
    """
    try:
        total_hours = 0.0

        for schedule in power_schedules:
            occurs_on = schedule.get("occursOn", 0)
            start_time_str = schedule.get("startTime", "00:00")
            end_time_str = schedule.get("endTime", "23:59")

            # Count active days per week
            active_days_per_week = 0
            for day in range(7):  # Monday to Sunday
                if occurs_on & (1 << day):
                    active_days_per_week += 1

            # Parse start and end times
            try:
                start_hour = int(start_time_str.split(":")[0])
                end_hour = int(end_time_str.split(":")[0])
            except:
                continue

            # Calculate hours per day
            if end_hour < start_hour:
                # Schedule spans midnight
                hours_per_day = (24 - start_hour) + end_hour
            else:
                # Normal schedule
                hours_per_day = end_hour - start_hour

            # Calculate total hours for 30-day month
            # 30 days = 4.28 weeks(30/7)
            total_hours += hours_per_day * active_days_per_week * 4.28

        return total_hours

    except Exception as e:
        print(f"Warning: Error calculating schedule duration: {str(e)}")
        return 0.0


def calculate_overall_average_powered_on_vms(template_info: dict) -> float:
    """
    Calculate overall average powered-on VMs per hour.

    Args:
        template_info: Template information with usage data

    Returns:
        float: Average powered-on VMs per hour
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms:
            return 0.0

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get powered-on data after cutoff
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])

        if cutoff_index >= len(powered_on_assigned) or cutoff_index >= len(powered_on_unassigned):
            return 0.0

        # Calculate total powered-on VMs and total hours
        total_powered_on_vms = 0
        total_data_points = 0

        for i in range(cutoff_index, min(len(powered_on_assigned), len(powered_on_unassigned))):
            assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
            unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
            total_powered_on_vms += assigned_val + unassigned_val
            total_data_points += 1

        if total_data_points == 0:
            return 0.0

        # Calculate average VMs per data point
        average_vms_per_point = total_powered_on_vms / total_data_points

        return average_vms_per_point

    except Exception as e:
        print(f"Warning: Error calculating overall average powered-on VMs: {str(e)}")
        return 0.0


def estimate_cost_savings_power_schedule_removal(template_info: dict) -> float:
    """
    Estimate cost savings for power schedule removal.

    Savings = (historical_powered_on_hours_during_schedule - expected_powered_on_hours_during_schedule) × vm_cost_per_hour

    Args:
        template_info: Template information

    Returns:
        float: Estimated monthly savings in USD
    """
    try:
        template = template_info.get("template", {})
        power_policy = template.get("powerPolicy", {})
        power_schedules = power_policy.get("powerSchedules", [])

        if not power_schedules:
            return 0.0

        # Get VM cost per hour
        vm_cost_per_hour = get_vm_cost_per_hour(template_info)

        # Calculate historical powered-on hours during schedule
        historical_powered_on_hours = calculate_scheduled_powered_on_hours(template_info, power_schedules)

        # Scale historical hours to 30-day month
        historical_powered_on_hours_monthly = calculate_actual_hours_per_month(historical_powered_on_hours, template_info)

        # Calculate expected baseline powered-on hours during schedule
        overall_average_powered_on_vms = calculate_overall_average_powered_on_vms(template_info)
        schedule_duration_hours = calculate_schedule_duration_30day_month(power_schedules)
        expected_powered_on_hours = overall_average_powered_on_vms * schedule_duration_hours

        # Calculate savings (both values now scaled to monthly)
        savings_hours = historical_powered_on_hours_monthly - expected_powered_on_hours

        if savings_hours <= 0:
            return 0.0

        # Calculate monthly savings
        monthly_savings = savings_hours * vm_cost_per_hour

        return round(monthly_savings, 2)

    except Exception as e:
        print(f"Warning: Error estimating power schedule removal savings: {str(e)}")
        return 0.0


def estimate_cost_savings_min_available_vms(old_min: float, new_min: float, template_info: dict) -> float:
    """
    Estimate cost savings for minimum available VMs reduction.

    Args:
        old_min: Current minimum ratio
        new_min: New minimum ratio
        template_info: Template information

    Returns:
        float: Estimated monthly savings in USD
    """
    try:
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        limit = spare_policy.get("limit", 100)

        vm_cost_per_hour = get_vm_cost_per_hour(template_info)

        # Calculate savings
        savings = limit * (old_min - new_min) * config.HOURS_PER_MONTH * vm_cost_per_hour
        return round(savings, 2)
    except Exception:
        return 0.0


def estimate_cost_savings_power_management_mode(template_info: dict) -> float:
    """
    Estimate cost savings for power management mode change.

    Savings = ∑ over sampling points [
        max(0, powered_on_vm_count − (sparePolicy.limit × powerPolicy.min))
        × 0.2
        × sampling_period
    ] × vm_cost_per_hour

    Args:
        template_info: Template information

    Returns:
        float: Estimated monthly savings in USD
    """
    try:
        vm_cost_per_hour = get_vm_cost_per_hour(template_info)

        # Get template configuration
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        power_policy = template.get("powerPolicy", {})

        limit = spare_policy.get("limit", 0)
        min_ratio = power_policy.get("min", 0)

        # Use fallback if min_ratio is missing or zero
        if not min_ratio:
            min_ratio = config.MIN_AVAILABLE_VMS_MIN_BOUND / 100.0  # Convert percentage to decimal

        min_baseline = limit * min_ratio

        if min_baseline <= 0:
            return 0.0

        # Get historical data
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms:
            return 0.0

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get powered-on data after cutoff
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])

        if cutoff_index >= len(powered_on_assigned) or cutoff_index >= len(powered_on_unassigned):
            return 0.0

        # Calculate sampling period in hours
        sampling_period_hours = timeslot_ms / (1000 * 60 * 60)

        # Calculate total savings across all sampling points
        total_savings = 0.0

        for i in range(cutoff_index, min(len(powered_on_assigned), len(powered_on_unassigned))):
            assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
            unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
            powered_on_vm_count = assigned_val + unassigned_val

            # Only include points where powered_on_vm_count > min_baseline
            if powered_on_vm_count > min_baseline:
                surplus_vms = powered_on_vm_count - min_baseline
                point_savings = surplus_vms * config.POWER_MANAGEMENT_REDUCTION_FACTOR * sampling_period_hours * vm_cost_per_hour
                total_savings += point_savings

        # Scale to monthly using the same method as other functions
        monthly_savings = calculate_actual_hours_per_month(total_savings, template_info)

        return round(monthly_savings, 2)

    except Exception as e:
        print(f"Warning: Error estimating power management mode savings: {str(e)}")
        return 0.0


def rule_1a_decrease_maximum_vms(org, resource_id, resource_type, template_info):
    """
    Rule 1a: Decrease Maximum VMs for under-utilization (requires "All at once" provisioning).
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        max_vms = spare_policy.get("limit")

        if not max_vms or max_vms < config.MIN_POOL_SIZE_FOR_RECOMMENDATIONS:
            return None

        # Condition 1: Check if provisioning approach is "All at once"
        if not is_all_at_once_provisioning(template_info):
            return None

        # Get utilization metrics using existing function
        usage_metrics = calculate_usage_metrics(template_info)

        # Find utilization percentage from metrics
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        # Condition 2: Check for under-utilization
        if utilization < config.UNDER_UTILIZATION_THRESHOLD:
            peak_utilized = calculate_peak_utilized_capacity(template_info)

            # Condition 3: Check if peak utilized capacity is <= 10% of max VMs
            if peak_utilized <= max_vms * 0.1:
                new_max_vms = calculate_gradient_based_decrease(peak_utilized, max_vms, utilization)

                # Validate that new_max_vms is reasonable (greater than 0 and less than current max_vms)
                if new_max_vms > 0 and new_max_vms < max_vms:
                    cost_savings = estimate_cost_savings_max_vms_reduction(max_vms, new_max_vms, template_info)

                    # Get the entire sparePolicy object for current_settings
                    current_spare_policy = spare_policy.copy()

                    # Create recommended_settings with limit replaced by new_max_vms
                    recommended_spare_policy = spare_policy.copy()
                    recommended_spare_policy["limit"] = new_max_vms

                    return {
                        "action": "Adjust Maximum VMs",
                        "justification": f"Pool has consistently low usage — peak usage is under 10% and average utilization is under {config.UNDER_UTILIZATION_THRESHOLD}%, potential cost savings: ${cost_savings}/month",
                        "current_settings": {"sparePolicy": current_spare_policy},
                        "recommended_settings": {"sparePolicy": recommended_spare_policy},
                        "estimated_savings": f"${cost_savings}/month",
                    }

    except Exception as e:
        print(f"Warning: Error in decrease maximum VMs rule: {str(e)}")

    return None


def rule_1b_increase_maximum_vms(org, resource_id, resource_type, template_info):
    """
    Rule 1b: Increase Maximum VMs for over-utilization.
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        max_vms = spare_policy.get("limit")

        if not max_vms or max_vms < config.MIN_POOL_SIZE_FOR_RECOMMENDATIONS:
            return None

        # Get utilization metrics using existing function
        usage_metrics = calculate_usage_metrics(template_info)

        # Find utilization percentage from metrics
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        # Check for over-utilization
        if utilization > config.OVER_UTILIZATION_THRESHOLD:
            # Additional gate: Utilized Capacity Hours / Total Pool Hours > threshold
            try:
                utilized_hours = calculate_filtered_hours(template_info, "utilized")
                observation_days = calculate_observation_period_days(template_info)
                observation_hours = max(0.0, observation_days * 24.0)
                if observation_hours <= 0:
                    return None

                total_pool_hours = max_vms * observation_hours
                if total_pool_hours <= 0:
                    return None

                utilized_to_pool_ratio = (utilized_hours / total_pool_hours) * 100.0
            except Exception:
                utilized_to_pool_ratio = 0.0

            if utilized_to_pool_ratio > config.UTILIZED_TO_POOL_RATIO_THRESHOLD:
                # Gradient increase based on how close utilization is to 100%
                try:
                    scaling = (utilization - config.OVER_UTILIZATION_THRESHOLD) / (100.0 - config.OVER_UTILIZATION_THRESHOLD)
                    scaling = max(0.0, min(1.0, scaling))
                    new_max_vms = math.ceil(max_vms * (1.0 + scaling * config.MAX_INCREASE_ADJUSTMENT_FACTOR))
                except Exception:
                    new_max_vms = max_vms

                # Validate that new_max_vms is reasonable (greater than current max_vms)
                if new_max_vms > max_vms:
                    return {
                        "action": "Adjust Maximum VMs",
                        "justification": (
                            f"Resource Utilization > {config.OVER_UTILIZATION_THRESHOLD}% and "
                            f"Utilized Capacity Hours / Total Pool Hours > {config.UTILIZED_TO_POOL_RATIO_THRESHOLD}%. "
                            f"Applied gradient increase. Note: This is a capacity increase recommendation."
                        ),
                        "current_settings": {"sparePolicy": {"limit": max_vms}},
                        "recommended_settings": {"sparePolicy": {"limit": new_max_vms}},
                        "estimated_savings": "N/A (Capacity increase)",
                    }

    except Exception as e:
        print(f"Warning: Error in increase maximum VMs rule: {str(e)}")

    return None


def rule_2_auto_scale_disk_type(org, resource_id, resource_type, template_info):
    """
    Rule 2: Enable Auto Scale Disk Type for cost optimization.
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})

        # Get utilization metrics
        usage_metrics = calculate_usage_metrics(template_info)
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        # Check all conditions
        # Condition 1: Check pool size  > threshold, if not return None
        spare_policy = template.get("sparePolicy", {})
        pool_size = spare_policy.get("limit", 0)
        if pool_size < config.MIN_POOL_SIZE_FOR_AUTO_SCALE_DISK_TYPE:
            return None

        # Condition 2: Check current auto scale settings
        infrastructure = template.get("infrastructure", {})
        disk_skus = infrastructure.get("diskSkus", [])

        if not disk_skus:
            return None

        disk_data = disk_skus[0].get("data", {})
        auto_scale_enabled = disk_data.get("diskSkuAutoScaleEnabled", False)
        current_disk_type = disk_data.get("diskSkuOnPowerOff", "Premium_LRS")

        if auto_scale_enabled or current_disk_type == "Standard_LRS":
            return None

        # Condition 3: Calculate powered-off ratio if it is greater than threshold, if not return None
        powered_off_ratio = calculate_powered_off_ratio(template_info)

        # Condition 4: Resource Utilization (%) < 50, if yes return None
        if utilization >= config.UNDER_UTILIZATION_THRESHOLD:
            return None

        # Condition 5: Check if powered-off ratio is greater than threshold, if yes return recommendation
        if powered_off_ratio >= config.POWERED_OFF_RATIO_THRESHOLD:
            cost_savings = estimate_cost_savings_auto_scale_disk(0, template_info)  # Hours calculated inside function

            return {
                "action": "Enable Auto Scale Disk Type",
                "justification": f"Pool has high powered-off time — VMs are powered off more than {config.POWERED_OFF_RATIO_THRESHOLD * 100}% of the time, disk cost optimization possible, potential cost savings: ${cost_savings}/month",
                "current_settings": {
                    "infrastructure": {"diskSkus": [{"data": {"diskSkuAutoScaleEnabled": False, "diskSkuOnPowerOff": current_disk_type}}]}
                },
                "recommended_settings": {
                    "infrastructure": {"diskSkus": [{"data": {"diskSkuAutoScaleEnabled": True, "diskSkuOnPowerOff": "Standard_LRS"}}]}
                },
                "estimated_savings": f"${cost_savings}/month",
            }

    except Exception as e:
        print(f"Warning: Error in auto scale disk type rule: {str(e)}")

    return None


def has_weekend_schedule(power_schedules: list) -> bool:
    """
    Check if any power schedule includes weekend days (Saturday/Sunday).

    Args:
        power_schedules: List of power schedule dictionaries

    Returns:
        bool: True if any schedule includes weekend days
    """
    try:
        for schedule in power_schedules:
            occurs_on = schedule.get("occursOn", 0)
            # Check if Saturday (32) or Sunday (64) bits are set
            # The occursOn field uses a 7-bit mask where each bit represents a day of the week:
            # Bit 0 (1): Monday
            # Bit 1 (2): Tuesday
            # Bit 2 (4): Wednesday
            # Bit 3 (8): Thursday
            # Bit 4 (16): Friday
            # Bit 5 (32): Saturday
            # Bit 6 (64): Sunday
            if occurs_on & 96:  # 32 + 64 = 96
                return True
        return False
    except Exception:
        return False


def calculate_schedule_resource_utilization(template_info: dict, power_schedules: list) -> float:
    """
    Calculate resource utilization during scheduled hours.

    Args:
        template_info: Template information with usage data
        power_schedules: List of power schedules

    Returns:
        float: Utilization percentage during scheduled hours
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms or not power_schedules:
            return 0.0

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get data arrays after cutoff
        consumed_sessions = history.get("consumedSessions", [])
        provisioned_vms = history.get("provisionedVms", [])

        if cutoff_index >= len(consumed_sessions) or cutoff_index >= len(provisioned_vms):
            return 0.0

        # Filter data to scheduled periods only
        scheduled_consumed = []
        scheduled_provisioned = []

        # Process each data point
        for i in range(cutoff_index, min(len(consumed_sessions), len(provisioned_vms))):
            # Calculate timestamp for this data point
            point_timestamp = start_timestamp + (i * timeslot_ms)
            point_datetime = datetime.datetime.fromtimestamp(point_timestamp / 1000, tz=datetime.timezone.utc)

            # Check if this point falls within any scheduled period
            if _is_within_scheduled_period(point_datetime, power_schedules):
                scheduled_consumed.append(consumed_sessions[i])
                scheduled_provisioned.append(provisioned_vms[i])

        # Calculate hours from scheduled data
        if not scheduled_consumed or not scheduled_provisioned:
            return 0.0

        # Handle MULTI_SESSION templates
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        sessions_per_vm = 1
        if template_type == "MULTI_SESSION":
            sessions_per_vm = template.get("sessionsPerVm", 1)

        # Convert timeslot to hours
        timeslot_hours = timeslot_ms / (1000 * 60 * 60)

        # Calculate scheduled hours
        scheduled_utilized_hours = sum(scheduled_consumed) * timeslot_hours
        scheduled_allocated_hours = sum(scheduled_provisioned) * timeslot_hours

        # For MULTI_SESSION, convert utilized sessions to VM-equivalent hours
        if template_type == "MULTI_SESSION" and sessions_per_vm > 1:
            scheduled_utilized_hours = scheduled_utilized_hours / sessions_per_vm

        # Calculate utilization percentage
        if scheduled_allocated_hours > 0:
            utilization = (scheduled_utilized_hours / scheduled_allocated_hours) * 100
            return max(0.0, utilization)

        return 0.0

    except Exception as e:
        print(f"Warning: Error calculating schedule resource utilization: {str(e)}")
        return 0.0


def _is_within_scheduled_period(point_datetime, power_schedules):
    """
    Check if a datetime point falls within any scheduled period.

    Args:
        point_datetime: UTC datetime to check
        power_schedules: List of power schedule dictionaries

    Returns:
        bool: True if point falls within any scheduled period
    """
    try:

        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = point_datetime.weekday()
        # Convert to our bit mask format (0=Monday, 6=Sunday)
        day_bit = 1 << day_of_week

        # Round to nearest hour for comparison
        point_hour = point_datetime.hour

        for schedule in power_schedules:
            occurs_on = schedule.get("occursOn", 0)
            start_time_str = schedule.get("startTime", "00:00")
            end_time_str = schedule.get("endTime", "23:59")
            # timezone_str = schedule.get("timeZone", "US/Eastern")

            # Check if this day is scheduled
            if not (occurs_on & day_bit):
                continue

            # Parse start and end times
            try:
                start_hour = int(start_time_str.split(":")[0])
                end_hour = int(end_time_str.split(":")[0])
            except:
                continue

            # Handle schedules that span midnight
            if end_hour < start_hour:
                # Schedule spans midnight (e.g., 22:00 to 06:00)
                if point_hour >= start_hour or point_hour < end_hour:
                    return True
            else:
                # Normal schedule (e.g., 08:00 to 17:00)
                if start_hour <= point_hour < end_hour:
                    return True

        return False

    except Exception:
        return False


def rule_3_power_schedule_removal(org, resource_id, resource_type, template_info):
    """
    Rule 3: Remove Power Management Schedule for dedicated pools.
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})

        # Check all conditions
        # Condition 1: Check if this is a DEDICATED template
        if template.get("templateType") != "DEDICATED":
            return None

        power_policy = template.get("powerPolicy", {})
        power_schedules = power_policy.get("powerSchedules", [])

        # Condition 2: Check if power schedules are empty or disabled, if yes return None
        if not power_schedules:
            return None

        # Get utilization metrics
        usage_metrics = calculate_usage_metrics(template_info)
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        # Condition 3: Check if utilization is above than 50%, if yes return None
        if utilization >= config.UNDER_UTILIZATION_THRESHOLD:
            return None

        # Condition 4: Check if power schedule includes weekend days or schedule utilization is lower than overall utilization, if yes return recommendation
        has_weekend = has_weekend_schedule(power_schedules)
        schedule_utilization = calculate_schedule_resource_utilization(template_info, power_schedules)

        # Only recommend if weekend schedule exists OR schedule utilization is lower than overall
        if has_weekend or schedule_utilization < utilization:
            cost_savings = estimate_cost_savings_power_schedule_removal(template_info)

            # Build justification based on which condition triggered
            if has_weekend:
                justification = f"Resource Utilization ({utilization:.1f}%) < {config.UNDER_UTILIZATION_THRESHOLD}% and power schedule includes weekend days, potential cost savings: ${cost_savings}/month"
            else:
                justification = f"Resource Utilization ({utilization:.1f}%) < {config.UNDER_UTILIZATION_THRESHOLD}% and schedule utilization ({schedule_utilization:.1f}%) < overall utilization ({utilization:.1f}%), potential cost savings: ${cost_savings}/month"

            return {
                "action": "Remove Power Management Schedule",
                "justification": justification,
                "current_settings": {"powerPolicy": {"powerSchedules": power_schedules}},
                "recommended_settings": {"powerPolicy": {"powerSchedules": []}},
                "estimated_savings": f"${cost_savings}/month",
            }

    except Exception as e:
        print(f"Warning: Error in power schedule removal rule: {str(e)}")

    return None


def calculate_idle_vm_ratio(template_info: dict) -> float:
    """
    Calculate percentage of time points where idle VMs > utilized VMs.

    Args:
        template_info: Template information with usage data

    Returns:
        float: Percentage of time points where idle VMs > utilized VMs
    """
    try:
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms:
            return 0.0

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get data arrays after cutoff
        consumed_sessions = history.get("consumedSessions", [])
        powered_on_assigned = history.get("poweredOnAssignedVms", [])
        powered_on_unassigned = history.get("poweredOnUnassignedVms", [])

        if cutoff_index >= len(consumed_sessions) or cutoff_index >= len(powered_on_assigned) or cutoff_index >= len(powered_on_unassigned):
            return 0.0

        # Handle MULTI_SESSION templates
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        sessions_per_vm = 1
        if template_type == "MULTI_SESSION":
            sessions_per_vm = template.get("sessionsPerVm", 1)

        # Count time points where idle VMs > utilized VMs
        idle_greater_count = 0
        total_points = 0

        for i in range(cutoff_index, min(len(consumed_sessions), len(powered_on_assigned), len(powered_on_unassigned))):
            assigned_val = powered_on_assigned[i] if i < len(powered_on_assigned) else 0
            unassigned_val = powered_on_unassigned[i] if i < len(powered_on_unassigned) else 0
            powered_on_vms = assigned_val + unassigned_val

            utilized_capacity = consumed_sessions[i] if i < len(consumed_sessions) else 0

            # Convert sessions to VM-equivalent for MULTI_SESSION
            if template_type == "MULTI_SESSION" and sessions_per_vm > 0:
                utilized_capacity = utilized_capacity / sessions_per_vm

            idle_vms = powered_on_vms - utilized_capacity

            if idle_vms > utilized_capacity:
                idle_greater_count += 1
            total_points += 1

        if total_points == 0:
            return 0.0

        return (idle_greater_count / total_points) * 100.0

    except Exception as e:
        print(f"Warning: Error calculating idle VM ratio: {str(e)}")
        return 0.0


def calculate_utilized_to_powered_ratio(template_info: dict) -> float:
    """
    Calculate Utilized Capacity Hours ÷ Powered-on VM Hours.

    Args:
        template_info: Template information with usage data

    Returns:
        float: Ratio as percentage
    """
    try:
        # Get utilized capacity hours
        utilized_hours = calculate_filtered_hours(template_info, "utilized")

        # Get powered-on hours
        powered_on_hours = calculate_filtered_hours(template_info, "powered_on")

        if powered_on_hours <= 0:
            return 0.0

        ratio = (utilized_hours / powered_on_hours) * 100.0
        return max(0.0, ratio)

    except Exception as e:
        print(f"Warning: Error calculating utilized to powered ratio: {str(e)}")
        return 0.0


def calculate_gradient_based_min_reduction(utilization: float, current_min: float) -> float:
    """
    Apply gradient-based scaling formula for minimum VMs reduction.

    Args:
        utilization: Resource utilization percentage
        current_min: Current minimum setting

    Returns:
        int: New recommended minimum value
    """
    try:
        # Apply gradient formula: ScalingFactor = (50 - U) / 50
        scaling_factor = (50.0 - utilization) / 50.0
        scaling_factor = max(0.0, min(1.0, scaling_factor))  # Clamp between 0 and 1

        # NewMin = ceil(OriginalMin × (0.5 + 0.5 × (1 - ScalingFactor)))
        new_min = current_min * (0.5 + 0.5 * (1 - scaling_factor))

        # Apply minimum bound
        new_min = max(config.MIN_AVAILABLE_VMS_MIN_BOUND, new_min)

        return int(round(new_min))

    except Exception as e:
        print(f"Warning: Error calculating gradient-based min reduction: {str(e)}")
        return current_min


def rule_4_minimum_available_vms(org, resource_id, resource_type, template_info):
    """
    Rule 4: Adjust Minimum Available VMs based on usage patterns.
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})
        power_policy = template.get("powerPolicy", {})
        current_min = power_policy.get("min", 0.5)

        # Get utilization metrics
        usage_metrics = calculate_usage_metrics(template_info)
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        # Check all 5 conditions
        # Condition 1: Resource Utilization (%) < 50
        if utilization >= config.UNDER_UTILIZATION_THRESHOLD:
            return None

        # Condition 2: In over 90% of sampling time points: idle VMs > utilized VMs
        idle_vm_ratio = calculate_idle_vm_ratio(template_info)
        if idle_vm_ratio < config.IDLE_VM_THRESHOLD:
            return None

        # Condition 3: Utilized Capacity Hours ÷ Powered-on VM Hours < 50%
        utilized_to_powered_ratio = calculate_utilized_to_powered_ratio(template_info)
        if utilized_to_powered_ratio >= config.UTILIZED_TO_POWERED_RATIO_THRESHOLD:
            return None

        # Condition 4: template["powerPolicy"]["min"] > 50%
        if current_min <= config.MIN_AVAILABLE_VMS_THRESHOLD:
            return None

        # Condition 5: occupancyPresetMode.DISABLED
        occupancy_preset_mode = power_policy.get("occupancyPresetMode")
        if occupancy_preset_mode != "DISABLED":
            return None

        # Apply gradient-based scaling
        new_min = calculate_gradient_based_min_reduction(utilization, current_min)

        # Only recommend if new_min is less than current_min
        if new_min >= current_min:
            return None

        cost_savings = estimate_cost_savings_min_available_vms(current_min, new_min, template_info)

        return {
            "action": "Adjust Minimum Available VMs",
            "justification": (
                f"Resource Utilization ({utilization:.1f}%) < {config.UNDER_UTILIZATION_THRESHOLD}%, "
                f"idle VMs > utilized VMs in {idle_vm_ratio:.1f}% of time points, "
                f"utilized/powered ratio ({utilized_to_powered_ratio:.1f}%) < {config.UTILIZED_TO_POWERED_RATIO_THRESHOLD}%, "
                f"current min ({current_min}%) > {config.MIN_AVAILABLE_VMS_THRESHOLD}%, "
                f"occupancyPresetMode is DISABLED. Applied gradient reduction, potential cost savings: ${cost_savings}/month"
            ),
            "current_settings": {"powerPolicy": {"min": current_min}},
            "recommended_settings": {"powerPolicy": {"min": new_min}},
            "estimated_savings": f"${cost_savings}/month",
        }

    except Exception as e:
        print(f"Warning: Error in minimum available VMs rule: {str(e)}")

    return None


def rule_5_power_management_mode(org, resource_id, resource_type, template_info):
    """
    Rule 5: Adjust Occupancy-Based Scaling Mode for better cost efficiency.
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")
        power_policy = template.get("powerPolicy", {})
        current_mode = power_policy.get("occupancyPresetMode", "BALANCED")

        # Get utilization metrics
        usage_metrics = calculate_usage_metrics(template_info)
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        # Check all 4 conditions
        # Condition 1: Resource Utilization (%) < 50
        if utilization >= config.UNDER_UTILIZATION_THRESHOLD:
            return None

        # Condition 2: Only for FLOATING and MULTI_SESSION templates
        if template_type not in ["FLOATING", "MULTI_SESSION"]:
            return None

        # Condition 3: Check Current mode is OPTIMIZED_FOR_PERFORMANCE or BALANCED
        if current_mode == "OPTIMIZED_FOR_COST":
            return None

        # Condition 4: Check if current mode is too aggressive even for most agggressive OPTIMIZED_FOR_PERFORMANCE low utilization
        lowest_power_management_thresholds = config.OCCUPANCY_THRESHOLDS.get("OPTIMIZED_FOR_PERFORMANCE")
        if utilization < lowest_power_management_thresholds["low"]:
            # Recommend switching to more cost-efficient mode
            recommended_mode = "OPTIMIZED_FOR_COST"

            cost_savings = estimate_cost_savings_power_management_mode(template_info)

            return {
                "action": "Adjust Occupancy-Based Scaling Mode",
                "justification": f"Pool usage is low — occupancy thresholds too high for current load; more cost-efficient mode recommended, potential cost savings: ${cost_savings}/month",
                "current_settings": {"powerPolicy": {"occupancyBasedScalingMode": current_mode}},
                "recommended_settings": {"powerPolicy": {"occupancyBasedScalingMode": recommended_mode}},
                "estimated_savings": f"${cost_savings}/month",
            }

    except Exception as e:
        print(f"Warning: Error in power management mode rule: {str(e)}")

    return None


def is_all_at_once_provisioning(template_info: dict) -> bool:
    """
    Check if the pool is configured with "All at once" provisioning approach.

    Args:
        template_info: Template information

    Returns:
        bool: True if provisioning is "All at once" (limit == max == min)
    """
    try:
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})

        limit = spare_policy.get("limit", 0)
        max_vms = spare_policy.get("max", 0)
        min_vms = spare_policy.get("min", 0)

        # "All at once" if limit == max == min
        return limit > 0 and limit == max_vms and max_vms == min_vms
    except Exception:
        return False


def utilized_capacity_below_baseline_all_points(template_info: dict) -> bool:
    """
    Check if utilized capacity is below pool_min_baseline for ALL sampling points.

    Args:
        template_info: Template information

    Returns:
        bool: True if utilized capacity < pool_min_baseline for all sampling points
    """
    try:
        template = template_info.get("template", {})
        spare_policy = template.get("sparePolicy", {})
        power_policy = template.get("powerPolicy", {})

        # Calculate pool_min_baseline
        limit = spare_policy.get("limit", 0)
        min_ratio = power_policy.get("min", 0)
        pool_min_baseline = limit * min_ratio

        if pool_min_baseline <= 0:
            return False

        # Get historical data
        meta_data = template_info.get("meta", {})
        history = meta_data.get("history", {})
        start_timestamp = history.get("startTimestamp")
        timeslot_ms = meta_data.get("timeslotMs", 0)

        if not start_timestamp or not timeslot_ms:
            return False

        # Calculate cutoff index
        cutoff_index = calculate_cutoff_index(start_timestamp, timeslot_ms, config.CAPACITY_UTILIZATION_CUTOFF_DATE)

        # Get consumed sessions data after cutoff
        consumed_sessions = history.get("consumedSessions", [])

        if cutoff_index >= len(consumed_sessions):
            return False

        # Handle MULTI_SESSION templates
        template_type = template.get("templateType", "")
        sessions_per_vm = 1
        if template_type == "MULTI_SESSION":
            sessions_per_vm = template.get("sessionsPerVm", 1)

        # Check if ALL sampling points have utilized capacity < pool_min_baseline
        for i in range(cutoff_index, len(consumed_sessions)):
            utilized_capacity = consumed_sessions[i]

            # Convert sessions to VM-equivalent for MULTI_SESSION
            if template_type == "MULTI_SESSION" and sessions_per_vm > 1:
                utilized_capacity = utilized_capacity / sessions_per_vm

            # If any point has utilized capacity >= pool_min_baseline, return False
            if utilized_capacity >= pool_min_baseline:
                return False

        return True

    except Exception as e:
        print(f"Warning: Error checking utilized capacity below baseline: {str(e)}")
        return False


def estimate_cost_savings_provisioning_change(template_info: dict) -> float:
    """
    Estimate cost savings for switching from "All at once" to "On demand" provisioning.

    Savings = (Allocated_VM_Hours - Powered_On_VM_Hours) × disk_cost_per_hour

    Args:
        template_info: Template information

    Returns:
        float: Estimated monthly savings in USD
    """
    try:
        # Get VM type and disk cost
        # template = template_info.get("template", {})
        # infrastructure = template.get("infrastructure", {})
        # vm_sku = infrastructure.get("vmSku", "Standard_D4ads_v5")

        # Get disk cost per hour for the VM type
        disk_cost_per_hour = get_disk_cost_per_hour(template_info, "Premium_LRS")  # Default to Premium_LRS

        # Calculate allocated VM hours
        allocated_hours = calculate_filtered_hours(template_info, "allocated")

        # Calculate powered-on VM hours
        powered_on_hours = calculate_filtered_hours(template_info, "powered_on")

        # Calculate savings
        savings_hours = allocated_hours - powered_on_hours
        if savings_hours <= 0:
            return 0.0

        # Scale to monthly
        monthly_savings = calculate_actual_hours_per_month(savings_hours, template_info)

        # Calculate total savings
        total_savings = monthly_savings * disk_cost_per_hour

        return round(total_savings, 2)

    except Exception as e:
        print(f"Warning: Error estimating provisioning change savings: {str(e)}")
        return 0.0


def rule_6_reevaluate_provisioning_all_at_once(org, resource_id, resource_type, template_info):
    """
    Rule 6: Reevaluate Provisioning: All at once - Recommend switching to "On demand" provisioning.
    """
    if resource_type.lower() != "pool":
        return None

    # Check if usage data is available
    if not has_usage_data(template_info):
        return None

    try:
        template = template_info.get("template", {})
        template_type = template.get("templateType", "")

        # Condition 1: Check if provisioning approach is "All at once"
        if not is_all_at_once_provisioning(template_info):
            return None

        # Condition 2: Check template type (exclude DEDICATED)
        if template_type == "DEDICATED":
            return None

        # Condition 3: Check Resource Utilization < 50%
        usage_metrics = calculate_usage_metrics(template_info)
        utilization = 0.0
        for metric in usage_metrics:
            if metric[0] == "Capacity Utilization":
                try:
                    utilization = float(metric[1].replace("%", ""))
                except:
                    utilization = 0.0
                break

        if utilization >= config.UNDER_UTILIZATION_THRESHOLD:
            return None

        # Condition 4: Check if for ALL sampling points, utilized capacity < pool_min_baseline
        if not utilized_capacity_below_baseline_all_points(template_info):
            return None

        # Condition 5: Check Powered_On_VM_Hours / Allocated_VM_Hours < 50%
        allocated_hours = calculate_filtered_hours(template_info, "allocated")
        powered_on_hours = calculate_filtered_hours(template_info, "powered_on")

        if allocated_hours <= 0:
            return None  # Avoid division by zero

        powered_on_to_allocated_ratio = (powered_on_hours / allocated_hours) * 100.0
        if powered_on_to_allocated_ratio >= config.POWERED_ON_TO_ALLOCATED_RATIO_THRESHOLD:
            return None

        # Calculate cost savings
        cost_savings = estimate_cost_savings_provisioning_change(template_info)

        # Get current spare policy
        spare_policy = template.get("sparePolicy", {})
        current_limit = spare_policy.get("limit", 0)
        current_max = spare_policy.get("max", 0)
        current_min = spare_policy.get("min", 0)

        # Calculate new values
        new_max = int(current_limit * 0.5)
        new_min = int(current_limit * 0.5)

        return {
            "action": "Reevaluate Provisioning: All at once",
            "justification": (
                f"Pool is configured with 'All at once' provisioning but has low utilization ({utilization:.1f}%). "
                f"Utilized capacity is consistently below minimum baseline across all sampling points. "
                f"Powered-on to allocated ratio ({powered_on_to_allocated_ratio:.1f}%) is below {config.POWERED_ON_TO_ALLOCATED_RATIO_THRESHOLD}%. "
                f"Switching to 'On demand' provisioning can reduce resource waste and lower operational costs, "
                f"potential cost savings: ${cost_savings}/month"
            ),
            "current_settings": {"sparePolicy": {"limit": current_limit, "max": current_max, "min": current_min}},
            "recommended_settings": {"sparePolicy": {"limit": current_limit, "max": new_max, "min": new_min}},
            "estimated_savings": f"${cost_savings}/month",
        }

    except Exception as e:
        print(f"Warning: Error in reevaluate provisioning rule: {str(e)}")

    return None


def resolve_recommendation_conflicts(recommendations):
    """
    Resolve conflicts between recommendations and return the best ones.

    Conflict resolution rules:
    1. Rule 6 (reevaluate provisioning) takes precedence over Rule 1a (decrease maximum VMs)
    2. Future conflicts can be added here as needed

    Args:
        recommendations: List of recommendation dictionaries

    Returns:
        List of resolved recommendations
    """
    if not recommendations:
        return []

    # If only one recommendation, return it
    if len(recommendations) == 1:
        return recommendations

    # Check for specific conflicts
    rule_6_rec = None
    rule_1a_rec = None
    other_recs = []

    for rec in recommendations:
        action = rec.get("action", "")
        if "Reevaluate Provisioning: All at once" in action:
            rule_6_rec = rec
        elif "Adjust Maximum VMs" in action:
            # Check if this is a decrease recommendation (under-utilization)
            justification = rec.get("justification", "")
            if "low usage" in justification.lower() or "under" in justification.lower():
                rule_1a_rec = rec
            else:
                other_recs.append(rec)
        else:
            other_recs.append(rec)

    # Apply conflict resolution: Rule 6 takes precedence over Rule 1a
    if rule_6_rec and rule_1a_rec:
        # Rule 6 wins, exclude Rule 1a
        resolved_recs = [rule_6_rec] + other_recs
        return resolved_recs

    # No conflicts, return all recommendations
    return recommendations


def generate_recommendations(org, resource_id, resource_type, template_info):
    """
    Generate recommendations by applying all rule functions with conflict resolution.
    """
    # Define all rules
    rules = [
        rule_1a_decrease_maximum_vms,
        rule_1b_increase_maximum_vms,
        rule_2_auto_scale_disk_type,
        rule_3_power_schedule_removal,
        rule_4_minimum_available_vms,
        rule_5_power_management_mode,
        rule_6_reevaluate_provisioning_all_at_once,
    ]

    # Collect all recommendations
    all_recommendations = []
    for rule_func in rules:
        rec = rule_func(org, resource_id, resource_type, template_info)
        if rec:
            all_recommendations.append(rec)

    # Apply conflict resolution
    recommendations = resolve_recommendation_conflicts(all_recommendations)

    if not recommendations:
        recommendations = [
            {
                "action": "No recommendations available.",
                "justification": "",
                "current_settings": {},
                "recommended_settings": {},
                "estimated_savings": "N/A",
            }
        ]
    return {"recommendations": recommendations}
