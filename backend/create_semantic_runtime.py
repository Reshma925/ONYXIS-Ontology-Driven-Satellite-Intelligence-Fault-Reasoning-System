from __future__ import annotations

import re
import shutil
from pathlib import Path
import owlready2
from owlready2 import destroy_entity


def _detect_ontology_iri(ontology_path: Path) -> str:
    text = ontology_path.read_text(encoding="utf-8", errors="ignore")
    ontology_match = re.search(r'<owl:Ontology[^>]*?rdf:about=["\']([^"\']+)["\']', text)
    if ontology_match:
        return ontology_match.group(1)
    base_match = re.search(r'xml:base=["\']([^"\']+)["\']', text)
    if base_match:
        return base_match.group(1)
    return str(ontology_path.resolve())


def _load_ontology_from_file(ontology_path: Path, world: owlready2.World) -> owlready2.Ontology:
    ontology_iri = _detect_ontology_iri(ontology_path)
    ontology = world.get_ontology(ontology_iri)
    with ontology_path.open("rb") as fileobj:
        ontology.load(fileobj=fileobj)
    return ontology

ORIGINAL_ONTOLOGY = Path(__file__).parent / "satellite_full (1).owl"
MASTER_ONTOLOGY = Path(__file__).parent / "satellite_full_MASTER.owl"
RUNTIME_ONTOLOGY = Path(__file__).parent / "satellite_semantic_runtime.owl"

KNOWN_FAULT_STATE_CLASSES = [
    "FaultState",
    "BatteryFaultState",
    "CriticalPowerFailureState",
    "ThermalFaultState",
    "CommunicationFaultState",
    "StarTrackerFaultState",
    "NavigationFaultState",
    "PropulsionFaultState",
]


def normalize_fault_state_class_name(name: str) -> str:
    clean = re.sub(r"_[0-9]+$", "", name)
    clean = re.sub(r"Fault$", "Fault", clean)
    clean = re.sub(r"Failure$", "Failure", clean)
    if clean.endswith("State"):
        return clean
    if clean.endswith("Fault") or clean.endswith("Failure"):
        return f"{clean}State"
    return f"{clean}FaultState"


def arg_to_str(arg: object) -> str:
    if isinstance(arg, owlready2.Variable):
        return f"?{arg.name}"
    if isinstance(arg, str):
        return repr(arg)
    iri = getattr(arg, "iri", None) or (getattr(arg, "get_iri", None) or (lambda: None))()
    name = getattr(arg, "name", None)
    if iri:
        iri = iri.replace("\\", "/")
        if "#" in iri:
            return iri.split("#", 1)[1]
        return iri.rstrip("/").split("/")[-1]
    if name and isinstance(name, str) and "/" not in name and "\\" not in name:
        return name
    return str(arg)


def term_key(arg: object) -> tuple[str, str]:
    if isinstance(arg, owlready2.Variable):
        return "var", arg.name
    return "individual", arg_to_str(arg)


def is_hasFault_atom(atom: object) -> bool:
    return getattr(getattr(atom, "property_predicate", None), "name", None) == "hasFault"


def is_fault_class_name(name: str | None) -> bool:
    if not name:
        return False
    return name.endswith("Fault") or name.endswith("Failure") or name.endswith("FaultState") or name == "Fault"


def is_triggers_action_atom(atom: object) -> bool:
    return getattr(getattr(atom, "property_predicate", None), "name", None) == "triggersAction"


def is_generic_fault_class_atom(atom: object) -> bool:
    return type(atom).__name__ == "ClassAtom" and atom_name(atom) == "Fault"


def collect_rule_variable_names(rule: owlready2.Imp) -> set[str]:
    names: set[str] = set()
    for atom in list(rule.body) + list(rule.head):
        for arg in atom.arguments:
            if isinstance(arg, owlready2.Variable):
                names.add(arg.name)
    return names


def choose_unique_variable_name(rule: owlready2.Imp, base: str = "x") -> str:
    existing = collect_rule_variable_names(rule)
    name = base
    idx = 1
    while name in existing:
        name = f"{base}{idx}"
        idx += 1
    return name


def atom_name(atom: object) -> str | None:
    if type(atom).__name__ == "ClassAtom":
        return arg_to_str(getattr(atom, "class_predicate", None))
    prop = getattr(atom, "property_predicate", None)
    if prop is not None:
        return arg_to_str(prop)
    return None


def is_triggers_action_atom(atom: object) -> bool:
    return getattr(getattr(atom, "property_predicate", None), "name", None) == "triggersAction"


