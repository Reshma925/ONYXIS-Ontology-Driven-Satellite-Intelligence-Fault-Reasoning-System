from pathlib import Path
import owlready2
p = Path('backend/satellite_semantic_runtime.owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for r in onto.rules():
    if 'hasFault' in str(r) and '->' in str(r):
        head = r.head
        print('RULE STR:', str(r))
        print('HEAD LEN', len(head))
        for i, atom in enumerate(head):
            print('HEAD ATOM', i, type(atom).__name__)
            print('  repr', atom)
            for a in ['class_predicate','property_predicate','builtin_predicate','predicate','arguments']:
                print(' ', a, getattr(atom, a, None))
            print('  dir sample', [x for x in dir(atom) if not x.startswith('_')][:40])
        print('BODY LEN', len(r.body))
        for i, atom in enumerate(r.body):
            print('BODY ATOM', i, type(atom).__name__)
            print('  repr', atom)
            for a in ['class_predicate','property_predicate','builtin_predicate','predicate','arguments']:
                print(' ', a, getattr(atom, a, None))
            print('  dir sample', [x for x in dir(atom) if not x.startswith('_')][:40])
        break
