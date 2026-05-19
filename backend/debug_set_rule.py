from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
with onto:
    if not hasattr(onto, 'FaultState'):
        class FaultState(owlready2.Thing):
            pass
    if not hasattr(onto, 'FooFaultState'):
        class FooFaultState(onto.FaultState if hasattr(onto,'FaultState') else owlready2.Thing):
            pass
rule = next(rule for rule in onto.rules() if any(getattr(getattr(atom,'property_predicate',None),'name',None)=='hasFault' for atom in rule.head))
text = cst.build_fault_state_rule_text(rule, 'FooFaultState')
print('rule text:', text)
try:
    imp = owlready2.Imp()
    imp.set_as_rule(text, namespaces=[onto])
    print('added rule')
except Exception as exc:
    print('exc', exc)
