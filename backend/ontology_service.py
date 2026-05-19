from __future__ import annotations

import io
import random
import re
import threading
import time
import traceback
import uuid
from collections import deque, defaultdict
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import owlready2
from owlready2 import World, get_ontology, sync_reasoner_pellet, ThingClass
import runpy
from decimal import Decimal
import rdflib

API_PORT = 8000
ONTOLOGY_PATH = Path(__file__).parent / "satellite_full (1).owl"
OVERLAY_PATH = Path(__file__).parent / "satellite_fault_state_overlay.owl"
RUNTIME_PATH = Path(__file__).parent / "satellite_semantic_runtime.owl"
MAX_TELEMETRY = 200
MAX_LOGS = 250
TELEMETRY_INTERVAL_SECONDS = 1.0
REASONING_INTERVAL_SECONDS = 10.0
ENABLE_REASONING_LOOP = True
# Number of telemetry cycles to collect before running Pellet deterministically
TELEMETRY_CYCLES_BEFORE_REASONING = 8
# Automatic scenario switch interval in telemetry cycles (roughly 3-5 seconds)
SCENARIO_SWITCH_CYCLES = 3
SCENARIO_SEQUENCE = [
    "Normal Operation",
    "Battery Drain",
    "Thermal Overload",
    "Signal Loss",
    "Cascading Failure",
]

