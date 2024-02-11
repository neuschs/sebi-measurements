import json
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Dict
from pymeasure.adapters import Adapter, VISAAdapter


@dataclass_json
@dataclass
class Offset:
    delay: float
    z0: float
    loss: float


@dataclass_json
@dataclass
class Standard:
    id: int
    label: str
    type: str
    medium: str
    min_frequency: float
    max_frequency: float
    offset: Offset
    coefficients: Dict[str, float]
    load_type: str


@dataclass_json
@dataclass
class Assignment:
    assignments: List[int]
    label: str


@dataclass_json
@dataclass
class CalibrationKit:
    label: str
    serial_number: str
    description: str
    standards: List[Standard]
    class_assignments: Dict[str, Assignment]


def check_vna(adapter: Adapter):
    if "8720A" in adapter.ask("OUTPIDEN"):
        return True
    else:
        return False


LOAD_TYPES = {"fixed": "FIXE", "sliding": "SLIL"}
STANDARD_TYPES = {"short": "STDTSHOR", "load": "STDTLOAD", "open": "STDTOPEN", "arbitrary": "STDTARBI",
                  "thru": "STDTDELA"}


def load_standard(adapter: Adapter, standard: Standard):
    assert 1 <= standard.id <= 8
    adapter.write(f"DEFS{standard.id}")
    assert standard.type.lower() in STANDARD_TYPES.keys()
    adapter.write(STANDARD_TYPES[standard.type])
    adapter.write(f"OFSD {standard.offset.delay * 1e15}FS")
    adapter.write(f"OFSL {standard.offset.loss}")
    adapter.write(f"OFSZ {standard.offset.z0}")
    adapter.write(f"MINF {standard.min_frequency}")
    adapter.write(f"MAXF {standard.max_frequency}")
    assert (standard.medium == "coax") or (standard.medium == "wave")
    adapter.write(str(standard.medium).upper())
    assert 1 <= len(standard.label) <= 10
    adapter.write(f"LABS \"{standard.label}\"")

    # hp 8720a supports only capacitive coefficients
    if standard.type.lower() == "open":
        assert len(standard.coefficients) == 4
        adapter.write(f"C0 {standard.coefficients['cl0']}")
        adapter.write(f"C1 {standard.coefficients['cl1']}")
        adapter.write(f"C2 {standard.coefficients['cl2']}")
        adapter.write(f"C3 {standard.coefficients['cl3']}")
    elif standard.type.lower() == "load":
        assert standard.load_type.lower() in LOAD_TYPES.keys()
        adapter.write(LOAD_TYPES[standard.load_type.lower()])
    adapter.write("STDD")


CLASS_TYPES = ["S11A", "S11B", "S11C", "S22A", "S22B", "S22C",
               "FWDT", "REVT", "FWDM", "REVM", "RESP", "RESI"]


def load_class_assignment(adapter: Adapter, _class: str, assignment: Assignment):
    assert _class in CLASS_TYPES
    adapter.write(f"SPEC{_class} {','.join(map(str, assignment.assignments))}")
    adapter.write("CLAD")
    assert 1 <= len(assignment.label) <= 10
    adapter.write(f"LABE{_class} \"{assignment.label}\"")


if __name__ == "__main__":
    resource_str = "GPIB0::16::INSTR"
    cal_file_path = "../calibration/kirkby_0776.json"

    adapter = VISAAdapter(resource_name=resource_str)

    if not check_vna(adapter):
        raise Exception("Error no VNA reachable !")

    cal_kit: CalibrationKit
    with open(cal_file_path) as file:
        file_content = file.read()
        CalibrationKit.schema().loads(file_content)
        cal_kit = CalibrationKit.from_json(file_content)

    if 1 > len(cal_kit.standards) > 8:
        raise Exception("Only 1..8 standards are allowed on a HP 8720A")

    for standard in cal_kit.standards:
        load_standard(adapter, standard)

    for _class, assignment in cal_kit.class_assignments.items():
        load_class_assignment(adapter, _class, assignment)

    adapter.write(f"LABK \"{cal_kit.label}\"")
    adapter.write("KITD")
    adapter.write("ENTO")
