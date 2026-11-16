import argparse
import json
from pathlib import Path
import sys

from .problems import DESCRIPTIONS
from .stress import repair_prompt, stress


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CounterEx milestone 1: trusted-code stress testing")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Run bundled, reviewed buggy and fixed examples")
    demo.add_argument("--output", type=Path, default=Path("runs/demo"))
    check = commands.add_parser("check", help="Stress-test a reviewed Python candidate")
    check.add_argument("--problem", choices=DESCRIPTIONS, required=True)
    check.add_argument("--candidate", type=Path, required=True)
    check.add_argument("--trusted-code", action="store_true", help="Acknowledge local execution is not sandboxed")
    check.add_argument("--output", type=Path, default=Path("runs/check"))
    check.add_argument("--seed", type=int, default=42)
    check.add_argument("--random-cases", type=int, default=50)
    check.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            report = stress(args.problem, args.candidate, seed=args.seed,
                            random_cases=args.random_cases, timeout=args.timeout, trusted=args.trusted_code)
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            prompt_path = args.output / "repair_prompt.txt"
            if report["failure"]:
                prompt_path.write_text(repair_prompt(report, args.candidate.read_text(encoding="utf-8")), encoding="utf-8")
            elif prompt_path.exists():
                prompt_path.unlink()
            print(json.dumps(report, indent=2))
            return 1 if report["failure"] else 0
        examples = Path(__file__).resolve().parent.parent / "examples"
        args.output.mkdir(parents=True, exist_ok=True)
        reports = []
        for problem in DESCRIPTIONS:
            for version in ("buggy", "fixed"):
                candidate = examples / f"{problem}_{version}.py"
                report = stress(problem, candidate, trusted=True)
                reports.append(report)
                if report["failure"]:
                    (args.output / f"{problem}_repair_prompt.txt").write_text(
                        repair_prompt(report, candidate.read_text(encoding="utf-8")), encoding="utf-8")
                print(f"{problem} / {version}: {report['status']} ({report['cases_passed']}/{report['cases_executed']} passed)")
        (args.output / "demo_report.json").write_text(json.dumps({
            "demo_type": "handwritten_fixtures_no_llm", "reports": reports}, indent=2) + "\n", encoding="utf-8")
        return 0 if all(r["status"] == ("failed" if i % 2 == 0 else "passed_tests")
                        for i, r in enumerate(reports)) else 1
    except (OSError, ValueError) as error:
        print(f"counterex: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
