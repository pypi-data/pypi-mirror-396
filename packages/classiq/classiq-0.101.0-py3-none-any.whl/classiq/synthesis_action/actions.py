from dataclasses import asdict, dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from classiq.interface.jobs import JobStatus

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import syncify_function

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class SynthesisActionFilters:
    """
    Filter parameters for querying synthesis actions.

    All filters are combined using AND logic: only actions matching all specified filters are returned.
    Range filters (with _min/_max suffixes) are inclusive.
    Datetime filters are compared against the job's timestamps.
    """

    status: JobStatus | None = None
    target_backend: str | None = None
    optimization_level: str | None = None
    program_id: str | None = None
    backend_name: str | None = None
    optimization_parameter: str | None = None
    random_seed: int | None = None
    max_width: int | None = None
    max_gate_count: int | None = None
    total_cost_min: float | None = None
    total_cost_max: float | None = None
    start_time_min: datetime | None = None
    start_time_max: datetime | None = None
    end_time_min: datetime | None = None
    end_time_max: datetime | None = None

    def format_filters(self) -> dict[str, Any]:
        """Convert filter fields to API kwargs, excluding None values and converting datetimes."""
        filter_dict = asdict(self)
        return {
            k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in filter_dict.items()
            if v is not None
        }


async def get_synthesis_actions_async(
    offset: int = 0,
    limit: int = 50,
    filters: SynthesisActionFilters | None = None,
) -> "pd.DataFrame":
    """Query synthesis actions with optional filters.
    Args:
        offset: Number of results to skip (default: 0)
        limit: Maximum number of results to return (default: 50)
        filters: Optional SynthesisActionFilters object containing filter parameters.

    Returns:
        A pandas DataFrame containing synthesis actions matching the filters.
        Each row represents a synthesis action with columns for all fields
        from SynthesisActionDetails (id, name, start_time, end_time, status, etc.).
    """
    import pandas as pd

    api_kwargs = filters.format_filters() if filters is not None else {}

    result = await ApiWrapper().call_query_synthesis_actions(
        offset, limit, http_client=None, **api_kwargs
    )

    if not result.results:
        return pd.DataFrame()

    return pd.DataFrame(action.model_dump() for action in result.results)


get_synthesis_actions = syncify_function(get_synthesis_actions_async)
get_synthesis_actions.__doc__ = """Query synthesis actions with optional filters.

    Args:
        offset: Number of results to skip (default: 0)
        limit: Maximum number of results to return (default: 50)
        filters: Optional SynthesisActionFilters object containing filter parameters.

    Returns:
        A pandas DataFrame containing synthesis actions matching the filters.
        Each row represents a synthesis action with columns for all fields
        from SynthesisActionDetails (id, name, start_time, end_time, status, etc.).

    Examples:
        # Query all actions:
        df = get_synthesis_actions(limit=10)

        # Query with filters:
        filters = SynthesisActionFilters(status="COMPLETED", target_backend="ibm")
        df = get_synthesis_actions(filters=filters, limit=10)
    """
