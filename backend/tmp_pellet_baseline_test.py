#!/usr/bin/env python3
from pathlib import Path
import owlready2

ONTOLOGY = Path(__file__).parent / "satellite_full (1).owl"
print("[BASELINE] Loading ontology:", ONTOLOGY)
onto = owlready2.get_ontology(str(ONTOLOGY)).load()
print("[BASELINE] Ontology base IRI:", onto.base_iri)
print("[BASELINE] Classes:", len(list(onto.classes())))
print("[BASELINE] Individuals:", len(list(onto.individuals())))
try:
    with onto:
        owlready2.sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=0)
    print("[BASELINE] Pellet reasoning completed successfully")
except Exception as e:
    print("[BASELINE ERROR] Pellet reasoning failed:", e)
    raise
