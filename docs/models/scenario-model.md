# Scenario model

This document defines the neutral scenario vocabulary for ABDP layers 2 and 3. It extends the primitive
boundary in [docs/models/domain-model.md](domain-model.md) and applies the layer rules from
[docs/architecture.md](../architecture.md); shock specifications, what-if framework implementation, and
layer 5 agent implementations stay out of scope.

## Scope and reused primitives

- This model defines neutral simulation vocabulary that `data` and `simulation` may encode without layer 5.
- This document reuses `subject`, `participant`, `segment`, `action`, and `snapshot` from the domain model.
- It introduces `scenario`, `action proposal`, and `simulation step` without redefining existing primitives.
- A `scenario` adds runnable structure and execution ordering, not domain meaning.

## Scenario and execution concepts

- A `scenario` binds one or more `subject` instances, participants, segments, and an entry `snapshot`.
- An `action proposal` is a candidate next `action` considered during a `simulation step` before recording.
- A `simulation step` is the smallest ordered execution unit in a scenario run.
- A step reads the current `snapshot`, evaluates available `action proposal` values, and may record an `action`.

## Relationship model

- A `scenario` contains one or more ordered `segment` values.
- Each `segment` contains zero or more ordered `simulation step` values.
- A `participant` may appear in one or more segments within the same scenario.
- A scenario may track one `subject` or multiple `subject` instances with stable identities across the run.
- Recorded `action` and resulting `snapshot` values stay associated with segment and subject identities.

## Seed-awareness expectation

- Scenario execution must be seed-aware whenever randomness affects proposals, action choice, or state transition.
- The same scenario inputs and same seed must produce the same ordered steps, `action` values, and `snapshot` values.
- Different seeds may change outcomes only where the simulation contract explicitly allows random variation.
- Seed-awareness constrains execution semantics here, not shock specifications or layer 5 agent implementations.
