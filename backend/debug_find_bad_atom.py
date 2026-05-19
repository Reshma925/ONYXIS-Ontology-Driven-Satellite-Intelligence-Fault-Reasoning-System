from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_semantic_runtime.owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for rule in onto.rules():
    if 'hasFault' in str(rule):
        for atom in list(rule.body) + list(rule.head):
            s = cst.atom_to_str(atom)
            if 'None(' in s or s.startswith('None'):
                print('BAD', s, 'for atom', type(atom).__name__, repr(atom))
                print(' class_predicate', getattr(atom, 'class_predicate', None), 'property_predicate', getattr(atom, 'property_predicate', None), 'args', atom.arguments)
                raise SystemExit
print('no bad atoms')
