from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.executions_response_benchmark_execution import (
        ExecutionsResponseBenchmarkExecution,  # noqa: F401
    )
    from ..models.executions_response_criteria import (
        ExecutionsResponseCriteria,  # noqa: F401
    )
    from ..models.executions_response_metric_values import (
        ExecutionsResponseMetricValues,  # noqa: F401
    )
    from ..models.executions_response_metrics import (
        ExecutionsResponseMetrics,  # noqa: F401
    )
    from ..models.executions_response_slices import (
        ExecutionsResponseSlices,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ExecutionsResponse")


@attrs.define
class ExecutionsResponse:
    """
    Attributes:
        benchmark_execution (ExecutionsResponseBenchmarkExecution):
        criteria (ExecutionsResponseCriteria):
        metric_values (ExecutionsResponseMetricValues):
        metrics (ExecutionsResponseMetrics):
        slices (ExecutionsResponseSlices):
    """

    benchmark_execution: "ExecutionsResponseBenchmarkExecution"
    criteria: "ExecutionsResponseCriteria"
    metric_values: "ExecutionsResponseMetricValues"
    metrics: "ExecutionsResponseMetrics"
    slices: "ExecutionsResponseSlices"
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.executions_response_benchmark_execution import (
            ExecutionsResponseBenchmarkExecution,  # noqa: F401
        )
        from ..models.executions_response_criteria import (
            ExecutionsResponseCriteria,  # noqa: F401
        )
        from ..models.executions_response_metric_values import (
            ExecutionsResponseMetricValues,  # noqa: F401
        )
        from ..models.executions_response_metrics import (
            ExecutionsResponseMetrics,  # noqa: F401
        )
        from ..models.executions_response_slices import (
            ExecutionsResponseSlices,  # noqa: F401
        )
        # fmt: on
        benchmark_execution = self.benchmark_execution.to_dict()
        criteria = self.criteria.to_dict()
        metric_values = self.metric_values.to_dict()
        metrics = self.metrics.to_dict()
        slices = self.slices.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "benchmark_execution": benchmark_execution,
                "criteria": criteria,
                "metric_values": metric_values,
                "metrics": metrics,
                "slices": slices,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.executions_response_benchmark_execution import (
            ExecutionsResponseBenchmarkExecution,  # noqa: F401
        )
        from ..models.executions_response_criteria import (
            ExecutionsResponseCriteria,  # noqa: F401
        )
        from ..models.executions_response_metric_values import (
            ExecutionsResponseMetricValues,  # noqa: F401
        )
        from ..models.executions_response_metrics import (
            ExecutionsResponseMetrics,  # noqa: F401
        )
        from ..models.executions_response_slices import (
            ExecutionsResponseSlices,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()
        benchmark_execution = ExecutionsResponseBenchmarkExecution.from_dict(
            d.pop("benchmark_execution")
        )

        criteria = ExecutionsResponseCriteria.from_dict(d.pop("criteria"))

        metric_values = ExecutionsResponseMetricValues.from_dict(d.pop("metric_values"))

        metrics = ExecutionsResponseMetrics.from_dict(d.pop("metrics"))

        slices = ExecutionsResponseSlices.from_dict(d.pop("slices"))

        obj = cls(
            benchmark_execution=benchmark_execution,
            criteria=criteria,
            metric_values=metric_values,
            metrics=metrics,
            slices=slices,
        )
        obj.additional_properties = d
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
