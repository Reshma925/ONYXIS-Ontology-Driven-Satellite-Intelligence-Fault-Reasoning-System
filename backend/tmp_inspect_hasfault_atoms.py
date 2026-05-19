from pathlib import Path
import re
text = Path('backend/satellite_semantic_runtime.owl').read_text(encoding='utf-8')
pattern = r'<swrl:IndividualPropertyAtom>(.*?)</swrl:IndividualPropertyAtom>'
for m in re.finditer(pattern, text, flags=re.S):
    atom = m.group(1)
    if 'hasFault' in atom:
        start = m.start()
        prefix = text.rfind('<swrl:Imp', 0, start)
        suffix = text.find('</swrl:Imp>', m.end())
        block = text[prefix:suffix+len('</swrl:Imp>')] if prefix != -1 and suffix != -1 else text[start:m.end()]
        print('--- ATOM ---')
        print(atom)
        print('--- CONTEXT ---')
        print(block[:600])
        print()
