# Project vision

> **Historical (v0.1 baseline).** See [Roadmap](roadmap.md) for current scope and [README](../README.md) for the current shipped surface.

A Python framework for reproducible agent-based decision simulation

## Problem statement
Teams that study or compare decision strategies often rebuild one-off simulations that are hard to rerun, inspect, and compare.
abdp exists to provide a shared Python framework for defining agent-based decision simulations whose assumptions, inputs, randomness, and outputs can be reproduced and reviewed.
Architecture details are deferred to separate docs.

## Target users
abdp serves researchers, analysts, and product or policy teams who need repeatable decision simulations instead of ad hoc scripts.
It is for people who want to model choices made by agents, rerun the same experiment with controlled randomness, and compare results with evidence they can explain to others.

## Non-goals
- Not a real-time simulation engine for live operational systems.
- Not a domain library with built-in business, policy, scientific, or game rules.
- Not an autonomous decision-making service that replaces human accountability.
- Not a generic workflow orchestrator for unrelated automation tasks.
- Not a promise of integrations or capabilities beyond the documented v0.1 scope.

## v0.1 promise
In v0.1, abdp will provide a clear, narrow foundation for reproducible agent-based decision simulation in Python.
It will define what the framework is for, who it serves, and the boundaries it intentionally keeps so the public API can stay aligned with that scope.
The v0.1 checklist is simple:
- state the problem abdp is for
- name the target users
- state the non-goals
- keep commitments limited to v0.1
This document sets scope, not implementation commitments beyond v0.1.
