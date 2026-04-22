"""Top-level forwarder so ``python -m abdp`` invokes the CLI."""

from abdp.cli.__main__ import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
