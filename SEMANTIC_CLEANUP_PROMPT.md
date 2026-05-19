# CRITICAL FINAL SEMANTIC CLEANUP REQUIRED

## STATUS SUMMARY

✅ **WHAT IS ALREADY CORRECT**
- IRIs are valid and stable
- Namespaces are properly configured
- SWRL rules load and execute
- Pellet reasoning engine is functional
- FaultState class hierarchy exists correctly
- Class-based semantic inference is active
- Components receive inferred FaultState classes

❌ **WHAT STILL NEEDS FIXING**
- Old FAULT-INDIVIDUAL architecture still present
- hasFault property model obsolete
- triggersAction still points to Fault entities, not Components
- Legacy fault individuals (BatteryFault_001, etc.) create semantic pollution
- Action inference rules still target Fault classes instead of Components
- Semantic model is SPLIT between class-centric and object-centric

---

## THE CORE PROBLEM

### Current Architecture (WRONG)
```
Battery_01 → hasFault → BatteryFault_001
BatteryFault_001 → triggersAction → PowerSaveMode
```

### Migrated Architecture (CORRECT BUT INCOMPLETE)
```
Battery_01 rdf:type BatteryFaultState (inferred)
Battery_01 → triggersAction → PowerSaveMode
```

### Why This Breaks Synchronization
Pellet infers FaultState classes onto components, but:
- Action semantics still reference old Fault individuals
- hasFault chains create semantic duplication
- UI can't reconcile class-based faults with object-based actions
- Reasoning engine must execute two contradictory models

---

## REQUIRED FINAL ARCHITECTURE

```
TELEMETRY INPUT
    ↓
COMPONENT DATATYPE ASSERTIONS
(e.g., Battery_01 hasTemperature 95.5)
    ↓
PELLET CLASS INFERENCE
(Battery_01 rdf:type BatteryFaultState)
    ↓
ACTION INFERENCE
(Battery_01 triggersAction PowerSaveMode)
    ↓
BACKEND EXTRACTION
(Query inferred classes and actions directly)
    ↓
UI SYNCHRONIZATION
(Single semantic source of truth)
```

---

## REQUIRED CHANGES (IN ORDER)

### CHANGE 1: REFACTOR triggersAction PROPERTY

**CURRENT (WRONG)**
```xml
<owl:ObjectProperty rdf:about="#triggersAction">
  <rdfs:domain rdf:resource="#Fault"/>
  <rdfs:range rdf:resource="#Action"/>
</owl:ObjectProperty>
```

**NEW (CORRECT)**
```xml
<owl:ObjectProperty rdf:about="#triggersAction">
  <rdfs:domain rdf:resource="#Component"/>
  <rdfs:range rdf:resource="#Action"/>
</owl:ObjectProperty>
```

---

### CHANGE 2: DELETE OLD FAULT INDIVIDUALS

Remove ALL instances matching pattern:
```xml
<owl:NamedIndividual rdf:about="#[*]Fault_[0-9]+">
```

Examples to delete:
- BatteryFault_001
- PCDUFault_001
- BusFault_001
- OverheatFault_001
- StarTrackerFault_001
- (and all others following this pattern)

**SAFE TO DELETE** because:
- Components now get inferred FaultState classes
- No SWRL rules depend on these individuals
- No other parts of ontology reference them

---

### CHANGE 3: REMOVE hasFault PROPERTY

Remove the entire property definition:
```xml
<owl:ObjectProperty rdf:about="#hasFault">
  ...
</owl:ObjectProperty>
```

And ALL its usage assertions.

**RATIONALE**
- Components now type to FaultState classes directly
- No need for object-based fault intermediaries
- hasFault chains are semantic duplication

---

### CHANGE 4: REFACTOR ACTION RULES

**OLD RULE PATTERN (WRONG)**
```xml
<rdf:Description rdf:about="#rule_BatteryFaultAction">
  <rdf:type rdf:resource="http://www.w3.org/2003/11/swrl#Rule"/>
  <swrl:body rdf:resource="#battery_fault_check"/>
  <swrl:head>
    <swrl:Atom>
      <swrl:propertyPredicate rdf:resource="#triggersAction"/>
      <swrl:argument1 rdf:resource="#BatteryFault"/>
      <swrl:argument2 rdf:resource="#PowerSaveMode"/>
    </swrl:Atom>
  </swrl:head>
</rdf:Description>
```

**NEW RULE PATTERN (CORRECT)**
```xml
<rdf:Description rdf:about="#rule_BatteryFaultAction">
  <rdf:type rdf:resource="http://www.w3.org/2003/11/swrl#Rule"/>
  <swrl:body>
    <swrl:Atom>
      <swrl:classPredicate rdf:resource="#BatteryFaultState"/>
      <swrl:argument1 rdf:variable="component"/>
    </swrl:Atom>
  </swrl:body>
  <swrl:head>
    <swrl:Atom>
      <swrl:propertyPredicate rdf:resource="#triggersAction"/>
      <swrl:argument1 rdf:variable="component"/>
      <swrl:argument2 rdf:resource="#PowerSaveMode"/>
    </swrl:Atom>
  </swrl:head>
</rdf:Description>
```

