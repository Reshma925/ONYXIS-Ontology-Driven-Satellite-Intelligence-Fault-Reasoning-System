#!/usr/bin/env python3

import os
import shutil

filePath = r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl'
tempPath = filePath + '.tmp'

fault_individuals = [
    'AlignmentFailure_001', 'AmplifierFault_001', 'AntennaFault_001', 'AntennaPointingFault_001', 'AttitudeControlFault_001',
    'BatteryFault_001', 'BusFault_001', 'ChargeControllerFault_001', 'CommandReceiverFault_001', 'DecoderFault_001',
    'DemodulatorFault_001', 'DeploymentFailure_001', 'DownconverterFault_001', 'DuplexerFault_001', 'EarthSensorFault_001',
    'EncoderFault_001', 'FilterFault_001', 'GNSSFault_001', 'GroundLinkFault_001', 'GyroFault_001',
    'HeaterFault_001', 'LNAFault_001', 'LOFault_001', 'MagnetometerFault_001', 'MagnetorquerFault_001',
    'MountFailure_001', 'OrbitControlFault_001', 'OverheatFault_001', 'PCDUFault_001', 'ReactionWheelFault_001',
    'RegulatorFault_001', 'SensorFault_001', 'SignalLossFault_001', 'SolarFault_001', 'StarTrackerFault_001',
    'StructuralFailure_001', 'SunSensorFault_001', 'TTCAntennaFault_001', 'TTCRadioFault_001', 'TelemetryEncoderFault_001',
    'ThrusterFault_001', 'TrackingFault_001', 'UnderheatFault_001', 'UpconverterFault_001', 'VibrationFailure_001'
]

# Read file
with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# For each fault individual, remove its definition block
count = 0
for fault in fault_individuals:
    start_tag = f'<owl:NamedIndividual rdf:about="#{fault}">'
    end_tag = '</owl:NamedIndividual>'
    
    start_idx = content.find(start_tag)
    # Debug output for first few
    if count < 3:
        print(f"  Looking for: {start_tag[:50]}...")
        print(f"  Found at: {start_idx}")
    if start_idx != -1:
        end_idx = content.find(end_tag, start_idx)
        if end_idx != -1:
            # Remove the entire block including trailing newlines
            end_idx = end_idx + len(end_tag)
            # Also remove the newline after the closing tag
            if end_idx < len(content) and content[end_idx] == '\r':
                end_idx += 1
            if end_idx < len(content) and content[end_idx] == '\n':
                end_idx += 1
            elif end_idx < len(content) and content[end_idx] == '\n':
                end_idx += 1
            
            content = content[:start_idx] + content[end_idx:]
            count += 1
            print(f"Removed {fault}")

# Write to file
with open(filePath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal removed: {count} fault individuals")
