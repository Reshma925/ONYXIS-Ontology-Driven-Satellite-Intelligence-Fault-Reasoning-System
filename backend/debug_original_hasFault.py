from pathlib import Path
import owlready2
p = Path('backend/satellite_full (1).owl').resolve()
onto = owlready2.World().get_ontology(str(p)).load()
for rule in onto.rules():
    if 'hasFault' in str(rule):
        print('RULE STR:', str(rule))
        print('HEAD', [type(a).__name__ + ':' + str(a) for a in rule.head])
        print('BODY', [type(a).__name__ + ':' + str(a) for a in rule.body])
        break
