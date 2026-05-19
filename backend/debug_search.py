from pathlib import Path
import owlready2
p = Path('backend/satellite_semantic_runtime.owl').resolve()
world = owlready2.World()
onto = world.get_ontology(str(p)).load()
for r in onto.rules():
    if 'hasFault' in str(r):
        print(str(r))
