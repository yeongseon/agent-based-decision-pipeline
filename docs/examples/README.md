# Examples

Two end-to-end worked examples ship with abdp. Both run on the public
`ScenarioRunner` surface, fold a real `selected_proposal` evidence stream
into an `AuditLog`, and serialize through `abdp.reporting.render_json_report`
so their outputs are diffable artifacts.

| Example | Run | Source |
| --- | --- | --- |
| Credit underwriting | `python -m examples.credit_underwriting` | [`examples/credit_underwriting`](../../examples/credit_underwriting) |
| Queue scheduling | `python -m examples.queue_scheduling` | [`examples/queue_scheduling`](../../examples/queue_scheduling) |

## Credit underwriting

A two-officer pipeline that classifies borrowers into risk tiers and emits
one `selected_proposal` evidence record per non-empty decision step. Run
locally with `python -m examples.credit_underwriting` for the short stdout
summary, or import `build_audit_log` from
[`examples/credit_underwriting`](../../examples/credit_underwriting) to obtain
a full `AuditLog` whose evidence stream is keyed by `selected_proposal`.

The frozen JSON snapshot below was rendered with `Seed(7)` and is the same
artifact `abdp run examples.credit_underwriting.audit:build_audit_log
--seed 7` would produce.

## Queue scheduling

A latency-baseline scheduler that dispatches queued requests across worker
agents and emits one `selected_proposal` evidence record per dispatched
proposal. Run locally with `python -m examples.queue_scheduling`, or import
`build_audit_log` from
[`examples/queue_scheduling`](../../examples/queue_scheduling) to obtain the
corresponding `AuditLog`.

The frozen JSON snapshot below was rendered with `Seed(11)` and is the same
artifact `abdp run examples.queue_scheduling.audit:build_audit_log
--seed 11` would produce.

## Frozen outputs

These checked-in JSON files are the byte-identical output of the audit
factories at the seeds noted above. They are regenerated only when the
example logic intentionally changes; `tests/meta/test_examples_outputs.py`
asserts that each file matches a fresh
`render_json_report(build_audit_log(seed))` and that every snapshot still
contains the reserved `selected_proposal` evidence key.

- [`outputs/credit_underwriting_report.json`](outputs/credit_underwriting_report.json) — `Seed(7)`, `scenario_key="credit-underwriting-baseline"`.
- [`outputs/queue_scheduling_report.json`](outputs/queue_scheduling_report.json) — `Seed(11)`, `scenario_key="latency-baseline"`.

To regenerate (only after an intentional behaviour change), render each
factory through `render_json_report` and overwrite the corresponding file
under `docs/examples/outputs/`.
