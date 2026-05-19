from pathlib import Path
import re
text = Path('backend/satellite_semantic_runtime.owl').read_text(encoding='utf-8')
for i, m in enumerate(re.finditer(r'<swrl:propertyPredicate rdf:resource="http://example.org/satellite#hasFault"', text)):
    start = max(0, m.start()-200)
    end = min(len(text), m.end()+200)
    snippet = text[start:end]
    print('--- occurrence', i+1, '---')
    print(snippet.replace('\n', '\n'))
    if i>=20:
        break
print('TOTAL', i+1)
