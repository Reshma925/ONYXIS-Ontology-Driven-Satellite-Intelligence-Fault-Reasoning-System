from pathlib import Path
text = Path('backend/satellite_full (1).owl').read_text(encoding='utf-8')
idx = text.find('hasFault')
print('first hasFault pos', idx)
print(text[idx-300:idx+600])
