from pathlib import Path
from owlready2 import get_ontology

onto = get_ontology(str(Path(__file__).parent / 'satellite_semantic_runtime.owl')).load()
interesting = [9,10,11,12,18,19,21,23,24,25,26,29,30,31,32,33,34,37,38,43,51,69,56,57,58,59,60,61,62,63,64,66,67,68]
for idx, rule in enumerate(onto.rules(), start=1):
    if idx not in interesting:
        continue
    body_atoms = list(rule.body)
    head_atoms = list(rule.head)
    print(f'RULE {idx:03d}: {rule}')
    print('  BODY ATOMS:')
    for atom in body_atoms:
        atom_type = type(atom).__name__
        print('   -', atom_type, getattr(getattr(atom, 'class_predicate', None), 'name', None), getattr(getattr(atom, 'property_predicate', None), 'name', None), getattr(atom, 'arguments', None))
    print('  HEAD ATOMS:')
    for atom in head_atoms:
        atom_type = type(atom).__name__
        print('   -', atom_type, getattr(getattr(atom, 'class_predicate', None), 'name', None), getattr(getattr(atom, 'property_predicate', None), 'name', None), getattr(atom, 'arguments', None))
    print()
