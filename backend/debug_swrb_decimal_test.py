#!/usr/bin/env python3
from pathlib import Path
import owlready2
from owlready2 import sync_reasoner_pellet
import rdflib

BASE = Path(__file__).parent
ONTOLOGY = BASE / "satellite_full_decimal_test.owl"
print("[DEBUG] Loading ontology:", ONTOLOGY)
onto = owlready2.get_ontology(str(ONTOLOGY)).load()
print("[DEBUG] Ontology base IRI:", onto.base_iri)

star = onto.search_one(iri="*STR_01") or onto.search_one(label="STR_01") or onto.search_one(name="STR_01")
if star is None:
    raise RuntimeError('STR_01 individual not found')
print("[DEBUG] Found STR_01", star)

prop = onto.search_one(iri="*hasTrackingError") or onto.search_one(label="hasTrackingError") or onto.search_one(name="hasTrackingError")
if prop is None:
    raise RuntimeError('hasTrackingError property not found')
print("[DEBUG] hasTrackingError property:", prop)
print("[DEBUG] property range:", getattr(prop, 'range', None))

# Clean up existing values in the underlying graph and insert a decimal literal
subj = rdflib.URIRef(star.iri)
pred = rdflib.URIRef(prop.iri)
print("[DEBUG] Clearing existing hasTrackingError triples")

with onto:
    graph = onto.world.as_rdflib_graph()
    graph.remove((subj, pred, None))
    lit = rdflib.Literal('11.22', datatype=rdflib.XSD.decimal)
    print("[DEBUG] Adding decimal literal", lit)
    graph.add((subj, pred, lit))

    class TestFaultState(owlready2.Thing):
        pass
    rule_text = 'StarTracker(?x) ^ hasTrackingError(?x, ?e) ^ greaterThan(?e, 5) -> TestFaultState(?x)'
    print("[DEBUG] Rule text:", rule_text)
    imp = owlready2.Imp(namespace=onto)
    imp.set_as_rule(rule_text, namespaces=[onto])
    print("[DEBUG] Rule created", imp)
    print("  body:", [str(a) for a in imp.body])
    print("  head:", [str(a) for a in imp.head])

print("[DEBUG] Running Pellet reasoner")
try:
    with onto:
        sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=0)
    print("[DEBUG] Pellet reasoning completed")
except Exception as e:
    print("[ERROR] Pellet reasoning failed:", e)
    raise

print("[DEBUG] STR_01 direct types:", [c.name for c in star.is_a])
print("[DEBUG] STR_01 inferred types:", [c.name for c in getattr(star, 'INDIRECT_is_a', [])])
print("[DEBUG] has TestFaultState:", 'TestFaultState' in [c.name for c in getattr(star, 'INDIRECT_is_a', [])])