def is_generic_fault_class_atom(atom: object) -> bool:
    return type(atom).__name__ == "ClassAtom" and atom_name(atom) == "Fault"


def atom_to_str(atom: object, var_subst: dict[str, str] | None = None, const_subst: dict[tuple[str, str], str] | None = None) -> str:
    def format_arg(arg: object) -> str:
        if isinstance(arg, owlready2.Variable):
            name = arg.name
            if var_subst and name in var_subst:
                return f"?{var_subst[name]}"
            return f"?{name}"
        key = term_key(arg)
        if const_subst and key in const_subst:
            return f"?{const_subst[key]}"
        return arg_to_str(arg)

    atom_type = type(atom).__name__
    args = ", ".join(format_arg(a) for a in atom.arguments)
    if atom_type == "ClassAtom":
        cls = getattr(atom, "class_predicate", None)
        cls_name = arg_to_str(cls)
        return f"{cls_name}({args})"
    if atom_type in {"IndividualPropertyAtom", "DatavaluedPropertyAtom"}:
        prop = getattr(atom, "property_predicate", None)
        prop_name = arg_to_str(prop)
        return f"{prop_name}({args})"
    if atom_type == "BuiltinAtom":
        builtin_name = "builtin"
        try:
            builtin = atom.builtin
            if builtin is not None:
                builtin_name = getattr(builtin, "name", None) or str(builtin)
        except Exception:
            pass
        return f"{builtin_name}({args})"
    return str(atom)


def find_fault_state_class_for_term(rule: owlready2.Imp, term: tuple[str, str]) -> str:
    for atom in rule.body:
        if type(atom).__name__ != "ClassAtom":
            continue
        arg = atom.arguments[0]
        if term_key(arg) != term:
            continue
        class_name = atom_name(atom)
        if is_fault_class_name(class_name):
            return normalize_fault_state_class_name(class_name)
    return "FaultState"


def build_fault_state_rule_text(rule: owlready2.Imp, state_class: str | None = None) -> str | None:
    all_atoms = list(rule.body) + list(rule.head)
    has_fault = any(is_hasFault_atom(atom) for atom in all_atoms)
    has_generic_fault = any(is_generic_fault_class_atom(atom) for atom in all_atoms)
    if not has_fault and not has_generic_fault:
        return None

    fault_subject_by_var: dict[str, str] = {}
    fault_subject_by_individual: dict[tuple[str, str], str] = {}
    fault_state_class_by_term: dict[tuple[str, str], str] = {}

    for atom in rule.body:
        if not is_hasFault_atom(atom):
            continue
        comp = atom.arguments[0]
        if isinstance(comp, owlready2.Variable):
            subject = comp.name
        else:
            subject = arg_to_str(comp)
        fault_term = atom.arguments[1]
        key = term_key(fault_term)
        if key[0] == "var":
            fault_subject_by_var[key[1]] = subject
            fault_state_class_by_term[key] = find_fault_state_class_for_term(rule, key)
        else:
            fault_subject_by_individual[key] = subject
            fault_state_class_by_term[key] = normalize_fault_state_class_name(key[1] or "Fault")

    body_fault_vars: set[str] = set()
    for atom in rule.body:
        if is_generic_fault_class_atom(atom):
            arg = atom.arguments[0]
            if isinstance(arg, owlready2.Variable):
                body_fault_vars.add(arg.name)

    triggers_subject_var: str | None = None
    for atom in rule.head:
        if not is_triggers_action_atom(atom):
            continue
        arg = atom.arguments[0]
        if isinstance(arg, owlready2.Variable):
            triggers_subject_var = arg.name
            break

    body_atoms: list[str] = []
    for atom in rule.body:
        if is_hasFault_atom(atom):
            continue
        if type(atom).__name__ == "ClassAtom":
            arg = atom.arguments[0]
            key = term_key(arg)
            if key in fault_state_class_by_term and is_fault_class_name(atom_name(atom)):
                continue
        body_atoms.append(atom_to_str(atom, var_subst=fault_subject_by_var, const_subst=fault_subject_by_individual))

    if not has_fault and triggers_subject_var and triggers_subject_var in body_fault_vars:
        component_var = choose_unique_variable_name(rule, "x")
        fault_subject_by_var[triggers_subject_var] = component_var
        body_atoms.insert(0, f"hasFault(?{component_var}, ?{triggers_subject_var})")

    for atom in rule.body:
        if not is_hasFault_atom(atom):
            continue
        subject = arg_to_str(atom.arguments[0])
        fault_term = atom.arguments[1]
        key = term_key(fault_term)
        state_class = fault_state_class_by_term.get(key) or "FaultState"
        body_atoms.insert(0, f"{state_class}({subject})")

    head_atoms: list[str] = []
    for atom in rule.head:
        if is_hasFault_atom(atom):
            subject = arg_to_str(atom.arguments[0])
            fault_term = atom.arguments[1]
            key = term_key(fault_term)
            if key[0] == "var":
                state_class = fault_state_class_by_term.get(key) or find_fault_state_class_for_term(rule, key)
            else:
                state_class = fault_state_class_by_term.get(key) or normalize_fault_state_class_name(key[1] if key[1] else "Fault")
            head_atoms.append(f"{state_class}({subject})")
            continue
        if type(atom).__name__ == "ClassAtom":
            arg = atom.arguments[0]
            key = term_key(arg)
            if key in fault_state_class_by_term and is_fault_class_name(atom_name(atom)):
                head_atoms.append(f"{fault_state_class_by_term[key]}({fault_subject_by_var.get(arg.name, fault_subject_by_individual.get(key, arg_to_str(arg)))})")
                continue
        head_atoms.append(atom_to_str(atom, var_subst=fault_subject_by_var, const_subst=fault_subject_by_individual))

    body_text = ", ".join(body_atoms)
    head_text = ", ".join(head_atoms)
    if not body_text:
        return f" -> {head_text}"
    return f"{body_text} -> {head_text}"


