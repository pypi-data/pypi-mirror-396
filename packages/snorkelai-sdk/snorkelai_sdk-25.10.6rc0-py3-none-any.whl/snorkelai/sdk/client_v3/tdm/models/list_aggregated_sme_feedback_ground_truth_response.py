from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.list_aggregated_sme_feedback_ground_truth_response_aggregated_ground_truth_type_0 import (
        ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0,  # noqa: F401
    )
    from ..models.list_aggregated_sme_feedback_ground_truth_response_aggregated_ground_truth_type_1 import (
        ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1,  # noqa: F401
    )
    # fmt: on


T = TypeVar("T", bound="ListAggregatedSmeFeedbackGroundTruthResponse")


@attrs.define
class ListAggregatedSmeFeedbackGroundTruthResponse:
    """
    Attributes:
        aggregated_ground_truth (Union['ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0',
            'ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1']):
    """

    aggregated_ground_truth: Union[
        "ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0",
        "ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1",
    ]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.list_aggregated_sme_feedback_ground_truth_response_aggregated_ground_truth_type_0 import (
            ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0,  # noqa: F401
        )
        from ..models.list_aggregated_sme_feedback_ground_truth_response_aggregated_ground_truth_type_1 import (
            ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1,  # noqa: F401
        )
        # fmt: on
        aggregated_ground_truth: Dict[str, Any]
        if isinstance(
            self.aggregated_ground_truth,
            ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0,
        ):
            aggregated_ground_truth = self.aggregated_ground_truth.to_dict()
        else:
            aggregated_ground_truth = self.aggregated_ground_truth.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aggregated_ground_truth": aggregated_ground_truth,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.list_aggregated_sme_feedback_ground_truth_response_aggregated_ground_truth_type_0 import (
            ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0,  # noqa: F401
        )
        from ..models.list_aggregated_sme_feedback_ground_truth_response_aggregated_ground_truth_type_1 import (
            ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1,  # noqa: F401
        )
        # fmt: on
        d = src_dict.copy()

        def _parse_aggregated_ground_truth(
            data: object,
        ) -> Union[
            "ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0",
            "ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                aggregated_ground_truth_type_0 = ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType0.from_dict(
                    data
                )

                return aggregated_ground_truth_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            aggregated_ground_truth_type_1 = ListAggregatedSmeFeedbackGroundTruthResponseAggregatedGroundTruthType1.from_dict(
                data
            )

            return aggregated_ground_truth_type_1

        aggregated_ground_truth = _parse_aggregated_ground_truth(
            d.pop("aggregated_ground_truth")
        )

        obj = cls(
            aggregated_ground_truth=aggregated_ground_truth,
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
