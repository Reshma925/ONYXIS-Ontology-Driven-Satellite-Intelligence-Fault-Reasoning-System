from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_semantic_runtime.owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for rule in onto.rules():
    if 'hasFault' in str(rule):
        print('RULE', str(rule))
        for atom in rule.body:
            print('ATOM', type(atom).__name__, '->', cst.atom_to_str(atom))
        print('HEAD', [cst.atom_to_str(atom) for atom in rule.head])
        break
