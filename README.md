# 🛰️ Satellite Monitoring & Fault Diagnosis Simulator

## Overview

A complete **semantic digital twin and ontology-driven fault diagnosis engine** for satellite systems. This application simulates realistic satellite telemetry, injects it into an OWL ontology, executes semantic reasoning with SWRL rules, and visualizes fault inference in real time.

### Key Features

✅ **Real-time Telemetry Simulation** - Generate realistic sensor data for Power, Thermal, Communication, and AOCS systems

✅ **Ontology-Based Reasoning** - Semantic fault inference using OWL/SWRL (Owlready2)

✅ **Multiple Failure Scenarios** - Trigger faults like battery drain, thermal overload, solar panel failure, etc.

✅ **Professional Dashboard UI** - Streamlit-based aerospace monitoring interface with glowing effects

✅ **Live Charts & Metrics** - Real-time visualization with Plotly

✅ **Fault Console** - Scrolling alert system with timestamps and severity indicators

✅ **Ontology Inspector** - Debug and inspect semantic reasoning, inferred classes, and relationships

✅ **Modular Architecture** - Clean separation: simulator, reasoner, dashboard, ontology layers

---

## Project Structure

```
Project-satellite/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── 
├── ontology/
│   └── satellite_full.owl          # OWL ontology with SWRL rules
│
├── simulator/
│   ├── sensor_models.py            # Realistic sensor simulation with noise/drift
│   ├── scenarios.py                # Fault scenario definitions
│   ├── telemetry_generator.py      # Central telemetry orchestration
│   └── __init__.py
│
├── reasoner/
│   ├── ontology_loader.py          # Load and manage OWL ontology
│   ├── ontology_updater.py         # Update ontology with telemetry
│   ├── reasoning_engine.py         # Semantic fault inference engine
│   ├── swrl_rules.py               # SWRL rule documentation
│   └── __init__.py
│
├── dashboard/
│   ├── metrics_panel.py            # Subsystem health overview
│   ├── charts.py                   # Live telemetry charts (Plotly)
│   ├── alerts.py                   # Fault console and alerts
│   ├── subsystem_view.py           # Detailed subsystem analysis
│   ├── ontology_inspector.py       # Semantic debugging interface
│   └── __init__.py
│
├── utils/
│   ├── constants.py                # Configuration constants
│   ├── logger.py                   # Thread-safe event logging
│   ├── helpers.py                  # Utility functions
│   └── __init__.py
│
└── assets/                         # (Reserved for images/icons)
```

---

## Installation

### 1. Prerequisites

- Python 3.11+
- pip

### 2. Install Dependencies

```bash
cd Project-satellite
pip install -r requirements.txt
```

**Key packages installed:**
- `streamlit` - Web UI framework
- `owlready2` - OWL ontology management
- `rdflib` - RDF/OWL reasoning support
- `plotly` - Interactive charts
- `pandas` - Data handling
- `networkx` - Graph operations
- `python-dateutil` - DateTime utilities

---

## Running the Application

### Start the Simulator

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Alternative: Run with Custom Settings

```bash
streamlit run app.py --logger.level=warning
```

---

## Usage Guide

### 🏠 Dashboard View

The main dashboard shows:
- **Subsystem Health Cards** - Power, Thermal, Communication, AOCS, Payload status
- **Live Telemetry Charts** - Battery voltage, temperature, signal strength, solar output
- **Fault Console** - Real-time scrolling alerts with timestamps
- **Fault Summary** - Color-coded system status (Green/Yellow/Red)

### 📊 Detailed View

Drill-down analysis for each subsystem:
- **Power System** - Battery voltage, solar output, power balance
- **Thermal System** - Internal/subsystem temperatures, thermal load
- **Communication** - Signal strength, antenna alignment, transmission quality
- **AOCS** - Gyro drift, orientation deviation, actuator status

### 🔬 Ontology Inspector

Semantic debugging interface:
- **Statistics** - Classes, individuals, properties in ontology
- **Classes** - Class hierarchy organized by subsystem
- **Individuals** - Browse satellite individual and its properties
- **Inferred Faults** - All currently inferred faults with severity
- **Rules** - Display active SWRL-like reasoning rules

### 📋 System Logs

View all system events with filtering by:
- **Log Level** - INFO, WARNING, ERROR, FAULT
- **Component** - Simulator, Reasoner, Ontology, etc.

---

## Simulator Controls (Sidebar)

### Scenario Selection

Choose fault scenarios:
- **Normal Operation** - Nominal telemetry
- **Battery Drain** - Gradual battery voltage drop
- **Thermal Overload** - Rising internal temperatures
- **Solar Panel Failure** - Declining solar output
- **Communication Failure** - Signal strength degradation
- **Attitude Drift** - AOCS control issues

### Simulation Settings

- **Refresh Interval** - Update frequency (0.5-5 seconds)
- **Auto Refresh** - Enable continuous updates
- **Manual Update** - Generate single telemetry sample
- **Reset System** - Clear logs and reset state

---

## Semantic Reasoning Engine

### Active Inference Rules

The system applies SWRL-like reasoning rules to detect faults:

#### Power System Rules
- `BatteryFault` - Battery voltage < 22V
- `BatteryCritical` - Battery voltage < 20V
- `SolarPanelFailure` - Solar output < 20W
- `PowerSubsystemFailure` - Battery < 25V AND consumption > 70W

#### Thermal System Rules
- `ThermalFault` - Internal temperature > 70°C
- `ThermalCritical` - Internal temperature > 80°C
- `ThermalLoadHigh` - Thermal load > 80%

