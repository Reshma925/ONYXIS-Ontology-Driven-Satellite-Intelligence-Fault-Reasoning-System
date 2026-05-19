from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for rule in onto.rules():
    if 'hasFault(' in str(rule) and '->' in str(rule):
        print('RULE', str(rule))
        print('HEAD', [cst.atom_to_str(a) for a in rule.head])
        print('BODY', [cst.atom_to_str(a) for a in rule.body])
        for atom in list(rule.body)+list(rule.head):
            print('ATOM', type(atom).__name__, 'clas', getattr(atom,'class_predicate',None), 'prop', getattr(atom,'property_predicate',None), 'builtin', getattr(atom,'builtin',None), 'args', atom.arguments)
        break
