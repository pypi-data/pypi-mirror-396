from typing import List, Optional, TypedDict

from baicai_base.utils.data import CodeStore


class BaselineState(TypedDict):
    """State management for the baseline builder graph.

    Attributes:
        messages: List of tuples containing user-assistant message history.
            Format: [("user", "request"), ("assistant", "response")]
        baseline_feedbacks: List of feedback messages from iterations.
            Format: [("user", "feedback")]
        baseline_codes: Storage for code versions and their execution results.
        error_message: Error message if any occurs during execution.
        baseline_success: Indicates if the baseline execution was successful.
        fail_fast: Flag to terminate execution on critical errors.
        baseline_builder_iter: Counter for overall builder iterations.
        baseline_iter: Counter for baseline model iterations.
    """

    messages: List[tuple[str, str]]
    baseline_feedbacks: List[tuple[str, str]]
    baseline_codes: CodeStore
    error_message: Optional[str]
    baseline_success: bool
    fail_fast: bool
    baseline_builder_iter: int
    baseline_iter: int
