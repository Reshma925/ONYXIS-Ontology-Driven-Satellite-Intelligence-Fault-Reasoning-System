from pathlib import Path
import owlready2

p = Path('backend/satellite_semantic_runtime.owl').resolve()
world = owlready2.World()
onto = world.get_ontology(str(p)).load()
for r in onto.rules():
    for atom in r.head:
        if getattr(getattr(atom, 'property_predicate', None), 'name', None) == 'hasFault':
            print('RULE:', r)
            for atom in r.body:
                print('ATOM', type(atom).__name__)
                print('  class_predicate:', getattr(atom, 'class_predicate', None))
                print('  property_predicate:', getattr(atom, 'property_predicate', None))
                try:
                    print('  class_predicate.name', getattr(atom.class_predicate, 'name', None))
                except Exception as e:
                    print('  class_predicate.name exception', e)
                try:
                    print('  property_predicate.name', getattr(atom.property_predicate, 'name', None))
                except Exception as e:
                    print('  property_predicate.name exception', e)
                try:
                    print('  arguments', [getattr(a,'name',str(a)) for a in atom.arguments])
                except Exception as e:
                    print('  arguments exception', e)
            print('---')
