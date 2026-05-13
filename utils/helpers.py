"""
Helper functions for Satellite Monitoring System
"""

from typing import Dict, Tuple
from utils.constants import COLORS, TELEMETRY_RANGES, FAULT_THRESHOLDS

def get_health_status(value: float, telemetry_key: str) -> Tuple[str, str]:
    """
    Determine health status based on telemetry value
    Returns: (status_string, color)
    """
    if telemetry_key not in TELEMETRY_RANGES:
        return "UNKNOWN", "#888888"
    
    ranges = TELEMETRY_RANGES[telemetry_key]
    
    # Check critical thresholds
    if telemetry_key == "battery_voltage":
        if value <= FAULT_THRESHOLDS.get("battery_voltage_critical", 20.0):
            return "CRITICAL", COLORS["critical"]
        if value <= FAULT_THRESHOLDS.get("battery_voltage_low", 22.0):
            return "WARNING", COLORS["warning"]
    
    elif telemetry_key == "internal_temp":
        if value >= FAULT_THRESHOLDS.get("internal_temp_critical", 80.0):
            return "CRITICAL", COLORS["critical"]
        if value >= FAULT_THRESHOLDS.get("internal_temp_high", 70.0):
            return "WARNING", COLORS["warning"]
    
    elif telemetry_key == "signal_strength":
        if value <= FAULT_THRESHOLDS.get("signal_strength_critical", -95.0):
            return "CRITICAL", COLORS["critical"]
        if value <= FAULT_THRESHOLDS.get("signal_strength_low", -85.0):
            return "WARNING", COLORS["warning"]
    
    elif telemetry_key == "thermal_load":
        if value >= FAULT_THRESHOLDS.get("thermal_load_high", 80.0):
            return "WARNING", COLORS["warning"]
    
    return "HEALTHY", COLORS["healthy"]

def format_telemetry_value(value: float, key: str) -> str:
    """Format telemetry value with appropriate units"""
    units = {
        "battery_voltage": "V",
        "battery_current": "A",
        "solar_output": "W",
        "power_consumption": "W",
        "internal_temp": "°C",
        "subsystem_temp": "°C",
        "thermal_load": "%",
        "signal_strength": "dBm",
        "antenna_alignment": "°",
        "transmission_quality": "%",
        "gyro_drift": "deg/s",
        "orientation_deviation": "°",
        "actuator_status": "%",
    }
    
    unit = units.get(key, "")
    return f"{value:.2f} {unit}".strip()

def normalize_value(value: float, key: str) -> float:
    """Normalize value to 0-100 scale for visualization"""
    if key not in TELEMETRY_RANGES:
        return 0.0
    
    ranges = TELEMETRY_RANGES[key]
    min_val = ranges["min"]
    max_val = ranges["max"]
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0.0, min(100.0, normalized))

def get_subsystem_health(telemetry: Dict[str, float]) -> Dict[str, Tuple[str, float]]:
    """
    Calculate health for each subsystem
    Returns: {subsystem: (status, percentage)}
    """
    health = {}
    
    # Power System
    power_values = [
        normalize_value(telemetry.get("battery_voltage", 28.0), "battery_voltage"),
        normalize_value(telemetry.get("solar_output", 100.0), "solar_output"),
        normalize_value(telemetry.get("power_consumption", 50.0), "power_consumption"),
    ]
    power_health = sum(power_values) / len(power_values) if power_values else 100.0
    power_status = "HEALTHY" if power_health > 80 else "WARNING" if power_health > 50 else "CRITICAL"
    health["power"] = (power_status, power_health)
    
    # Thermal System
    thermal_values = [
        normalize_value(telemetry.get("internal_temp", 25.0), "internal_temp"),
        normalize_value(telemetry.get("subsystem_temp", 20.0), "subsystem_temp"),
        100.0 - normalize_value(telemetry.get("thermal_load", 40.0), "thermal_load"),
    ]
    thermal_health = sum(thermal_values) / len(thermal_values) if thermal_values else 100.0
    thermal_status = "HEALTHY" if thermal_health > 80 else "WARNING" if thermal_health > 50 else "CRITICAL"
    health["thermal"] = (thermal_status, thermal_health)
    
    # Communication System
    comm_values = [
        normalize_value(telemetry.get("signal_strength", -60.0), "signal_strength"),
        normalize_value(telemetry.get("transmission_quality", 90.0), "transmission_quality"),
    ]
    comm_health = sum(comm_values) / len(comm_values) if comm_values else 100.0
    comm_status = "HEALTHY" if comm_health > 80 else "WARNING" if comm_health > 50 else "CRITICAL"
    health["communication"] = (comm_status, comm_health)
    
    # AOCS
    aocs_values = [
        100.0 - normalize_value(telemetry.get("gyro_drift", 0.0), "gyro_drift"),
        100.0 - normalize_value(telemetry.get("orientation_deviation", 5.0), "orientation_deviation"),
        normalize_value(telemetry.get("actuator_status", 100.0), "actuator_status"),
    ]
    aocs_health = sum(aocs_values) / len(aocs_values) if aocs_values else 100.0
    aocs_status = "HEALTHY" if aocs_health > 80 else "WARNING" if aocs_health > 50 else "CRITICAL"
    health["aocs"] = (aocs_status, aocs_health)
    
    # Payload (assume healthy for now)
    health["payload"] = ("HEALTHY", 100.0)
    
    return health

def format_timestamp(dt) -> str:
    """Format datetime to HH:MM:SS"""
    return dt.strftime("%H:%M:%S") if hasattr(dt, 'strftime') else str(dt)
