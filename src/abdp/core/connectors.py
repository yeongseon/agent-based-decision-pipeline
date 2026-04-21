"""Core connector protocol contract:

- Defines the minimal core connector contract.
- Domain-neutral and transport-agnostic.
- Synchronous only.
- Contract consists of ``name`` and ``send(request) -> response``.
- Intended for structural typing in core; implementations live outside core.
- Runtime protocol checks are shallow: they verify attribute presence only and
  do not validate call signatures or generic type arguments.
- No guarantees about retries, rate limiting, thread safety, connection
  lifecycle, or resource management.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["Connector"]


@runtime_checkable
class Connector[RequestT, ResponseT](Protocol):
    @property
    def name(self) -> str: ...

    def send(self, request: RequestT) -> ResponseT: ...
