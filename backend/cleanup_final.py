#!/usr/bin/env python3
"""
Fixed Direct RDF/XML Cleanup - Remove old fault individuals
"""

import re

ontology_path = r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl'

print("=" * 80)
print("FINAL RDF/XML CLEANUP: Removing Old Fault Individuals")
print("=" * 80)

# Read the file
print(f"\n[1] Reading ontology file...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

original_line_count = len(lines)
print(f"    ✓ File size: {original_line_count:,} lines")

# List of fault individuals to remove
fault_individuals = {
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
}

print(f"\n[2] Removing {len(fault_individuals)} runtime fault individuals...")
removed_count = 0
result_lines = []
skip_until_close = False

i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line starts a fault individual
    is_fault_start = False
    for fault_name in fault_individuals:
        if f'rdf:about="#{fault_name}"' in line:
            is_fault_start = True
            removed_count += 1
            print(f"    - Removing {fault_name}")
            break
    
    if is_fault_start:
        # Skip lines until we find the closing tag
        skip_until_close = True
        i += 1
        while i < len(lines) and '</owl:NamedIndividual>' not in lines[i]:
            i += 1
        # Skip the closing tag itself
        if i < len(lines) and '</owl:NamedIndividual>' in lines[i]:
            i += 1
        # Skip blank line if next line is blank
        if i < len(lines) and lines[i].strip() == '':
            i += 1
        skip_until_close = False
    else:
        result_lines.append(line)
        i += 1

print(f"    ✓ Removed {removed_count} fault individual blocks")

# Remove propagatesTo relationships
print(f"\n[3] Removing propagatesTo relationships...")
propagates_removed = 0
final_lines = []
for line in result_lines:
    if '<propagatesTo rdf:resource=' in line:
        propagates_removed += 1
        print(f"    - Removed: {line.strip()}")
    else:
        final_lines.append(line)

print(f"    ✓ Removed {propagates_removed} propagatesTo assertions")

# Write back
print(f"\n[4] Writing cleaned ontology...")
with open(ontology_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

new_line_count = len(final_lines)
print(f"    ✓ File size: {new_line_count:,} lines (removed {original_line_count - new_line_count} lines)")

# Verification
print(f"\n[5] Verification...")
with open(ontology_path, 'r', encoding='utf-8') as f:
    verify_content = f.read()

remaining_faults = 0
for fault_name in fault_individuals:
    if f'rdf:about="#{fault_name}"' in verify_content:
        remaining_faults += 1
        print(f"    ⚠ {fault_name} still present")

if remaining_faults == 0:
    print(f"    ✓ All runtime fault individuals removed")

remaining_propagates = verify_content.count('<propagatesTo')
if remaining_propagates == 0:
    print(f"    ✓ All propagatesTo assertions removed")
else:
    print(f"    ⚠ {remaining_propagates} propagatesTo assertions still present")

# Final summary
print(f"\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
print(f"✓ Removed {removed_count} runtime fault individual blocks")
print(f"✓ Removed {propagates_removed} propagatesTo relationships")
print(f"✓ Lines removed: {original_line_count - new_line_count}")
print(f"✓ Ontology cleaned and ready for semantic validation")
print("=" * 80)

