from pathlib import Path
import owlready2

onto = owlready2.get_ontology(str(Path('satellite_semantic_runtime.owl').resolve())).load()
rules = list(onto.rules())
print('TOTAL_RULES', len(rules))
bad = False
for idx, rule in enumerate(rules, start=1):
    if 'hasFault' in str(rule):
        print('RULE', idx, str(rule))
        if 'C:\\Users' in str(rule):
            print('BAD', idx)
            bad = True
            break
print('BAD_FOUND', bad)
