#!/usr/bin/env python3
"""
Direct RDF/XML Cleanup - Remove old fault individuals

This script directly processes the RDF/XML file to remove:
1. All runtime fault individuals (ending with _001)
2. All propagatesTo relationships
3. Maintains valid RDF/XML structure
"""

import re

ontology_path = r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl'

print("=" * 80)
print("DIRECT RDF/XML CLEANUP: Removing Old Fault Individuals")
print("=" * 80)

# Read the file
print(f"\n[1] Reading ontology file...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_size = len(content)
print(f"    ✓ File size: {original_size:,} bytes")

# List of fault individuals to remove
fault_individuals = [
    'AmplifierFault_001', 'AntennaFault_001', 'AntennaPointingFault_001', 'AttitudeControlFault_001',
    'BatteryFault_001', 'ChargeControllerFault_001', 'CommandReceiverFault_001', 'DecoderFault_001',
    'DemodulatorFault_001', 'DownconverterFault_001', 'DuplexerFault_001', 'EarthSensorFault_001',
    'EncoderFault_001', 'FilterFault_001', 'GNSSFault_001', 'GroundLinkFault_001',
    'GyroFault_001', 'HeaterFault_001', 'LNAFault_001', 'LOFault_001',
    'MagnetometerFault_001', 'MagnetorquerFault_001', 'OrbitControlFault_001', 'OverheatFault_001',
    'PCDUFault_001', 'ReactionWheelFault_001', 'SensorFault_001', 'SignalLossFault_001',
    'SolarFault_001', 'StarTrackerFault_001', 'SunSensorFault_001', 'TTCAntennaFault_001',
    'TTCRadioFault_001', 'TelemetryEncoderFault_001', 'ThrusterFault_001', 'TrackingFault_001',
    'UnderheatFault_001', 'UpconverterFault_001', 'BusFault_001', 'RegulatorFault_001'
]

print(f"\n[2] Removing {len(fault_individuals)} runtime fault individuals...")
removed_count = 0

for fault_name in fault_individuals:
    # Pattern to match the NamedIndividual block
    # Matches from opening tag to closing tag, including all content
    pattern = rf'<owl:NamedIndividual rdf:about="#{fault_name}">\s*.*?</owl:NamedIndividual>\s*'
    
    # Count occurrences before removal
    matches = len(re.findall(pattern, content, re.DOTALL))
    if matches > 0:
        removed_count += matches
        print(f"    - Removing {fault_name}: {matches} occurrence(s)")
        # Remove the entire NamedIndividual block
        content = re.sub(pattern, '', content, flags=re.DOTALL)

print(f"    ✓ Total fault individual blocks removed: {removed_count}")

# Remove references in propagatesTo
print(f"\n[3] Removing propagatesTo relationships...")
propagates_count = len(re.findall(r'<propagatesTo rdf:resource=".*?"/>', content))
if propagates_count > 0:
    print(f"    - Found {propagates_count} propagatesTo assertions")
    content = re.sub(r'\s*<propagatesTo rdf:resource="[^"]*"/>\n', '', content)
    print(f"    ✓ Removed propagatesTo assertions")

# Clean up double blank lines created by removal
print(f"\n[4] Cleaning up formatting...")
before_lines = content.count('\n')
content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
after_lines = content.count('\n')
print(f"    ✓ Cleaned up extra blank lines ({before_lines} → {after_lines} lines)")

# Write back
print(f"\n[5] Writing cleaned ontology...")
with open(ontology_path, 'w', encoding='utf-8') as f:
    f.write(content)

new_size = len(content)
size_reduction = original_size - new_size
print(f"    ✓ File size: {new_size:,} bytes (reduced by {size_reduction:,} bytes)")

# Verification
print(f"\n[6] Verification...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    verify_content = f.read()

remaining_faults = 0
for fault_name in fault_individuals:
    if f'rdf:about="#{fault_name}"' in verify_content:
        remaining_faults += 1
        print(f"    ⚠ {fault_name} still present")

if remaining_faults == 0:
    print(f"    ✓ No runtime fault individuals remaining")

remaining_propagates = len(re.findall(r'<propagatesTo', verify_content))
if remaining_propagates == 0:
    print(f"    ✓ No propagatesTo assertions remaining")
else:
    print(f"    ⚠ {remaining_propagates} propagatesTo assertions still present")

# Summary
print(f"\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
print(f"✓ Removed {removed_count} runtime fault individual blocks")
print(f"✓ Removed propagatesTo relationships")
print(f"✓ File size reduced from {original_size:,} to {new_size:,} bytes")
print(f"✓ Ontology ready for semantic validation")
print("=" * 80)

