#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import ontology_service as svc

mapped = []
for key, definition in svc.OntologyEngine(svc.ONTOLOGY_PATH)._build_telemetry_definitions().items():
    if definition.property:
        mapped.append((key, definition))

print('mapped count', len(mapped))
for key, definition in mapped:
    print('TEST', key, definition.individual, definition.property, definition.value)
    eng = svc.OntologyEngine(svc.ONTOLOGY_PATH)
    ind = eng.individuals.get(definition.individual)
    if ind is None:
        print('  missing individual', definition.individual)
        continue
    prop_obj = eng.property_cache.get(definition.property)
    if prop_obj is None:
        print('  missing prop', definition.property)
        continue
    safe_value = eng._normalize_ontology_value(prop_obj, definition.value)
    print('  safe_value', safe_value, type(safe_value))
    with eng.onto:
        try:
            delattr(ind, definition.property)
        except Exception:
            try:
                setattr(ind, definition.property, [])
            except Exception:
                pass
        setattr(ind, definition.property, [safe_value])
    try:
        out = eng._capture_reasoner_output()
        print('  OK')
    except Exception as e:
        print('  FAILED', type(e).__name__, str(e)[:500])
    print('----')
