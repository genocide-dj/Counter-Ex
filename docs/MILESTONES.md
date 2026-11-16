# Project milestones

The supplied roadmap spans 24 weeks and asks four research questions: repair gain,
oracle reliability, training signal, and transfer to mathematics. This deliverable
provides an early engineering foundation, approximately 10–20% of planned scope.
No research question is answered yet, and weeks of study are not claimed complete.

| Stage | Deliverable | Status |
| --- | --- | --- |
| 1. Verification foundation | Two problems, reviewed oracles, generators, local runner, failure reports, prompts, tests | Implemented |
| 2. Isolation and baseline | Contained execution, one small model, dataset adapter, 50-problem pilot, raw generation logs | Next |
| 3. CounterEx loop | Model-generated oracle/generator validation, up to 3 repair rounds, replay, stop conditions | Planned |
| 4. Evaluation | Direct sampling, best-of-N, public-sample self-debug and CounterEx under matched budgets | Planned |
| 5. Oracle reliability | Cross-check multiple oracles, held-out official tests, false-alarm analysis | Planned |
| 6. Training and transfer | Optional GRPO/LoRA or rejection-sampling SFT, MATH-500 transfer | Planned |
| 7. Final deliverables | Ablations, failure taxonomy, reproducibility package, report and demo | Planned |

## Acceptance criteria for the next stage

1. Sandbox tests show denied network access, enforced memory/time limits and full child cleanup.
2. A model adapter logs model revision, decoding parameters, prompt, output and token usage.
3. Dataset records retain source IDs, dates and licenses. Development and held-out tests remain separate.
4. A fixed 50-problem pilot can be rerun from configuration, without sharing hidden answers in prompts.
5. Baseline accuracy and execution failures are recorded separately. The fixture demo is excluded.

## Evaluation decisions still required

Select the model after checking available GPU memory. Establish a documented
benchmark cutoff and compatible data licensing before downloads. Match token or
sampling budgets across methods. Use trusted held-out tests to measure repair
success, because agreement with a generated oracle alone can reward shared bugs.
Distinguish no counterexample found, execution failure, and externally verified
success. Define oracle false alarms using independently established expected outputs.

## Suggested first commit

`feat: add CounterEx stress-testing foundation and two runnable demos`
