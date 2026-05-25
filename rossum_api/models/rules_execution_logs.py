from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ExecutionResult = Literal["success", "failure", "partial_success"]


@dataclass
class RulesExecutionLog:
    """One firing of a :class:`~rossum_api.models.rule.Rule` on a single annotation.

    Each record captures the trigger condition expression evaluated at firing
    time, the field values it saw (``trigger_condition_values``), whether the
    condition matched (``trigger_condition_results``), and the actions that were
    executed. For line-item rules, the result/values/actions arrays are aligned
    by index — one element per line-item row.

    Attributes
    ----------
    rule_id
        ID of the :class:`~rossum_api.models.rule.Rule` that was executed.
    rule_name
        Name of the rule at the time of execution.
    queue_id
        ID of the :class:`~rossum_api.models.queue.Queue` where the rule was triggered.
    annotation_id
        ID of the :class:`~rossum_api.models.annotation.Annotation` that triggered the rule.
    request_id
        Unique identifier for this rule execution request.
    created_at
        Timestamp when the rule was executed.
    trigger_event
        Event that triggered the rule evaluation (e.g. ``annotation_imported``).
    trigger_condition
        The trigger condition expression that was evaluated.
    execution_result
        Overall result: ``success``, ``failure``, or ``partial_success``
        (the latter applies to line-item rules where some rows succeeded and others failed).
    trigger_condition_results
        Boolean per evaluation: a single-element array for regular rules,
        one element per row for line-item rules.
    trigger_condition_values
        Field values passed to the condition. Keys are schema IDs referenced
        in the trigger condition. Aligned by index with ``trigger_condition_results``.
    execution_error
        Error message if the rule execution failed.
    actions
        Actions executed per condition result. ``None`` if all conditions
        evaluated to ``False``. Aligned by index with ``trigger_condition_results``;
        elements are ``None`` for rows where the condition was ``False``.

    References
    ----------
    https://rossum.app/api/docs/openapi/api/rules-execution-log/
    """

    rule_id: int
    rule_name: str
    queue_id: int
    annotation_id: int
    request_id: str
    created_at: str
    trigger_event: str
    trigger_condition: str
    execution_result: ExecutionResult
    trigger_condition_results: list[bool] | None = None
    trigger_condition_values: list[dict[str, Any]] | None = None
    execution_error: str | None = None
    actions: list[list[dict[str, Any]] | None] | None = None
