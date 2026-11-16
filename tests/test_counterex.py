import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from counterex.problems import generate_cases, oracle, validate
from counterex.runner import run_python
from counterex.stress import repair_prompt, stress

ROOT = Path(__file__).resolve().parents[1]


class ProblemTests(unittest.TestCase):
    def test_known_derangements(self):
        self.assertEqual([oracle("derangements", {"n": n}) for n in range(9)],
                         [1, 0, 1, 2, 9, 44, 265, 1854, 14833])

    def test_pairs_known_answers(self):
        for case, expected in [({"a": [], "k": 1}, 0),
                               ({"a": [0, 0, 0], "k": 2}, 3),
                               ({"a": [-1, 1, 2], "k": 3}, 2)]:
            self.assertEqual(oracle("divisible_pairs", case), expected)

    def test_invalid_cases(self):
        for problem, case in [("derangements", {"n": -1}), ("derangements", {"n": 9}),
                              ("derangements", {"n": True}), ("divisible_pairs", {"a": [1], "k": 0}),
                              ("divisible_pairs", {"a": [True], "k": 1}),
                              ("divisible_pairs", {"a": [1] * 9, "k": 1})]:
            with self.subTest(case=case), self.assertRaises(ValueError):
                validate(problem, case)

    def test_reproducible_valid_generation(self):
        a = generate_cases("divisible_pairs", 17, 100)
        self.assertEqual(a, generate_cases("divisible_pairs", 17, 100))
        self.assertNotEqual(a, generate_cases("divisible_pairs", 18, 100))
        for case in a:
            validate("divisible_pairs", case)

    def test_invalid_generator_configuration(self):
        for problem, count in [("unknown", 1), ("derangements", -1)]:
            with self.assertRaises(ValueError):
                generate_cases(problem, random_cases=count)


class RunnerTests(unittest.TestCase):
    def execute(self, source, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "candidate.py"
            file.write_text(source, encoding="utf-8")
            return run_python(file, {"n": 3}, trusted=True, **kwargs)

    def test_integer_protocol(self):
        self.assertEqual(self.execute("import json,sys; print(json.load(sys.stdin)['n'])").value, 3)

    def test_reject_non_integer_or_extra_output(self):
        for output in ["true", "1.0", "null", "[1]", "debug\\n2"]:
            with self.subTest(output=output):
                self.assertEqual(self.execute(f"print({output!r})").status, "invalid_output")

    def test_runtime_and_syntax_errors(self):
        for source in ["raise RuntimeError('example')", "def broken(:"]:
            self.assertEqual(self.execute(source).status, "runtime_error")

    def test_timeout(self):
        self.assertEqual(self.execute("while True: pass", timeout=0.2).status, "timeout")

    def test_output_limit(self):
        self.assertEqual(self.execute("print('x' * 100000)", output_limit=1024).status, "output_limit")

    def test_trust_required(self):
        with self.assertRaises(ValueError):
            run_python(ROOT / "examples/derangements_fixed.py", {"n": 3})

    def test_invalid_timeout(self):
        for timeout in [0, -1, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                self.execute("print(1)", timeout=timeout)


class PipelineTests(unittest.TestCase):
    def test_finds_both_planted_bugs_and_builds_feedback(self):
        for problem, case, expected, actual in [
            ("divisible_pairs", {"a": [1, 2], "k": 3}, 1, 2),
            ("derangements", {"n": 3}, 2, 4),
        ]:
            candidate = ROOT / "examples" / f"{problem}_buggy.py"
            report = stress(problem, candidate, trusted=True)
            failure = report["failure"]
            self.assertEqual(failure["input"], case)
            self.assertEqual((failure["expected"], failure["actual"]), (expected, actual))
            self.assertEqual(failure["kind"], "wrong_answer")
            self.assertIn('"expected"', repair_prompt(report, candidate.read_text()))

    def test_corrected_candidates_pass(self):
        for problem in ["divisible_pairs", "derangements"]:
            report = stress(problem, ROOT / "examples" / f"{problem}_fixed.py", trusted=True)
            self.assertEqual(report["status"], "passed_tests")
            self.assertEqual(report["cases_passed"], report["cases_available"])
            with self.assertRaises(ValueError):
                repair_prompt(report, "")

    def test_cli_exit_codes_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            args = [sys.executable, "-m", "counterex", "check", "--problem", "derangements",
                    "--candidate", str(ROOT / "examples/derangements_buggy.py"), "--output", directory]
            untrusted = subprocess.run(args, cwd=ROOT, capture_output=True)
            self.assertEqual(untrusted.returncode, 2)
            failed = subprocess.run(args + ["--trusted-code"], cwd=ROOT, capture_output=True)
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(json.loads((Path(directory) / "report.json").read_text())["status"], "failed")
            self.assertTrue((Path(directory) / "repair_prompt.txt").exists())
            args[args.index("--candidate") + 1] = str(ROOT / "examples/derangements_fixed.py")
            passed = subprocess.run(args + ["--trusted-code"], cwd=ROOT, capture_output=True)
            self.assertEqual(passed.returncode, 0)
            self.assertFalse((Path(directory) / "repair_prompt.txt").exists())


if __name__ == "__main__":
    unittest.main()
