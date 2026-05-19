from pathlib import Path
import owlready2
import importlib.util

spec = importlib.util.spec_from_file_location('csr', Path('create_semantic_runtime.py').resolve())
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
onto = owlready2.get_ontology(str(Path('satellite_semantic_runtime.owl').resolve())).load()
for idx, rule in enumerate(list(onto.rules()), start=1):
    if idx != 74:
        continue
    print('RULE', idx, str(rule))
    for atom in list(rule.body) + list(rule.head):
        print('ATOM', type(atom).__name__)
        print('  class_predicate', getattr(getattr(atom, 'class_predicate', None), 'name', None))
        print('  property_predicate', getattr(getattr(atom, 'property_predicate', None), 'name', None))
        print('  arguments', atom.arguments)
        for a in atom.arguments:
            print('    arg repr', repr(a))
            print('    arg type', type(a))
            print('    arg name', getattr(a, 'name', None))
            print('    arg iri', getattr(a, 'iri', None))
            print('    arg class', a.__class__)
    print('REBUILT', mod.build_fault_state_rule_text(rule))
    break
