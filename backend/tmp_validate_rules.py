import re
from pathlib import Path
from owlready2 import get_ontology, sync_reasoner_pellet

owl_path = Path(__file__).parent / 'satellite_semantic_runtime.owl'
onto = get_ontology(str(owl_path)).load()
rules = list(onto.rules())
print('RULE_COUNT', len(rules))
rel_props = ['connectedTo', 'dependsOn', 'feedsPowerTo', 'feedsSignalTo', 'feedsDataTo', 'feedsCommandTo', 'cools', 'heats', 'controls', 'propagatesTo', 'affectsComponent', 'belongsToSubsystem']
telemetry_props = [
    'hasTemperature', 'hasVibration', 'hasTrackingError', 'hasChargeLevel', 'hasSignalStrength',
    'hasBitErrorRate', 'hasDecodingError', 'hasAttitudeError', 'hasAngularRate', 'hasBandwidth',
    'hasCarrierFrequency', 'hasChargeRate', 'hasCoolingEfficiency', 'hasCycleCount', 'hasDegradationRate',
    'hasDischargeRate', 'hasGain', 'hasPointingError', 'hasPriority', 'hasSeverity', 'hasTransmitPower',
    'hasSunVectorError', 'hasSensorAccuracy', 'hasRegulatedVoltage', 'hasThrust', 'hasEncodingQuality',
    'hasPressure', 'hasCurrent', 'hasRegulatedVoltage', 'hasPower', 'hasVoltage', 'hasCurrent'
]

categories = {'telemetry': [], 'propagation': [], 'action': [], 'pure': []}

for idx, rule in enumerate(rules, 1):
    text = str(rule)
    body, head = (text.split('->') + ['', ''])[:2]
    has_builtin = bool(re.search(r'swrlb:(greaterThan|lessThan|equal|notEqual|greaterThanOrEqual|lessThanOrEqual)', text))
    has_telemetry = any(p in body for p in telemetry_props)
    tele = has_builtin or has_telemetry
    prop = any(r in body or r in head for r in rel_props)
    act = 'triggersAction' in head or 'triggersAction' in text or 'triggersMode' in head or 'triggersMode' in text
    if tele:
        categories['telemetry'].append(idx)
    elif act:
        categories['action'].append(idx)
    elif prop:
        categories['propagation'].append(idx)
    else:
        categories['pure'].append(idx)
    print(f'R{idx:03d}: tele={tele} prop={prop} act={act}')

print('\nCATEGORY_COUNTS', {k: len(v) for k, v in categories.items()})
print('TELEMETRY_RULES', categories['telemetry'])
print('PROPAGATION_RULES', categories['propagation'])
print('ACTION_RULES', categories['action'])
print('PURE_RULES', categories['pure'])

print('\nRunning Pellet reasoner...')
with onto:
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
print('REASONING DONE')
try:
    inconsistent = onto.world.inconsistent
except AttributeError:
    try:
        inconsistent = onto.world.inconsistent()
    except Exception as e:
        inconsistent = f'UNKNOWN({e})'
print('WORLD INCONSISTENT', inconsistent)

fault_classes = [c for c in onto.classes() if c.name.endswith('FaultState')]
print('FAULTSTATE_CLASS_COUNT', len(fault_classes))
count = 0
for c in sorted(fault_classes, key=lambda x: x.name):
    inst = list(c.instances())
    if inst:
        print(c.name, len(inst))
    count += len(inst)
print('TOTAL_FAULTSTATE_INDIVIDUALS', count)