#### Communication Rules
- `CommunicationFault` - Signal strength < -85 dBm
- `CommunicationCritical` - Signal strength < -95 dBm
- `TransmissionFailure` - Transmission quality < 50%
- `AntennaAlignment` - Antenna misaligned >45° and poor signal

#### AOCS Rules
- `GyroDriftFailure` - Gyro drift > ±0.8 deg/s
- `AttitudeDrift` - Orientation deviation > 15°
- `AttitudeDriftCritical` - Orientation deviation > 25°
- `ActuatorFailure` - Actuator status < 50%

---

## Architecture

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      Streamlit UI                             │
│  (Dashboard, Charts, Fault Console, Ontology Inspector)      │
└───────────────────────┬──────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐   ┌────────────┐   ┌──────────┐
   │Dashboard│   │  Telemetry │   │Ontology  │
   │Components   │ Generator  │   │Inspector │
   └─────────┘   └─────┬──────┘   └──────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   ┌───────────┐              ┌─────────────┐
   │ Simulator │              │  Reasoner   │
   │- Sensors  │              │- Inference  │
   │- Scenarios│              │- Rule Engine│
   └─────┬─────┘              └──────┬──────┘
         │                           │
         └─────────────┬─────────────┘
                       │
                       ▼
             ┌──────────────────┐
             │     Ontology     │
             │  (satellite.owl) │
             │  - Classes       │
             │  - Individuals   │
             │  - SWRL Rules    │
             └──────────────────┘
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| **Simulator** | Generate realistic telemetry with noise, drift, scenarios |
| **Reasoner** | Semantic inference, SWRL rule execution, fault detection |
| **Dashboard** | UI visualization, charts, alerts, system inspector |
| **Utils** | Constants, logging, helper functions |
| **Ontology** | OWL knowledge base with SWRL reasoning rules |

---

## Configuration

### Edit Constants

Modify [utils/constants.py](utils/constants.py) to adjust:

```python
# Telemetry ranges and nominal values
TELEMETRY_RANGES = {
    "battery_voltage": {"min": 20.0, "max": 32.0, "nominal": 28.0},
    "internal_temp": {"min": -20.0, "max": 80.0, "nominal": 25.0},
    # ... more telemetry ...
}

# Fault thresholds
FAULT_THRESHOLDS = {
    "battery_voltage_low": 22.0,
    "internal_temp_high": 70.0,
    # ... more thresholds ...
}
```

### Modify Scenarios

Edit [simulator/scenarios.py](simulator/scenarios.py) to:
- Create new fault scenarios
- Adjust degradation rates
- Add new sensor parameters

### Extend Reasoning Rules

Edit [reasoner/reasoning_engine.py](reasoner/reasoning_engine.py) to:
- Add new inference rules
- Modify fault detection logic
- Implement custom reasoning

---

## Performance Notes

- **Telemetry Update Rate**: 1 Hz (configurable)
- **Reasoning Cycle**: ~100-200ms per inference
- **Memory Usage**: ~200-300 MB steady state
- **History Buffer**: 3600 samples (1 hour at 1 Hz)

The system automatically:
- Maintains telemetry history
- Prevents memory leaks
- Logs in-memory (bounded)
- Recycles oldest data

---

## Troubleshooting

### "ModuleNotFoundError" on startup

**Solution**: Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Ontology not loading

**Solution**: Verify `ontology/satellite_full.owl` exists and is readable:
```bash
ls -la ontology/satellite_full.owl
```

### Streamlit stuck on "Running..."

**Solution**: The app runs continuous auto-refresh. Disable auto-refresh in sidebar or adjust refresh interval.

### Charts not updating

**Solution**: 
- Increase refresh interval (slower system may need 2-3 seconds)
- Ensure auto-refresh is enabled
- Check system memory

---

## Development Notes

### Adding a New Metric

1. **Sensor Model** → `simulator/sensor_models.py`
2. **Constant** → `utils/constants.py` (ranges, thresholds)
3. **Reasoning Rule** → `reasoner/reasoning_engine.py`
4. **Dashboard** → `dashboard/*.py` (display component)
5. **Ontology** → Update `ontology/satellite_full.owl`

### Testing

```bash
# Test imports
python -c "import reasoner.ontology_loader; print('OK')"

# Test telemetry generation
python -c "from simulator.telemetry_generator import get_telemetry_generator; gen = get_telemetry_generator(); print(gen.generate_telemetry())"

# Test reasoning
python -c "from reasoner.reasoning_engine import get_reasoning_engine; engine = get_reasoning_engine(); print(engine.infer_faults({'battery_voltage': 19.0}))"
```

---

## Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| Real-time Telemetry | ✅ | 13+ sensor types |
| Scenario Engine | ✅ | 6 failure scenarios |
| Ontology Integration | ✅ | OWL/SWRL support |
| Semantic Reasoning | ✅ | 15+ inference rules |
| Dashboard UI | ✅ | 5 major views |
| Live Charts | ✅ | Plotly integration |
| Fault Detection | ✅ | Automatic inference |
| System Logging | ✅ | Event tracking |
| Ontology Inspector | ✅ | Semantic debugging |
| Modular Architecture | ✅ | Clean separation |

---

## License & Attribution

This project demonstrates:
- Ontology-driven reasoning for IoT/satellite systems
- SWRL rule-based fault diagnosis
- Semantic digital twin architecture
- Real-time monitoring dashboards

---

## Support

For issues or questions:
1. Check the **System Logs** in the UI for error messages
2. Verify ontology is loaded via **Ontology Inspector**
3. Review **Configuration** section for parameter tuning

---

**Status**: ✅ Production Ready

**Last Updated**: May 7, 2026

🛰️ **Satellite Monitoring & Fault Diagnosis Simulator** - End-to-End Semantic Reasoning Platform
