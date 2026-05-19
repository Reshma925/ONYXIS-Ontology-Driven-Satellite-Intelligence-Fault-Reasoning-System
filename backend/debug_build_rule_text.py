from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for rule in onto.rules():
    if getattr(getattr(rule.head[0], 'property_predicate', None), 'name', None) == 'hasFault':
        print('orig rule:', str(rule))
        print('rule text:', cst.build_fault_state_rule_text(rule, 'FooFaultState'))
        break