### Rules to Add/Refactor

**For BatteryFaultState**
```
OverheatFaultState(?component) 
→ triggersAction(?component, SafeMode)
```

**For StarTrackerFaultState**
```
StarTrackerFaultState(?component) 
→ triggersAction(?component, RecalibrationMode)
```

**For PCDUFaultState** (if exists)
```
PCDUFaultState(?component) 
→ triggersAction(?component, PowerCycleMode)
```

---

### CHANGE 5: VERIFY COMPONENT-CENTRIC CLASSES

Ensure these classes exist with correct semantics:
```xml
<owl:Class rdf:about="#FaultState">
  <rdfs:comment>Parent class for all fault state inferences</rdfs:comment>
</owl:Class>

<owl:Class rdf:about="#BatteryFaultState">
  <rdfs:subClassOf rdf:resource="#FaultState"/>
</owl:Class>

<owl:Class rdf:about="#OverheatFaultState">
  <rdfs:subClassOf rdf:resource="#FaultState"/>
</owl:Class>

<owl:Class rdf:about="#StarTrackerFaultState">
  <rdfs:subClassOf rdf:resource="#FaultState"/>
</owl:Class>
```

---

## EXPECTED POST-CLEANUP ONTOLOGY

### Component Assertions
```xml
<owl:NamedIndividual rdf:about="#Battery_01">
  <rdf:type rdf:resource="#Battery"/>
  <rdf:type rdf:resource="#Component"/>
  <hasTemperature rdf:datatype="...xsd:float">95.5</hasTemperature>
  <hasCurrentDraw rdf:datatype="...xsd:float">12.3</hasCurrentDraw>
</owl:NamedIndividual>
```

### Post-Pellet Inferences
```
Battery_01 rdf:type BatteryFaultState (INFERRED)
Battery_01 triggersAction PowerSaveMode (INFERRED)
```

### Pellet Query Result
```
SELECT ?component ?action WHERE {
  ?component rdf:type FaultState .
  ?component triggersAction ?action .
}

Results:
Battery_01 | PowerSaveMode
STR_01 | RecalibrationMode
OBC_01 | SafeMode
```

---

## VALIDATION CHECKLIST

After cleanup, verify:

- [ ] No individuals matching pattern `*Fault_[0-9]+` exist
- [ ] hasFault property definition removed
- [ ] hasFault assertions removed completely
- [ ] triggersAction domain is Component (not Fault)
- [ ] triggersAction range is Action
- [ ] All action SWRL rules target FaultState classes, not Fault individuals
- [ ] All SWRL rules use component variables correctly
- [ ] Pellet loads ontology without errors
- [ ] Pellet reasoning completes successfully
- [ ] Owlready2 can parse ontology without warnings
- [ ] All IRIs remain valid (no broken references)
- [ ] All namespaces remain stable
- [ ] RDF/XML structure remains valid
- [ ] No malformed SWRL blocks
- [ ] No filesystem paths in RDF

---

## IMPLEMENTATION CONSTRAINTS

### DO
- ✅ Remove old fault individuals systematically
- ✅ Update property domains/ranges in OWL definitions
- ✅ Refactor SWRL rules to use component variables
- ✅ Keep all FaultState classes
- ✅ Keep all Component individuals
- ✅ Keep all Action individuals
- ✅ Keep all datatype assertions
- ✅ Maintain namespace prefixes
- ✅ Preserve IRI structure

### DO NOT
- ❌ Hardcode fault logic in Python
- ❌ Hardcode actions in backend
- ❌ Manually inject inferred faults
- ❌ Create reasoning outside ontology
- ❌ Introduce filesystem paths
- ❌ Break RDF/XML validity
- ❌ Modify namespace URIs
- ❌ Change class hierarchy
- ❌ Malform SWRL XML

---

## FINAL GOAL

A **PURE SEMANTIC DIGITAL TWIN ARCHITECTURE**:

```
Telemetry Data
    ↓
Ontology Assertions
    ↓
Pellet Reasoning Engine
    ↓
Inferred FaultState Classes on Components
    ↓
Inferred Component Actions
    ↓
Backend extracts semantic state directly
    ↓
UI synchronization from single source of truth

NO hardcoded fault logic
NO fault individual chains
NO split semantic models
NO Python-level reasoning
```

---

## SUCCESS CRITERIA

✅ Pellet executes without errors
✅ All FaultState inferences work correctly
✅ All action inferences work correctly
✅ Backend can query: `?component rdf:type FaultState . ?component triggersAction ?action`
✅ UI receives single, consistent fault+action model
✅ No more synchronization conflicts
✅ Ontology is semantically pure and unified
✅ All old fault architecture completely removed

