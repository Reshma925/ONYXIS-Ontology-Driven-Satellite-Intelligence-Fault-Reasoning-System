from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
with onto:
    class FaultState(owlready2.Thing):
        pass
    class FooFaultState(onto.FaultState):
        pass
rule = next(rule for rule in onto.rules() if any(getattr(getattr(atom,'property_predicate',None),'name',None)=='hasFault' for atom in rule.head))
text = cst.build_fault_state_rule_text(rule, 'FooFaultState')
print('rule text', text)
for name in ['Imp()', 'Imp(namespace=onto)', 'Imp(name=0, namespace=onto)', 'Imp(name=0, namespace=onto.world)']:
    try:
        print('trying', name)
        if name == 'Imp()':
            imp = owlready2.Imp()
        elif name == 'Imp(namespace=onto)':
            imp = owlready2.Imp(namespace=onto)
        elif name == 'Imp(name=0, namespace=onto)':
            imp = owlready2.Imp(name=0, namespace=onto)
        elif name == 'Imp(name=0, namespace=onto.world)':
            imp = owlready2.Imp(name=0, namespace=onto.world)
        imp.set_as_rule(text, namespaces=[onto])
        print('success', name)
    except Exception as e:
        print('fail', name, e)
