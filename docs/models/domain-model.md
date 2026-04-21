# Domain model

This document fixes the conceptual boundary between framework concepts and domain concepts for ABDP, and
the rule that admits new framework abstractions and generic contracts for domain plugins to build on. It
applies the layer rules from [docs/architecture.md](../architecture.md) to the modeling layer; agent and
evaluation APIs stay out of scope here.

## Framework concepts vs. domain concepts

- Framework concepts describe reusable decision-model structure without assuming a business field.
- Domain concepts describe field-specific meaning and stay outside `abdp.core`.
- Domain plugins map their own objects onto framework primitives without changing the core framework.
- A domain concept gives field-specific meaning to a subject, participant, segment, action, or snapshot.

## Primitive invariants

- `subject` is the focal unit of state for a run and keeps a stable identity across segments and snapshots.
- `participant` is an actor or system role with a stable identity for a run and is not a subject by default.
- `segment` is an ordered slice of a run that groups related actions and snapshots without adding domain meaning.
- `action` is a recorded decision step in a segment and is treated as an append-only fact for that run.
- `snapshot` is an immutable state view that stays reproducible for the same inputs and seed-aware execution.

## Abstraction admission rule

- A new framework abstraction is justified only when the same need is evidenced in at least two domains.
- One domain-specific use case is not enough to add a new primitive to `abdp.core`.
- If the evidence is weaker than two domains, keep the concept in the domain plugin and map it onto existing primitives.
- Generic contracts belong in the framework only after the same boundary and invariants hold in at least two domains.
