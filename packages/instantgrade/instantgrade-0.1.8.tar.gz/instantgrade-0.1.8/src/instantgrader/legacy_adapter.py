"""
This module redirects new architecture calls back to the old system.
Nothing inside existing code changes.

It provides a small wrapper that calls the legacy `instantgrade` Evaluator.
"""
from typing import Any


def run_grading_with_legacy_system(solution_path: str, submissions_path: str, **kwargs: Any):
    """
    Instantiate and run the existing Evaluator from the legacy package.

    This is a safe shim that preserves existing behaviour.
    """
    # Import inside function to avoid import-time side-effects
    from instantgrade.evaluator import Evaluator

    evaluator = Evaluator(
        solution_file_path=solution_path,
        submission_folder_path=submissions_path,
        **{k: v for k, v in kwargs.items() if v is not None},
    )

    # Run the legacy evaluation pipeline
    return evaluator.run()
