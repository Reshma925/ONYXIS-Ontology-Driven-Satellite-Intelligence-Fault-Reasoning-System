#!/usr/bin/env python3
import owlready2
from owlready2 import World, Thing, DataProperty, ObjectProperty, Imp, sync_reasoner_pellet
from rdflib import URIRef


def build_mini_ontology():
    world = World()
    onto = world.get_ontology("http://example.org/minimal-proof.owl")
    with onto:
        class Battery(Thing):
            pass

        class BatteryFault(Thing):
            pass

        class hasVoltage(DataProperty):
            pass

        class hasFault(ObjectProperty):
            pass

    battery = onto.Battery("Battery_01")
    onto.BatteryFault("BatteryFault_001")
    return onto, battery


def run_reasoner(onto):
    try:
        with onto:
            sync_reasoner_pellet(
                infer_property_values=True,
                infer_data_property_values=True,
                debug=0,
            )
        return True, None
    except Exception as e:
        return False, str(e)


def dump_hasFault(onto, battery):
    print("  Battery_01.hasFault =", list(getattr(battery, "hasFault", [])))
    print("  Battery_01.INDIRECT_hasFault =", list(getattr(battery, "INDIRECT_hasFault", [])))
    graph = onto.world.as_rdflib_graph()
    has_fault_uri = URIRef(str(onto.hasFault.iri))
    print("  RDF hasFault triples:")
    found = False
    for subj, pred, obj in graph.triples((None, has_fault_uri, None)):
        found = True
        print("    ", subj, pred, obj)
    if not found:
        print("    (none)")


def add_rule(onto, rule_text):
    with onto:
        imp = Imp(namespace=onto)
        imp.set_as_rule(rule_text, namespaces=[onto])
    print("  rule:", rule_text)
    print("  body:", [str(atom) for atom in imp.body])
    print("  head:", [str(atom) for atom in imp.head])


def main():
    print("[MINIMAL PROOF] Case 0: direct SWRL class inference")
    onto, battery = build_mini_ontology()
    add_rule(onto, "Battery(?c) -> BatteryFault(?c)")
    ok, err = run_reasoner(onto)
    print("  Pellet reasoner passed:", ok)
    if err:
        print("  error:", err)
    print("  Battery_01 types after reasoning:", [c.name for c in getattr(battery, 'INDIRECT_is_a', [])])

    print("\n[MINIMAL PROOF] Case 1: direct SWRL object-property assertion")
    onto, battery = build_mini_ontology()
    add_rule(onto, "Battery(?c) -> hasFault(?c, BatteryFault_001)")
    ok, err = run_reasoner(onto)
    print("  Pellet reasoner passed:", ok)
    if err:
        print("  error:", err)
    dump_hasFault(onto, battery)

    print("\n[MINIMAL PROOF] Case 2: value-triggered SWRL builtin")
    onto, battery = build_mini_ontology()
    battery.hasVoltage = [0.0]
    add_rule(onto, "Battery(?c) ^ hasVoltage(?c, ?v) ^ lessThan(?v, 1.0) -> hasFault(?c, BatteryFault_001)")
    ok, err = run_reasoner(onto)
    print("  Pellet reasoner passed:", ok)
    if err:
        print("  error:", err)
    dump_hasFault(onto, battery)


if __name__ == "__main__":
    main()
