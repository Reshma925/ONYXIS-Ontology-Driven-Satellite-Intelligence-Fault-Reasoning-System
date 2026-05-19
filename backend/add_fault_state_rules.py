from __future__ import annotations

import re
from pathlib import Path
import owlready2

ONTO_PATH = Path(__file__).parent / "satellite_full (1).owl"
OVERLAY_OUT = Path(__file__).parent / "satellite_fault_state_overlay.owl"

KNOWN_FAULT_STATE_CLASSES = [
    "BatteryFaultState",
    "CriticalPowerFailureState",
    "ThermalFaultState",
    "CommunicationFaultState",
    "StarTrackerFaultState",
    "NavigationFaultState",
    "PropulsionFaultState",
    "FaultState",
]


def normalize_fault_state_class_name(name: str) -> str:
    clean_name = re.sub(r"_[0-9]+$", "", name)
    if clean_name.endswith("State"):
        return clean_name
    if clean_name.endswith("Fault") or clean_name.endswith("Failure"):
        return clean_name + "State"
    return clean_name + "FaultState"


def arg_to_str(arg: object) -> str:
    # Variables must be prefixed with '?' for SWRL rule syntax
    if isinstance(arg, owlready2.Variable):
        return f"?{arg.name}"
    name = getattr(arg, "name", None)
    if name:
        return name
    iri = getattr(arg, "iri", None) or getattr(arg, "get_iri", lambda: None)()
    if iri:
        if "#" in iri:
            return iri.split("#", 1)[1]
        return iri.rstrip("/").split("/")[-1]
    # Fallback: if str(arg) looks like a python/Owlready representation containing
    # a path and a dot-prefixed local name (e.g. C:\...\file.owl.LocalName),
    # extract the trailing local name.
    s = str(arg)
    if "." in s and ("\\" in s or "/" in s):
        return s.split(".")[-1]
    return s


def atom_to_str(atom: object) -> str:
    atom_type = type(atom).__name__
    if atom_type == "ClassAtom":
        args = ", ".join(arg_to_str(a) for a in atom.arguments)
        cls = getattr(atom, "class_predicate", None)
        cls_name = getattr(cls, "name", None)
        if not cls_name:
            iri = getattr(cls, "iri", None)
            if iri:
                cls_name = iri.split("#", 1)[1] if "#" in iri else iri.rstrip("/").split("/")[-1]
        return f"{cls_name}({args})"
    if atom_type in {"IndividualPropertyAtom", "DatavaluedPropertyAtom"}:
        args = ", ".join(arg_to_str(a) for a in atom.arguments)
        prop = getattr(atom, "property_predicate", None)
        prop_name = getattr(prop, "name", None)
        if not prop_name:
            iri = getattr(prop, "iri", None)
            if iri:
                prop_name = iri.split("#", 1)[1] if "#" in iri else iri.rstrip("/").split("/")[-1]
        return f"{prop_name}({args})"
    if atom_type == "BuiltinAtom":
        args = ", ".join(arg_to_str(a) for a in atom.arguments)
        builtin = getattr(atom, "builtin", None)
        builtin_name = getattr(builtin, "name", str(builtin)) if builtin is not None else "builtin"
        return f"{builtin_name}({args})"
    return str(atom)


def build_overlay_rule_text(rule: owlready2.Imp, state_class: str, subject_var: object) -> str:
    body_text = ", ".join(atom_to_str(atom) for atom in rule.body)
    subj_text = arg_to_str(subject_var)
    return f"{body_text} -> {state_class}({subj_text})"


def class_defined(onto: owlready2.Ontology, class_name: str) -> bool:
    return class_name in {cls.name for cls in onto.classes()}


def ensure_class_definition(onto: owlready2.Ontology, class_name: str) -> None:
    if class_defined(onto, class_name):
        return
    with onto:
        type(class_name, (onto.FaultState,), {})


def main() -> None:
    if not ONTO_PATH.exists():
        raise FileNotFoundError(f"Original ontology not found: {ONTO_PATH}")

    if OVERLAY_OUT.exists():
        OVERLAY_OUT.unlink()

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

    world = owlready2.World()
    original = _load_ontology_from_file(ONTO_PATH, world)

    overlay = world.get_ontology(str(OVERLAY_OUT.resolve()))
    overlay.imported_ontologies.append(original)

    with overlay:
        class FaultState(owlready2.Thing):
            pass

    for class_name in KNOWN_FAULT_STATE_CLASSES:
        if class_name != "FaultState":
            ensure_class_definition(overlay, class_name)

    added = 0
    for rule in list(original.rules()):
        for atom in rule.head:
            if getattr(atom, "property_predicate", None) is getattr(original, "hasFault", None) or getattr(getattr(atom, "property_predicate", None), "name", None) == "hasFault":
                subject = atom.arguments[0]
                fault_object = atom.arguments[1]
                if isinstance(fault_object, owlready2.Variable):
                    state_class = "FaultState"
                else:
                    state_class = normalize_fault_state_class_name(fault_object.name)
                    ensure_class_definition(overlay, state_class)
                rule_text = build_overlay_rule_text(rule, state_class, subject)
                try:
                    with overlay:
                        imp = owlready2.Imp()
                        # resolve names against the overlay ontology
                        # resolve names against both the overlay and the original ontology
                        imp.set_as_rule(rule_text, namespaces=[overlay, original])
                    added += 1
                except Exception as exc:
                    print("Failed to add overlay rule:", rule_text)
                    print(exc)

    overlay.save(file=str(OVERLAY_OUT))
    print(f"Saved overlay ontology with {added} new class-inference rules to {OVERLAY_OUT}")


if __name__ == "__main__":
    main()


