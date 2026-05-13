#!/usr/bin/env python
"""
Project Verification Script
Checks that all components are properly configured and ready to run
"""

import sys
import os

print("=" * 70)
print("🛰️  SATELLITE MONITORING & FAULT DIAGNOSIS SIMULATOR")
print("     PROJECT VERIFICATION")
print("=" * 70)

# Check 1: Python Version
print("\n✓ Python Version Check")
print(f"  Python {sys.version.split()[0]} (Required: 3.11+)")

if sys.version_info < (3, 11):
    print("  ⚠️  WARNING: Python 3.11+ recommended")

# Check 2: Directory Structure
print("\n✓ Directory Structure")
required_dirs = [
    "simulator",
    "reasoner",
    "dashboard",
    "utils",
    "ontology",
    "assets",
]

for dir_name in required_dirs:
    if os.path.isdir(dir_name):
        print(f"  ✅ {dir_name}/")
    else:
        print(f"  ❌ {dir_name}/ NOT FOUND")

# Check 3: Key Files
print("\n✓ Key Files")
required_files = [
    "app.py",
    "requirements.txt",
    "README.md",
    "ontology/satellite_full.owl",
    "simulator/telemetry_generator.py",
    "reasoner/reasoning_engine.py",
    "dashboard/metrics_panel.py",
    "utils/constants.py",
]

for file_name in required_files:
    if os.path.isfile(file_name):
        file_size = os.path.getsize(file_name)
        print(f"  ✅ {file_name} ({file_size:,} bytes)")
    else:
        print(f"  ❌ {file_name} NOT FOUND")

# Check 4: Module Imports
print("\n✓ Python Module Imports")
modules_to_check = [
    ("streamlit", "Streamlit UI"),
    ("owlready2", "OWL Ontology"),
    ("plotly", "Charts"),
    ("pandas", "Data"),
    ("networkx", "Graph"),
]

for module_name, description in modules_to_check:
    try:
        __import__(module_name)
        print(f"  ✅ {module_name:<15} - {description}")
    except ImportError:
        print(f"  ❌ {module_name:<15} - {description} (NOT INSTALLED)")

# Check 5: Local Modules
print("\n✓ Local Module Structure")
try:
    from reasoner.ontology_loader import get_ontology_loader
    from simulator.telemetry_generator import get_telemetry_generator
    from reasoner.reasoning_engine import get_reasoning_engine
    from utils.logger import get_logger
    print("  ✅ All local modules importable")
except ImportError as e:
    print(f"  ❌ Import error: {e}")

# Check 6: Configuration
print("\n✓ Configuration Check")
try:
    from utils.constants import TELEMETRY_RANGES, FAULT_THRESHOLDS, SCENARIOS
    print(f"  ✅ {len(TELEMETRY_RANGES)} telemetry parameters configured")
    print(f"  ✅ {len(FAULT_THRESHOLDS)} fault thresholds configured")
    print(f"  ✅ {len(SCENARIOS)} scenarios available")
except Exception as e:
    print(f"  ❌ Configuration error: {e}")

# Summary
print("\n" + "=" * 70)
print("✅ PROJECT VERIFICATION COMPLETE")
print("=" * 70)
print("\n📝 TO START THE APPLICATION:\n")
print("   streamlit run app.py\n")
print("🌐 Browser will open at: http://localhost:8501\n")
print("=" * 70)
print("\n📚 Documentation: See README.md for detailed usage guide\n")
