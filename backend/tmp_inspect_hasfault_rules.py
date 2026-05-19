from pathlib import Path
import re
text = Path('backend/satellite_semantic_runtime.owl').read_text(encoding='utf-8')
# split SWRL implications
imps = re.findall(r'<swrl:Imp.*?<swrl:body>(.*?)</swrl:body>.*?<swrl:head>(.*?)</swrl:head>.*?</swrl:Imp>', text, flags=re.S)
for idx, (body, head) in enumerate(imps, start=1):
    body_has = 'hasFault' in body
    head_has = 'hasFault' in head
    if body_has or head_has:
        print('RULE', idx, 'body_has', body_has, 'head_has', head_has)
        if body_has:
            for m in re.finditer(r'<swrl:IndividualPropertyAtom>(.*?)</swrl:IndividualPropertyAtom>', body, flags=re.S):
                atom = m.group(1)
                if 'hasFault' in atom:
                    print('  BODY ATOM:', repr(atom[:200]))
        if head_has:
            for m in re.finditer(r'<swrl:IndividualPropertyAtom>(.*?)</swrl:IndividualPropertyAtom>', head, flags=re.S):
                atom = m.group(1)
                if 'hasFault' in atom:
                    print('  HEAD ATOM:', repr(atom[:200]))
        print('---')
print('TOTAL RULES WITH hasFault', sum(1 for body, head in imps if 'hasFault' in body or 'hasFault' in head))
