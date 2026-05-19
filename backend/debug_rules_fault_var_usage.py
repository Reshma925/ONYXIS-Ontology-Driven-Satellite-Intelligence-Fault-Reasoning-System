from pathlib import Path
import owlready2
from collections import defaultdict
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for i, rule in enumerate(onto.rules()):
    mappings = []
    for atom in rule.body:
        if getattr(getattr(atom,'property_predicate',None),'name',None) == 'hasFault':
            comp, fault = atom.arguments
            if isinstance(fault, owlready2.Variable):
                mappings.append((comp.name, fault.name))
    if mappings:
        used = []
        for atom in rule.body + rule.head:
            args = atom.arguments
            for comp_var, fault_var in mappings:
                if any(getattr(arg,'name',None)==fault_var for arg in args):
                    used.append((type(atom).__name__, getattr(getattr(atom,'property_predicate',None),'name',None) or getattr(getattr(atom,'class_predicate',None),'name',None), args))
        if used:
            print('RULE', i, str(rule))
            print('MAPPINGS', mappings)
            for item in used:
                print(' ', item)
            print('---')
