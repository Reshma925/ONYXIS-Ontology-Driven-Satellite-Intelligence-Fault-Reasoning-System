#!/usr/bin/env python3
from pathlib import Path
from decimal import Decimal
import owlready2
from owlready2 import sync_reasoner_pellet

BASE = Path(__file__).parent
ONTOLOGY = BASE / "satellite_full (1).owl"


def load_onto():
    onto = owlready2.get_ontology(str(ONTOLOGY)).load()
    star = onto.search_one(iri="*STR_01") or onto.search_one(label="STR_01") or onto.search_one(name="STR_01")
    if star is None:
        raise RuntimeError("STR_01 individual not found")
    prop = onto.search_one(iri="*hasTrackingError") or onto.search_one(label="hasTrackingError") or onto.search_one(name="hasTrackingError")
    if prop is None:
        raise RuntimeError("hasTrackingError property not found")
    return onto, star, prop


def run_reasoner(onto):
    try:
        with onto:
            sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=0)
        return True, None
    except Exception as e:
        return False, str(e)


def print_summary(label, star):
    direct = [c.name for c in star.is_a]
    inferred = [c.name for c in getattr(star, 'INDIRECT_is_a', [])]
    print(f"  direct: {direct}")
    print(f"  inferred: {inferred}")
    print(f"  has TestFaultState: {'TestFaultState' in inferred}")


print("[TEST] Numeric builtin compatibility tests")

# Baseline: simple rule and float insertion
onto, star, prop = load_onto()
print("\n[CASE 1] float value + greaterThan(?e, 5.0)")
star.hasTrackingError = [11.22]
print("  assigned value type", type(star.hasTrackingError[0]), "value", star.hasTrackingError[0])
with onto:
    class TestFaultState(owlready2.Thing):
        pass
rule_text = "StarTracker(?x) ^ hasTrackingError(?x, ?e) ^ greaterThan(?e, 5.0) -> TestFaultState(?x)"
print("  rule:", rule_text)
imp = owlready2.Imp(namespace=onto)
imp.set_as_rule(rule_text, namespaces=[onto])
ok, err = run_reasoner(onto)
print("  Pellet passed:", ok)
if not ok:
    print("  error:", err)
else:
    print_summary('float', star)

# Case 2: decimal insertion + integer literal
onto, star, prop = load_onto()
print("\n[CASE 2] decimal value + greaterThan(?e, 5)")
star.hasTrackingError = [Decimal('11.22')]
print("  assigned value type", type(star.hasTrackingError[0]), "value", star.hasTrackingError[0])
with onto:
    class TestFaultState(owlready2.Thing):
        pass
rule_text = "StarTracker(?x) ^ hasTrackingError(?x, ?e) ^ greaterThan(?e, 5) -> TestFaultState(?x)"
print("  rule:", rule_text)
imp = owlready2.Imp(namespace=onto)
imp.set_as_rule(rule_text, namespaces=[onto])
ok, err = run_reasoner(onto)
print("  Pellet passed:", ok)
if not ok:
    print("  error:", err)
else:
    print_summary('decimal int literal', star)

# Case 3: decimal insertion + xsd:decimal literal
onto, star, prop = load_onto()
print("\n[CASE 3] decimal value + greaterThan(?e, \"5\"^^xsd:decimal)")
star.hasTrackingError = [Decimal('11.22')]
print("  assigned value type", type(star.hasTrackingError[0]), "value", star.hasTrackingError[0])
with onto:
    class TestFaultState(owlready2.Thing):
        pass
rule_text = 'StarTracker(?x) ^ hasTrackingError(?x, ?e) ^ greaterThan(?e, "5"^^xsd:decimal) -> TestFaultState(?x)'
print("  rule:", rule_text)
imp = owlready2.Imp(namespace=onto)
xsd_ns = owlready2.default_world.get_namespace('http://www.w3.org/2001/XMLSchema#')
imp.set_as_rule(rule_text, namespaces=[onto, xsd_ns])
ok, err = run_reasoner(onto)
print("  Pellet passed:", ok)
if not ok:
    print("  error:", err)
else:
    print_summary('decimal xsd literal', star)

print("\n[TEST COMPLETE]")
