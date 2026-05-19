from pathlib import Path
import owlready2

p = Path('backend/satellite_semantic_runtime.owl').resolve()
world = owlready2.World()
onto = world.get_ontology(str(p)).load()
for r in onto.rules():
    if len(r.head) > 0 and getattr(getattr(r.head[0],'property_predicate',None),'name',None) == 'hasFault':
        print('rule repr', r)
        for atom in r.body:
            print('atom type', type(atom).__name__)
            print('attrs', [a for a in dir(atom) if not a.startswith('_')][:50])
            print('property_predicate', getattr(atom,'property_predicate',None))
            print('class_predicate', getattr(atom,'class_predicate',None))
            try:
                print('name', getattr(atom,'name',None))
            except Exception as e:
                print('name exception', e)
            try:
                print('arguments', atom.arguments)
            except Exception as e:
                print('arguments exception', e)
            print('---')
        break
