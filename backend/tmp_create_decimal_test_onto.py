from pathlib import Path

src = Path(__file__).parent / 'satellite_full (1).owl'
dst = Path(__file__).parent / 'satellite_full_decimal_test.owl'
text = src.read_text(encoding='utf-8')
old = '<owl:DatatypeProperty rdf:about="http://example.org/satellite#hasTrackingError">\n        <rdfs:domain rdf:resource="http://example.org/satellite#StarTracker"/>\n        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#double"/>'
new = '<owl:DatatypeProperty rdf:about="http://example.org/satellite#hasTrackingError">\n        <rdfs:domain rdf:resource="http://example.org/satellite#StarTracker"/>\n        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#decimal"/>'
if old not in text:
    raise SystemExit('Original hasTrackingError declaration not found')
text = text.replace(old, new, 1)
dst.write_text(text, encoding='utf-8')
print(f'Created {dst}')
