"""
Reasoning Engine for Semantic Fault Inference
"""

from typing import List, Dict
from utils.logger import get_logger
from reasoner.ontology_loader import get_ontology_loader
from reasoner.ontology_updater import get_ontology_updater
from utils.constants import FAULT_THRESHOLDS

logger = get_logger()

class ReasoningEngine:
    """Execute semantic reasoning to infer faults"""
    
    def __init__(self):
        self.loader = get_ontology_loader()
        self.updater = get_ontology_updater()
        self.current_faults = set()
    
    def infer_faults(self, telemetry: Dict[str, float], satellite_name: str = "Satellite1") -> List[str]:
        """
        Infer faults based on telemetry values and ontology reasoning
        
        Returns:
            List of inferred fault class names
        """
        if not self.loader.is_loaded:
            logger.warning("Ontology not loaded, cannot perform reasoning", "ReasoningEngine")
            return []
        
        inferred_faults = []
        
        try:
            # Perform semantic reasoning based on telemetry thresholds
            new_faults = self._apply_semantic_rules(telemetry)
            
            # Log new faults
            for fault in new_faults:
                if fault not in self.current_faults:
                    logger.fault(f"New fault detected: {fault}", "ReasoningEngine")
                    self.current_faults.add(fault)
                inferred_faults.append(fault)
            
            # Check for resolved faults
            resolved_faults = self.current_faults - set(new_faults)
            for fault in resolved_faults:
                logger.info(f"Fault resolved: {fault}", "ReasoningEngine")
                self.current_faults.remove(fault)
            
            # Update current faults
            self.current_faults = set(new_faults)
            
            return inferred_faults
        
        except Exception as e:
            logger.error(f"Error during fault inference: {str(e)}", "ReasoningEngine")
            return []
    
    def _apply_semantic_rules(self, telemetry: Dict[str, float]) -> List[str]:
        """
        Apply semantic reasoning rules to infer faults
        These rules mirror SWRL-like logic in Python
        """
        faults = []
        
        try:
            # Rule 1: Battery Fault Detection
            battery_voltage = telemetry.get("battery_voltage", 28.0)
            if battery_voltage <= FAULT_THRESHOLDS.get("battery_voltage_critical", 20.0):
                faults.append("BatteryCritical")
            elif battery_voltage <= FAULT_THRESHOLDS.get("battery_voltage_low", 22.0):
                faults.append("BatteryFault")
            
            # Rule 2: Thermal Overload Detection
            internal_temp = telemetry.get("internal_temp", 25.0)
            subsystem_temp = telemetry.get("subsystem_temp", 20.0)
            thermal_load = telemetry.get("thermal_load", 40.0)
            
            if internal_temp >= FAULT_THRESHOLDS.get("internal_temp_critical", 80.0):
                faults.append("ThermalCritical")
            elif internal_temp >= FAULT_THRESHOLDS.get("internal_temp_high", 70.0):
                faults.append("ThermalFault")
            
            if thermal_load >= FAULT_THRESHOLDS.get("thermal_load_high", 80.0):
                faults.append("ThermalLoadHigh")
            
            # Rule 3: Communication Failure Detection
            signal_strength = telemetry.get("signal_strength", -60.0)
            transmission_quality = telemetry.get("transmission_quality", 90.0)
            
            if signal_strength <= FAULT_THRESHOLDS.get("signal_strength_critical", -95.0):
                faults.append("CommunicationCritical")
            elif signal_strength <= FAULT_THRESHOLDS.get("signal_strength_low", -85.0):
                faults.append("CommunicationFault")
            
            if transmission_quality < 50.0:
                faults.append("TransmissionFailure")
            
            # Rule 4: AOCS Failure Detection
            gyro_drift = telemetry.get("gyro_drift", 0.0)
            orientation_deviation = telemetry.get("orientation_deviation", 5.0)
            actuator_status = telemetry.get("actuator_status", 100.0)
            
            if abs(gyro_drift) > 0.8:
                faults.append("GyroDriftFailure")
            
            if orientation_deviation > 25.0:
                faults.append("AttitudeDriftCritical")
            elif orientation_deviation > 15.0:
                faults.append("AttitudeDrift")
            
            if actuator_status < FAULT_THRESHOLDS.get("actuator_status_low", 50.0):
                faults.append("ActuatorFailure")
            
            # Rule 5: Power Subsystem Failure (composite)
            power_consumption = telemetry.get("power_consumption", 50.0)
            solar_output = telemetry.get("solar_output", 100.0)
            
            if solar_output < 20.0:
                faults.append("SolarPanelFailure")
            
            if battery_voltage < 25.0 and power_consumption > 70.0:
                faults.append("PowerSubsystemFailure")
            
            # Rule 6: Antenna Alignment Issue
            antenna_alignment = telemetry.get("antenna_alignment", 180.0)
            if abs(antenna_alignment - 180.0) > 45.0 and signal_strength < -70.0:
                faults.append("AntennaAlignment")
            
            return faults
        
        except Exception as e:
            logger.error(f"Error applying semantic rules: {str(e)}", "ReasoningEngine")
            return faults
    
    def get_active_faults(self) -> List[str]:
        """Get currently active faults"""
        return list(self.current_faults)
    
    def get_fault_details(self, fault_name: str) -> Dict[str, str]:
        """Get human-readable details about a fault"""
        fault_descriptions = {
            "BatteryFault": "Battery voltage is low - subsystem degradation possible",
            "BatteryCritical": "Critical battery voltage - immediate action required",
            "ThermalFault": "Internal temperature elevated - thermal management needed",
            "ThermalCritical": "Critical internal temperature - emergency cooling required",
            "ThermalLoadHigh": "Thermal load exceeding nominal - subsystem may overheat",
            "CommunicationFault": "Signal strength degraded - communication may be unreliable",
            "CommunicationCritical": "Critical signal loss - communication failure imminent",
            "TransmissionFailure": "Transmission quality critical - link may be lost",
            "GyroDriftFailure": "Gyroscope drift exceeding limits - attitude control affected",
            "AttitudeDrift": "Orientation deviation detected - corrective action needed",
            "AttitudeDriftCritical": "Critical attitude drift - satellite pointing failure",
            "ActuatorFailure": "Actuator status critical - AOCS control limited",
            "SolarPanelFailure": "Solar panel output critically low - power deficit",
            "PowerSubsystemFailure": "Power subsystem failure - insufficient power generation",
            "AntennaAlignment": "Antenna misalignment detected - signal degradation",
        }
        return {
            "name": fault_name,
            "severity": self._get_fault_severity(fault_name),
            "description": fault_descriptions.get(fault_name, "Unknown fault"),
        }
    
    def _get_fault_severity(self, fault_name: str) -> str:
        """Determine fault severity"""
        if "Critical" in fault_name:
            return "CRITICAL"
        elif "Failure" in fault_name:
            return "SEVERE"
        else:
            return "WARNING"

# Global reasoning engine instance
_reasoning_engine = None

def get_reasoning_engine() -> ReasoningEngine:
    """Get global reasoning engine instance"""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
