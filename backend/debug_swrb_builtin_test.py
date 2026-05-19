#!/usr/bin/env python3
from pathlib import Path
import owlready2
from owlready2 import sync_reasoner_pellet

BASE = Path(__file__).parent
ONTOLOGY = BASE / "satellite_full (1).owl"


def load_star_tracker():
    onto = owlready2.get_ontology(str(ONTOLOGY)).load()
    star = onto.search_one(iri="*STR_01") or onto.search_one(label="STR_01") or onto.search_one(name="STR_01")
    if star is None:
        raise RuntimeError("STR_01 individual not found")
    return onto, star


def run_reasoner(onto):
    try:
        with onto:
            sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=0)
        return True, None
    except Exception as e:
        return False, str(e)


def summarize_individual(star):
    direct = [c.name for c in star.is_a]
    inferred = [c.name for c in getattr(star, 'INDIRECT_is_a', [])]
    return direct, inferred


print("[SCENARIO] Baseline ontology inference")
onto, star = load_star_tracker()
print("  base IRI:", onto.base_iri)
print("  direct types:", [c.name for c in star.is_a])
ok, err = run_reasoner(onto)
print("  Pellet passed:", ok)
if not ok:
    print("  error:", err)
else:
    print("  inferred types:", [c.name for c in getattr(star, 'INDIRECT_is_a', [])])

print("\n[SCENARIO] Simple rule without builtin")
onto, star = load_star_tracker()
with onto:
    class SimpleTestState(owlready2.Thing):
        pass
rule_text_simple = "StarTracker(?x) -> SimpleTestState(?x)"
print("  rule:", rule_text_simple)
imp_simple = owlready2.Imp(namespace=onto)
imp_simple.set_as_rule(rule_text_simple, namespaces=[onto])
print("  created rule:", imp_simple)
print("  body:", [str(atom) for atom in imp_simple.body])
print("  head:", [str(atom) for atom in imp_simple.head])
ok, err = run_reasoner(onto)
print("  Pellet passed:", ok)
if not ok:
    print("  error:", err)
else:
    direct, inferred = summarize_individual(star)
    print("  direct types:", direct)
    print("  inferred types:", inferred)
    print("  has SimpleTestState:", 'SimpleTestState' in inferred)

print("\n[SCENARIO] Builtin rule with greaterThan")
onto, star = load_star_tracker()
prop = onto.search_one(iri="*hasTrackingError") or onto.search_one(label="hasTrackingError") or onto.search_one(name="hasTrackingError")
if prop is None:
    raise RuntimeError("hasTrackingError property not found")
star.hasTrackingError = [11.22]
with onto:
    class TestFaultState(owlready2.Thing):
        pass
rule_text_builtin = "StarTracker(?x) ^ hasTrackingError(?x, ?e) ^ greaterThan(?e, 5.0) -> TestFaultState(?x)"
print("  rule:", rule_text_builtin)
imp_builtin = owlready2.Imp(namespace=onto)
imp_builtin.set_as_rule(rule_text_builtin, namespaces=[onto])
print("  created rule:", imp_builtin)
print("  body:", [str(atom) for atom in imp_builtin.body])
print("  head:", [str(atom) for atom in imp_builtin.head])
ok, err = run_reasoner(onto)
print("  Pellet passed:", ok)
if not ok:
    print("  error:", err)
else:
    direct, inferred = summarize_individual(star)
    print("  direct types:", direct)
    print("  inferred types:", inferred)
    print("  has TestFaultState:", 'TestFaultState' in inferred)

print("\n[SCENARIO] Completed")
