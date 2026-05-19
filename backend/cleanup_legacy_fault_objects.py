from pathlib import Path
import re

path = Path(__file__).parent / 'satellite_semantic_runtime.owl'
backup = path.with_suffix('.owl.bak')

text = path.read_text(encoding='utf-8')
if not backup.exists():
    backup.write_text(text, encoding='utf-8')

pattern = re.compile(r'<owl:NamedIndividual rdf:about="#(?:[^"<>]*?(?:Fault_001|Failure_001))">.*?</owl:NamedIndividual>\s*', re.S)
text, n_removed = pattern.subn('', text)
print(f'Removed {n_removed} old runtime fault/failure individuals')

rule_pattern = re.compile(r'<swrl:Imp>.*?<swrl:propertyPredicate rdf:resource="#propagatesTo".*?</swrl:Imp>\s*', re.S)
text, n_rules = rule_pattern.subn('', text)
print(f'Removed {n_rules} propagatesTo SWRL rule blocks')

text, n_refs = re.subn(r'<[^>]*propagatesTo[^>]*>.*?</[^>]*>\s*', '', text, flags=re.S)
print(f'Removed {n_refs} stray propagatesTo tags')

for token in ['Fault_001', 'Failure_001', 'propagatesTo']:
    print(f'{token}: {text.count(token)} occurrences remain')

path.write_text(text, encoding='utf-8')
print('Cleanup complete')
