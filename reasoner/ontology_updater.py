"""
Ontology Updater for Satellite Monitoring System
"""

from typing import Dict, Any, List
from utils.logger import get_logger
from reasoner.ontology_loader import get_ontology_loader

logger = get_logger()

class OntologyUpdater:
    """Update ontology with telemetry data"""
    
    def __init__(self):
        self.loader = get_ontology_loader()
        self.last_update = None
    
    def update_telemetry(self, telemetry: Dict[str, float], satellite_individual_name: str = "Satellite1") -> bool:
        """
        Update ontology with telemetry data
        
        Args:
            telemetry: Dictionary of telemetry values
            satellite_individual_name: Name of satellite individual in ontology
        
        Returns:
            True if successful, False otherwise
        """
        if not self.loader.is_loaded:
            logger.error("Ontology not loaded", "OntologyUpdater")
            return False
        
        try:
            # Get the satellite individual
            satellite = self.loader.get_individual(satellite_individual_name)
            if satellite is None:
                logger.warning(f"Satellite individual '{satellite_individual_name}' not found", "OntologyUpdater")
                return False
            
            # Map telemetry to ontology properties
            property_mapping = {
                "battery_voltage": "hasBatteryVoltage",
                "battery_current": "hasBatteryCurrent",
                "solar_output": "hasSolarOutput",
                "power_consumption": "hasPowerConsumption",
                "internal_temp": "hasInternalTemperature",
                "subsystem_temp": "hasSubsystemTemperature",
                "thermal_load": "hasThermalLoad",
                "signal_strength": "hasSignalStrength",
                "antenna_alignment": "hasAntennaAlignment",
                "transmission_quality": "hasTransmissionQuality",
                "gyro_drift": "hasGyroDrift",
                "orientation_deviation": "hasOrientationDeviation",
                "actuator_status": "hasActuatorStatus",
            }
            
            # Update each property
            for telemetry_key, property_name in property_mapping.items():
                if telemetry_key in telemetry:
                    self._set_property_value(satellite, property_name, telemetry[telemetry_key])
            
            # Synchronize changes
            self.loader.onto.save()
            logger.info(f"Telemetry updated for {satellite_individual_name}", "OntologyUpdater")
            self.last_update = telemetry
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating telemetry: {str(e)}", "OntologyUpdater")
            return False
    
    def _set_property_value(self, individual: Any, property_name: str, value: Any) -> bool:
        """
        Set a property value on an individual
        """
        try:
            prop = self.loader.get_property(property_name)
            if prop is None:
                # Try to get from individual's class
                try:
                    prop = getattr(individual.__class__, property_name)
                except:
                    logger.warning(f"Property '{property_name}' not found", "OntologyUpdater")
                    return False
            
            # Set the property value
            setattr(individual, property_name, [float(value)])
            return True
        
        except Exception as e:
            logger.warning(f"Error setting property '{property_name}': {str(e)}", "OntologyUpdater")
            return False
    
    def get_telemetry_from_ontology(self, satellite_individual_name: str = "Satellite1") -> Dict[str, float]:
        """
        Read telemetry values from ontology
        """
        if not self.loader.is_loaded:
            return {}
        
        try:
            satellite = self.loader.get_individual(satellite_individual_name)
            if satellite is None:
                return {}
            
            telemetry = {}
            
            # Read all relevant properties
            property_mapping = {
                "battery_voltage": "hasBatteryVoltage",
                "battery_current": "hasBatteryCurrent",
                "solar_output": "hasSolarOutput",
                "power_consumption": "hasPowerConsumption",
                "internal_temp": "hasInternalTemperature",
                "subsystem_temp": "hasSubsystemTemperature",
                "thermal_load": "hasThermalLoad",
                "signal_strength": "hasSignalStrength",
                "antenna_alignment": "hasAntennaAlignment",
                "transmission_quality": "hasTransmissionQuality",
                "gyro_drift": "hasGyroDrift",
                "orientation_deviation": "hasOrientationDeviation",
                "actuator_status": "hasActuatorStatus",
            }
            
            for telemetry_key, property_name in property_mapping.items():
                try:
                    values = getattr(satellite, property_name, [])
                    if values:
                        telemetry[telemetry_key] = float(values[0])
                except:
                    pass
            
            return telemetry
        
        except Exception as e:
            logger.warning(f"Error reading telemetry from ontology: {str(e)}", "OntologyUpdater")
            return {}
    
    def infer_fault_class(self, fault_class_name: str, satellite_individual_name: str = "Satellite1") -> bool:
        """
        Infer a fault class for the satellite
        """
        if not self.loader.is_loaded:
            return False
        
        try:
            satellite = self.loader.get_individual(satellite_individual_name)
            fault_class = self.loader.get_class(fault_class_name)
            
            if satellite is None or fault_class is None:
                return False
            
            # Add fault to satellite's types
            if satellite not in fault_class.instances():
                fault_class.instances().append(satellite)
            
            self.loader.onto.save()
            return True
        
        except Exception as e:
            logger.warning(f"Error inferring fault: {str(e)}", "OntologyUpdater")
            return False
    
    def get_inferred_faults(self, satellite_individual_name: str = "Satellite1") -> List[str]:
        """
        Get all inferred faults for a satellite
        """
        if not self.loader.is_loaded:
            return []
        
        try:
            satellite = self.loader.get_individual(satellite_individual_name)
            if satellite is None:
                return []
            
            # Get all types/classes the satellite belongs to
            faults = []
            for cls in satellite.is_a:
                class_name = str(cls).split(".")[-1].rstrip("'")
                if "Fault" in class_name or "Failure" in class_name:
                    faults.append(class_name)
            
            return faults
        
        except Exception as e:
            logger.warning(f"Error retrieving faults: {str(e)}", "OntologyUpdater")
            return []

# Global updater instance
_ontology_updater = None

def get_ontology_updater() -> OntologyUpdater:
    """Get global ontology updater instance"""
    global _ontology_updater
    if _ontology_updater is None:
        _ontology_updater = OntologyUpdater()
    return _ontology_updater
