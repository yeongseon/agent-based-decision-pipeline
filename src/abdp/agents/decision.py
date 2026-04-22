from typing import Protocol, runtime_checkable


@runtime_checkable
class AgentDecision[A](Protocol):
    """Output of an agent for a single scenario step.

    ``agent_id`` identifies the emitting agent; ``proposals`` are the actions
    the agent suggests for this step. The ordered tuple preserves deterministic
    downstream tie-breaking.
    """

    agent_id: str
    proposals: tuple[A, ...]
