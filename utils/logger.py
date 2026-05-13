"""
Logger for Satellite Monitoring System
"""

from datetime import datetime
from typing import List, Dict
import threading

class SystemLogger:
    """Thread-safe logger for system events"""
    
    def __init__(self, max_logs: int = 1000):
        self.max_logs = max_logs
        self.logs: List[Dict] = []
        self.lock = threading.Lock()
    
    def log(self, level: str, message: str, component: str = "System"):
        """Log a message with timestamp"""
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "component": component,
                "message": message,
            }
            self.logs.append(log_entry)
            
            # Keep only recent logs
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[-self.max_logs:]
    
    def info(self, message: str, component: str = "System"):
        """Log info level"""
        self.log("INFO", message, component)
    
    def warning(self, message: str, component: str = "System"):
        """Log warning level"""
        self.log("WARNING", message, component)
    
    def error(self, message: str, component: str = "System"):
        """Log error level"""
        self.log("ERROR", message, component)
    
    def fault(self, message: str, component: str = "Reasoning"):
        """Log fault inference"""
        self.log("FAULT", message, component)
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent logs"""
        with self.lock:
            return self.logs[-limit:] if len(self.logs) > limit else self.logs
    
    def get_recent_faults(self, limit: int = 50) -> List[Dict]:
        """Get recent fault logs"""
        with self.lock:
            faults = [log for log in self.logs if log["level"] == "FAULT"]
            return faults[-limit:] if len(faults) > limit else faults
    
    def clear(self):
        """Clear all logs"""
        with self.lock:
            self.logs = []

# Global logger instance
_logger = SystemLogger()

def get_logger() -> SystemLogger:
    """Get global logger instance"""
    return _logger
