"""Public surface for the ``abdp.cli`` package.

The CLI package exposes :func:`load_audit_log_factory` for resolving
``module.path:callable`` specs into audit-log factories, and
:class:`LoaderError` for malformed-spec, missing-module, missing-attribute,
non-callable, and invalid-return errors. The argparse entrypoint lives
in ``abdp.cli.__main__`` and is intentionally NOT part of the public
surface; subsequent issues extend ``__all__`` against the frozen surface
test in ``tests/cli/test_cli_public_surface.py``.
"""

import abdp.cli.inspect as _inspect  # noqa: F401  -- force-import so submodule pop sticks via sys.modules.
import abdp.cli.report as _report  # noqa: F401  -- force-import so submodule pop sticks via sys.modules.
import abdp.cli.run as _run  # noqa: F401  -- force-import so submodule pop sticks via sys.modules.
from abdp.cli.loader import LoaderError, load_audit_log_factory

globals().pop("loader", None)
globals().pop("run", None)
globals().pop("report", None)
globals().pop("inspect", None)
del _run
del _report
del _inspect

__all__: tuple[str, ...] = ("LoaderError", "load_audit_log_factory")
