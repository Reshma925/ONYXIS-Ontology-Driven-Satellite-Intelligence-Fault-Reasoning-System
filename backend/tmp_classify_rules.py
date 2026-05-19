from pathlib import Path
from owlready2 import get_ontology

onto = get_ontology(str(Path(__file__).parent / 'satellite_semantic_runtime.owl')).load()

telemetry_rules = []
propagation_rules = []
action_rules = []
pure_rules = []
loop_risks = []
non_triggering_candidates = []

for idx, rule in enumerate(onto.rules(), start=1):
    body = list(rule.body)
    head = list(rule.head)
    body_types = [type(atom).__name__ for atom in body]
    head_types = [type(atom).__name__ for atom in head]
    body_props = [getattr(atom.property_predicate, 'name', None) for atom in body if type(atom).__name__ == 'IndividualPropertyAtom']
    head_props = [getattr(atom.property_predicate, 'name', None) for atom in head if type(atom).__name__ == 'IndividualPropertyAtom']
    body_data = [getattr(atom.property_predicate, 'name', None) for atom in body if type(atom).__name__ == 'DatavaluedPropertyAtom']
    head_data = [getattr(atom.property_predicate, 'name', None) for atom in head if type(atom).__name__ == 'DatavaluedPropertyAtom']
    head_classes = [getattr(atom.class_predicate, 'name', None) for atom in head if type(atom).__name__ == 'ClassAtom']
    body_classes = [getattr(atom.class_predicate, 'name', None) for atom in body if type(atom).__name__ == 'ClassAtom']
    has_builtin = any(type(atom).__name__ == 'BuiltinAtom' for atom in body)
    has_dataval = bool(body_data)
    has_indiv = bool(body_props)
    has_triggers = 'triggersAction' in head_props
    head_fault = any(cls and cls.endswith('FaultState') for cls in head_classes)
    body_fault = any(cls and cls.endswith('FaultState') for cls in body_classes)
    body_fault_or_sub = body_fault or any(cls == 'Fault' for cls in body_classes)
    in_props = any(prop for prop in body_props if prop)
    out_props = any(prop for prop in head_props if prop)
    pred_pairs = [(getattr(atom.property_predicate, 'name', None), atom.arguments) for atom in body if type(atom).__name__ == 'IndividualPropertyAtom']

    line = f'R{idx:03d}: body_types={body_types}, head_types={head_types}, body_props={body_props}, head_props={head_props}, body_data={body_data}, head_classes={head_classes}'
    if has_triggers:
        action_rules.append((idx, line))
    elif has_dataval and has_builtin and head_fault:
        telemetry_rules.append((idx, line))
    elif has_indiv and head_fault:
        propagation_rules.append((idx, line))
    else:
        pure_rules.append((idx, line))
    
    # loop risk if this is a fault propagation rule with fault in both body and head and a non-symmetric property
    if head_fault and body_fault_or_sub and has_indiv:
        loop_risks.append((idx, line))

print('Counts:')
print(' telemetry:', len(telemetry_rules))
print(' propagation:', len(propagation_rules))
print(' action:', len(action_rules))
print(' pure:', len(pure_rules))
print(' loop risk:', len(loop_risks))
print()

for label, collection in [('Telemetry', telemetry_rules), ('Propagation', propagation_rules), ('Action', action_rules), ('Pure', pure_rules)]:
    print(f'=== {label} RULES ({len(collection)}) ===')
    for idx, line in collection:
        print(idx)
    print()

print('=== LOOP RISK RULES ===')
for idx, line in loop_risks:
    print(idx)
