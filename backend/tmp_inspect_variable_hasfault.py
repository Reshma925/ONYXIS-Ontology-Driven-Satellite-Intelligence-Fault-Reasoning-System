from pathlib import Path
import re
text = Path('backend/satellite_semantic_runtime.owl').read_text(encoding='utf-8')
occ = 0
for m in re.finditer(r'<rdf:Description>\s*<rdf:type rdf:resource="http://www.w3.org/2003/11/swrl#IndividualPropertyAtom".*?<swrl:propertyPredicate rdf:resource="http://example.org/satellite#hasFault".*?</rdf:Description>', text, flags=re.S):
    occ += 1
    atom = m.group(0)
    if 'Fault_001' not in atom and 'Fault' in atom:
        start = max(0, m.start()-300)
        end = min(len(text), m.end()+300)
        print('--- occ', occ, '---')
        print(text[start:end])
        print()
