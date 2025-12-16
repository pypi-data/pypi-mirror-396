"""
Copyright © 2025 Omnissa, LLC.
"""

"""
Configuration file for HCS Advisor recommendations.
Contains thresholds, constants, and Azure cost data for recommendation calculations.
"""

# Observation and Timing Configuration
MINIMUM_OBSERVATION_DAYS = 2  # Minimum observation period in days
CAPACITY_UTILIZATION_CUTOFF_DATE = "2025-08-04 14:30:00"

# Data Quality Configuration
USE_MINIMUM_DATA_REQUIREMENT = False  # Set to True in production for 14 days minimum
MINIMUM_OBSERVATION_DAYS_PRODUCTION = 14  # Minimum days required in production

# Utilization Thresholds
UNDER_UTILIZATION_THRESHOLD = 50.0  # Percentage
OVER_UTILIZATION_THRESHOLD = 95.0  # Percentage

# Increase Recommendation Thresholds
# Gate on Utilized Capacity Hours / Total Pool Hours (percentage)
UTILIZED_TO_POOL_RATIO_THRESHOLD = 95.0
# Maximum gradient increase allowed (e.g., 0.2 means up to +20%)
MAX_INCREASE_ADJUSTMENT_FACTOR = 0.2

# Pool Size Limits
MIN_POOL_SIZE_FOR_RECOMMENDATIONS = (
    5  # minimum pool size for recommendations,  It doesn’t make sense to make a recommendation for too small pool.
)
MIN_POOL_SIZE_FOR_AUTO_SCALE_DISK_TYPE = 100

# Powered-off Ratio Threshold
POWERED_OFF_RATIO_THRESHOLD = 0.30  # 30%

# Gradient-based Decrease Configuration
MIN_UTILIZATION_THRESHOLD = 1.0  # 1% baseline
MAX_UTILIZATION_THRESHOLD = 50.0  # 50% upper bound
MAX_REDUCTION_FACTOR = 0.5  # At most 50% of new Max VMs

# Occupancy-based Power Management Thresholds
OCCUPANCY_THRESHOLDS = {
    "OPTIMIZED_FOR_PERFORMANCE": {"low": 23.0, "high": 50.0, "range": 27.0},
    "BALANCED": {"low": 31.0, "high": 66.0, "range": 35.0},
    "OPTIMIZED_FOR_COST": {"low": 38.0, "high": 80.0, "range": 42.0},
}

# Azure VM SKU Costs (per hour in USD)
# Source: Azure Pricing Calculator (prices may vary by region)
AZURE_VM_COSTS = {
    "Standard_D4ads_v5": 0.201,
    "Standard_D8ads_v5": 0.402,
    "Standard_D16ads_v5": 0.804,
    "Standard_D32ads_v5": 1.608,
    "Standard_D4s_v3": 0.192,
    "Standard_D8s_v3": 0.384,
    "Standard_D16s_v3": 0.768,
    "Standard_D32s_v3": 1.536,
    "Standard_D4s_v4": 0.192,
    "Standard_D8s_v4": 0.384,
    "Standard_D16s_v4": 0.768,
    "Standard_D32s_v4": 1.536,
    "Standard_D4s_v5": 0.192,
    "Standard_D8s_v5": 0.384,
    "Standard_D16s_v5": 0.768,
    "Standard_D32s_v5": 1.536,
    "Standard_E4s_v3": 0.252,
    "Standard_E8s_v3": 0.504,
    "Standard_E16s_v3": 1.008,
    "Standard_E32s_v3": 2.016,
    "Standard_E4s_v4": 0.252,
    "Standard_E8s_v4": 0.504,
    "Standard_E16s_v4": 1.008,
    "Standard_E32s_v4": 2.016,
    "Standard_E4s_v5": 0.252,
    "Standard_E8s_v5": 0.504,
    "Standard_E16s_v5": 1.008,
    "Standard_E32s_v5": 2.016,
    # Default cost for unknown SKUs
    "DEFAULT": 0.201,
}

# Azure Disk Costs (per hour in USD for 128GB disk)
# Source: Azure Pricing Calculator (prices may vary by region)
AZURE_DISK_COSTS = {
    "Premium_LRS": 0.14,  # Premium SSD
    "Standard_LRS": 0.03,  # Standard HDD
    "StandardSSD_LRS": 0.08,  # Standard SSD
    "UltraSSD_LRS": 0.25,  # Ultra SSD
    # Default cost for unknown disk types
    "DEFAULT": 0.14,
}

# Hours per month for cost calculations
HOURS_PER_MONTH = 24 * 30  # 30 days per month

# Assumed reduction factor for power management mode savings
POWER_MANAGEMENT_REDUCTION_FACTOR = 0.2  # 20% reduction

# Minimum Available VMs Rule Thresholds
IDLE_VM_THRESHOLD = 90.0  # Percentage of sampling time points where idle VMs > utilized VMs
UTILIZED_TO_POWERED_RATIO_THRESHOLD = 50.0  # Threshold for Utilized Capacity Hours ÷ Powered-on VM Hours
MIN_AVAILABLE_VMS_THRESHOLD = 50.0  # Threshold for current min setting
MIN_AVAILABLE_VMS_MIN_BOUND = 5.0  # Minimum bound for new min value (5%)

# Rule 6 Reevaluate Provisioning Thresholds
POWERED_ON_TO_ALLOCATED_RATIO_THRESHOLD = 50.0  # Threshold for Powered-on VM Hours ÷ Allocated VM Hours
