#!/usr/bin/env python3

filePath = r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl'

fault_individuals = [
    'AlignmentFailure_001', 'AmplifierFault_001', 'AntennaFault_001', 'AntennaPointingFault_001',
    'AttitudeControlFault_001', 'BatteryFault_001', 'BusFault_001', 'ChargeControllerFault_001',
    'CommandReceiverFault_001', 'DecoderFault_001', 'DemodulatorFault_001', 'DownconverterFault_001',
    'DuplexerFault_001', 'EarthSensorFault_001', 'EncoderFault_001', 'FilterFault_001',
    'GNSSFault_001', 'GroundLinkFault_001', 'GyroFault_001', 'HeaterFault_001',
    'LNAFault_001', 'LOFault_001', 'MagnetometerFault_001', 'MagnetorquerFault_001',
    'MountFailure_001', 'OrbitControlFault_001', 'OverheatFault_001', 'PCDUFault_001',
    'ReactionWheelFault_001', 'RegulatorFault_001', 'SensorFault_001', 'SignalLossFault_001',
    'SolarFault_001', 'StarTrackerFault_001', 'StructuralFailure_001', 'SunSensorFault_001',
    'TTCAntennaFault_001', 'TTCRadioFault_001', 'TelemetryEncoderFault_001', 'ThrusterFault_001',
    'TrackingFault_001', 'UnderheatFault_001', 'UpconverterFault_001', 'VibrationFailure_001'
]

with open(filePath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

result = []
i = 0
count = 0

while i < len(lines):
    line = lines[i]
    
    # Check if this line starts a fault individual
    is_fault = False
    for fault in fault_individuals:
        if f'rdf:about="#{fault}"' in line:
            is_fault = True
            count += 1
            break
    
    if is_fault:
        # Skip this line and all lines until we find </owl:NamedIndividual>
        while i < len(lines) and '</owl:NamedIndividual>' not in lines[i]:
            i += 1
        i += 1  # Skip the closing tag itself
        # Skip the next blank line if it exists
        if i < len(lines) and lines[i].strip() == '':
            i += 1
    else:
        result.append(line)
        i += 1

with open(filePath, 'w', encoding='utf-8') as f:
    f.writelines(result)

print(f"Removed {count} fault individuals")
