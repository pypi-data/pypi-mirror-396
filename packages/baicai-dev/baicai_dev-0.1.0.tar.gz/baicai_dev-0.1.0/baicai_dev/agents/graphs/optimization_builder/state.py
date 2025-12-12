from typing import List, Optional, TypedDict

from baicai_base.utils.data import CodeStore, ModelStore


class OptimizationState(TypedDict):
    """State management for the optimization builder graph.

    Attributes:
        messages: List of tuples containing user-assistant message history.
            Format: [("user", "request"), ("assistant", "response")]
        workflow_codes: List of different versions of workflow code and results.
        final_baseline_codes: CodeStore containing the final baseline code.
        error_message: Error message if any occurs during execution.
        optimization_feedbacks: List of feedback messages from iterations.
            Format: [("user", "feedback")]
        optimization_codes: ModelStore containing optimization versions and results.
            Format: [{"code": str, "result": dict, "best_model": bool}]

        optimization_success: Indicates if the optimization was successful.
        evaluation_success: Indicates if the evaluation was successful.
        fail_fast: Flag to terminate execution on critical errors.
        re_run: Flag to re-run optimization process.
        stop: Flag to stop optimization process.

        optimization_builder_iter: Counter for overall builder iterations.
        optimization_iter: Counter for optimization code iterations.
    """

    messages: List[tuple[str, str]]
    workflow_codes: List
    final_baseline_codes: CodeStore
    error_message: Optional[str]
    optimization_feedbacks: List[tuple[str, str]]
    optimization_codes: ModelStore

    optimization_success: bool
    evaluation_success: bool
    fail_fast: bool
    re_run: bool
    stop: bool

    optimization_builder_iter: int
    optimization_iter: int
