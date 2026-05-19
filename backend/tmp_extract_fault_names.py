from pathlib import Path
import re
text = Path('backend/satellite_semantic_runtime.owl').read_text(encoding='utf-8')
class_names = re.findall(r'<owl:Class rdf:about="http://example.org/satellite#([A-Za-z0-9_]+Fault)"', text)
ind_names = re.findall(r'<owl:NamedIndividual rdf:about="http://example.org/satellite#([A-Za-z0-9_]+Fault_[0-9]+)"', text)
print('# classes', len(class_names))
for name in sorted(set(class_names)):
    print(name)
print('---')
print('# individuals', len(ind_names))
for name in sorted(set(ind_names)):
    print(name)
