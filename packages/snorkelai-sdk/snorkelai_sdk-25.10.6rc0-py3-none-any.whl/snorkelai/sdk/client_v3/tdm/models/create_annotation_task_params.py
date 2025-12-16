from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

import attrs

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.annotation_form import AnnotationForm  # noqa: F401
    from ..models.annotation_question import AnnotationQuestion  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreateAnnotationTaskParams")


@attrs.define
class CreateAnnotationTaskParams:
    """
    Attributes:
        annotation_form (AnnotationForm):
        name (str):
        allow_auto_commit (Union[Unset, bool]):  Default: False.
        allow_reassignment (Union[Unset, bool]):  Default: False.
        description (Union[Unset, str]):
        num_required_submission (Union[Unset, int]):
        questions (Union[Unset, List['AnnotationQuestion']]):
        user_visibility (Union[Unset, List[int]]):
    """

    annotation_form: "AnnotationForm"
    name: str
    allow_auto_commit: Union[Unset, bool] = False
    allow_reassignment: Union[Unset, bool] = False
    description: Union[Unset, str] = UNSET
    num_required_submission: Union[Unset, int] = UNSET
    questions: Union[Unset, List["AnnotationQuestion"]] = UNSET
    user_visibility: Union[Unset, List[int]] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        from ..models.annotation_question import AnnotationQuestion  # noqa: F401
        # fmt: on
        annotation_form = self.annotation_form.to_dict()
        name = self.name
        allow_auto_commit = self.allow_auto_commit
        allow_reassignment = self.allow_reassignment
        description = self.description
        num_required_submission = self.num_required_submission
        questions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.questions, Unset):
            questions = []
            for questions_item_data in self.questions:
                questions_item = questions_item_data.to_dict()
                questions.append(questions_item)

        user_visibility: Union[Unset, List[int]] = UNSET
        if not isinstance(self.user_visibility, Unset):
            user_visibility = self.user_visibility

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_form": annotation_form,
                "name": name,
            }
        )
        if allow_auto_commit is not UNSET:
            field_dict["allow_auto_commit"] = allow_auto_commit
        if allow_reassignment is not UNSET:
            field_dict["allow_reassignment"] = allow_reassignment
        if description is not UNSET:
            field_dict["description"] = description
        if num_required_submission is not UNSET:
            field_dict["num_required_submission"] = num_required_submission
        if questions is not UNSET:
            field_dict["questions"] = questions
        if user_visibility is not UNSET:
            field_dict["user_visibility"] = user_visibility

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.annotation_form import AnnotationForm  # noqa: F401
        from ..models.annotation_question import AnnotationQuestion  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotation_form = AnnotationForm.from_dict(d.pop("annotation_form"))

        name = d.pop("name")

        _allow_auto_commit = d.pop("allow_auto_commit", UNSET)
        allow_auto_commit = UNSET if _allow_auto_commit is None else _allow_auto_commit

        _allow_reassignment = d.pop("allow_reassignment", UNSET)
        allow_reassignment = (
            UNSET if _allow_reassignment is None else _allow_reassignment
        )

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _num_required_submission = d.pop("num_required_submission", UNSET)
        num_required_submission = (
            UNSET if _num_required_submission is None else _num_required_submission
        )

        _questions = d.pop("questions", UNSET)
        questions = []
        _questions = UNSET if _questions is None else _questions
        for questions_item_data in _questions or []:
            questions_item = AnnotationQuestion.from_dict(questions_item_data)

            questions.append(questions_item)

        _user_visibility = d.pop("user_visibility", UNSET)
        user_visibility = cast(
            List[int], UNSET if _user_visibility is None else _user_visibility
        )

        obj = cls(
            annotation_form=annotation_form,
            name=name,
            allow_auto_commit=allow_auto_commit,
            allow_reassignment=allow_reassignment,
            description=description,
            num_required_submission=num_required_submission,
            questions=questions,
            user_visibility=user_visibility,
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
