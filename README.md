# Counter-Ex

Guided repair for small LLMs on competitive programming and mathematics.

**Milestone 1: executable verification foundation.** This initial implementation
targets roughly 10–20% of the project scope. That is a planning estimate, not a
measured percentage of research completed.

CounterEx aims to find bugs by comparing a candidate program with a small
brute-force oracle, then send a counterexample back to a model for repair.
This release implements the test-and-feedback portion, using reviewed oracles
and handwritten candidate fixtures. It does not call or train an LLM.

## Run it

Requires Python 3.11 or newer. No third-party packages, GPU, API key, or dataset
download is needed. Run these commands from this folder:

```powershell
python -m counterex demo
python -m unittest discover -s tests -v
```

The demo runs buggy and corrected versions of both roadmap examples:

```text
divisible_pairs / buggy: failed (2/3 passed)
divisible_pairs / fixed: passed_tests (56/56 passed)
derangements / buggy: failed (3/4 passed)
derangements / fixed: passed_tests (9/9 passed)
```

Inspect `runs/demo/demo_report.json` and the two repair prompt text files.
The corrected programs are supplied fixtures, not model-generated repairs.
The demo exits successfully when it finds the planted bugs and the corrected
programs pass. These are software smoke tests, not benchmark or repair-rate results.

## Check a reviewed candidate

```powershell
python -m counterex check --problem divisible_pairs --candidate examples/divisible_pairs_buggy.py --trusted-code --seed 42 --random-cases 50 --output runs/my-check
```

A candidate reads one JSON object from stdin and prints one JSON integer.
Each test runs in a fresh Python process. Exit codes: `0` means all generated
tests passed, `1` means a test failed, and `2` means an input or configuration error.
The command writes `report.json` and, upon failure, `repair_prompt.txt`.
Fix the candidate manually and rerun the same command to replay the test suite.

### Example counterexamples

| Problem | Input | Expected | Buggy output | Cause |
| --- | --- | --- | --- | --- |
| Divisible pairs | `{"a": [1, 2], "k": 3}` | 1 | 2 | Counts both `(i,j)` and `(j,i)` |
| Derangements | `{"n": 3}` | 2 | 4 | Uses the incorrect formula `n! - (n-1)!` |

`passed_tests` only means agreement on the tested small inputs. It does not
establish correctness or performance for the original large constraints.

## Implemented

- Input validation and seeded case generation, including edge cases.
- O(n²) pair-count oracle and exhaustive permutation oracle for n <= 8.
- Local runner with timeout, captured diagnostics, and output monitoring.
- Distinct wrong-answer, timeout, runtime-error, invalid-output, and output-limit results.
- First-counterexample reports with seed, candidate SHA-256 and test counts.
- Repair prompt construction and runnable examples in both project domains.
- Unit/integration tests and GitHub Actions configuration.

## Execution boundary

**Only execute code you have reviewed and trust.** The local runner is not a
security sandbox. A temporary working directory and Python `-I` do not block
filesystem access, network access, or process spawning. There is no memory limit
or process-tree containment. Output is monitored periodically, so disk writes
can exceed the threshold between polls. The runner stops its direct child only.
The demo automatically runs the bundled reviewed fixtures. Arbitrary candidate
execution requires `--trusted-code`.

Before integrating model-generated programs, implement and test an isolated
execution service with network disabled, restricted filesystem access, memory/CPU
quotas and process-tree cleanup. Do not feed unreviewed model output to this runner.

## Project layout

```text
counterex/       input validation, oracles, runner, stress engine, CLI
examples/        intentionally buggy and corrected reference candidates
tests/           correctness and failure-path tests
docs/            scope, architecture, next steps and Git instructions
evidence/        recorded demo output from this milestone
.github/         automated test workflow
```

See [the milestone plan](docs/MILESTONES.md), [architecture](docs/ARCHITECTURE.md),
[reference notes](docs/REFERENCE_NOTES.md), and [push instructions](docs/GIT_START.md).

## Next milestone

Build the isolated runner, then integrate one small open model and a bounded
repair loop. Evaluate against held-out trusted tests before interpreting model
oracle disagreements as real bugs. Dataset adapters, pass@1 comparisons, oracle
reliability, token accounting, GRPO/LoRA and full mathematics transfer remain open.
