from pathlib import Path
import owlready2
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
print('rules with affectsComponent:')
for i, rule in enumerate(onto.rules()):
    if any(getattr(getattr(atom,'property_predicate',None),'name',None)=='affectsComponent' for atom in list(rule.head)+list(rule.body)):
        print('RULE', i, str(rule))
        for atom in rule.body:
            print('  BODY', type(atom).__name__, getattr(getattr(atom,'property_predicate',None),'name',None) or getattr(getattr(atom,'class_predicate',None),'name',None), atom.arguments)
        for atom in rule.head:
            print('  HEAD', type(atom).__name__, getattr(getattr(atom,'property_predicate',None),'name',None) or getattr(getattr(atom,'class_predicate',None),'name',None), atom.arguments)
        print('---')
