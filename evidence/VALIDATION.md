# Milestone validation

Executed locally on Windows with Python 3.11.9 on 2026-11-16.

## Automated tests

Command: `python -m unittest discover -s tests -v`

Result: **15 tests passed**, 10.569 seconds in the observed run.
Tests cover known oracle answers, rejected inputs, seeded generation, strict
integer output parsing, runtime/syntax errors, timeouts, output limits, explicit
trust acknowledgment, invalid timeouts, planted bugs, corrected candidates,
repair feedback, CLI exit codes and removal of stale repair prompts.

## Demonstration

Command: `python -m counterex demo --output evidence/demo`

| Candidate | Result | Passed / executed |
| --- | --- | --- |
| Divisible pairs, buggy | Wrong answer on third case | 2 / 3 |
| Divisible pairs, fixed | Passed generated suite | 56 / 56 |
| Derangements, buggy | Wrong answer at n=3 | 3 / 4 |
| Derangements, fixed | Passed exhaustive small domain | 9 / 9 |

The JSON report and generated prompts are in `demo/`. These results use
handwritten fixtures and establish software behavior only. No model inference,
benchmark accuracy, automatic repair gain, oracle reliability study or training
was measured. GitHub Actions is configured but has not run remotely. Linux and
Python 3.12 were not tested locally.
