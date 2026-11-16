# Architecture

`CLI -> seeded cases -> validator -> reviewed oracle -> candidate runner -> comparison -> report -> repair prompt`

The first release keeps the oracle inside the trusted host process. Candidate
programs run as separate Python processes and communicate through JSON stdin/stdout.
Both problem domains return exact integers, avoiding ambiguous text normalization.
Each case starts a fresh process. The stress engine stops at the first failure.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `problems.py` | Problem descriptions, bounded input validation, independent brute-force oracles and generators |
| `runner.py` | Trusted local execution and explicit execution statuses |
| `stress.py` | Comparison, reproducibility metadata, first-failure feedback |
| `__main__.py` | CLI, JSON reports, repair prompts and fixture demo |

The pair-count generator prepends six edge cases to the requested random cases.
The derangement domain is only nine inputs, so it is enumerated in full and the
random-case count has no effect on that problem. Pair inputs include empty arrays
and negative integers as deliberately defined synthetic cases. An eventual
benchmark adapter must honor the benchmark's own constraints.

## Report contract (schema version 1)

Reports contain the problem, candidate basename and SHA-256, seed, requested
random-case count, timeout, oracle identifier, available/executed/passed counts,
status, and a nullable failure. A failure carries its zero-based case index,
input, expected/actual values, kind, and captured execution details.
`actual` is null when no valid integer was returned. Failure diagnostics can
contain local traceback information; review reports before publishing.

The seed and candidate hash support replay on the same software version. Record
the Git commit and Python version for scientific runs. Python's random generator
behavior is not promised identical across every future Python release.

## Extension boundaries

Replace the trusted runner with a contained service before executing generated
code. Add a model adapter that consumes the problem and feedback. Implement a
separate bounded controller for generation, validation, execution and repair.
The controller must retain earlier counterexamples and recheck repairs against
them. Keep hidden evaluation tests out of model prompts. Never treat a generated
oracle as established ground truth without independent checks.

Counterexample minimization, arbitrary problem plugins, C++ execution, batching,
model APIs and training are intentionally outside this milestone.
