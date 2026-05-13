"""
Fault Scenarios for Satellite Telemetry Simulation
"""

from typing import Dict
import random

class ScenarioBase:
    """Base class for fault scenarios"""
    
    def __init__(self, name: str):
        self.name = name
        self.active = False
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply scenario modifications to telemetry"""
        return telemetry
    
    def start(self):
        """Start scenario"""
        self.active = True
    
    def stop(self):
        """Stop scenario"""
        self.active = False

class NormalScenario(ScenarioBase):
    """Normal operation - no faults"""
    
    def __init__(self):
        super().__init__("Normal Operation")
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """No modifications in normal scenario"""
        return telemetry

class BatteryDrainScenario(ScenarioBase):
    """Simulates gradual battery drain"""
    
    def __init__(self):
        super().__init__("Battery Drain")
        self.time_step = 0
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply battery drain"""
        if not self.active:
            return telemetry
        
        self.time_step += 1
        
        # Gradual voltage decrease
        drain_rate = 0.5 / 60  # Drain 0.5V per minute
        voltage_drop = drain_rate * self.time_step
        
        telemetry["battery_voltage"] = max(15.0, telemetry.get("battery_voltage", 28.0) - voltage_drop)
        
        # Increased current draw
        telemetry["battery_current"] = min(50.0, telemetry.get("battery_current", 10.0) + voltage_drop * 5)
        
        # Increased power consumption
        telemetry["power_consumption"] = min(100.0, telemetry.get("power_consumption", 50.0) + voltage_drop * 3)
        
        return telemetry

class ThermalOverloadScenario(ScenarioBase):
    """Simulates thermal system overload"""
    
    def __init__(self):
        super().__init__("Thermal Overload")
        self.time_step = 0
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply thermal overload"""
        if not self.active:
            return telemetry
        
        self.time_step += 1
        
        # Rapid temperature increase
        temp_increase = 1.0 * self.time_step  # +1°C per step
        
        telemetry["internal_temp"] = min(95.0, telemetry.get("internal_temp", 25.0) + temp_increase)
        telemetry["subsystem_temp"] = min(80.0, telemetry.get("subsystem_temp", 20.0) + temp_increase * 0.8)
        
        # Increased thermal load
        telemetry["thermal_load"] = min(100.0, telemetry.get("thermal_load", 40.0) + temp_increase * 0.5)
        
        return telemetry

class SolarPanelFailureScenario(ScenarioBase):
    """Simulates solar panel degradation"""
    
    def __init__(self):
        super().__init__("Solar Panel Failure")
        self.time_step = 0
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply solar panel failure"""
        if not self.active:
            return telemetry
        
        self.time_step += 1
        
        # Gradual solar output decrease
        failure_rate = 2.0 / 30  # 90% output loss over 30 steps
        solar_degradation = failure_rate * self.time_step
        
        telemetry["solar_output"] = max(5.0, telemetry.get("solar_output", 100.0) * (1.0 - solar_degradation))
        
        # Battery voltage decreases due to lack of charge
        telemetry["battery_voltage"] = max(18.0, telemetry.get("battery_voltage", 28.0) - solar_degradation * 3)
        
        # Battery current increases as system compensates
        telemetry["battery_current"] = min(50.0, telemetry.get("battery_current", 10.0) + solar_degradation * 8)
        
        return telemetry

class CommunicationFailureScenario(ScenarioBase):
    """Simulates communication system degradation"""
    
    def __init__(self):
        super().__init__("Communication Failure")
        self.time_step = 0
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply communication failure"""
        if not self.active:
            return telemetry
        
        self.time_step += 1
        
        # Signal strength degradation
        signal_degrade = 0.5 * self.time_step  # 0.5 dBm per step
        telemetry["signal_strength"] = max(-110.0, telemetry.get("signal_strength", -60.0) - signal_degrade)
        
        # Transmission quality loss
        quality_loss = 2.0 * self.time_step  # 2% per step
        telemetry["transmission_quality"] = max(10.0, telemetry.get("transmission_quality", 90.0) - quality_loss)
        
        # Antenna misalignment
        telemetry["antenna_alignment"] = (telemetry.get("antenna_alignment", 180.0) + random.uniform(-30, 30)) % 360
        
        return telemetry

class AttitudeDriftScenario(ScenarioBase):
    """Simulates AOCS failure causing attitude drift"""
    
    def __init__(self):
        super().__init__("Attitude Drift")
        self.time_step = 0
    
    def apply(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply attitude drift"""
        if not self.active:
            return telemetry
        
        self.time_step += 1
        
        # Gyro drift increases
        drift_accumulation = 0.03 * self.time_step  # Increasing drift
        telemetry["gyro_drift"] = max(-1.0, min(1.0, telemetry.get("gyro_drift", 0.0) + drift_accumulation * 0.1))
        
        # Orientation deviation increases
        telemetry["orientation_deviation"] = min(30.0, telemetry.get("orientation_deviation", 5.0) + 0.5 * self.time_step)
        
        # Actuator status degrades
        telemetry["actuator_status"] = max(20.0, telemetry.get("actuator_status", 100.0) - 1.5 * self.time_step)
        
        return telemetry

class ScenarioManager:
    """Manage fault scenarios"""
    
    def __init__(self):
        self.scenarios = {
            "normal": NormalScenario(),
            "battery_drain": BatteryDrainScenario(),
            "thermal_overload": ThermalOverloadScenario(),
            "solar_failure": SolarPanelFailureScenario(),
            "comm_failure": CommunicationFailureScenario(),
            "attitude_drift": AttitudeDriftScenario(),
        }
        self.active_scenario = self.scenarios["normal"]
    
    def set_scenario(self, scenario_name: str) -> bool:
        """Set active scenario"""
        if scenario_name not in self.scenarios:
            return False
        
        # Stop current scenario
        self.active_scenario.stop()
        self.active_scenario.time_step = 0
        
        # Start new scenario
        self.active_scenario = self.scenarios[scenario_name]
        self.active_scenario.start()
        self.active_scenario.time_step = 0
        
        return True
    
    def apply_scenario(self, telemetry: Dict[str, float]) -> Dict[str, float]:
        """Apply active scenario to telemetry"""
        return self.active_scenario.apply(telemetry)
    
    def get_active_scenario(self) -> str:
        """Get name of active scenario"""
        return self.active_scenario.name
    
    def get_scenarios_list(self) -> list:
        """Get list of available scenarios"""
        return list(self.scenarios.keys())
