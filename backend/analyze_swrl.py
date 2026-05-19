#!/usr/bin/env python3
"""
Analyze SWRL Rules Architecture

Examine all 88 SWRL rules and report their current semantic structure.
Identify rules that need alignment with component-centric architecture.
"""

from owlready2 import *
import re

ontology_path = r'c:\Users\K NAGAMANGESWARA RAO\OneDrive\Desktop\onyx-aether-core-main\backend\satellite_semantic_runtime.owl'

print("=" * 80)
print("SWRL RULES ARCHITECTURE ANALYSIS")
print("=" * 80)

# Read raw RDF/XML to analyze rule structure
with open(ontology_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all swrl:Imp (SWRL rules)
rule_pattern = r'<swrl:Imp>(.*?)</swrl:Imp>'
rules = re.findall(rule_pattern, content, re.DOTALL)

print(f"\n[1] Total SWRL Rules Found: {len(rules)}")

# Categorize rules by their structure
component_centric = 0
class_based = 0
property_based = 0
action_based = 0
fault_object_based = 0
unknown = 0

rule_details = []

for i, rule in enumerate(rules):
    rule_info = {
        'number': i + 1,
        'type': 'unknown',
        'has_component': False,
        'has_telemetry': False,
        'infers_class': False,
        'infers_action': False,
        'uses_fault_objects': False,
        'head_atoms': []
    }
    
    # Check for component variables
    if 'urn:swrl#x' in rule or 'swrl:argument1 rdf:resource="urn:swrl#x' in rule:
        rule_info['has_component'] = True
    
    # Check for telemetry properties
    telemetry_props = ['hasTemperature', 'hasChargeLevel', 'hasVibration', 'hasTrackingError', 
                      'hasAngularRate', 'hasGain', 'hasBitErrorRate', 'hasVoltage', 
                      'hasCurrentDraw', 'hasDischargeRate', 'hasChargeRate', 'hasPressure',
                      'hasSignalStrength', 'hasAttitudeError', 'hasPointingError']
    
    for prop in telemetry_props:
        if prop in rule:
            rule_info['has_telemetry'] = True
            break
    
    # Check what the rule head infers
    head_match = re.search(r'<swrl:head>(.*?)</swrl:head>', rule, re.DOTALL)
    if head_match:
        head_content = head_match.group(1)
        
        # Check if it's a class atom (ClassAtom) - good for semantic state inference
        if 'swrl:ClassAtom' in head_content:
            rule_info['infers_class'] = True
            rule_info['type'] = 'class_inference'
            # Extract which class
            class_match = re.search(r'swrl:classPredicate rdf:resource="#([^"]+)"', head_content)
            if class_match:
                rule_info['head_atoms'].append(('class', class_match.group(1)))
        
        # Check if it's a property atom - for triggersAction
        if 'swrl:propertyPredicate' in head_content and 'triggersAction' in head_content:
            rule_info['infers_action'] = True
            rule_info['type'] = 'action_inference'
            rule_info['head_atoms'].append(('action', 'triggersAction'))
    
    # Check for fault object usage
    fault_keywords = ['Fault_001', 'propagatesTo', 'hasFault']
    for keyword in fault_keywords:
        if keyword in rule:
            rule_info['uses_fault_objects'] = True
            break
    
    # Categorize
    if rule_info['has_component'] and rule_info['has_telemetry'] and rule_info['infers_class']:
        component_centric += 1
        rule_info['category'] = 'CORRECT: Component-Centric'
    elif rule_info['infers_action']:
        action_based += 1
        rule_info['category'] = 'ACTION: Component Triggers'
    elif rule_info['infers_class']:
        class_based += 1
        rule_info['category'] = 'CLASS: Semantic State'
    elif rule_info['uses_fault_objects']:
        fault_object_based += 1
        rule_info['category'] = 'ERROR: Uses Fault Objects'
    else:
        unknown += 1
        rule_info['category'] = 'UNKNOWN: Needs Review'
    
    rule_details.append(rule_info)

# Summary report
print(f"\n[2] Rule Classification Summary")
print(f"    ✓ Component-Centric Rules: {component_centric}")
print(f"    - Class-Based Inference: {class_based}")
print(f"    - Action-Based Inference: {action_based}")
print(f"    ⚠ Fault-Object Based: {fault_object_based}")
print(f"    ? Unknown/Other: {unknown}")

# List rules that need attention
print(f"\n[3] Rule Details (First 20)...")
for rule_info in rule_details[:20]:
    status = "✓" if "CORRECT" in rule_info['category'] else "⚠" if "ERROR" in rule_info['category'] else "→"
    print(f"    {status} Rule {rule_info['number']:3d}: {rule_info['category']}")
    if rule_info['head_atoms']:
        for atom_type, atom_value in rule_info['head_atoms']:
            print(f"       → Infers: {atom_type.upper()} {atom_value}")

print(f"\n[4] Architecture Assessment")
total_rules = len(rules)
aligned_rules = component_centric + action_based
if aligned_rules == total_rules:
    print(f"    ✓ ALL {total_rules} rules are component-centric aligned")
elif fault_object_based > 0:
    print(f"    ⚠ {fault_object_based} rules still use OLD fault-object architecture")
    print(f"    ⚠ {total_rules - aligned_rules - fault_object_based} rules need review")
else:
    print(f"    → {aligned_rules}/{total_rules} rules properly aligned")
    print(f"    → {total_rules - aligned_rules - fault_object_based} rules need review")

print(f"\n[5] Next Steps")
if fault_object_based > 0:
    print(f"    1. REMOVE all fault-object based rules ({fault_object_based} rules)")
    print(f"    2. REBUILD as component-centric semantic rules")
    print(f"    3. ENSURE all rules follow pattern:")
    print(f"       ComponentType(?x) ∧ telemetry(?x, ?v) ∧ comparison(?v, threshold)")
    print(f"       → SemanticStateClass(?x)")
else:
    print(f"    ✓ All rules follow correct architecture")
    print(f"    → Ready for Pellet execution")
    print(f"    → Backend can extract: individual.INDIRECT_is_a")

print(f"\n" + "=" * 80)

