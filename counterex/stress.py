"""Compare candidates against reviewed oracles and produce repair feedback."""

import hashlib
import json
from pathlib import Path

from .problems import DESCRIPTIONS, generate_cases, oracle
from .runner import run_python


def stress(problem: str, candidate: Path, *, seed: int = 42,
           random_cases: int = 50, timeout: float = 2.0, trusted: bool = False) -> dict:
    candidate = Path(candidate)
    cases = generate_cases(problem, seed, random_cases)
    report = {
        "schema_version": 1, "problem": problem, "candidate": candidate.name,
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "seed": seed, "random_cases_requested": random_cases, "timeout_seconds": timeout,
        "oracle": "reviewed_brute_force_v1", "cases_available": len(cases),
        "cases_executed": 0, "cases_passed": 0,
        "status": "passed_tests", "failure": None,
    }
    for index, case in enumerate(cases):
        expected = oracle(problem, case)
        result = run_python(candidate, case, timeout=timeout, trusted=trusted)
        report["cases_executed"] += 1
        if result.status != "ok" or result.value != expected:
            report["status"] = "failed"
            report["failure"] = {"case_index": index, "input": case,
                                 "expected": expected, "actual": result.value,
                                 "kind": "wrong_answer" if result.status == "ok" else result.status,
                                 "execution": result.to_dict()}
            break
        report["cases_passed"] += 1
    return report


def repair_prompt(report: dict, source: str) -> str:
    if report["failure"] is None:
        raise ValueError("A repair prompt requires a failing test")
    return ("Repair the Python program using the observed failure. Return only Python source.\n"
            "Read one JSON object from stdin and print one JSON integer to stdout.\n"
            "Passing these tests is not a proof of correctness on larger inputs.\n\n"
            f"Problem: {DESCRIPTIONS[report['problem']]}\n"
            f"Observed failure:\n{json.dumps(report['failure'], indent=2)}\n\n"
            f"Current program:\n```python\n{source}\n```\n")
