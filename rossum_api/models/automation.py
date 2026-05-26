from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

AutomationTargetType = Literal["legacy_thresholds", "automation_assistant_v1"]

AutomationSetupExcludeBlocker = Literal["error_message", "extension"]

DocumentBlockerGranularity = Literal["annotation", "datapoint"]


@dataclass
class DailyEstimatedErrorRate:
    """One data point of the estimated error-rate timeseries.

    Attributes
    ----------
    date
        ISO 8601 date of the bucket.
    error_rate_estimate
        Estimated error rate for the bucket from [0, 1] interval.
    is_quality_estimate
        Whether the estimate has enough samples to be considered reliable.
    window_document_count
        Number of documents in the moving-average window the estimate was computed from.
    """

    date: str
    error_rate_estimate: float
    is_quality_estimate: bool
    window_document_count: int


@dataclass
class DocumentAutomationTimeSeriesData:
    """One data point of the document-automation timeseries.

    Attributes
    ----------
    date
        ISO 8601 date of the bucket.
    automated_count
        Documents automated without human review.
    non_automated_count
        Documents that required human review.
    touched_count
        Documents the human edited.
    touchless_count
        Documents the human confirmed without edits.
    """

    date: str
    automated_count: int | float
    non_automated_count: int | float
    touched_count: int | float
    touchless_count: int | float

    def __post_init__(self) -> None:
        self.automated_count = int(self.automated_count)
        self.non_automated_count = int(self.non_automated_count)
        self.touched_count = int(self.touched_count)
        self.touchless_count = int(self.touchless_count)


@dataclass
class DocumentBlocker:
    """Aggregated count of documents blocked by a single blocker type.

    Attributes
    ----------
    blocker
        Blocker type (e.g. ``low_score``, ``error_message``, ``extension``).
        See :data:`~rossum_api.models.automation_blocker.AutomationBlockerTypes`
        for the full list of blocker types reported by the platform.
    document_count
        Number of documents the blocker fired on.
    granularity
        Whether the blocker applies to a whole annotation or a single datapoint.
    example_annotation_ids
        Sample annotation IDs the blocker fired on.
    """

    blocker: str
    document_count: int
    granularity: DocumentBlockerGranularity
    example_annotation_ids: list[int] = field(default_factory=list)


@dataclass
class DatapointStatistics:
    """Per-field automation statistics derived from the moving-average window.

    Attributes
    ----------
    schema_id
        Schema ID of the datapoint.
    blocked_document_counts
        Deprecated. Mapping ``blocker_type -> document_count`` for this field.
    estimated_error_rate
        Estimated error rate for the field (0.0 - 1.0), or ``None`` if it cannot be estimated.
    confidence_threshold
        Confidence threshold currently configured for the field, or ``None`` if not set.
    blockers
        Per-blocker document counts for this field.
    is_quality_estimate
        Whether the error-rate estimate has enough samples to be considered reliable.
    """

    schema_id: str
    is_quality_estimate: bool
    blocked_document_counts: dict[str, int] = field(default_factory=dict)
    estimated_error_rate: float | None = None
    confidence_threshold: float | None = None
    blockers: list[DocumentBlocker] = field(default_factory=list)


@dataclass
class AutomationStats:
    """Current automation statistics for a queue.

    Returned by ``GET /queues/{id}/automation_setup_current_stats``.

    Attributes
    ----------
    document_automation_rate
        Fraction of documents automated (0.0 - 1.0).
    document_touchless_rate
        Fraction of documents whose predictions were all correct (>= automation rate).
    document_automation_timeseries
        Per-day document-automation breakdown.
    datapoint_statistics
        Per-field automation statistics.
    document_blockers
        Aggregated document counts per blocker type.
    estimated_error_rate_timeseries
        Per-day estimated error-rate timeseries.
    estimated_error_rate
        Overall estimated error rate for the queue, or ``None`` if it cannot be estimated.
    is_aurora_queue
        Whether the queue uses the Aurora engine.
    """

    document_automation_rate: float
    document_touchless_rate: float | None = None
    document_automation_timeseries: list[DocumentAutomationTimeSeriesData] = field(
        default_factory=list
    )
    datapoint_statistics: list[DatapointStatistics] = field(default_factory=list)
    document_blockers: list[DocumentBlocker] = field(default_factory=list)
    estimated_error_rate_timeseries: list[DailyEstimatedErrorRate] | None = None
    estimated_error_rate: float | None = None
    is_aurora_queue: bool | None = None


@dataclass
class AutomationProjections:
    """Result of an automation-setup projection request.

    Returned by ``POST /queues/{id}/automation_setup_projections``.

    Attributes
    ----------
    baseline
        Current-state statistics for the queue (no error-rate limits applied).
    projections
        Projected statistics — one per requested error-rate target.
    total_document_count
        Total documents in the queue's analysis window.
    used_document_count
        Documents actually used to compute the projection (subset of total).
    """

    baseline: AutomationStats
    total_document_count: int
    used_document_count: int
    projections: list[AutomationStats] = field(default_factory=list)


@dataclass
class FieldErrorRateLimit:
    """Per-field error-rate limit used as input for projection requests.

    Attributes
    ----------
    schema_id
        Schema ID of the field.
    error_rate_limit
        Maximum acceptable error rate for the field (0.0 - 1.0).
    """

    schema_id: str
    error_rate_limit: float


@dataclass
class DatapointAutomationTarget:
    """Per-field automation target stored on a saved :class:`AutomationTarget`.

    Attributes
    ----------
    schema_id
        Schema ID of the field.
    error_rate_target
        Target error rate for the field (0.0 - 1.0).
    confidence_threshold
        Confidence threshold applied to the field.
    error_rate_limit
        Optional upper bound on the field's error rate, or ``None`` if not constrained.
    """

    schema_id: str
    error_rate_target: float
    confidence_threshold: float
    error_rate_limit: float | None = None


@dataclass
class AutomationTarget:
    """Saved automation target for a queue.

    Returned by ``GET /queues/{id}/automation_targets`` (as a list of results) and
    by ``POST /queues/{id}/automation_targets`` (single saved target with ``datetime``
    populated by the server).

    Attributes
    ----------
    automation_rate_target
        Target automation rate (0.0 - 1.0).
    error_rate_target
        Target error rate (0.0 - 1.0).
    type
        Target type — ``automation_assistant_v1`` for the assistant flow,
        ``legacy_thresholds`` for direct per-field threshold configuration.
    datapoint_automation_targets
        Per-field targets.
    datetime
        Server-assigned timestamp of when the target was saved.
    """

    automation_rate_target: float
    error_rate_target: float
    type: AutomationTargetType
    datapoint_automation_targets: list[DatapointAutomationTarget] = field(default_factory=list)
    datetime: str | None = None
