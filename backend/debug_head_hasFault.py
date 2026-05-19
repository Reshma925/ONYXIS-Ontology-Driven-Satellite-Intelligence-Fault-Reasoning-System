from pathlib import Path
import owlready2
p = Path('backend/satellite_semantic_runtime.owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for rule in onto.rules():
    for atom in rule.head:
        if getattr(getattr(atom, 'property_predicate', None), 'name', None) == 'hasFault':
            print('RULE STR:', str(rule))
            for pos, atom in enumerate(rule.body):
                print('BODY ATOM', pos, type(atom).__name__, 'repr', atom)
                print('  class_pred', getattr(atom, 'class_predicate', None))
                print('  property_pred', getattr(atom, 'property_predicate', None))
                print('  builtin', getattr(atom, 'builtin', None))
                print('  args', atom.arguments)
                print('  serialized', __import__('create_semantic_runtime').atom_to_str(atom))
            print('HEAD ATOMS', [__import__('create_semantic_runtime').atom_to_str(a) for a in rule.head])
            raise SystemExit
print('no head hasFault rule found')
