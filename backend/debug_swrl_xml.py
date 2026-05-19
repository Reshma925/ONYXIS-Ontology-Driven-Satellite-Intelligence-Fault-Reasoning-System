from pathlib import Path
text = Path('backend/satellite_full (1).owl').read_text(encoding='utf-8')
start = 0
for i in range(5):
    idx = text.find('swrl:IndividualPropertyAtom', start)
    if idx == -1:
        break
    print('occurrence', i, 'pos', idx)
    print(text[idx-200:idx+800])
    print('-'*80)
    start = idx + 1
