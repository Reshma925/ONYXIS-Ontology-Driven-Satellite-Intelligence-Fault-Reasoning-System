from pathlib import Path
import owlready2
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for i, rule in enumerate(onto.rules()):
    body_has = any(getattr(getattr(atom,'property_predicate',None),'name',None)=='hasFault' for atom in rule.body)
    head_has = any(getattr(getattr(atom,'property_predicate',None),'name',None)=='hasFault' for atom in rule.head)
    if body_has and not head_has:
        print('RULE', i, str(rule))
        for atom in rule.body:
            print('  BODY', type(atom).__name__, getattr(getattr(atom,'property_predicate',None),'name',None) or getattr(getattr(atom,'class_predicate',None),'name',None), atom.arguments)
        for atom in rule.head:
            print('  HEAD', type(atom).__name__, getattr(getattr(atom,'property_predicate',None),'name',None) or getattr(getattr(atom,'class_predicate',None),'name',None), atom.arguments)
        print('---')
