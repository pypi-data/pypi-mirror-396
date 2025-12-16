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

from ..models.llmaj_response_validation_status import LLMAJResponseValidationStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.llmaj_response_rationale import LLMAJResponseRationale  # noqa: F401
    from ..models.llmaj_response_score import LLMAJResponseScore  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="LLMResponse")


@attrs.define
class LLMResponse:
    """
    Attributes:
        status (List[LLMAJResponseValidationStatus]):
        error_message (Union[Unset, str]):  Default: ''.
        rationale (Union[Unset, LLMAJResponseRationale]):
        raw_response (Union[Unset, str]):  Default: ''.
        score (Union[Unset, LLMAJResponseScore]):
    """

    status: List[LLMAJResponseValidationStatus]
    error_message: Union[Unset, str] = ""
    rationale: Union[Unset, "LLMAJResponseRationale"] = UNSET
    raw_response: Union[Unset, str] = ""
    score: Union[Unset, "LLMAJResponseScore"] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.llmaj_response_rationale import (
            LLMAJResponseRationale,  # noqa: F401
        )
        from ..models.llmaj_response_score import LLMAJResponseScore  # noqa: F401
        # fmt: on
        status = []
        for status_item_data in self.status:
            status_item = status_item_data.value
            status.append(status_item)

        error_message = self.error_message
        rationale: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.rationale, Unset):
            rationale = self.rationale.to_dict()
        raw_response = self.raw_response
        score: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.score, Unset):
            score = self.score.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if rationale is not UNSET:
            field_dict["rationale"] = rationale
        if raw_response is not UNSET:
            field_dict["raw_response"] = raw_response
        if score is not UNSET:
            field_dict["score"] = score

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.llmaj_response_rationale import (
            LLMAJResponseRationale,  # noqa: F401
        )
        from ..models.llmaj_response_score import LLMAJResponseScore  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        status = []
        _status = d.pop("status")
        for status_item_data in _status:
            status_item = LLMAJResponseValidationStatus(status_item_data)

            status.append(status_item)

        _error_message = d.pop("error_message", UNSET)
        error_message = UNSET if _error_message is None else _error_message

        _rationale = d.pop("rationale", UNSET)
        _rationale = UNSET if _rationale is None else _rationale
        rationale: Union[Unset, LLMAJResponseRationale]
        if isinstance(_rationale, Unset):
            rationale = UNSET
        else:
            rationale = LLMAJResponseRationale.from_dict(_rationale)

        _raw_response = d.pop("raw_response", UNSET)
        raw_response = UNSET if _raw_response is None else _raw_response

        _score = d.pop("score", UNSET)
        _score = UNSET if _score is None else _score
        score: Union[Unset, LLMAJResponseScore]
        if isinstance(_score, Unset):
            score = UNSET
        else:
            score = LLMAJResponseScore.from_dict(_score)

        obj = cls(
            status=status,
            error_message=error_message,
            rationale=rationale,
            raw_response=raw_response,
            score=score,
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
