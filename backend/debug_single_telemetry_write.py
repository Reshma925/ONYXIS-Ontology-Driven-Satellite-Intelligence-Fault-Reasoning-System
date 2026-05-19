#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import ontology_service as svc

key = 'internalTemp'
definition = svc.OntologyEngine(svc.ONTOLOGY_PATH)._build_telemetry_definitions()[key]
print('Testing', key, definition.individual, definition.property, definition.value)
engine = svc.OntologyEngine(svc.ONTOLOGY_PATH)
ind = engine.individuals.get(definition.individual)
prop_obj = engine.property_cache.get(definition.property)
print('Property object:', prop_obj)
print('Declared range:', engine._get_property_declared_range_uri(prop_obj))
print('Current values:', list(getattr(ind, definition.property, [])))
print('Current rdf values:')
import rdflib
subj = rdflib.URIRef(ind.iri)
pred = rdflib.URIRef(prop_obj.iri)
g = engine.world.as_rdflib_graph()
for obj in g.objects(subject=subj, predicate=pred):
    print('  ', obj, type(obj))

safe_value = engine._normalize_ontology_value(prop_obj, definition.value)
print('safe_value', safe_value, type(safe_value))
with engine.onto:
    try:
        delattr(ind, definition.property)
        print('delattr succeeded')
    except Exception as e:
        print('delattr failed', e)
        try:
            setattr(ind, definition.property, [])
            print('setattr empty list succeeded')
        except Exception as e2:
            print('setattr empty list failed', e2)
    setattr(ind, definition.property, [safe_value])
    print('after assign values:', list(getattr(ind, definition.property, [])))
    print('after assign rdf values:')
    for obj in g.objects(subject=subj, predicate=pred):
        print('  ', obj, type(obj))

try:
    output = engine._capture_reasoner_output()
    print('Reasoner OK')
    print(output)
except Exception as exc:
    print('Reasoner FAILED:', type(exc).__name__, exc)
