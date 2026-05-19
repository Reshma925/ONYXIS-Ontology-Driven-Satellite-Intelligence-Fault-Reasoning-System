import re
from pathlib import Path

owl_file = Path(__file__).parent / 'satellite_semantic_runtime.owl'
text = owl_file.read_text(encoding='utf-8')

# Find all SWRL rules
rule_pattern = re.compile(r'<swrl:Imp>(.*?)</swrl:Imp>', re.DOTALL)
rules = rule_pattern.findall(text)

print("=" * 120)
print("EXAMINING RULES 55, 56, 57 - THE hasFault RULES")
print("=" * 120)

for idx in [55, 56, 57]:
    if idx <= len(rules):
        rule = rules[idx - 1]
        
        # Extract body and head more clearly
        body_match = re.search(r'<swrl:body>(.*?)</swrl:body>', rule, re.DOTALL)
        head_match = re.search(r'<swrl:head>(.*?)</swrl:head>', rule, re.DOTALL)
        
        body_text = body_match.group(1) if body_match else ""
        head_text = head_match.group(1) if head_match else ""
        
        # Extract class atoms
        body_classes = re.findall(r'swrl:classPredicate rdf:resource="#([^"]+)"', body_text)
        head_classes = re.findall(r'swrl:classPredicate rdf:resource="#([^"]+)"', head_text)
        
        # Extract properties
        body_props = re.findall(r'swrl:propertyPredicate rdf:resource="#([^"]+)"', body_text)
        head_props = re.findall(r'swrl:propertyPredicate rdf:resource="#([^"]+)"', head_text)
        
        # Extract variables
        body_vars = re.findall(r'rdf:resource="urn:swrl#([^"]+)"', body_text)
        head_vars = re.findall(r'rdf:resource="urn:swrl#([^"]+)"', head_text)
        
        print(f"\n{'='*120}")
        print(f"RULE {idx}:")
        print(f"{'='*120}")
        print(f"Body classes: {body_classes}")
        print(f"Body properties: {body_props}")
        print(f"Body variables: {set(body_vars)}")
        print(f"Head classes: {head_classes}")
        print(f"Head properties: {head_props}")
        print(f"Head variables: {set(head_vars)}")
        
        # Find hasFault usage
        if 'hasFault' in body_text:
            print("\n⚠ hasFault appears in BODY:")
            start = body_text.find('hasFault') - 50
            end = body_text.find('hasFault') + 100
            print(body_text[max(0, start):end])
        
        if 'hasFault' in head_text:
            print("\n⚠ hasFault appears in HEAD:")
            start = head_text.find('hasFault') - 50
            end = head_text.find('hasFault') + 100
            print(head_text[max(0, start):end])
        
        print(f"\nFull body ({len(body_text)} chars):")
        print(body_text[:500])
        print("\n...")
        print(body_text[-200:])
        
        print(f"\nFull head ({len(head_text)} chars):")
        print(head_text[:300])
        if len(head_text) > 300:
            print("\n...")
            print(head_text[-200:])

print(f"\n{'='*120}")
print("ANALYSIS COMPLETE")
print(f"{'='*120}")
