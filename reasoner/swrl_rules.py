"""
SWRL Rules for Satellite Fault Detection
(Semantic Web Rule Language - represented in Python for runtime execution)
"""

# Note: These rules are implemented in the ReasoningEngine
# This file documents the semantic logic in SWRL-like syntax for reference

SWRL_RULES = """

// Rule 1: Battery Low Voltage Detection
Satellite(?s) ∧ hasBatteryVoltage(?s, ?v) ∧ lessThan(?v, 22.0) → BatteryFault(?s)

// Rule 2: Battery Critical Voltage
Satellite(?s) ∧ hasBatteryVoltage(?s, ?v) ∧ lessThan(?v, 20.0) → BatteryCritical(?s)

// Rule 3: Thermal Overload Detection  
Satellite(?s) ∧ hasInternalTemperature(?s, ?t) ∧ greaterThan(?t, 70.0) → ThermalFault(?s)

// Rule 4: Thermal Critical
Satellite(?s) ∧ hasInternalTemperature(?s, ?t) ∧ greaterThan(?t, 80.0) → ThermalCritical(?s)

// Rule 5: Thermal Load High
Satellite(?s) ∧ hasThermalLoad(?s, ?load) ∧ greaterThan(?load, 80.0) → ThermalLoadHigh(?s)

// Rule 6: Communication Degradation
Satellite(?s) ∧ hasSignalStrength(?s, ?sig) ∧ lessThan(?sig, -85.0) → CommunicationFault(?s)

// Rule 7: Communication Critical
Satellite(?s) ∧ hasSignalStrength(?s, ?sig) ∧ lessThan(?sig, -95.0) → CommunicationCritical(?s)

// Rule 8: Transmission Quality Loss
Satellite(?s) ∧ hasTransmissionQuality(?s, ?tq) ∧ lessThan(?tq, 50.0) → TransmissionFailure(?s)

// Rule 9: Gyro Drift Detection
Satellite(?s) ∧ hasGyroDrift(?s, ?drift) ∧ greaterThan(abs(?drift), 0.8) → GyroDriftFailure(?s)

// Rule 10: Attitude Deviation
Satellite(?s) ∧ hasOrientationDeviation(?s, ?dev) ∧ greaterThan(?dev, 15.0) → AttitudeDrift(?s)

// Rule 11: Critical Attitude Deviation
Satellite(?s) ∧ hasOrientationDeviation(?s, ?dev) ∧ greaterThan(?dev, 25.0) → AttitudeDriftCritical(?s)

// Rule 12: Actuator Failure
Satellite(?s) ∧ hasActuatorStatus(?s, ?status) ∧ lessThan(?status, 50.0) → ActuatorFailure(?s)

// Rule 13: Solar Panel Failure
Satellite(?s) ∧ hasSolarOutput(?s, ?solar) ∧ lessThan(?solar, 20.0) → SolarPanelFailure(?s)

// Rule 14: Power Subsystem Failure (Composite)
Satellite(?s) ∧ hasBatteryVoltage(?s, ?v) ∧ lessThan(?v, 25.0) ∧ 
hasPowerConsumption(?s, ?pc) ∧ greaterThan(?pc, 70.0) → PowerSubsystemFailure(?s)

// Rule 15: Antenna Misalignment
Satellite(?s) ∧ hasAntennaAlignment(?s, ?align) ∧ greaterThan(abs(sub(?align, 180)), 45.0) ∧
hasSignalStrength(?s, ?sig) ∧ lessThan(?sig, -70.0) → AntennaAlignment(?s)

// Rule 16: Subsystem Operational Status
Satellite(?s) ∧ hasTemperature(?s, ?temp) ∧ hasVoltage(?s, ?volt) ∧
greaterThan(?temp, 50.0) ∧ lessThan(?volt, 22.0) → SubsystemDegraded(?s)

"""

def get_rule_documentation() -> dict:
    """Get documentation of all inference rules"""
    return {
        "battery_rules": [
            "BatteryFault: Triggered when battery voltage < 22V",
            "BatteryCritical: Triggered when battery voltage < 20V",
        ],
        "thermal_rules": [
            "ThermalFault: Triggered when internal temperature > 70°C",
            "ThermalCritical: Triggered when internal temperature > 80°C",
            "ThermalLoadHigh: Triggered when thermal load > 80%",
        ],
        "communication_rules": [
            "CommunicationFault: Triggered when signal strength < -85 dBm",
            "CommunicationCritical: Triggered when signal strength < -95 dBm",
            "TransmissionFailure: Triggered when transmission quality < 50%",
        ],
        "aocs_rules": [
            "GyroDriftFailure: Triggered when gyro drift exceeds ±0.8 deg/s",
            "AttitudeDrift: Triggered when orientation deviation > 15°",
            "AttitudeDriftCritical: Triggered when orientation deviation > 25°",
            "ActuatorFailure: Triggered when actuator status < 50%",
        ],
        "power_rules": [
            "SolarPanelFailure: Triggered when solar output < 20W",
            "PowerSubsystemFailure: Triggered when battery < 25V AND consumption > 70W",
        ],
        "antenna_rules": [
            "AntennaAlignment: Triggered when antenna misaligned by >45° AND signal < -70 dBm",
        ],
    }