def class_defined(onto: owlready2.Ontology, class_name: str) -> bool:
    return class_name in {cls.name for cls in onto.classes()}


def ensure_class_definition(onto: owlready2.Ontology, class_name: str) -> None:
    if class_defined(onto, class_name):
        return
    with onto:
        type(class_name, (onto.FaultState,), {})


def main() -> None:
    if not ORIGINAL_ONTOLOGY.exists():
        raise FileNotFoundError(f"Original ontology not found: {ORIGINAL_ONTOLOGY}")

    if not MASTER_ONTOLOGY.exists():
        shutil.copy(ORIGINAL_ONTOLOGY, MASTER_ONTOLOGY)
        print(f"Created master ontology copy: {MASTER_ONTOLOGY}")

    if RUNTIME_ONTOLOGY.exists():
        RUNTIME_ONTOLOGY.unlink()

    shutil.copy(MASTER_ONTOLOGY, RUNTIME_ONTOLOGY)
    print(f"Created runtime ontology copy: {RUNTIME_ONTOLOGY}")

    world = owlready2.World()
    onto = _load_ontology_from_file(RUNTIME_ONTOLOGY, world)

    added_rules = 0
    added_classes = set(KNOWN_FAULT_STATE_CLASSES)
    runtime_state_classes = set()

    for rule in list(onto.rules()):
        for atom in list(rule.head) + list(rule.body):
            if not is_hasFault_atom(atom):
                continue

            fault_object = atom.arguments[1]
            if isinstance(fault_object, owlready2.Variable):
                key = term_key(fault_object)
                runtime_state_classes.add(find_fault_state_class_for_term(rule, key))
            else:
                fault_name = getattr(fault_object, "name", None)
                if not fault_name:
                    fault_name = getattr(fault_object, "iri", None)
                runtime_state_classes.add(normalize_fault_state_class_name(fault_name or "Fault"))

    with onto:
        class FaultState(owlready2.Thing):
            pass
        for class_name in sorted(runtime_state_classes):
            if class_name == "FaultState":
                continue
            if not class_defined(onto, class_name):
                type(class_name, (FaultState,), {})
                added_classes.add(class_name)

    for rule in list(onto.rules()):
        rule_text = build_fault_state_rule_text(rule)
        if rule_text is None:
            continue

        try:
            with onto:
                destroy_entity(rule)
        except Exception as exc:
            print(f"Warning: could not destroy old hasFault rule: {exc}")

        try:
            with onto:
                imp = owlready2.Imp(namespace=onto)
                imp.set_as_rule(rule_text, namespaces=[onto])
            added_rules += 1
        except Exception as exc:
            print("Failed to add runtime rule:", repr(rule_text))
            print(exc)

    onto.save(file=str(RUNTIME_ONTOLOGY), format="rdfxml")
    print(f"Saved runtime ontology with {added_rules} additional FaultState rules to {RUNTIME_ONTOLOGY}")
    print(f"Created {len(added_classes) - len(KNOWN_FAULT_STATE_CLASSES)} additional fault state subclasses if needed.")


if __name__ == "__main__":
    main()
