from pathlib import Path
import owlready2
from owlready2 import destroy_entity

p = Path('backend/satellite_semantic_runtime.owl').resolve()
world = owlready2.World()
onto = world.get_ontology(str(p)).load()
print('initial rule count', len(list(onto.rules())))
for r in onto.rules():
    print('rule head types', [type(atom).__name__ for atom in r.head])
    print('rule repr', r)
    try:
        destroy_entity(r)
        print('destroy_entity succeeded')
    except Exception as e:
        print('destroy_entity failed', type(e), e)
    break
print('after rule count', len(list(onto.rules())))
