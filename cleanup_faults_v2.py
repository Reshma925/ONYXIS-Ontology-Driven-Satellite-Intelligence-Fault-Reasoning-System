#!/usr/bin/env python3

filePath = r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl'

# Read the file
with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# List of fault individuals to remove
fault_patterns = [
    r'<owl:NamedIndividual rdf:about="#AlignmentFailure_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#AmplifierFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#AntennaFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#AntennaPointingFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#AttitudeControlFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#BatteryFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#BusFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#ChargeControllerFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#CommandReceiverFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#DecoderFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#DemodulatorFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#DownconverterFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#DuplexerFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#EarthSensorFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#EncoderFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#FilterFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#GNSSFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#GroundLinkFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#GyroFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#HeaterFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#LNAFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#LOFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#MagnetometerFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#MagnetorquerFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#MountFailure_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#OrbitControlFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#OverheatFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#PCDUFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#ReactionWheelFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#RegulatorFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#SensorFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#SignalLossFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#SolarFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#StarTrackerFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#StructuralFailure_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#SunSensorFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#TTCAntennaFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#TTCRadioFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#TelemetryEncoderFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#ThrusterFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#TrackingFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#UnderheatFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#UpconverterFault_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
    r'<owl:NamedIndividual rdf:about="#VibrationFailure_001">[\s\S]*?</owl:NamedIndividual>\s*\n',
]

import re
count = 0
for pattern in fault_patterns:
    match = re.search(pattern, content)
    if match:
        count += 1
    content = re.sub(pattern, '', content)

# Write back
with open(filePath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Removed {count} fault individual blocks")
