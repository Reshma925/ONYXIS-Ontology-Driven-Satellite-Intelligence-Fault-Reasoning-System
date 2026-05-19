from pathlib import Path
import owlready2
p = Path('backend/satellite_semantic_runtime.owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
xs = [str(r) for r in onto.rules() if 'FaultState' in str(r)]
print(len(xs))
print('\n'.join(xs[:20]))
