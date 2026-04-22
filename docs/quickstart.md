# 10-Minute Modeling Quickstart

Build your first reproducible scenario with `abdp.agents` and `abdp.scenario`. The snippets below form one self-contained, runnable program; copy them top-to-bottom into a single file. For a richer, multi-tier worked example see [`examples/credit_underwriting`](../examples/credit_underwriting).

## Install

```bash
uv sync
uv run python -m examples.credit_underwriting
```

## Domain types

Define minimal participant, segment, and proposal types satisfying the abdp simulation protocols (`ParticipantState`, `SegmentState`, `ActionProposal`):

```python
from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from abdp.core.types import JsonValue, Seed
from abdp.data.snapshot_manifest import SnapshotTier

@dataclass(frozen=True, slots=True, kw_only=True)
class Borrower:
    participant_id: str
    credit_score: int

@dataclass(frozen=True, slots=True, kw_only=True)
class TierSegment:
    segment_id: str
    participant_ids: tuple[str, ...]

@dataclass(slots=True, kw_only=True)
class CreditAction:
    proposal_id: str
    actor_id: str
    action_key: str
    payload: JsonValue
```

## Agent

Implement `abdp.agents.Agent[S, P, A]` to inspect the simulation state and emit proposals:

```python
from dataclasses import dataclass
from typing import override
from abdp.agents import Agent, AgentContext, AgentDecision

@dataclass(slots=True, kw_only=True)
class TierDecision:
    agent_id: str
    proposals: tuple[CreditAction, ...]

@dataclass(slots=True, kw_only=True)
class TierOfficer(Agent[TierSegment, Borrower, CreditAction]):
    agent_id: str

    @override
    def decide(
        self,
        context: AgentContext[TierSegment, Borrower, CreditAction],
    ) -> AgentDecision[CreditAction]:
        proposals = tuple(
            CreditAction(
                proposal_id=f"approve-{p.participant_id}-step{context.step_index}",
                actor_id=self.agent_id,
                action_key="approve",
                payload={"participant_id": p.participant_id},
            )
            for p in context.state.participants
        )
        return TierDecision(agent_id=self.agent_id, proposals=proposals)
```

The agent receives an `AgentContext` snapshot each step and returns an `AgentDecision`.

## Resolver

Implement `abdp.scenario.ActionResolver` to fold proposals into the next state:

```python
from typing import override
from abdp.scenario import ActionResolver
from abdp.simulation import SimulationState

HANDLED = frozenset({"approve"})

class CreditResolver(ActionResolver[TierSegment, Borrower, CreditAction]):
    @override
    def resolve(
        self,
        state: SimulationState[TierSegment, Borrower, CreditAction],
        proposals: tuple[CreditAction, ...],
    ) -> SimulationState[TierSegment, Borrower, CreditAction]:
        unknown = next((p.action_key for p in proposals if p.action_key not in HANDLED), None)
        if unknown is not None:
            raise ValueError(f"Unknown action_key: {unknown}")
        return SimulationState[TierSegment, Borrower, CreditAction](
            step_index=state.step_index + 1,
            seed=state.seed,
            snapshot_ref=state.snapshot_ref,
            segments=state.segments,
            participants=(),
            pending_actions=(),
        )
```

The resolver owns all state transitions; agents only propose. Draining `participants` here causes the runner to terminate when no more proposals are emitted.

## ScenarioSpec

Build an `abdp.simulation.ScenarioSpec` carrying the seed and initial state:

```python
from abdp.simulation import ScenarioSpec, SnapshotRef

SNAPSHOT_TIER: SnapshotTier = "bronze"

class CreditScenario(ScenarioSpec[TierSegment, Borrower, CreditAction]):
    def __init__(self, *, scenario_key: str, seed: Seed) -> None:
        self._scenario_key = scenario_key
        self._seed = seed

    @property
    def scenario_key(self) -> str:
        return self._scenario_key

    @property
    def seed(self) -> Seed:
        return self._seed

    @override
    def build_initial_state(self) -> SimulationState[TierSegment, Borrower, CreditAction]:
        borrowers = (Borrower(participant_id="b-alice", credit_score=780),)
        tiers = (TierSegment(segment_id="tier-prime", participant_ids=("b-alice",)),)
        return SimulationState[TierSegment, Borrower, CreditAction](
            step_index=0,
            seed=self.seed,
            snapshot_ref=SnapshotRef(
                snapshot_id=UUID("11111111-1111-1111-1111-111111111111"),
                tier=SNAPSHOT_TIER,
                storage_key="snapshots/bronze/quickstart-initial.json",
            ),
            segments=tiers,
            participants=borrowers,
            pending_actions=(),
        )
```

## Run

Wire agents and resolver into a `ScenarioRunner`:

```python
from abdp.scenario import ScenarioRunner

scenario = CreditScenario(scenario_key="quickstart-baseline", seed=Seed(7))
runner = ScenarioRunner[TierSegment, Borrower, CreditAction](
    agents=(TierOfficer(agent_id="officer-prime"),),
    resolver=CreditResolver(),
    max_steps=8,
)
run = runner.run(scenario)
```

Same `(scenario, runner)` pair always produces the same `ScenarioRun`.

## Inspect

Read the recorded run to assert outcomes:

```python
assert run.scenario_key == "quickstart-baseline"
assert int(run.seed) == 7
assert run.step_count == 2
assert run.final_state.step_index == 1
assert run.final_state.participants == ()
```

For a complete worked example with multiple risk tiers and decision branches, run `python -m examples.credit_underwriting` and inspect [`tests/integration/test_credit_underwriting_example.py`](../tests/integration/test_credit_underwriting_example.py) for the full assertion shape.
