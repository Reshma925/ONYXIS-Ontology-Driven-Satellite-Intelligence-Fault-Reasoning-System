"""
Telemetry Generator for Satellite Monitoring System
"""

import time
from typing import Dict
from datetime import datetime
from simulator.sensor_models import SensorSuite
from simulator.scenarios import ScenarioManager
from utils.logger import get_logger

logger = get_logger()

class TelemetryGenerator:
    """Generate realistic satellite telemetry"""
    
    def __init__(self):
        self.sensors = SensorSuite()
        self.scenario_manager = ScenarioManager()
        self.telemetry_history = []
        self.is_running = False
        self.last_update_time = None
        self.update_count = 0
    
    def generate_telemetry(self) -> Dict[str, float]:
        """
        Generate one telemetry sample
        
        Returns:
            Dictionary of telemetry values
        """
        try:
            # Read all sensors
            telemetry = self.sensors.read_all()
            
            # Apply active scenario
            telemetry = self.scenario_manager.apply_scenario(telemetry)
            
            # Update statistics
            self.last_update_time = datetime.now()
            self.update_count += 1
            
            # Store in history
            self.telemetry_history.append({
                "timestamp": self.last_update_time,
                "data": telemetry.copy()
            })
            
            # Keep only recent history
            if len(self.telemetry_history) > 3600:  # Keep 1 hour at 1 Hz
                self.telemetry_history = self.telemetry_history[-3600:]
            
            logger.info(f"Telemetry generated - Scenario: {self.scenario_manager.get_active_scenario()}", "TelemetryGenerator")
            
            return telemetry
        
        except Exception as e:
            logger.error(f"Error generating telemetry: {str(e)}", "TelemetryGenerator")
            return self.sensors.read_all()
    
    def set_scenario(self, scenario_name: str) -> bool:
        """Set active scenario"""
        if self.scenario_manager.set_scenario(scenario_name):
            logger.info(f"Scenario changed to: {scenario_name}", "TelemetryGenerator")
            return True
        else:
            logger.warning(f"Invalid scenario: {scenario_name}", "TelemetryGenerator")
            return False
    
    def get_active_scenario(self) -> str:
        """Get active scenario name"""
        return self.scenario_manager.get_active_scenario()
    
    def get_available_scenarios(self) -> list:
        """Get list of available scenarios"""
        return self.scenario_manager.get_scenarios_list()
    
    def get_telemetry_history(self, limit: int = 100) -> list:
        """Get telemetry history"""
        return self.telemetry_history[-limit:] if len(self.telemetry_history) > limit else self.telemetry_history
    
    def get_statistics(self) -> Dict:
        """Get telemetry generation statistics"""
        return {
            "update_count": self.update_count,
            "last_update": self.last_update_time,
            "history_length": len(self.telemetry_history),
            "active_scenario": self.get_active_scenario(),
        }
    
    def reset(self):
        """Reset telemetry generator"""
        self.sensors = SensorSuite()
        self.scenario_manager.set_scenario("normal")
        self.telemetry_history = []
        self.update_count = 0
        logger.info("Telemetry generator reset", "TelemetryGenerator")

# Global telemetry generator instance
_telemetry_generator = None

def get_telemetry_generator() -> TelemetryGenerator:
    """Get global telemetry generator instance"""
    global _telemetry_generator
    if _telemetry_generator is None:
        _telemetry_generator = TelemetryGenerator()
    return _telemetry_generator
