"""
Sensor Models for realistic telemetry generation
"""

import random
import math
from typing import Dict
from utils.constants import TELEMETRY_RANGES

class SensorModel:
    """Base sensor model with noise and drift"""
    
    def __init__(self, nominal_value: float, min_value: float, max_value: float, noise_level: float = 0.02):
        self.nominal_value = nominal_value
        self.min_value = min_value
        self.max_value = max_value
        self.noise_level = noise_level
        self.current_value = nominal_value
        self.drift = 0.0
    
    def read(self) -> float:
        """Read sensor value with noise and drift"""
        # Add random noise
        noise = random.gauss(0, (self.max_value - self.min_value) * self.noise_level)
        
        # Add drift component
        self.drift += random.gauss(0, 0.01)
        self.drift = max(-0.5, min(0.5, self.drift))  # Bound drift
        
        # Generate value
        value = self.nominal_value + self.drift + noise
        
        # Clamp to range
        self.current_value = max(self.min_value, min(self.max_value, value))
        
        return self.current_value
    
    def set_nominal(self, value: float):
        """Change nominal operating point"""
        self.nominal_value = max(self.min_value, min(self.max_value, value))

class PowerSensors:
    """Power system sensors"""
    
    def __init__(self):
        ranges = TELEMETRY_RANGES
        
        self.battery_voltage = SensorModel(
            ranges["battery_voltage"]["nominal"],
            ranges["battery_voltage"]["min"],
            ranges["battery_voltage"]["max"],
            noise_level=0.01
        )
        
        self.battery_current = SensorModel(
            ranges["battery_current"]["nominal"],
            ranges["battery_current"]["min"],
            ranges["battery_current"]["max"],
            noise_level=0.03
        )
        
        self.solar_output = SensorModel(
            ranges["solar_output"]["nominal"],
            ranges["solar_output"]["min"],
            ranges["solar_output"]["max"],
            noise_level=0.05
        )
        
        self.power_consumption = SensorModel(
            ranges["power_consumption"]["nominal"],
            ranges["power_consumption"]["min"],
            ranges["power_consumption"]["max"],
            noise_level=0.02
        )
    
    def read_all(self) -> Dict[str, float]:
        """Read all power sensors"""
        return {
            "battery_voltage": self.battery_voltage.read(),
            "battery_current": self.battery_current.read(),
            "solar_output": self.solar_output.read(),
            "power_consumption": self.power_consumption.read(),
        }

class ThermalSensors:
    """Thermal system sensors"""
    
    def __init__(self):
        ranges = TELEMETRY_RANGES
        
        self.internal_temp = SensorModel(
            ranges["internal_temp"]["nominal"],
            ranges["internal_temp"]["min"],
            ranges["internal_temp"]["max"],
            noise_level=0.01
        )
        
        self.subsystem_temp = SensorModel(
            ranges["subsystem_temp"]["nominal"],
            ranges["subsystem_temp"]["min"],
            ranges["subsystem_temp"]["max"],
            noise_level=0.01
        )
        
        self.thermal_load = SensorModel(
            ranges["thermal_load"]["nominal"],
            ranges["thermal_load"]["min"],
            ranges["thermal_load"]["max"],
            noise_level=0.02
        )
    
    def read_all(self) -> Dict[str, float]:
        """Read all thermal sensors"""
        return {
            "internal_temp": self.internal_temp.read(),
            "subsystem_temp": self.subsystem_temp.read(),
            "thermal_load": self.thermal_load.read(),
        }

class CommunicationSensors:
    """Communication system sensors"""
    
    def __init__(self):
        ranges = TELEMETRY_RANGES
        
        self.signal_strength = SensorModel(
            ranges["signal_strength"]["nominal"],
            ranges["signal_strength"]["min"],
            ranges["signal_strength"]["max"],
            noise_level=0.03
        )
        
        self.antenna_alignment = SensorModel(
            ranges["antenna_alignment"]["nominal"],
            ranges["antenna_alignment"]["min"],
            ranges["antenna_alignment"]["max"],
            noise_level=0.02
        )
        
        self.transmission_quality = SensorModel(
            ranges["transmission_quality"]["nominal"],
            ranges["transmission_quality"]["min"],
            ranges["transmission_quality"]["max"],
            noise_level=0.02
        )
    
    def read_all(self) -> Dict[str, float]:
        """Read all communication sensors"""
        return {
            "signal_strength": self.signal_strength.read(),
            "antenna_alignment": self.antenna_alignment.read(),
            "transmission_quality": self.transmission_quality.read(),
        }

class AOCSSensors:
    """Attitude and Orbit Control System sensors"""
    
    def __init__(self):
        ranges = TELEMETRY_RANGES
        
        self.gyro_drift = SensorModel(
            ranges["gyro_drift"]["nominal"],
            ranges["gyro_drift"]["min"],
            ranges["gyro_drift"]["max"],
            noise_level=0.05
        )
        
        self.orientation_deviation = SensorModel(
            ranges["orientation_deviation"]["nominal"],
            ranges["orientation_deviation"]["min"],
            ranges["orientation_deviation"]["max"],
            noise_level=0.02
        )
        
        self.actuator_status = SensorModel(
            ranges["actuator_status"]["nominal"],
            ranges["actuator_status"]["min"],
            ranges["actuator_status"]["max"],
            noise_level=0.01
        )
    
    def read_all(self) -> Dict[str, float]:
        """Read all AOCS sensors"""
        return {
            "gyro_drift": self.gyro_drift.read(),
            "orientation_deviation": self.orientation_deviation.read(),
            "actuator_status": self.actuator_status.read(),
        }

class SensorSuite:
    """Complete sensor suite for satellite"""
    
    def __init__(self):
        self.power = PowerSensors()
        self.thermal = ThermalSensors()
        self.communication = CommunicationSensors()
        self.aocs = AOCSSensors()
    
    def read_all(self) -> Dict[str, float]:
        """Read all sensors"""
        telemetry = {}
        telemetry.update(self.power.read_all())
        telemetry.update(self.thermal.read_all())
        telemetry.update(self.communication.read_all())
        telemetry.update(self.aocs.read_all())
        return telemetry
