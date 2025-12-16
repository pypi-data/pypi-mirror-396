"""Top-level package for the new instantgrade architecture.

This package is a skeleton used during an incremental migration.
"""

__all__ = [
    "core",
    "executors",
    "evaluators",
    "reporting",
]

# Export common top-level symbols for backward compatibility.
# Some consumers expect to import `Evaluator` directly from `instantgrade`:
#   from instantgrade import Evaluator
# Provide that by re-exporting the class from its module.
try:
    # Prefer relative import to support package moves and editable installs
    from .evaluators.python.evaluator import Evaluator  # type: ignore

    __all__.append("Evaluator")
except Exception:
    # Import errors here should not break package import in minimal setups.
    # The CI/test runner will surface failures when attempting to import Evaluator.
    pass
