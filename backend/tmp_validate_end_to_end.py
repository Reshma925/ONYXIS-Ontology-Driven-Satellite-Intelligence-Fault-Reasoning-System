from pathlib import Path
from backend.ontology_service import OntologyEngine

engine = OntologyEngine(Path('backend/satellite_semantic_runtime.owl'))

# Example telemetry values to force fault triggers
sample_updates = {
    'STR_01': {'hasTrackingError': 11.88},
    'Battery_01': {'hasChargeLevel': 15.0},
    'RW_01': {'hasVibration': 0.0231},
}

print('\n=== TELEMETRY WRITE CHECK ===')
for individual, props in sample_updates.items():
    for prop_name, value in props.items():
        print(f'WRITE => {individual}.{prop_name} = {value}')
        engine._write_ontology_property(individual, prop_name, value)

print('\n=== TELEMETRY VALUES AFTER WRITE ===')
for individual, props in sample_updates.items():
    if individual not in engine.individuals:
        print(f'  MISSING INDIVIDUAL {individual}')
        continue
    ind = engine.individuals[individual]
    for prop_name in props:
        try:
            print(f'  {individual}.{prop_name} =', list(getattr(ind, prop_name, [])))
        except Exception as exc:
            print(f'  {individual}.{prop_name} ERROR {exc}')

print('\n=== RUNNING PELLET ===')
engine._run_reasoner()

print('\n=== EXTRACTED INFERRED CLASSES ===')
for ind_name, ind in sorted(engine.individuals.items()):
    inferred = [cls.name for cls in getattr(ind, 'INDIRECT_is_a', None) or [] if hasattr(cls, 'name')]
    if inferred:
        print(f'  {ind_name}: {inferred}')

print('\n=== HASFAULT TRIPLES IN RDF GRAPH ===')
for subj, pred, obj in engine.world.as_rdflib_graph():
    if 'hasFault' in str(pred):
        print('  ', subj, pred, obj)

print('\n=== EXTRACTED FAULTS ===')
engine._extract_state(int(time.time()*1000), infer_semantics=True)
for fault in engine.faults:
    print('  ', fault.id, fault.component, fault.name, fault.severity, fault.hasFault)

print('\n=== INFERRED CLASSES CACHE ===')
print(engine.inferredClasses)
