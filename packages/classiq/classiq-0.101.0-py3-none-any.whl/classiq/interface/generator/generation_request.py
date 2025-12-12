from datetime import datetime

from pydantic import ConfigDict, Field

from classiq.interface.helpers.versioned_model import VersionedModel
from classiq.interface.jobs import JobStatus


class SynthesisActionDetails(VersionedModel):
    """
    Details of a synthesis user action.
    """

    model_config = ConfigDict(frozen=True)
    id: str

    name: str | None = Field(default=None)
    start_time: datetime
    end_time: datetime | None = Field(default=None)

    target_backend: str | None = Field(default=None)
    backend_name: str | None = Field(default=None)
    optimization_level: str | None = Field(default=None)
    optimization_parameter: str | None = Field(default=None)

    status: JobStatus

    program_id: str | None = Field(default=None)

    error: str | None = Field(default=None)

    cost: float | None = Field(default=None)

    random_seed: int | None = Field(default=None)
    max_width: int | None = Field(default=None)
    max_gate_count: int | None = Field(default=None)


class SynthesisActionsQueryResults(VersionedModel):
    results: list[SynthesisActionDetails]
