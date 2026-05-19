import pathlib
import owlready2

p = pathlib.Path('backend/satellite_semantic_runtime.owl').resolve()
world = owlready2.World()
onto = world.get_ontology(str(p)).load()
rules = list(onto.rules())
print('before', len(rules))
r = rules[0]
print('head', [(type(atom).__name__, getattr(getattr(atom, 'property_predicate', None), 'name', None), getattr(getattr(atom, 'class_predicate', None), 'name', None)) for atom in r.head])
print('has __destroy__', hasattr(r, '__destroy__'))
try:
    with onto:
        r.__destroy__()
    print('destroyed ok')
except Exception as e:
    print('destroy failed', e)
print('after', len(list(onto.rules())))
