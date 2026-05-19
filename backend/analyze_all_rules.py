import re
from pathlib import Path

owl_file = Path(__file__).parent / 'satellite_semantic_runtime.owl'
text = owl_file.read_text(encoding='utf-8')

# Extract all SWRL rules
rule_pattern = re.compile(r'<swrl:Imp>(.*?)</swrl:Imp>', re.DOTALL)
rules = rule_pattern.findall(text)

print(f"TOTAL SWRL RULES: {len(rules)}\n")
print("=" * 100)

for idx, rule in enumerate(rules, 1):
    # Extract body
    body_match = re.search(r'<swrl:body>(.*?)</swrl:body>', rule, re.DOTALL)
    body_text = body_match.group(1) if body_match else ""
    
    # Extract head
    head_match = re.search(r'<swrl:head>(.*?)</swrl:head>', rule, re.DOTALL)
    head_text = head_match.group(1) if head_match else ""
    
    # Check for legacy patterns
    has_fault_001 = 'Fault_001' in rule or 'Failure_001' in rule
    has_propagates = 'propagatesTo' in rule
    has_hasfault = 'hasFault' in rule
    
    # Extract class atoms in head
    head_classes = re.findall(r'swrl:classPredicate rdf:resource="#([^"]+)"', head_text)
    
    # Extract component class in body
    body_classes = re.findall(r'swrl:classPredicate rdf:resource="#([^"]+)"', body_text)
    
    # Check for telemetry properties
    telemetry_props = re.findall(r'swrl:propertyPredicate rdf:resource="#([^"]+)"', body_text)
    
    # Check for comparisons
    has_comparison = 'swrlb:' in rule
    
    print(f"\nRULE {idx}:")
    print(f"  Legacy patterns: Fault_001={has_fault_001}, propagatesTo={has_propagates}, hasFault={has_hasfault}")
    print(f"  Body classes: {body_classes}")
    print(f"  Telemetry properties: {telemetry_props[:3]}")  # First 3
    print(f"  Head inferred classes: {head_classes}")
    print(f"  Has comparison: {has_comparison}")
    print(f"  Rule length: {len(rule)} chars")
    
    # Print first 200 chars of rule for context
    rule_preview = re.sub(r'\s+', ' ', rule)[:200]
    print(f"  Preview: {rule_preview}...")

print("\n" + "=" * 100)
print(f"\nSUMMARY ANALYSIS:")

# Count legacy patterns
legacy_count = sum(1 for rule in rules if 'Fault_001' in rule or 'Failure_001' in rule)
propagates_count = sum(1 for rule in rules if 'propagatesTo' in rule)
hasfault_count = sum(1 for rule in rules if 'hasFault' in rule)
action_count = sum(1 for rule in rules if 'triggersAction' in rule)
telemetry_count = sum(1 for rule in rules if any(prop in rule for prop in 
    ['hasTemperature', 'hasVibration', 'hasTrackingError', 'hasChargeLevel']))

print(f"Rules with legacy Fault_001/Failure_001: {legacy_count}")
print(f"Rules with propagatesTo: {propagates_count}")
print(f"Rules with hasFault: {hasfault_count}")
print(f"Rules inferring triggersAction: {action_count}")
print(f"Rules checking telemetry: {telemetry_count}")

print("\nRules need validation and potential rewriting.")
