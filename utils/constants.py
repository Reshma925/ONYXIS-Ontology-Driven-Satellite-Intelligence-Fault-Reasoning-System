"""
Constants for Satellite Monitoring System
"""

# Ontology Configuration
ONTOLOGY_PATH = "ontology/satellite_full.owl"
ONTOLOGY_NAMESPACE = "http://example.org/satellite#"

# Telemetry Ranges (Normal Operations)
TELEMETRY_RANGES = {
    # Power System (Volts, Amps, Watts)
    "battery_voltage": {"min": 20.0, "max": 32.0, "nominal": 28.0},
    "battery_current": {"min": 0.0, "max": 50.0, "nominal": 10.0},
    "solar_output": {"min": 5.0, "max": 150.0, "nominal": 100.0},
    "power_consumption": {"min": 5.0, "max": 100.0, "nominal": 50.0},
    
    # Thermal System (Celsius)
    "internal_temp": {"min": -20.0, "max": 80.0, "nominal": 25.0},
    "subsystem_temp": {"min": -10.0, "max": 60.0, "nominal": 20.0},
    "thermal_load": {"min": 0.0, "max": 100.0, "nominal": 40.0},
    
    # Communication System (dBm, Degrees)
    "signal_strength": {"min": -100.0, "max": -30.0, "nominal": -60.0},
    "antenna_alignment": {"min": 0.0, "max": 360.0, "nominal": 180.0},
    "transmission_quality": {"min": 0.0, "max": 100.0, "nominal": 90.0},
    
    # AOCS (Degrees, deg/s)
    "gyro_drift": {"min": -1.0, "max": 1.0, "nominal": 0.0},
    "orientation_deviation": {"min": 0.0, "max": 30.0, "nominal": 5.0},
    "actuator_status": {"min": 0.0, "max": 100.0, "nominal": 100.0},
}

# Fault Thresholds
FAULT_THRESHOLDS = {
    "battery_voltage_low": 22.0,
    "battery_voltage_critical": 20.0,
    "internal_temp_high": 70.0,
    "internal_temp_critical": 80.0,
    "signal_strength_low": -85.0,
    "signal_strength_critical": -95.0,
    "actuator_status_low": 50.0,
    "thermal_load_high": 80.0,
}

# Scenarios
SCENARIOS = {
    "normal": "Normal Operation",
    "battery_drain": "Battery Drain",
    "thermal_overload": "Thermal Overload",
    "solar_failure": "Solar Panel Failure",
    "comm_failure": "Communication Failure",
    "attitude_drift": "Attitude Drift",
}

# UI Colors
COLORS = {
    "healthy": "#00FF00",
    "warning": "#FFAA00",
    "critical": "#FF0000",
    "background": "#0a0e27",
    "card_bg": "#1a1f3a",
    "text_primary": "#ffffff",
}

# Subsystems
SUBSYSTEMS = {
    "power": "Power System",
    "thermal": "Thermal System",
    "communication": "Communication System",
    "aocs": "AOCS (Attitude & Orbit Control)",
    "payload": "Payload",
}

# Update intervals
TELEMETRY_UPDATE_INTERVAL = 1  # seconds
REASONING_UPDATE_INTERVAL = 2  # seconds