app = FastAPI(title="ONYXIS Ontology Service", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class LogEntry(BaseModel):
    id: str
    timestamp: int
    category: str
    severity: str
    message: str


class TelemetryTick(BaseModel):
    id: str
    timestamp: int
    channel: str
    value: str
    unit: str


class FaultEntry(BaseModel):
    id: str
    name: str
    severity: str
    component: str
    swrlRule: str
    evidence: str
    propagationRisk: str
    timestamp: int
    explanation: str
    hasFault: str
    subsystem: str


class SubsystemMetric(BaseModel):
    value: float
    unit: str
    label: str
    nominal: Optional[List[float]] = None


class SubsystemState(BaseModel):
    key: str
    name: str
    icon: str
    status: str
    metrics: Dict[str, SubsystemMetric]
    faultIds: List[str]


class SwrlRuleInfo(BaseModel):
    id: str
    name: str
    condition: str
    active: bool


class OntologyState(BaseModel):
    bootedAt: int
    now: int
    satellite: str
    subsystems: Dict[str, SubsystemState]
    faults: List[FaultEntry]
    logs: List[LogEntry]
    telemetry: List[TelemetryTick]
    series: Dict[str, List[Dict[str, float]]]
    scenario: str
    pellet: bool
    swrl: bool
    semantic: bool
    propagation: bool
    speed: float
    reasoningLatency: float
    ontologySync: str
    individuals: List[str]
    inferredClasses: List[str]
    swrlRules: List[SwrlRuleInfo]


class OntologyInspect(BaseModel):
    classes: List[str]
    subclasses: List[str]
    individuals: List[str]
    datatypeProperties: List[str]
    objectProperties: List[str]
    swrlRules: List[SwrlRuleInfo]


@dataclass
class TelemetryDefinition:
    channel: str
    unit: str
    label: str
    individual: Optional[str]
    property: Optional[str]
    subsystem: str
    value: float
    nominal: Optional[List[float]] = None
    delta: float = 0.0


def _detect_ontology_iri(ontology_path: Path) -> str:
    text = ontology_path.read_text(encoding="utf-8", errors="ignore")
    ontology_match = re.search(r'<owl:Ontology[^>]*?rdf:about=["\']([^"\']+)["\']', text)
    if ontology_match:
        return ontology_match.group(1)
    base_match = re.search(r'xml:base=["\']([^"\']+)["\']', text)
    if base_match:
        return base_match.group(1)
    return str(ontology_path.resolve())


def _load_ontology_from_file(ontology_path: Path, world: Optional[World] = None) -> owlready2.Ontology:
    if world is None:
        world = World()
    ontology_iri = _detect_ontology_iri(ontology_path)
    ontology = world.get_ontology(ontology_iri)
    with ontology_path.open("rb") as fileobj:
        ontology.load(fileobj=fileobj)
    return ontology


class OntologyEngine:
    def __init__(self, ontology_path: Path):
        self.lock = threading.RLock()
        self.ontology_path = ontology_path
        # TEMPORARY DEBUG: force loading the original ontology for comparison.
        ontology_to_load = self.ontology_path
        print(f"[ONTOLOGY] Debug forcing original ontology load: {ontology_to_load}")

        self.onto = _load_ontology_from_file(ontology_to_load)
        self.world = self.onto.world
        self.bootedAt = int(time.time() * 1000)
        self.start_time = time.time()

        self._background_telemetry_thread: Optional[threading.Thread] = None
        self._background_reasoning_thread: Optional[threading.Thread] = None
        self._background_telemetry_running = False
        self._background_reasoning_running = False
        self._cached_state: Optional[OntologyState] = None
        self._cached_state_lock = threading.Lock()

        # Use the ontology world so overlay/imported ontologies are included
        self.classes = sorted({c.name for c in self.world.classes()})
        self.subclasses = sorted({cls.name for c in self.world.classes() for cls in c.subclasses()})
        self.individuals = {ind.name: ind for ind in self.world.individuals()}
        self.data_properties = sorted({p.name for p in self.world.data_properties()})
        self.object_properties = sorted({p.name for p in self.world.object_properties()})
        self.property_cache = {p.name: p for p in self.world.properties()}
        self.swrl_rules = self._parse_swrl_rules()
        self.fault_rule_map = self._build_fault_rule_map()

        self.telemetry_definitions = self._build_telemetry_definitions()
        self.telemetry_frames = deque([], maxlen=MAX_TELEMETRY)
        self.series: Dict[str, List[Dict[str, float]]] = defaultdict(list)
        self.logs: deque[LogEntry] = deque([], maxlen=MAX_LOGS)
        self.scenario = "Normal Operation"
        self._scenario_cycle_count = 0
        self.pellet = True
        self.swrl = True
        self.semantic = True
        self.propagation = True
        self.speed = 1.0
        self.inferredClasses: List[str] = []
        self.last_latency = 0.0
        self.ontologySync = "SYNCED"
        self.faults: List[FaultEntry] = []
        self.subsystems: Dict[str, SubsystemState] = {}
        self._audit_telemetry_mappings()
        self._audit_declared_value_datatypes()

    def _relax_telemetry_property_domains(self) -> None:
        """Relax telemetry property domains to the generic Component class before reasoning."""
        component_cls = getattr(self.onto, "Component", None)
        if component_cls is None:
            return
        graph = self.world.as_rdflib_graph()
        component_ref = rdflib.URIRef(component_cls.iri)
        for definition in self.telemetry_definitions.values():
            if not definition.property:
                continue
            prop_obj = self.property_cache.get(definition.property)
            if prop_obj is None or not getattr(prop_obj, "iri", None):
                continue
            prop_ref = rdflib.URIRef(prop_obj.iri)
            existing_domains = list(graph.objects(subject=prop_ref, predicate=rdflib.RDFS.domain))
            if not existing_domains:
                continue
            with self.onto:
                for domain in existing_domains:
                    if domain != component_ref:
                        graph.remove((prop_ref, rdflib.RDFS.domain, domain))
                graph.add((prop_ref, rdflib.RDFS.domain, component_ref))
            print(f"[ONTOLOGY PATCH] Telemetry property {definition.property} domain relaxed to Component")

    def _swrl_arg_to_str(self, arg: object) -> str:
        if isinstance(arg, owlready2.Variable):
            return f"?{arg.name}"
        name = getattr(arg, "name", None)
        if isinstance(name, str) and name:
            return name
        iri = getattr(arg, "iri", None) or (getattr(arg, "get_iri", None) or (lambda: None))()
        if iri:
            iri = str(iri).replace("\\", "/")
            if "#" in iri:
                return iri.split("#", 1)[1]
            return iri.rstrip("/").split("/")[-1]
        s = str(arg)
        if "." in s and ("\\" in s or "/" in s):
            return s.split(".")[-1]
        return s

    def _swrl_atom_to_str(self, atom: object) -> str:
        atom_type = type(atom).__name__
        args = ", ".join(self._swrl_arg_to_str(a) for a in getattr(atom, "arguments", []))
        if atom_type == "ClassAtom":
            cls = getattr(atom, "class_predicate", None)
            cls_name = self._swrl_arg_to_str(cls)
            return f"{cls_name}({args})"
        if atom_type in {"IndividualPropertyAtom", "DatavaluedPropertyAtom"}:
            prop = getattr(atom, "property_predicate", None)
            prop_name = self._swrl_arg_to_str(prop)
            return f"{prop_name}({args})"
        if atom_type == "BuiltinAtom":
            builtin = getattr(atom, "builtin", None)
            builtin_name = getattr(builtin, "name", None) or str(builtin) if builtin is not None else "builtin"
            return f"{builtin_name}({args})"
        return str(atom)

    def _parse_swrl_rules(self) -> List[SwrlRuleInfo]:
        rows: List[SwrlRuleInfo] = []
        for idx, rule in enumerate(self.onto.rules(), start=1):
            condition = " ^ ".join(self._swrl_atom_to_str(atom) for atom in rule.body)
            head = " ^ ".join(self._swrl_atom_to_str(atom) for atom in rule.head)
            rows.append(SwrlRuleInfo(id=f"R{idx:03d}", name=head or f"Rule {idx}", condition=condition, active=True))
        return rows

    def _build_fault_rule_map(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        for rule in self.swrl_rules:
            if "hasFault(" not in rule.name and "hasFault(" not in rule.condition:
                continue
            for text in (rule.name, rule.condition):
                for match in re.finditer(r"hasFault\([^)]*\)", text):
                    atom = match.group(0)
                    parts = atom[8:-1].split(",")
                    if len(parts) < 2:
                        continue
                    target = parts[-1].strip()
                    short_target = target.split(".")[-1]
                    if short_target:
                        mapping[short_target] = rule.id
        return mapping

    def _build_telemetry_definitions(self) -> Dict[str, TelemetryDefinition]:
        return {
            "batteryVoltage": TelemetryDefinition(
                channel="Battery Voltage", unit="V", label="Battery Voltage",
                individual="Battery_01", property=None, subsystem="power",
                value=28.0, nominal=[26, 29.5], delta=0.15,
            ),
            "batteryCharge": TelemetryDefinition(
                channel="Battery Charge", unit="%", label="Charge Level",
                individual="Battery_01", property="hasChargeLevel", subsystem="power",
                value=87.0, nominal=[40, 100], delta=0.4,
            ),
            "dischargeRate": TelemetryDefinition(
                channel="Discharge Rate", unit="A", label="Discharge Rate",
                individual="Battery_01", property="hasDischargeRate", subsystem="power",
                value=1.2, nominal=[0, 3.5], delta=0.05,
            ),
            "solarIrradiance": TelemetryDefinition(
                channel="Solar Irradiance", unit="W/m²", label="Solar Irradiance",
                individual="SolarArray_01", property="hasIrradiance", subsystem="power",
                value=1361.0, nominal=[800, 1400], delta=5.0,
            ),
            "solarOutput": TelemetryDefinition(
                channel="Solar Output", unit="W", label="Solar Output",
                individual="SolarArray_01", property="hasGeneratedPower", subsystem="power",
                value=320.0, nominal=[200, 400], delta=3.5,
            ),
            "powerConsumption": TelemetryDefinition(
                channel="Power Consumption", unit="W", label="Power Consumption",
                individual="Power_01", property=None, subsystem="power",
                value=245.0, nominal=[150, 350], delta=4.0,
            ),
            "pcduOutput": TelemetryDefinition(
                channel="PCDU Output", unit="V", label="PCDU Output",
                individual="PCDU_01", property="hasOutputVoltage", subsystem="power",
                value=28.1, nominal=[27.5, 28.5], delta=0.05,
            ),
            "busVoltage": TelemetryDefinition(
                channel="Bus Voltage", unit="V", label="Bus Voltage",
                individual="BusLine_01", property="hasBusVoltage", subsystem="power",
                value=28.0, nominal=[27.5, 28.5], delta=0.04,
            ),
            "internalTemp": TelemetryDefinition(
                channel="Internal Temp", unit="°C", label="Internal Temp",
                individual="Battery_01", property="hasTemperature", subsystem="thermal",
                value=21.0, nominal=[15, 30], delta=0.3,
            ),
            "thermalLoad": TelemetryDefinition(
                channel="Thermal Load", unit="W", label="Thermal Load",
                individual="Thermal_01", property=None, subsystem="thermal",
                value=180.0, nominal=[100, 280], delta=3.0,
            ),
            "heaterOutput": TelemetryDefinition(
                channel="Heater Output", unit="W", label="Heater Output",
                individual="Heater_01", property="hasHeatLevel", subsystem="thermal",
                value=45.0, nominal=[0, 120], delta=1.5,
            ),
            "signalStrength": TelemetryDefinition(
                channel="Signal Strength", unit="dBm", label="Signal Strength",
                individual="TTCAntenna_01", property="hasSignalStrength", subsystem="comm",
                value=-62.0, nominal=[-80, -50], delta=0.8,
            ),
            "txQuality": TelemetryDefinition(
                channel="TX Quality", unit="%", label="TX Quality",
                individual="TelemetryEncoder_01", property="hasEncodingQuality", subsystem="comm",
                value=96.0, nominal=[85, 100], delta=0.6,
            ),
            "antennaAlignment": TelemetryDefinition(
                channel="Antenna Alignment", unit="°", label="Antenna Align",
                individual="Antenna_01", property=None, subsystem="comm",
                value=0.4, nominal=[0, 1.5], delta=0.06,
            ),
            "ttcStatus": TelemetryDefinition(
                channel="TTC Status", unit="OK", label="TTC Status",
                individual="TTC_01", property=None, subsystem="comm",
                value=1.0, nominal=[1, 1], delta=0.0,
            ),
            "rfPower": TelemetryDefinition(
                channel="RF Output", unit="W", label="RF Output",
                individual="PowerAmp_01", property="hasOutputPower", subsystem="comm",
                value=18.0, nominal=[12, 22], delta=0.5,
            ),
            "encQuality": TelemetryDefinition(
                channel="Encoder Quality", unit="%", label="Encoding Quality",
                individual="TelemetryEncoder_01", property="hasEncodingQuality", subsystem="comm",
                value=99.0, nominal=[95, 100], delta=0.3,
            ),
            "decoderError": TelemetryDefinition(
                channel="Decoder Error", unit="%", label="Decoder Err",
                individual="Decoder_01", property="hasDecodingError", subsystem="comm",
                value=0.02, nominal=[0, 0.5], delta=0.01,
            ),
            "uplinkStatus": TelemetryDefinition(
                channel="Uplink", unit="OK", label="Uplink",
                individual="Comm_01", property=None, subsystem="comm",
                value=1.0, nominal=[1, 1], delta=0.0,
            ),
            "gyroDrift": TelemetryDefinition(
                channel="Gyro Drift", unit="°/s", label="Gyro Drift",
                individual="GYRO_01", property="hasAngularRate", subsystem="aocs",
                value=0.02, nominal=[0, 0.1], delta=0.01,
            ),
            "angularRate": TelemetryDefinition(
                channel="Angular Rate", unit="°/s", label="Angular Rate",
                individual="GYRO_01", property="hasAngularRate", subsystem="aocs",
                value=0.5, nominal=[0, 2], delta=0.06,
            ),
            "orientationDev": TelemetryDefinition(
                channel="Orientation Deviation", unit="°", label="Orientation Dev",
                individual="AC_01", property="hasAttitudeError", subsystem="aocs",
                value=0.3, nominal=[0, 1.5], delta=0.05,
            ),
            "rwVibration": TelemetryDefinition(
                channel="Reaction Wheel Vibration", unit="g", label="Reaction Wheel Health",
                individual="RW_01", property="hasVibration", subsystem="aocs",
                value=0.05, nominal=[0, 0.3], delta=0.01,
            ),
            "starTrackerErr": TelemetryDefinition(
                channel="Star Tracker Error", unit="arcsec", label="Star Tracker Err",
                individual="STR_01", property="hasTrackingError", subsystem="aocs",
                value=12.0, nominal=[0, 50], delta=0.8,
            ),
            "gnssError": TelemetryDefinition(
                channel="GNSS Error", unit="m", label="GNSS Error",
                individual="GNSS_01", property="hasPositionError", subsystem="aocs",
                value=1.8, nominal=[0, 8], delta=0.1,
            ),
            "magnetometer": TelemetryDefinition(
                channel="Magnetometer", unit="OK", label="Magnetometer",
                individual="MAG_01", property="hasMagneticFieldError", subsystem="aocs",
                value=1.0, nominal=[1, 1], delta=0.0,
            ),
            "thrusterState": TelemetryDefinition(
                channel="Thruster State", unit="OK", label="Thrusters",
                individual="THR_01", property="hasThrust", subsystem="aocs",
                value=1.0, nominal=[0, 1], delta=0.0,
            ),
            "cpuLoad": TelemetryDefinition(
                channel="CPU Load", unit="%", label="CPU Load",
                individual="OBC_01", property=None, subsystem="obc",
                value=42.0, nominal=[10, 75], delta=0.8,
            ),
            "memoryUsage": TelemetryDefinition(
                channel="Memory Usage", unit="%", label="Memory Usage",
                individual="OBC_01", property=None, subsystem="obc",
                value=58.0, nominal=[20, 80], delta=0.7,
            ),
            "processingLoad": TelemetryDefinition(
                channel="Processing Load", unit="%", label="Processing",
                individual="OBC_01", property=None, subsystem="obc",
                value=38.0, nominal=[10, 70], delta=0.6,
            ),
            "dataThroughput": TelemetryDefinition(
                channel="Data Throughput", unit="Mbps", label="Throughput",
                individual="OBC_01", property=None, subsystem="obc",
                value=12.4, nominal=[2, 25], delta=0.4,
            ),
            "taskQueue": TelemetryDefinition(
                channel="Task Queue", unit="", label="Task Queue",
                individual="OBC_01", property=None, subsystem="obc",
                value=18.0, nominal=[0, 50], delta=0.8,
            ),
            "obcTemp": TelemetryDefinition(
                channel="OBC Temp", unit="°C", label="OBC Temp",
                individual="OBC_01", property=None, subsystem="obc",
                value=38.0, nominal=[10, 55], delta=0.4,
            ),
            "structuralStress": TelemetryDefinition(
                channel="Structural Stress", unit="MPa", label="Stress",
                individual="Structure_01", property=None, subsystem="structure",
                value=18.0, nominal=[0, 60], delta=0.6,
            ),
            "vibration": TelemetryDefinition(
                channel="Vibration", unit="g", label="Vibration",
                individual="Structure_01", property=None, subsystem="structure",
                value=0.04, nominal=[0, 0.25], delta=0.01,
            ),
            "mountStability": TelemetryDefinition(
                channel="Mount Stability", unit="%", label="Mount Stab.",
                individual="Mount_01", property=None, subsystem="structure",
                value=99.0, nominal=[95, 100], delta=0.1,
            ),
            "frameIntegrity": TelemetryDefinition(
                channel="Frame Integrity", unit="%", label="Frame Int.",
                individual="Frame_01", property=None, subsystem="structure",
                value=100.0, nominal=[98, 100], delta=0.05,
            ),
            "panelStability": TelemetryDefinition(
                channel="Panel Stability", unit="%", label="Panel Stab.",
                individual="SolarPanel_01", property=None, subsystem="structure",
                value=98.0, nominal=[95, 100], delta=0.1,
            ),
        }

    def _audit_telemetry_mappings(self) -> None:
        """Audit telemetry property mappings and log metadata for consistency debugging."""
        self._log("Ontology", "INFO", "Auditing telemetry property mappings and constraints...")
        
        for key, definition in self.telemetry_definitions.items():
            if definition.property:
                if definition.property not in self.data_properties:
                    msg = f"Telemetry {key} maps to unknown property {definition.property}"
                    print(f"[ONTOLOGY] {msg}")
                    self._log("Ontology", "WARNING", msg)
                else:
                    try:
                        prop_obj = self.property_cache.get(definition.property)
                        individual = self.individuals.get(definition.individual) if definition.individual else None
                        if prop_obj is not None and individual is not None:
                            if not self._individual_matches_property_domain(individual, prop_obj):
                                domains = self._get_property_domain_uris(prop_obj)
                                msg = (f"Telemetry {key} maps to property {definition.property}, but individual "
                                       f"{definition.individual} is not compatible with domains {domains}")
                                print(f"[ONTOLOGY] {msg}")
                                self._log("Ontology", "WARNING", msg)
                        metadata = []
                        if hasattr(prop_obj, 'is_functional') and prop_obj.is_functional:
                            metadata.append("FunctionalProperty")
                        if hasattr(prop_obj, 'max_cardinality'):
                            metadata.append(f"maxCard={prop_obj.max_cardinality}")
                        if hasattr(prop_obj, 'range') and prop_obj.range:
                            metadata.append(f"range={prop_obj.range}")
                        if metadata:
                            msg = f"Property {definition.property}: {', '.join(metadata)}"
                            self._log("Ontology", "INFO", msg)
                    except Exception:
                        pass
                continue
            
            # Try to find a matching data property by heuristics
            candidates = [p for p in self.data_properties if key.lower() in p.lower() or definition.label.replace(" ", "").lower() in p.lower()]
            chosen = None
            for candidate in candidates:
                prop_obj = self.property_cache.get(candidate)
                individual = self.individuals.get(definition.individual) if definition.individual else None
                if prop_obj is not None and individual is not None and not self._individual_matches_property_domain(individual, prop_obj):
                    continue
                chosen = candidate
                break
            if chosen:
                definition.property = chosen
                msg = f"Telemetry {key} auto-mapped to ontology property {chosen}"
                print(f"[ONTOLOGY] {msg}")
                self._log("Ontology", "INFO", msg)
            else:
                camel = "has" + "".join([w.capitalize() for w in key.split("_")])
                if camel in self.data_properties:
                    prop_obj = self.property_cache.get(camel)
                    individual = self.individuals.get(definition.individual) if definition.individual else None
                    if prop_obj is not None and individual is not None and self._individual_matches_property_domain(individual, prop_obj):
                        definition.property = camel
                        msg = f"Telemetry {key} auto-mapped to ontology property {camel}"
                        print(f"[ONTOLOGY] {msg}")
                        self._log("Ontology", "INFO", msg)
                    else:
                        msg = f"Telemetry field {key} has no ontology datatype property mapping"
                        print(f"[ONTOLOGY] {msg}")
                        self._log("Ontology", "WARNING", msg)
                else:
                    msg = f"Telemetry field {key} has no ontology datatype property mapping"
                    print(f"[ONTOLOGY] {msg}")
                    self._log("Ontology", "WARNING", msg)

    def _get_property_declared_range_uri(self, prop_obj) -> Optional[str]:
        """Return the raw RDF range IRI for a property, if declared."""
        if (prop_obj is None) or (not hasattr(prop_obj, 'iri')):
            return None
        try:
            graph = self.world.as_rdflib_graph()
            prop_ref = rdflib.URIRef(prop_obj.iri)
            ranges = list(graph.objects(subject=prop_ref, predicate=rdflib.RDFS.range))
            if ranges:
                return str(ranges[0])
        except Exception:
            pass
        return None

    def _audit_declared_value_datatypes(self) -> None:
        """Audit datatype ranges declared on properties against actual literal values."""
        graph = self.world.as_rdflib_graph()
        for prop_name in self.data_properties:
            prop_obj = self.property_cache.get(prop_name)
            if not prop_obj:
                continue
            declared_uri = self._get_property_declared_range_uri(prop_obj)
            if not declared_uri:
                continue
            prop_ref = rdflib.URIRef(prop_obj.iri)
            for subj, _, obj in graph.triples((None, prop_ref, None)):
                if isinstance(obj, rdflib.Literal):
                    observed_uri = str(obj.datatype) if obj.datatype is not None else 'None'
                    if observed_uri != declared_uri:
                        msg = (f"[DATATYPE MISMATCH] {prop_name} declared={declared_uri} "
                               f"observed={observed_uri} on {subj}")
                        print(msg)
                        self._log("Ontology", "WARNING", msg)

    def tick_once(self) -> None:
        """Perform one telemetry generation and reasoning cycle (EXPLICIT, not autonomous)."""
        with self.lock:
            now = int(time.time() * 1000)
            self._inject_scenario_telemetry(now)
            self._run_reasoner()
            self._extract_state(now)

    def _inject_scenario_telemetry(self, timestamp: int) -> None:
        """Apply scenario-based modifications and write telemetry to ontology with deduplication."""
        ontology_writes: Dict[tuple, float] = {}

        for key, definition in self.telemetry_definitions.items():
            target, speed, jitter = self._compute_scenario_target(key, definition)
            delta = target - float(definition.value)
            trend = delta * speed
            noise = random.uniform(-jitter, jitter)
            old_value = float(definition.value)
            definition.value = float(definition.value + trend + noise)
            if self.scenario != "Normal Operation":
                print(f"[SCENARIO] {self.scenario} applying {key}: {old_value:.3f} -> {definition.value:.3f} target={target} trend={trend:.3f} noise={noise:.3f}")
            else:
                print(f"[TELEMETRY DRIFT] {key}: {old_value:.3f} -> {definition.value:.3f} target={target} trend={trend:.3f} noise={noise:.3f}")

            if definition.unit == "%":
                definition.value = round(max(0.0, min(100.0, definition.value)), 2)
            elif definition.unit == "dBm":
                definition.value = round(max(-120.0, min(-40.0, definition.value)), 2)
            elif definition.unit == "W/m²":
                definition.value = round(max(0.0, definition.value), 2)
            elif definition.unit == "W":
                definition.value = round(max(0.0, definition.value), 2)
            elif definition.unit == "V":
                definition.value = round(max(0.0, definition.value), 3)
            elif definition.unit == "°C":
                definition.value = round(definition.value, 2)
            elif definition.unit == "g":
                definition.value = round(definition.value, 4)
            elif definition.unit == "°/s":
                definition.value = round(definition.value, 4)
            elif definition.unit == "m":
                definition.value = round(definition.value, 3)
            elif definition.unit == "arcsec":
                definition.value = round(definition.value, 2)
            else:
                definition.value = round(definition.value, 3)

            tick = TelemetryTick(
                id=str(uuid.uuid4()),
                timestamp=timestamp,
                channel=definition.channel,
                value=str(definition.value),
                unit=definition.unit,
            )
            self.telemetry_frames.appendleft(tick)
            self._append_series(key, definition.value)

            if definition.property and definition.individual:
                prop_obj = self.property_cache.get(definition.property)
                individual = self.individuals.get(definition.individual)
                if prop_obj is None:
                    msg = f"[INVALID TELEMETRY] property {definition.property} is unknown for telemetry {key}"
                    print(msg)
                    self._log("Ontology", "WARNING", msg)
                    continue
                if individual is None:
                    msg = f"[INVALID TELEMETRY] individual {definition.individual} is unknown for telemetry {key}"
                    print(msg)
                    self._log("Ontology", "WARNING", msg)
                    continue
                if not self._individual_matches_property_domain(individual, prop_obj):
                    domains = self._get_property_domain_uris(prop_obj)
                    individual_types = [c.name for c in getattr(individual, 'INDIRECT_is_a', []) if hasattr(c, 'name')]
                    msg = (f"[INVALID TELEMETRY] {definition.individual}.{definition.property} has declared domains {domains} "
                           f"but individual types are {individual_types}; skipping runtime write")
                    print(msg)
                    self._log("Ontology", "WARNING", msg)
                    continue

                write_key = (definition.individual, definition.property)
                if write_key in ontology_writes:
                    old_val = ontology_writes[write_key]
                    msg = f"[DEDUP] {definition.individual}.{definition.property}: {old_val} → {definition.value} (collision in telemetry mappings)"
                    print(msg)
                    self._log("Ontology", "WARNING", msg)
                ontology_writes[write_key] = definition.value
            else:
                if definition.individual and definition.property is None:
                    self._log("Ontology", "INFO", f"Telemetry field {key} applies to {definition.individual} without ontology property mapping")
                else:
                    self._log("Telemetry", "WARNING", f"Telemetry field {key} has no ontology mapping")

        for (individual_name, prop_name), value in ontology_writes.items():
            print(f"[WRITE QUEUE] {individual_name}.{prop_name} = {value}")
            self._write_ontology_property(individual_name, prop_name, value)

    def _append_series(self, key: str, value: float) -> None:
        series = self.series[key]
        series.append({"t": int(time.time() * 1000), "v": value})
        self.series[key] = series[-MAX_TELEMETRY:]

    def _compute_scenario_target(self, key: str, definition: TelemetryDefinition) -> tuple[float, float, float]:
        """Return (target, speed, jitter) for the current scenario and telemetry key."""
        nominal_mid = float(sum(definition.nominal) / len(definition.nominal)) if definition.nominal else float(definition.value)
        if self.scenario == "Normal Operation":
            return nominal_mid, 0.06, max(0.02, definition.delta * 0.4)

        if self.scenario == "Battery Drain":
            if key == "batteryCharge":
                return 25.0, 0.08, 0.15
            if key == "batteryVoltage":
                return 25.8, 0.04, 0.04
            if key == "dischargeRate":
                return 3.4, 0.06, 0.08
            if key == "solarOutput":
                return 315.0, 0.03, 1.4
            if key == "pcduOutput":
                return 27.4, 0.02, 0.02
            if key == "internalTemp":
                return 30.0, 0.05, 0.1
            if key == "obcTemp":
                return 44.0, 0.04, 0.12
            return nominal_mid, 0.03, max(0.01, definition.delta * 0.3)

        if self.scenario == "Thermal Overload":
            if key == "internalTemp":
                return 90.0, 0.09, 0.35
            if key == "obcTemp":
                return 96.0, 0.08, 0.25
            if key == "heaterOutput":
                return 98.0, 0.07, 1.5
            if key == "thermalLoad":
                return 255.0, 0.05, 2.5
            if key == "cpuLoad":
                return 72.0, 0.05, 0.9
            if key == "memoryUsage":
                return 78.0, 0.05, 0.8
            if key == "processingLoad":
                return 70.0, 0.04, 0.7
            return nominal_mid, 0.02, max(0.01, definition.delta * 0.2)

        if self.scenario == "Signal Loss":
            if key == "signalStrength":
                return -88.0, 0.08, 0.8
            if key == "txQuality":
                return 34.0, 0.07, 0.6
            if key == "antennaAlignment":
                return 6.0, 0.06, 0.15
            if key == "decoderError":
                return 1.5, 0.05, 0.12
            if key == "uplinkStatus":
                return 0.0, 0.12, 0.05
            if key == "rfPower":
                return 12.0, 0.03, 0.4
            if key == "encQuality":
                return 87.0, 0.04, 0.6
            return nominal_mid, 0.03, max(0.01, definition.delta * 0.2)

        if self.scenario == "Cascading Failure":
            if key == "batteryCharge":
                return 22.0, 0.1, 0.25
            if key == "batteryVoltage":
                return 24.3, 0.06, 0.05
            if key == "signalStrength":
                return -92.0, 0.1, 1.0
            if key == "txQuality":
                return 28.0, 0.08, 0.7
            if key == "antennaAlignment":
                return 7.8, 0.07, 0.2
            if key == "orientationDev":
                return 6.5, 0.06, 0.2
            if key == "starTrackerErr":
                return 130.0, 0.08, 1.8
            if key == "gnssError":
                return 18.0, 0.05, 0.15
            if key == "panelStability":
                return 90.0, 0.04, 0.12
            if key == "structuralStress":
                return 48.0, 0.05, 0.25
            if key == "vibration":
                return 0.18, 0.05, 0.02
            if key == "ttcStatus" or key == "uplinkStatus" or key == "thrusterState" or key == "magnetometer":
                return 0.0, 0.12, 0.05
            return nominal_mid, 0.03, max(0.01, definition.delta * 0.25)

        return nominal_mid, 0.03, max(0.01, definition.delta * 0.4)

    def _auto_rotate_scenario_if_needed(self, cycle: int) -> None:
        self._scenario_cycle_count += 1
        if self._scenario_cycle_count < SCENARIO_SWITCH_CYCLES:
            return
        self._scenario_cycle_count = 0
        try:
            current_index = SCENARIO_SEQUENCE.index(self.scenario)
        except ValueError:
            current_index = 0
        next_index = (current_index + 1) % len(SCENARIO_SEQUENCE)
        self.scenario = SCENARIO_SEQUENCE[next_index]
        self._log("System", "INFO", f"Auto-switched scenario to {self.scenario}")
        print(f"[SCENARIO] Auto-switched to {self.scenario} after {SCENARIO_SWITCH_CYCLES} cycles")

    def _write_ontology_property(self, individual_name: str, prop_name: str, value: float) -> None:
        print(f"[WRITE START] {individual_name}.{prop_name} = {value}")
        individual = self.individuals.get(individual_name)
        if not individual:
            self._log("Ontology", "WARNING", f"Missing individual {individual_name} for property {prop_name}")
            print(f"[WRITE ABORT] missing individual {individual_name}")
            return
        if prop_name not in self.data_properties:
            self._log("Ontology", "WARNING", f"Missing datatype property {prop_name} for individual {individual_name}")
            print(f"[WRITE ABORT] missing data property {prop_name}")
            return
        try:
            print(f"[WRITE STEP] resolving property object for {prop_name}")
            prop_obj = self.property_cache.get(prop_name)
            print(f"[WRITE STEP] property object resolved: {prop_obj}")
            print(f"[WRITE STEP] normalizing value for {individual_name}.{prop_name}")
            safe_value = self._normalize_ontology_value(prop_obj, value)
            safe_datatype = self._format_value_datatype(safe_value)
            declared_ranges = self._get_property_range_uris(prop_obj)
            domains = self._get_property_domain_uris(prop_obj)
            domain_ok = True
            domain_names: List[str] = []
            if domains:
                domain_ok = False
                for domain_uri in domains:
                    domain_candidates = [cls for cls in self.onto.classes() if getattr(cls, 'iri', None) == domain_uri]
                    if domain_candidates:
                        domain_names.append(domain_candidates[0].name)
                        if self._individual_satisfies_class(individual, domain_candidates[0]):
                            domain_ok = True
            if not domains:
                domain_names = ["<none declared>"]
            print(f"[TELEMETRY WRITE VALIDATION] {individual_name}.{prop_name} value={value} safe={safe_value} datatype={safe_datatype} declared_ranges={declared_ranges} domains={domain_names} domain_ok={domain_ok}")
            if not domain_ok:
                self._log("Ontology", "WARNING", f"Domain mismatch on {individual_name}.{prop_name}: individual not instance of declared domains {domain_names}")

            # Store old values for logging
            prop_values = getattr(individual, prop_name, [])
            try:
                old_values = list(prop_values)
            except Exception:
                old_values = []
            print(f"[WRITE STEP] current values for {individual_name}.{prop_name} = {old_values}")

            # Use internal Owlready2 API to clean old triples at the store level.
            # This is the only reliable way to remove residual literals left over from previous writes.
            try:
                subj_storid = individual.storid
                pred_storid = prop_obj.storid if hasattr(prop_obj, 'storid') else None
                if pred_storid is not None:
                    print(f"[WRITE CLEANUP] Using raw storid deletion: subj={subj_storid} pred={pred_storid}")
                    with self.onto:
                        # Call the internal _del_data_triple_raw_spod method to delete all existing data triples
                        # for this (subject, predicate) pair regardless of object value or datatype.
                        self.onto._del_data_triple_raw_spod(subj_storid, pred_storid, None, None)
                    print(f"[WRITE CLEANUP] Raw storid deletion completed")
            except Exception as exc:
                print(f"[WRITE CLEANUP ERROR] {exc}")
                self._log("Ontology", "WARNING", f"Failed to cleanup old triples for {individual_name}.{prop_name}: {exc}")

            # Now assign the new value via Owlready2 API
            try:
                with self.onto:
                    try:
                        delattr(individual, prop_name)
                        print(f"[WRITE STEP] cleared attribute via delattr for {individual_name}.{prop_name}")
                    except Exception:
                        try:
                            setattr(individual, prop_name, [])
                            print(f"[WRITE STEP] cleared attribute via setattr(empty list) for {individual_name}.{prop_name}")
                        except Exception as exc:
                            print(f"[WRITE STEP] failed clearing attribute fallback: {exc}")

                    setattr(individual, prop_name, [safe_value])

                # Verify resulting property length; if >1 attempt rdflib graph cleanup
                final_vals = list(getattr(individual, prop_name, []))
                if len(final_vals) != 1:
                    msg = f"[WRITE VERIFY] {individual_name}.{prop_name} has {len(final_vals)} values after assignment: {final_vals}"
                    print(msg)
                    self._log("Ontology", "CRITICAL", msg)
                    self.ontologySync = "INCONSISTENT"

                msg_write = f"[ONTOLOGY WRITE]\n{individual_name}.{prop_name}: {old_values} → [{safe_value}] (final={final_vals})"
                print(msg_write)
                self._log("Ontology", "INFO", msg_write)

            except Exception as exc:
                print(f"[WRITE STEP ERROR] {exc}")
                raise
        except Exception as exc:
            self._log("Ontology", "CRITICAL", f"Failed writing {individual_name}.{prop_name}={value}: {exc}")
            print(f"[WRITE FAILED] {individual_name}.{prop_name}: {exc}")

    def _normalize_ontology_value(self, prop_obj, value: Any) -> Any:
        """Cast telemetry data into ontology-compatible datatype values."""
        if prop_obj is None:
            return value

        declared_range_uri = self._get_property_declared_range_uri(prop_obj)
        if isinstance(value, rdflib.Literal):
            return value

        if declared_range_uri == str(rdflib.XSD.decimal):
            try:
                # rdflib / Owlready2 do not reliably accept Decimal objects directly
                # Convert Decimal (and numeric strings) to native float for storage
                if isinstance(value, Decimal):
                    return float(value)
                if isinstance(value, (float, int)):
                    return float(value)
                if isinstance(value, str):
                    # attempt parse then convert to float
                    try:
                        return float(Decimal(value))
                    except Exception:
                        return value
            except Exception:
                pass

        if declared_range_uri == str(rdflib.XSD.double):
            try:
                return float(value)
            except (TypeError, ValueError):
                return value

        if declared_range_uri == str(rdflib.XSD.float):
            try:
                return float(value)
            except (TypeError, ValueError):
                return value

        if declared_range_uri == str(rdflib.XSD.integer):
            try:
                return int(value)
            except (TypeError, ValueError):
                return value

        if declared_range_uri == str(rdflib.XSD.boolean):
            try:
                return bool(value)
            except Exception:
                return value

        if isinstance(value, str):
            try:
                if float in getattr(prop_obj, 'range', []):
                    value = float(value)
                elif int in getattr(prop_obj, 'range', []):
                    value = int(value)
            except (TypeError, ValueError):
                pass

        if float in getattr(prop_obj, 'range', []):
            try:
                return float(value)
            except (TypeError, ValueError):
                return value
        if int in getattr(prop_obj, 'range', []):
            try:
                return int(value)
            except (TypeError, ValueError):
                return value
        if bool in getattr(prop_obj, 'range', []):
            return bool(value)
        return value

    def _get_property_domain_uris(self, prop_obj) -> List[str]:
        if not prop_obj or not getattr(prop_obj, 'iri', None):
            return []
        try:
            graph = self.world.as_rdflib_graph()
            prop_ref = rdflib.URIRef(prop_obj.iri)
            return [str(o) for o in graph.objects(subject=prop_ref, predicate=rdflib.RDFS.domain)]
        except Exception:
            return []

    def _individual_matches_property_domain(self, individual, prop_obj) -> bool:
        if individual is None or prop_obj is None or not getattr(prop_obj, 'iri', None):
            return False
        domains = self._get_property_domain_uris(prop_obj)
        if not domains:
            return True
        for domain_uri in domains:
            domain_classes = [cls for cls in self.onto.classes() if getattr(cls, 'iri', None) == domain_uri]
            for domain_cls in domain_classes:
                if self._individual_satisfies_class(individual, domain_cls):
                    return True
        return False

    def _get_property_range_uris(self, prop_obj) -> List[str]:
        if not prop_obj or not getattr(prop_obj, 'iri', None):
            return []
        try:
            graph = self.world.as_rdflib_graph()
            prop_ref = rdflib.URIRef(prop_obj.iri)
            return [str(o) for o in graph.objects(subject=prop_ref, predicate=rdflib.RDFS.range)]
        except Exception:
            return []

    def _format_value_datatype(self, value: Any) -> str:
        if isinstance(value, rdflib.Literal):
            return str(value.datatype) if value.datatype is not None else 'Literal'
        if isinstance(value, Decimal):
            return str(rdflib.XSD.decimal)
        if isinstance(value, float):
            return str(rdflib.XSD.double)
        if isinstance(value, bool):
            return str(rdflib.XSD.boolean)
        if isinstance(value, int):
            return str(rdflib.XSD.integer)
        return type(value).__name__

    def _get_class_ancestors(self, cls) -> List[ThingClass]:
        ancestors = getattr(cls, 'ancestors', [])
        if callable(ancestors):
            try:
                ancestors = ancestors()
            except Exception:
                return []
        return ancestors or []

    def _individual_satisfies_class(self, individual, cls) -> bool:
        if cls is None or not isinstance(cls, ThingClass):
            return False
        indirect = getattr(individual, 'INDIRECT_is_a', None)
        if indirect is not None and cls in indirect:
            return True
        for asserted in getattr(individual, 'is_a', []):
            if asserted is cls:
                return True
            if isinstance(asserted, ThingClass) and cls in self._get_class_ancestors(asserted):
                return True
        return False

    def _collect_functional_violations(self) -> List[str]:
        diagnostics: List[str] = []
        for ind_name, individual in self.individuals.items():
            try:
                for prop in individual.get_properties():
                    try:
                        vals = list(prop[individual])
                    except Exception:
                        try:
                            vals = list(getattr(individual, prop.name, []))
                        except Exception:
                            vals = []
                    if not vals:
                        continue
                    is_func = getattr(prop, 'is_functional', False)
                    max_card = getattr(prop, 'max_cardinality', None)
                    if is_func or (max_card is not None and int(max_card) == 1):
                        if len(vals) > 1:
                            diagnostics.append(
                                f"[FUNCTIONAL_VIOLATION] {ind_name}.{prop.name} values={vals} functional={is_func} max_card={max_card}"
                            )
            except Exception:
                pass
        return diagnostics

    def _collect_datatype_mismatches(self) -> List[str]:
        diagnostics: List[str] = []
        graph = self.world.as_rdflib_graph()
        for prop_name in self.data_properties:
            prop_obj = self.property_cache.get(prop_name)
            if not prop_obj or not getattr(prop_obj, 'iri', None):
                continue
            declared_ranges = self._get_property_range_uris(prop_obj)
            if not declared_ranges:
                continue
            prop_ref = rdflib.URIRef(prop_obj.iri)
            for subj, _, obj in graph.triples((None, prop_ref, None)):
                if not isinstance(obj, rdflib.Literal):
                    continue
                observed_uri = str(obj.datatype) if obj.datatype is not None else 'None'
                if observed_uri not in declared_ranges:
                    individual_name = subj.split('#')[-1] if isinstance(subj, rdflib.URIRef) else str(subj)
                    diagnostics.append(
                        f"[DATATYPE_MISMATCH] {individual_name}.{prop_name} declared={declared_ranges} observed={observed_uri} value={obj}"
                    )
        return diagnostics

    def _collect_domain_violations(self) -> List[str]:
        diagnostics: List[str] = []
        graph = self.world.as_rdflib_graph()
        for prop_name in self.data_properties:
            prop_obj = self.property_cache.get(prop_name)
            if not prop_obj or not getattr(prop_obj, 'iri', None):
                continue
            domains = self._get_property_domain_uris(prop_obj)
            if not domains:
                continue
            prop_ref = rdflib.URIRef(prop_obj.iri)
            for subj, _, _ in graph.triples((None, prop_ref, None)):
                individual_name = subj.split('#')[-1] if isinstance(subj, rdflib.URIRef) else str(subj)
                individual = self.individuals.get(individual_name)
                if individual is None:
                    continue
                for domain_uri in domains:
                    domain_candidates = [cls for cls in self.onto.classes() if getattr(cls, 'iri', None) == domain_uri]
                    if not domain_candidates:
                        continue
                    domain_cls = domain_candidates[0]
                    if not self._individual_satisfies_class(individual, domain_cls):
                        diagnostics.append(
                            f"[DOMAIN_VIOLATION] {individual_name}.{prop_name} individual not instance of declared domain {domain_cls.name} ({domain_uri})"
                        )
        return diagnostics

    def _collect_conflicting_class_memberships(self) -> List[str]:
        diagnostics: List[str] = []
        for individual_name, individual in self.individuals.items():
            classes = [cls for cls in (getattr(individual, 'INDIRECT_is_a', None) or getattr(individual, 'is_a', [])) if isinstance(cls, ThingClass)]
            class_names = {cls.name for cls in classes}
            for cls in classes:
                disjoint = getattr(cls, 'disjoint_with', []) or []
                for dis in disjoint:
                    dis_name = dis.name if isinstance(dis, ThingClass) else str(dis)
                    if dis_name in class_names:
                        diagnostics.append(
                            f"[DISJOINTNESS] {individual_name} belongs to disjoint classes {cls.name} and {dis_name}"
                        )
        return diagnostics

    def _print_pre_reasoning_diagnostics(self) -> None:
        print("[PRE-PELLET DIAGNOSTICS] Gathering runtime assertion checks before Pellet reasoning")
        functional_violations = self._collect_functional_violations()
        if functional_violations:
            print("[PRE-PELLET DIAGNOSTICS] Functional property violations:")
            for msg in functional_violations:
                print(msg)
        else:
            print("[PRE-PELLET DIAGNOSTICS] No functional property violations detected")

        datatype_violations = self._collect_datatype_mismatches()
        if datatype_violations:
            print("[PRE-PELLET DIAGNOSTICS] Datatype mismatches:")
            for msg in datatype_violations:
                print(msg)
        else:
            print("[PRE-PELLET DIAGNOSTICS] No datatype mismatches detected")

        domain_violations = self._collect_domain_violations()
        if domain_violations:
            print("[PRE-PELLET DIAGNOSTICS] Domain violations:")
            for msg in domain_violations:
                print(msg)
        else:
            print("[PRE-PELLET DIAGNOSTICS] No explicit domain violations detected")

        disjoint_violations = self._collect_conflicting_class_memberships()
        if disjoint_violations:
            print("[PRE-PELLET DIAGNOSTICS] Conflicting class memberships:")
            for msg in disjoint_violations:
                print(msg)
        else:
            print("[PRE-PELLET DIAGNOSTICS] No disjoint class membership conflicts detected")

        print("[PRE-PELLET DIAGNOSTICS] Completed runtime assertion checks")

    def _check_ontology_consistency(self) -> bool:
        """Pre-flight check: verify ontology is consistent before Pellet execution."""
        try:
            # Attempt to read basic ontology statistics to verify integrity
            individual_count = len(self.individuals)
            class_count = len(self.classes)
            
            # Check for obviously broken individuals
            for individual_name, individual in self.individuals.items():
                # Verify individual is still accessible
                try:
                    _ = individual.name
                    # Spot-check a few properties for accessibility
                    _ = individual.is_a
                except Exception as e:
                    self._log("Ontology", "WARNING", f"Individual {individual_name} appears corrupted: {e}")
                    return False
            
            return True
        except Exception as e:
            self._log("Ontology", "CRITICAL", f"Pre-flight consistency check failed: {e}")
            return False

    def _scan_for_cardinality_violations(self) -> List[str]:
        """Scan ontology for multi-valued properties that violate functional/maxCardinality constraints.

        Returns a list of diagnostic messages found.
        """
        diagnostics: List[str] = []
        try:
            for ind_name, individual in self.individuals.items():
                try:
                    for prop in individual.get_properties():
                        try:
                            vals = list(prop[individual])
                        except Exception:
                            # fallback to getattr if rdflib access fails
                            try:
                                vals = list(getattr(individual, prop.name, []))
                            except Exception:
                                vals = []
                        if not vals:
                            continue
                        # Check functional property or max_cardinality == 1
                        is_func = getattr(prop, 'is_functional', False)
                        max_card = getattr(prop, 'max_cardinality', None)
                        if is_func or (max_card is not None and int(max_card) == 1):
                            if len(vals) > 1:
                                msg = f"[CARD_VIOLATION] {ind_name} {prop.name} values={vals} functional={is_func} max_card={max_card}"
                                diagnostics.append(msg)
                        # Also detect datatype mismatches lazily.
                        # Only report when observed values appear to violate the declared range.
                        try:
                            range_info = getattr(prop, 'range', None)
                            if range_info:
                                observed_types = {type(v).__name__ for v in vals}
                                mismatch = False
                                for v in vals:
                                    if isinstance(v, str):
                                        mismatch = mismatch or str not in range_info
                                    elif isinstance(v, bool):
                                        mismatch = mismatch or bool not in range_info
                                    elif isinstance(v, int):
                                        mismatch = mismatch or not any(
                                            isinstance(r, type) and r in {int, float}
                                            for r in range_info
                                        )
                                    elif isinstance(v, float):
                                        mismatch = mismatch or not any(
                                            isinstance(r, type) and r in {int, float}
                                            for r in range_info
                                        )
                                if mismatch:
                                    msg = f"[RANGE_INFO] {ind_name} {prop.name} range={range_info} observed={observed_types}"
                                    diagnostics.append(msg)
                        except Exception:
                            pass
                except Exception as e:
                    diagnostics.append(f"[SCAN ERROR] scanning individual {ind_name}: {e}")
        except Exception as e:
            diagnostics.append(f"[SCAN ERROR] top-level scan failure: {e}")
        # Emit diagnostics to logs for visibility
        for d in diagnostics:
            print(d)
            self._log("Ontology", "WARNING", d)
        return diagnostics

    def _startup_consistency_check(self) -> None:
        self._log("Ontology", "INFO", "Running startup ontology consistency check")
        try:
            output = self._capture_reasoner_output()
            if output.strip():
                self._log("Ontology", "INFO", f"Startup Pellet output:\n{output}")
            self._log("Ontology", "INFO", "Startup ontology consistency check passed")
        except Exception as exc:
            self._log("Ontology", "CRITICAL", f"Startup ontology inconsistency detected: {exc}")
            self._diagnose_inconsistency()

    def _capture_reasoner_output(self) -> str:
        buffer = StringIO()
        try:
            print("[PELLET] starting reasoner call")
            with redirect_stdout(buffer), redirect_stderr(buffer):
                with self.onto:
                    sync_reasoner_pellet(self.world, infer_property_values=True, infer_data_property_values=True, debug=0)
            print("[PELLET] reasoner call completed")
        except Exception as exc:
            buffer.write(f"\n[REASONER EXCEPTION] {exc}\n")
            output = buffer.getvalue()
            raise RuntimeError(output) from exc
        return buffer.getvalue()

    def _run_reasoner(self) -> None:
        if not (self.pellet and self.swrl and self.semantic):
            self._log("Pellet", "INFO", "Pellet reasoning skipped because semantic mode or Pellet engine is disabled")
            self.last_latency = 0.0
            return
        
        if not self._check_ontology_consistency():
            self._log("Pellet", "CRITICAL", "Pellet execution skipped: ontology failed pre-flight consistency check")
            self.last_latency = 0.0
            return
        
        try:
            # Run a diagnostics scan for cardinality/datatype issues before Pellet
            self._log("Pellet", "INFO", "Running pre-Pellet validation scan")
            scan_msgs = self._scan_for_cardinality_violations()
            if scan_msgs:
                self._log("Pellet", "WARNING", f"Pre-Pellet diagnostics found {len(scan_msgs)} potential issues")

            issue_messages: List[str] = []
            issue_messages.extend(self._collect_functional_violations())
            issue_messages.extend(self._collect_datatype_mismatches())
            issue_messages.extend(self._collect_domain_violations())
            issue_messages.extend(self._collect_conflicting_class_memberships())
            issue_messages.extend(scan_msgs)

            if issue_messages:
                print("[PRE-PELLET ABORT] Pre-flight validation found runtime ontology issues")
                for msg in issue_messages:
                    print(msg)
                self._log("Pellet", "CRITICAL", f"Pellet reasoning aborted: {len(issue_messages)} preflight ontology issues detected")
                self.last_latency = 0.0
                return

            self._print_pre_reasoning_diagnostics()
            print("[PELLET START]")
            start = time.perf_counter()
            output = self._capture_reasoner_output()
            self.last_latency = (time.perf_counter() - start) * 1000
            print("[PELLET END]")
            print(f"[PELLET DURATION] {self.last_latency:.0f}ms")
            
            pellet_msg = f"[PELLET]\nreasoning executed successfully in {self.last_latency:.0f}ms"
            print(pellet_msg)
            self._log("Pellet", "INFO", pellet_msg)
            if output.strip():
                self._log("Pellet", "INFO", f"Pellet output:\n{output}")
            self._print_reasoning_diagnostics()
        except Exception as exc:
            self.last_latency = 0.0
            error_str = str(exc)
            output_text = ''
            if isinstance(exc, Exception) and exc.args:
                output_text = str(exc.args[0])
            if "inconsistent" in error_str.lower() or "inconsistency" in error_str.lower():
                self._log("Pellet", "CRITICAL", f"[ONTOLOGY INCONSISTENCY]\nPellet detected inconsistent state: {exc}")
                print(f"[PELLET ERROR] ONTOLOGY INCONSISTENT:\n{exc}")
                if output_text:
                    self._log("Pellet", "CRITICAL", f"Pellet diagnostic output:\n{output_text}")
                    print(f"[PELLET DIAGNOSTIC OUTPUT]\n{output_text}")
                self._diagnose_inconsistency(output_text)
            else:
                self._log("Pellet", "CRITICAL", f"Pellet reasoning failure: {exc}")
                print(f"[PELLET ERROR] {exc}")
    
    def _diagnose_inconsistency(self, debug_output: Optional[str] = None) -> None:
        """Attempt to identify which assertions caused inconsistency."""
        self._log("Ontology", "INFO", "Diagnosing inconsistency...")
        if debug_output:
            self._log("Ontology", "CRITICAL", f"Pellet diagnostic output:\n{debug_output}")
            print(f"[DIAGNOSTIC OUTPUT]\n{debug_output}")
        
        # Check for disjoint class membership
        self._diagnose_disjoint_memberships()
        # Check for property cardinality violations
        self._diagnose_cardinality_violations()
        
        # Check each telemetry-injected individual for suspicious assertions
        for key, definition in self.telemetry_definitions.items():
            if not definition.individual:
                continue
            
            individual_name = definition.individual
            if individual_name not in self.individuals:
                continue
            
            individual = self.individuals[individual_name]
            
            if not definition.property:
                continue
            
            try:
                current_value = getattr(individual, definition.property, [])
                if current_value and len(current_value) > 1:
                    msg = f"[INCONSISTENCY SUSPECT] {individual_name}.{definition.property} has multiple values: {current_value} (should be single-valued)"
                    print(msg)
                    self._log("Ontology", "WARNING", msg)
                elif current_value:
                    val = current_value[0]
                    if definition.nominal:
                        nominal_min, nominal_max = definition.nominal
                        if val < nominal_min - 10 or val > nominal_max + 10:
                            msg = f"[VALUE RANGE] {individual_name}.{definition.property}={val} outside tolerance [{nominal_min}-10, {nominal_max}+10]"
                            print(msg)
                            self._log("Ontology", "WARNING", msg)
            except Exception as e:
                self._log("Ontology", "WARNING", f"Could not diagnose {individual_name}.{definition.property}: {e}")

    def _diagnose_disjoint_memberships(self) -> None:
        for individual_name, individual in self.individuals.items():
            classes = [cls for cls in (getattr(individual, "INDIRECT_is_a", None) or getattr(individual, "is_a", [])) if isinstance(cls, ThingClass)]
            class_names = {cls.name for cls in classes}
            for cls in classes:
                disjoint = getattr(cls, "disjoint_with", []) or []
                for dis in disjoint:
                    dis_name = dis.name if isinstance(dis, ThingClass) else str(dis)
                    if dis_name in class_names:
                        msg = f"[DISJOINTNESS] {individual_name} belongs to disjoint classes {cls.name} and {dis_name}"
                        print(msg)
                        self._log("Ontology", "WARNING", msg)

    def _diagnose_cardinality_violations(self) -> None:
        for key, definition in self.telemetry_definitions.items():
            if not definition.individual or not definition.property:
                continue
            individual_name = definition.individual
            if individual_name not in self.individuals:
                continue
            individual = self.individuals[individual_name]
            try:
                current_value = getattr(individual, definition.property, [])
                if current_value and len(current_value) > 1:
                    prop_obj = self.property_cache.get(definition.property)
                    if prop_obj is not None:
                        func = getattr(prop_obj, "is_functional", False)
                        max_card = getattr(prop_obj, "max_cardinality", None)
                        msg = f"[CARDINALITY] {individual_name}.{definition.property} has {len(current_value)} values"
                        if func:
                            msg += ", property is FunctionalProperty"
                        if max_card is not None:
                            msg += f", max_cardinality={max_card}"
                        print(msg)
                        self._log("Ontology", "WARNING", msg)
            except Exception as e:
                self._log("Ontology", "WARNING", f"Could not inspect cardinality for {individual_name}.{definition.property}: {e}")

    def _print_reasoning_diagnostics(self) -> None:
        print("[REASONING DIAGNOSTICS] Full individual class inference results:")
        for individual_name, individual in sorted(self.individuals.items()):
            direct = [cls.name for cls in getattr(individual, "is_a", []) if isinstance(cls, ThingClass)]
            inferred = [cls.name for cls in getattr(individual, "INDIRECT_is_a", None) or [] if isinstance(cls, ThingClass)]
            print(f"{individual_name}:")
            print("  direct:")
            if direct:
                for cls_name in sorted(direct):
                    print(f"  - {cls_name}")
            else:
                print("  - (none)")
            print("  inferred:")
            if inferred:
                for cls_name in sorted(inferred):
                    print(f"  - {cls_name}")
            else:
                print("  - (none)")

        fault_state_cls = getattr(self.onto, "FaultState", None)
        inferred_faults: Dict[str, List[str]] = {}
        for individual_name, individual in sorted(self.individuals.items()):
            inferred = [cls for cls in getattr(individual, "INDIRECT_is_a", None) or [] if isinstance(cls, ThingClass)]
            fault_state_names = []
            for cls in inferred:
                is_fault_state = False
                try:
                    if fault_state_cls is not None and (cls is fault_state_cls or fault_state_cls in getattr(cls, "ancestors", [])):
                        is_fault_state = True
                except Exception:
                    is_fault_state = False
                if is_fault_state or cls.name.endswith("FaultState") or cls.name.endswith("FailureState"):
                    fault_state_names.append(cls.name)
            if fault_state_names:
                inferred_faults[individual_name] = sorted(set(fault_state_names))

        print("[REASONING DIAGNOSTICS] Inferred FaultState subclasses:")
        if inferred_faults:
            for individual_name, fault_names in inferred_faults.items():
                print(f"{individual_name}:")
                for fault_name in fault_names:
                    print(f"  - {fault_name}")
        else:
            print("  (none)")
        print(f"[REASONING DIAGNOSTICS] FaultState individuals count: {len(inferred_faults)}")

        print("[REASONING DIAGNOSTICS] Telemetry individual property values:")
        for definition in self.telemetry_definitions.values():
            if not definition.individual or not definition.property:
                continue
            if definition.individual not in self.individuals:
                print(f"  {definition.individual}.{definition.property} = INDIVIDUAL_MISSING")
                continue
            individual = self.individuals[definition.individual]
            try:
                value = getattr(individual, definition.property, [])
                print(f"  {definition.individual}.{definition.property} = {value}")
            except Exception as exc:
                print(f"  {definition.individual}.{definition.property} = ERROR {exc}")

        print("[REASONING DIAGNOSTICS] hasFault relations in RDF graph:")
        for subj, pred, obj in self.world.as_rdflib_graph():
            if "hasFault" in str(pred):
                print(f"  {subj} {pred} {obj}")

        print("[REASONING DIAGNOSTICS] hasFault object properties on individuals:")
        for individual_name, individual in sorted(self.individuals.items()):
            if hasattr(individual, "hasFault"):
                try:
                    has_fault_values = getattr(individual, "hasFault", [])
                    if has_fault_values:
                        print(f"  {individual_name}.hasFault = {list(has_fault_values)}")
                except Exception as exc:
                    print(f"  {individual_name}.hasFault ERROR {exc}")
            if hasattr(individual, "INDIRECT_hasFault"):
                try:
                    indirect_has_fault_values = getattr(individual, "INDIRECT_hasFault", [])
                    if indirect_has_fault_values:
                        print(f"  {individual_name}.INDIRECT_hasFault = {list(indirect_has_fault_values)}")
                except Exception as exc:
                    print(f"  {individual_name}.INDIRECT_hasFault ERROR {exc}")

        print("[REASONING DIAGNOSTICS] Loaded SWRL rules:")
        for rule in self.swrl_rules:
            print(f"  {rule.id}: {rule.condition} -> {rule.name}")

    def _extract_state(self, now: int, infer_semantics: bool = False) -> None:
        if infer_semantics:
            self.inferredClasses = self._extract_inferred_classes()
        faults = self._extract_faults(now) if infer_semantics else self.faults
        subsystems = self._build_subsystem_states(faults)
        self.faults = faults
        self.subsystems = subsystems
        self.scenario = self.scenario

    def _refresh_telemetry_metrics(self) -> None:
        for key, definition in self.telemetry_definitions.items():
            subsystem_key = definition.subsystem
            subsystem = self.subsystems.get(subsystem_key)
            if subsystem is None:
                subsystem = SubsystemState(
                    key=subsystem_key,
                    name=self._subsystem_label(subsystem_key),
                    icon=self._subsystem_icon(subsystem_key),
                    status="NOMINAL",
                    metrics={},
                    faultIds=[],
                )
            subsystem.metrics[key] = SubsystemMetric(
                value=definition.value,
                unit=definition.unit,
                label=definition.label,
                nominal=definition.nominal,
            )
            self.subsystems[subsystem_key] = subsystem

    def _extract_inferred_classes(self) -> List[str]:
        classes = set()
        for individual in self.individuals.values():
            # Prefer INDIRECT inferred classes when available to capture Pellet-derived memberships
            inferred = getattr(individual, "INDIRECT_is_a", None) or getattr(individual, "is_a", [])
            for cls in inferred:
                if isinstance(cls, ThingClass):
                    classes.add(cls.name)
        return sorted(classes)

    def _is_fault_class(self, cls: ThingClass, fault_state_cls: Optional[ThingClass] = None) -> bool:
        if not isinstance(cls, ThingClass):
            return False
        try:
            if fault_state_cls is not None and (cls is fault_state_cls or fault_state_cls in self._get_class_ancestors(cls)):
                return True
        except Exception:
            pass
        name = getattr(cls, "name", "")
        if name.endswith("FaultState") or name.endswith("FailureState"):
            return True
        if name.endswith("Fault") or name.endswith("Failure"):
            return True
        if "Fault" in name or "Failure" in name:
            return True
        return False

    def _extract_faults(self, now: int) -> List[FaultEntry]:
        # Prefer explicit `hasFault` assertions inferred by Pellet.
        explicit_faults = self._extract_explicit_faults(now)
        inferred_class_faults = self._extract_faults_from_inferred_classes(now)
        if not explicit_faults:
            return inferred_class_faults

        # Merge explicit and class-inferred faults, avoiding duplicate IDs.
        seen_ids = {fault.id for fault in explicit_faults}
        merged_faults = list(explicit_faults)
        for fault in inferred_class_faults:
            if fault.id not in seen_ids:
                merged_faults.append(fault)
                seen_ids.add(fault.id)
        return merged_faults

    def _extract_explicit_faults(self, now: int) -> List[FaultEntry]:
        results: List[FaultEntry] = []
        real_component_individuals = set(
            defn.individual for defn in self.telemetry_definitions.values() if defn.individual
        )
        for individual_name in real_component_individuals:
            if individual_name not in self.individuals:
                continue
            individual = self.individuals[individual_name]
            if hasattr(individual, "hasFault"):
                for fault in getattr(individual, "hasFault", []):
                    if not fault or not getattr(fault, "name", None):
                        continue
                    severity = "CRITICAL"
                    if hasattr(fault, "hasSeverity") and getattr(fault, "hasSeverity"):
                        severity = str(getattr(fault, "hasSeverity")[0])
                    rule_id = self.fault_rule_map.get(fault.name, "UNKNOWN")
                    evidence = self._build_evidence(individual_name)
                    subsystem = self._component_to_subsystem(individual_name)
                    print(f"[ONTOLOGY INFERENCE]\n{individual_name} hasFault {fault.name}")
                    results.append(FaultEntry(
                        id=f"{individual_name}-{fault.name}",
                        name=fault.name,
                        severity=severity,
                        component=individual_name,
                        swrlRule=rule_id,
                        evidence=evidence,
                        propagationRisk="CRITICAL" if severity == "CRITICAL" else "MEDIUM",
                        timestamp=now,
                        explanation="Inferred by Pellet execution against satellite_full.owl SWRL rules.",
                        hasFault=f"{individual_name} hasFault {fault.name}",
                        subsystem=subsystem,
                    ))

        if not results:
            # Fallback: inspect raw RDF triples for any inferred hasFault relations.
            fault_prop = getattr(self.onto, "hasFault", None)
            if fault_prop is not None and getattr(fault_prop, "iri", None):
                has_fault_uri = rdflib.URIRef(fault_prop.iri)
                for subj, _, obj in self.world.as_rdflib_graph().triples((None, has_fault_uri, None)):
                    if not isinstance(subj, rdflib.URIRef) or not isinstance(obj, rdflib.URIRef):
                        continue
                    individual_name = subj.split("#")[-1]
                    fault_name = obj.split("#")[-1]
                    if individual_name not in self.individuals:
                        continue
                    severity = "CRITICAL"
                    rule_id = self.fault_rule_map.get(fault_name, "UNKNOWN")
                    evidence = self._build_evidence(individual_name)
                    subsystem = self._component_to_subsystem(individual_name)
                    print(f"[RDF INFERENCE]\n{individual_name} hasFault {fault_name}")
                    results.append(FaultEntry(
                        id=f"{individual_name}-{fault_name}",
                        name=fault_name,
                        severity=severity,
                        component=individual_name,
                        swrlRule=rule_id,
                        evidence=evidence,
                        propagationRisk="CRITICAL",
                        timestamp=now,
                        explanation="Inferred by raw RDF hasFault triple extraction.",
                        hasFault=f"{individual_name} hasFault {fault_name}",
                        subsystem=subsystem,
                    ))
        return results

    def _extract_faults_from_inferred_classes(self, now: int) -> List[FaultEntry]:
        results: List[FaultEntry] = []
        real_component_individuals = set(
            defn.individual for defn in self.telemetry_definitions.values() if defn.individual
        )
        # Try to resolve the canonical FaultState class from the ontology
        fault_state_cls = getattr(self.onto, "FaultState", None)
        if fault_state_cls is None:
            # fallback: search by name among ontology classes
            for c in self.onto.classes():
                if c.name == "FaultState":
                    fault_state_cls = c
                    break
        for individual_name in real_component_individuals:
            if individual_name not in self.individuals:
                continue
            individual = self.individuals[individual_name]
            inferred = getattr(individual, "INDIRECT_is_a", None) or getattr(individual, "is_a", [])
            for cls in inferred:
                if not isinstance(cls, ThingClass):
                    continue
                if not self._is_fault_class(cls, fault_state_cls):
                    continue
                fault_name = cls.name
                rule_id = self.fault_rule_map.get(fault_name, "CLASS_INFERENCE")
                severity = "CRITICAL" if "Critical" in fault_name or "Failure" in fault_name else "WARNING"
                evidence = self._build_evidence(individual_name)
                subsystem = self._component_to_subsystem(individual_name)
                print(f"[CLASS INFERENCE]\n{individual_name} is a {fault_name}")
                results.append(FaultEntry(
                    id=f"{individual_name}-{fault_name}",
                    name=fault_name,
                    severity=severity,
                    component=individual_name,
                    swrlRule=rule_id,
                    evidence=evidence,
                    propagationRisk="CRITICAL" if severity == "CRITICAL" else "MEDIUM",
                    timestamp=now,
                    explanation="Fault inferred from Pellet class reasoning fallback.",
                    hasFault=f"{individual_name} is a {fault_name}",
                    subsystem=subsystem,
                ))
        return results

    def _build_evidence(self, individual_name: str) -> str:
        evidence_items = []
        for key, definition in self.telemetry_definitions.items():
            if definition.individual == individual_name:
                evidence_items.append(f"{key}={definition.value}{definition.unit}")
        return ", ".join(evidence_items) or "ontology-synchronized telemetry"

    def _component_to_subsystem(self, component_name: str) -> str:
        mapping = {
            "Battery_01": "power",
            "SolarArray_01": "power",
            "PCDU_01": "power",
            "BusLine_01": "power",
            "OBC_01": "obc",
            "TTCAntenna_01": "comm",
            "Antenna_01": "comm",
            "Comm_01": "comm",
            "GYRO_01": "aocs",
            "RW_01": "aocs",
            "AC_01": "aocs",
            "STR_01": "aocs",
            "GNSS_01": "aocs",
            "MAG_01": "aocs",
            "THR_01": "aocs",
            "Thermal_01": "thermal",
            "Heater_01": "thermal",
            "Frame_01": "structure",
            "Structure_01": "structure",
            "SolarPanel_01": "structure",
            "Mount_01": "structure",
        }
        return mapping.get(component_name, "power")

    def _build_subsystem_states(self, faults: List[FaultEntry]) -> Dict[str, SubsystemState]:
        subsystems: Dict[str, SubsystemState] = {}
        for key, definition in self.telemetry_definitions.items():
            subsystem = definition.subsystem
            subsystems.setdefault(subsystem, SubsystemState(
                key=subsystem,
                name=self._subsystem_label(subsystem),
                icon=self._subsystem_icon(subsystem),
                status="NOMINAL",
                metrics={},
                faultIds=[],
            ))
            subsystems[subsystem].metrics[key] = SubsystemMetric(
                value=definition.value,
                unit=definition.unit,
                nominal=definition.nominal,
                label=definition.label,
            )

        for fault in faults:
            sub = fault.subsystem
            if sub not in subsystems:
                subsystems[sub] = SubsystemState(
                    key=sub,
                    name=self._subsystem_label(sub),
                    icon=self._subsystem_icon(sub),
                    status="NOMINAL",
                    metrics={},
                    faultIds=[],
                )
            subsystems[sub].faultIds.append(fault.id)
            if fault.severity == "CRITICAL":
                subsystems[sub].status = "CRITICAL"
            elif fault.severity == "WARNING" and subsystems[sub].status != "CRITICAL":
                subsystems[sub].status = "WARNING"
            elif subsystems[sub].status == "NOMINAL":
                subsystems[sub].status = "DEGRADED"

        for sub in subsystems.values():
            if sub.status == "NOMINAL" and sub.faultIds:
                sub.status = "DEGRADED"
        return subsystems

    def _subsystem_label(self, key: str) -> str:
        return {
            "power": "Power System",
            "thermal": "Thermal System",
            "comm": "Communication",
            "aocs": "AOCS",
            "obc": "OBC System",
            "structure": "Structure",
        }.get(key, key.title())

    def _subsystem_icon(self, key: str) -> str:
        return {
            "power": "⚡",
            "thermal": "🌡",
            "comm": "📡",
            "aocs": "🛰",
            "obc": "🧠",
            "structure": "🏗",
        }.get(key, "◉")

    def _log(self, category: str, severity: str, message: str) -> None:
        entry = LogEntry(
            id=str(uuid.uuid4()),
            timestamp=int(time.time() * 1000),
            category=category,
            severity=severity,
            message=message,
        )
        self.logs.appendleft(entry)

    def _reset(self) -> None:
        self.scenario = "Normal Operation"
        self.pellet = True
        self.swrl = True
        self.semantic = True
        self.propagation = True
        self.ontologySync = "SYNCED"
        self.last_latency = 0.0
        for definition in self.telemetry_definitions.values():
            definition.value = float(definition.value)
        self._log("System", "INFO", "System reset and ontology synchronization initialized")

    def _resync(self) -> None:
        self.ontologySync = "SYNCING"
        self._log("Ontology", "INFO", "Ontology resynchronization initiated")
        time.sleep(0.8)
        self.ontologySync = "SYNCED"
        self._log("Ontology", "INFO", "Ontology synchronized successfully")

    def set_scenario(self, scenario: str) -> None:
        self.scenario = scenario
        self._scenario_cycle_count = 0
        self._log("System", "INFO", f"Scenario set to {scenario}")

    def set_toggle(self, name: str, value: bool) -> None:
        if name == "pellet":
            self.pellet = value
        elif name == "swrl":
            self.swrl = value
        elif name == "semantic":
            self.semantic = value
        elif name == "propagation":
            self.propagation = value
        self._log("System", "INFO", f"Toggle {name} set to {value}")

    def get_inspection(self) -> OntologyInspect:
        return OntologyInspect(
            classes=self.classes,
            subclasses=self.subclasses,
            individuals=sorted(self.individuals.keys()),
            datatypeProperties=self.data_properties,
            objectProperties=self.object_properties,
            swrlRules=self.swrl_rules,
        )

    def get_cached_state(self) -> OntologyState:
        with self._cached_state_lock:
            if self._cached_state is not None:
                return self._cached_state
        print("[CACHE] no cached state available, acquiring direct snapshot lock")
        with self.lock:
            print("[CACHE] [LOCK ACQUIRED] building direct snapshot")
            snapshot = self._build_state_snapshot()
            print("[CACHE] [LOCK RELEASED] direct snapshot built")
        return snapshot

    def _build_state_snapshot(self) -> OntologyState:
        now = int(time.time() * 1000)
        return OntologyState(
            bootedAt=self.bootedAt,
            now=now,
            satellite=self._compute_satellite_status(),
            subsystems=self.subsystems,
            faults=self.faults,
            logs=list(self.logs),
            telemetry=list(self.telemetry_frames),
            series=dict(self.series),
            scenario=self.scenario,
            pellet=self.pellet,
            swrl=self.swrl,
            semantic=self.semantic,
            propagation=self.propagation,
            speed=self.speed,
            reasoningLatency=self.last_latency,
            ontologySync=self.ontologySync,
            individuals=sorted(self.individuals.keys()),
            inferredClasses=self.inferredClasses,
            swrlRules=self.swrl_rules,
        )

    def _update_cached_state(self) -> None:
        print("[CACHE] acquiring snapshot copy lock")
        with self.lock:
            print("[CACHE] [LOCK ACQUIRED] copying snapshot data")
            bootedAt = self.bootedAt
            satellite = self._compute_satellite_status()
            subsystems = dict(self.subsystems)
            faults = list(self.faults)
            logs = list(self.logs)
            telemetry = list(self.telemetry_frames)
            # Append derived metrics so charts stay aligned with reasoning snapshots
            try:
                # Record current active fault count and reasoning latency into series
                self._append_series("activeFaults", float(len(faults)))
                self._append_series("reasoningLatency", float(self.last_latency))
            except Exception:
                # Ensure caching proceeds even if series append fails
                pass
            series = dict(self.series)
            scenario = self.scenario
            pellet = self.pellet
            swrl = self.swrl
            semantic = self.semantic
            propagation = self.propagation
            speed = self.speed
            reasoningLatency = self.last_latency
            ontologySync = self.ontologySync
            individuals = sorted(self.individuals.keys())
            inferredClasses = list(self.inferredClasses)
            swrlRules = self.swrl_rules
            print("[CACHE] [LOCK RELEASED] snapshot copy complete")
        print(f"[CACHE] [SNAPSHOT] faults={len(faults)} inferredClasses={len(inferredClasses)} subystems={len(subsystems)}")
        snapshot = OntologyState(
            bootedAt=bootedAt,
            now=int(time.time() * 1000),
            satellite=satellite,
            subsystems=subsystems,
            faults=faults,
            logs=logs,
            telemetry=telemetry,
            series=series,
            scenario=scenario,
            pellet=pellet,
            swrl=swrl,
            semantic=semantic,
            propagation=propagation,
            speed=speed,
            reasoningLatency=reasoningLatency,
            ontologySync=ontologySync,
            individuals=individuals,
            inferredClasses=inferredClasses,
            swrlRules=swrlRules,
        )
        with self._cached_state_lock:
            self._cached_state = snapshot

    def _background_telemetry_loop(self) -> None:
        self._log("System", "INFO", f"Background telemetry loop started ({TELEMETRY_INTERVAL_SECONDS}-second interval)")
        print("[TELEMETRY LOOP] Main loop entering while loop")
        cycle = 0
        while self._background_telemetry_running:
            cycle += 1
            print(f"[TELEMETRY LOOP] Cycle {cycle}")
            try:
                print(f"[TELEMETRY LOOP] Cycle {cycle}: acquiring lock...")
                # Inject telemetry under lock to ensure consistent writes for this cycle
                with self.lock:
                    print(f"[TELEMETRY LOOP] Cycle {cycle}: [LOCK ACQUIRED] injecting telemetry")
                    self._inject_scenario_telemetry(int(time.time() * 1000))
                    print(f"[TELEMETRY LOOP] Cycle {cycle}: [LOCK RELEASED] telemetry injection complete")

                # Refresh metrics and update cache (non-ontology state)
                print(f"[TELEMETRY LOOP] Cycle {cycle}: lock released, refreshing telemetry metrics only...")
                self._refresh_telemetry_metrics()
                print(f"[TELEMETRY LOOP] Cycle {cycle}: [SEMANTIC PRESERVED] faults={len(self.faults)} inferredClasses={len(self.inferredClasses)}")
                self._update_cached_state()
                self._auto_rotate_scenario_if_needed(cycle)

                # If we've completed the configured number of telemetry cycles, perform
                # a deterministic reasoning phase: freeze ontology state, run Pellet on
                # the exact snapshot, extract inferred state, update cache, then resume.
                if cycle % TELEMETRY_CYCLES_BEFORE_REASONING == 0 and self.pellet and self.swrl and self.semantic:
                    print(f"[TELEMETRY LOOP] Cycle {cycle}: Reached {TELEMETRY_CYCLES_BEFORE_REASONING} cycles — initiating deterministic reasoning phase")
                    # Acquire lock to prevent any telemetry writes during reasoning
                    with self.lock:
                        try:
                            print(f"[TELEMETRY LOOP] Cycle {cycle}: [REASONING LOCK ACQUIRED] running Pellet on frozen snapshot")
                            # Pre-flight consistency check
                            if self._check_ontology_consistency():
                                # Run diagnostics scan to report any cardinality/datatype issues
                                scan_msgs = self._scan_for_cardinality_violations()
                                if scan_msgs:
                                    self._log("Pellet", "WARNING", f"Deterministic pre-Pellet scan found {len(scan_msgs)} potential issues")

                                # Print extended pre-reasoning diagnostics in the actual telemetry reasoning path
                                self._print_pre_reasoning_diagnostics()

                                start = time.perf_counter()
                                output = self._capture_reasoner_output()
                                self.last_latency = (time.perf_counter() - start) * 1000
                                self._log("Pellet", "INFO", f"Deterministic Pellet executed in {self.last_latency:.0f}ms")
                                if output.strip():
                                    self._log("Pellet", "INFO", f"Pellet output:\n{output}")
                            else:
                                self._log("Pellet", "CRITICAL", "Deterministic Pellet skipped: pre-flight check failed")

                            # Extract semantic state from the frozen ontology after reasoning
                            print(f"[TELEMETRY LOOP] Cycle {cycle}: [REASONING COMPLETE] extracting semantic state")
                            self._print_reasoning_diagnostics()
                            self._extract_state(int(time.time() * 1000), infer_semantics=True)
                            print(f"[TELEMETRY LOOP] Cycle {cycle}: [INFERRED CLASSES COUNT] {len(self.inferredClasses)}")
                            print(f"[TELEMETRY LOOP] Cycle {cycle}: [INFERRED fault count] {len(self.faults)}")
                            print(f"[TELEMETRY LOOP] Cycle {cycle}: [REASONING LOCK RELEASED]")
                        except Exception as exc:
                            self._log("System", "CRITICAL", f"Deterministic reasoning exception: {exc}\n{traceback.format_exc()}")
                            print(f"[TELEMETRY LOOP DETERMINISTIC ERROR] {exc}")
                            print(traceback.format_exc())

                    # Update cached snapshot so frontend reads only from completed semantic snapshot
                    print(f"[TELEMETRY LOOP] Cycle {cycle}: updating cached state with deterministic inference")
                    self._update_cached_state()
                    print(f"[TELEMETRY LOOP] Cycle {cycle}: deterministic reasoning phase complete — resuming telemetry cycles")
                else:
                    print(f"[TELEMETRY LOOP] Cycle {cycle}: COMPLETE")
            except Exception as e:
                self._log("System", "CRITICAL", f"Telemetry loop exception: {e}")
                print(f"[TELEMETRY LOOP ERROR] {e}")
            time.sleep(TELEMETRY_INTERVAL_SECONDS)
        self._log("System", "INFO", "Background telemetry loop stopped")

    def _background_reasoning_loop(self) -> None:
        # Deprecated: deterministic reasoning is now coordinated inside the telemetry loop
        self._log("System", "INFO", "Background reasoning loop deprecated; reasoning performed deterministically from telemetry loop")
        return

    def start_background_loop(self) -> None:
        if self._background_telemetry_running or self._background_reasoning_running:
            self._log("System", "WARNING", "Background loops already running")
            return
        self._background_telemetry_running = True
        # Reasoning is coordinated deterministically inside the telemetry loop
        self._background_reasoning_running = False
        self._background_telemetry_thread = threading.Thread(target=self._background_telemetry_loop, daemon=True)
        self._background_telemetry_thread.start()
        # Do not start a separate reasoning thread; deterministic reasoning runs
        # after a configured number of telemetry cycles inside the telemetry loop.
        self._background_reasoning_thread = None
        self._log("System", "INFO", "Background telemetry loop started (deterministic reasoning integrated)")

    def stop_background_loop(self) -> None:
        if not self._background_telemetry_running and not self._background_reasoning_running:
            return
        self._background_telemetry_running = False
        self._background_reasoning_running = False
        if self._background_telemetry_thread is not None:
            self._background_telemetry_thread.join(timeout=5)
        if self._background_reasoning_thread is not None:
            self._background_reasoning_thread.join(timeout=5)
        self._log("System", "INFO", "Background telemetry and reasoning loops stopped")

    def _compute_satellite_status(self) -> str:
        if any(f.name == "SafeMode" or f.name.endswith("SafeMode_01") for f in self.faults):
            return "SAFE MODE"
        # Inferred class extraction is disabled during stability testing to avoid concurrent Owlready2 traversal
        if any(f.severity == "CRITICAL" for f in self.faults):
            return "CRITICAL"
        if any(f.severity == "WARNING" for f in self.faults):
            return "WARNING"
        if self.ontologySync != "SYNCED":
            return "DEGRADED"
        return "NOMINAL"


engine: Optional[OntologyEngine] = None


@app.on_event("startup")
def startup_event() -> None:
    global engine
    print("[STARTUP] loading ontology...")
    engine = OntologyEngine(ONTOLOGY_PATH)
    print("[STARTUP] ontology loaded")
    print("[STARTUP] skipping startup consistency validation for responsiveness")
    print("Loaded ontology classes...", len(engine.classes))
    print("Loaded SWRL rules...", len(engine.swrl_rules))
    engine._log("System", "INFO", "Ontology service started - background telemetry and reasoning loops enabled")
    engine._extract_state(int(time.time() * 1000), infer_semantics=True)
    engine._update_cached_state()
    engine.start_background_loop()
    print("[STARTUP] background telemetry and reasoning loops started")


@app.on_event("shutdown")
def shutdown_event() -> None:
    global engine
    if engine is not None:
        engine.stop_background_loop()


@app.get("/api/inspect", response_model=OntologyInspect)
def inspect_ontology() -> OntologyInspect:
    if engine is None:
        raise RuntimeError("Ontology engine not initialized")
    return engine.get_inspection()


@app.get("/api/state", response_model=OntologyState)
def get_state() -> OntologyState:
    if engine is None:
        raise RuntimeError("Ontology engine not initialized")
    return engine.get_cached_state()


class ControlRequest(BaseModel):
    action: str
    payload: Optional[Dict[str, Any]] = None


@app.post("/api/control")
def control(request: ControlRequest = Body(...)) -> Dict[str, str]:
    if engine is None:
        return {"status": "engine-not-initialized"}
    applied = False
    if request.action == "reset":
        engine._reset()
        applied = True
    elif request.action == "reason":
        engine._run_reasoner()
        applied = True
    elif request.action == "resync":
        engine._resync()
        applied = True
    elif request.action == "scenario":
        scenario = request.payload and request.payload.get("scenario")
        if scenario:
            engine.set_scenario(str(scenario))
            applied = True
    elif request.action == "toggle":
        name = request.payload and request.payload.get("name")
        value = request.payload and request.payload.get("value")
        if name and isinstance(value, bool):
            engine.set_toggle(str(name), value)
            applied = True
    else:
        return {"status": "unknown action"}
    if applied:
        engine._update_cached_state()
    return {"status": "ok"}
