from pathlib import Path
import owlready2
import create_semantic_runtime as cst
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
count=0
for rule in onto.rules():
    if any(getattr(getattr(atom,'property_predicate',None),'name',None)=='hasFault' for atom in rule.head):
        count+=1
        try:
            print('RULE', str(rule))
            print('TEXT', cst.build_fault_state_rule_text(rule, 'FooFaultState'))
        except Exception as e:
            print('ERR', e)
print('count', count)
