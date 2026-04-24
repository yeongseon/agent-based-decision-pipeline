# Review

`abdp.review` adds deterministic self-correction on top of the scenario loop.
`ReviewLoopRunner` runs one logical step, asks a deterministic critic to score it,
and either commits the accepted result or records the rejected attempt on the
Inspector plane only.

## Two-plane execution model

Review keeps the same split introduced for Inspector:

| Plane | What changes during review |
| --- | --- |
| **Canonical** | Only accepted or policy-selected committed outcomes become `ScenarioRun.steps` and reach downstream evidence/audit code. |
| **Inspector** | Every rejected or accepted review attempt is emitted as `review.attempt` trace metadata. |

Rejected attempts never belong in canonical evidence. They exist only so an
operator can inspect *how* the loop arrived at the committed step.

See [ADR 0001](adr/0001-two-plane-execution-model.md) for the rationale.

## Public surface

```python
from abdp.review import (
    CorrectionPolicy,
    Critic,
    Reviser,
    ReviewAttempt,
    ReviewDecision,
    ReviewLoopRunner,
    ReviewTrace,
)
```

### CorrectionPolicy

```python
CorrectionPolicy(
    max_retries=1,
    min_score=0.8,
    on_fail="rollback",  # Literal["rollback", "revise", "stop"]
)
```

- `max_retries` counts additional attempts after the first proposal.
- `min_score` is the critic threshold in `[0.0, 1.0]`.
- `on_fail` decides the terminal outcome after retries are exhausted:
  - `rollback` — stop without committing the rejected step; the terminal
    `review.attempt` remains in tracing with `disposition="rollback"`.
  - `stop` — stop without committing the rejected step; the terminal
    `review.attempt` remains in tracing with `disposition="stop"`.
  - `revise` — commit one final deterministic revised proposal and stop.

## Critic and Reviser contracts

`Critic` and `Reviser` are runtime-checkable `Protocol`s.

- `Critic.evaluate(step) -> ReviewDecision`
- `Reviser.revise(attempt) -> tuple[ActionProposal, ...]`

The stable contract assumes both are deterministic. For the same canonical
state, policy, and proposal sequence, they must return the same score / revised
proposal tuple.

## ReviewLoopRunner

```python
from abdp.inspector import MemoryTraceStore, TraceRecorder
from abdp.review import CorrectionPolicy, ReviewDecision, ReviewLoopRunner

store = MemoryTraceStore()
recorder = TraceRecorder(store=store, seed=seed, run_id="ignored-by-review")

runner = ReviewLoopRunner(
    agents=(agent,),
    resolver=resolver,
    max_steps=5,
    critic=critic,
    reviser=reviser,
    policy=CorrectionPolicy(max_retries=1, min_score=0.8, on_fail="rollback"),
    recorder=recorder,
)
run = runner.run(spec)
```

The canonical `ScenarioRun` stays deterministic and frozen. When `max_retries=0`
and the critic accepts immediately, the canonical output is byte-identical to a
plain `ScenarioRunner` run.

## review.attempt events

Each reviewed attempt is emitted as a `review.attempt` event with deterministic
identity and a `parent_event_id` pointing to the surrounding `step.begin` event.

Attributes include:

- `attempt_no`
- `accepted`
- `score`
- `critique`
- `disposition` (`accept`, `retry`, `rollback`, `revise`, `stop`)

The Review runner derives a stable trace run id from `(scenario, seed, policy,
critic type, reviser type)` so repeated executions produce byte-identical trace
event sequences even if the caller supplied a different `TraceRecorder.run_id`.

## Determinism and isolation

- The retry loop always restarts from the last committed `SimulationState`.
- Rejected attempts stay in tracing only.
- Canonical evidence can only be written by the resolver for the accepted or
  policy-selected committed attempt.
- For a fixed `(seed, scenario, policy, critic, reviser)` tuple, two runs
  produce byte-identical canonical output and byte-identical trace events.
