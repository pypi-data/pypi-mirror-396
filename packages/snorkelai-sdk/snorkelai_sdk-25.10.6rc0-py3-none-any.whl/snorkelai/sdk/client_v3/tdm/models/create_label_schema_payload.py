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

from ..models.data_type import DataType
from ..models.task_type import TaskType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.create_label_schema_payload_label_descriptions import (
        CreateLabelSchemaPayloadLabelDescriptions,  # noqa: F401
    )
    from ..models.create_label_schema_payload_label_map import (
        CreateLabelSchemaPayloadLabelMap,  # noqa: F401
    )
    from ..models.create_label_schema_payload_label_ordinality import (
        CreateLabelSchemaPayloadLabelOrdinality,  # noqa: F401
    )
    from ..models.extractor_config import ExtractorConfig  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="CreateLabelSchemaPayload")


@attrs.define
class CreateLabelSchemaPayload:
    """
    Attributes:
        data_type (DataType):
        dataset_uid (int):
        is_multi_label (bool):
        label_map (CreateLabelSchemaPayloadLabelMap):
        name (str):
        task_type (TaskType):
        allow_overlapping (Union[Unset, bool]):
        description (Union[Unset, str]):
        entity_origin_uid (Union[Unset, int]):
        extractor_config (Union[Unset, ExtractorConfig]):
        image_field (Union[Unset, str]):
        iou_agreement_threshold (Union[Unset, float]):
        is_benchmark_label_schema (Union[Unset, bool]):  Default: False.
        is_text_label (Union[Unset, bool]):  Default: False.
        label_column (Union[Unset, str]):
        label_descriptions (Union[Unset, CreateLabelSchemaPayloadLabelDescriptions]):
        label_ordinality (Union[Unset, CreateLabelSchemaPayloadLabelOrdinality]):
        pdf_url_field (Union[Unset, str]):
        primary_field (Union[Unset, str]):
    """

    data_type: DataType
    dataset_uid: int
    is_multi_label: bool
    label_map: "CreateLabelSchemaPayloadLabelMap"
    name: str
    task_type: TaskType
    allow_overlapping: Union[Unset, bool] = UNSET
    description: Union[Unset, str] = UNSET
    entity_origin_uid: Union[Unset, int] = UNSET
    extractor_config: Union[Unset, "ExtractorConfig"] = UNSET
    image_field: Union[Unset, str] = UNSET
    iou_agreement_threshold: Union[Unset, float] = UNSET
    is_benchmark_label_schema: Union[Unset, bool] = False
    is_text_label: Union[Unset, bool] = False
    label_column: Union[Unset, str] = UNSET
    label_descriptions: Union[Unset, "CreateLabelSchemaPayloadLabelDescriptions"] = (
        UNSET
    )
    label_ordinality: Union[Unset, "CreateLabelSchemaPayloadLabelOrdinality"] = UNSET
    pdf_url_field: Union[Unset, str] = UNSET
    primary_field: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.create_label_schema_payload_label_descriptions import (
            CreateLabelSchemaPayloadLabelDescriptions,  # noqa: F401
        )
        from ..models.create_label_schema_payload_label_map import (
            CreateLabelSchemaPayloadLabelMap,  # noqa: F401
        )
        from ..models.create_label_schema_payload_label_ordinality import (
            CreateLabelSchemaPayloadLabelOrdinality,  # noqa: F401
        )
        from ..models.extractor_config import ExtractorConfig  # noqa: F401
        # fmt: on
        data_type = self.data_type.value
        dataset_uid = self.dataset_uid
        is_multi_label = self.is_multi_label
        label_map = self.label_map.to_dict()
        name = self.name
        task_type = self.task_type.value
        allow_overlapping = self.allow_overlapping
        description = self.description
        entity_origin_uid = self.entity_origin_uid
        extractor_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.extractor_config, Unset):
            extractor_config = self.extractor_config.to_dict()
        image_field = self.image_field
        iou_agreement_threshold = self.iou_agreement_threshold
        is_benchmark_label_schema = self.is_benchmark_label_schema
        is_text_label = self.is_text_label
        label_column = self.label_column
        label_descriptions: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_descriptions, Unset):
            label_descriptions = self.label_descriptions.to_dict()
        label_ordinality: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.label_ordinality, Unset):
            label_ordinality = self.label_ordinality.to_dict()
        pdf_url_field = self.pdf_url_field
        primary_field = self.primary_field

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_type": data_type,
                "dataset_uid": dataset_uid,
                "is_multi_label": is_multi_label,
                "label_map": label_map,
                "name": name,
                "task_type": task_type,
            }
        )
        if allow_overlapping is not UNSET:
            field_dict["allow_overlapping"] = allow_overlapping
        if description is not UNSET:
            field_dict["description"] = description
        if entity_origin_uid is not UNSET:
            field_dict["entity_origin_uid"] = entity_origin_uid
        if extractor_config is not UNSET:
            field_dict["extractor_config"] = extractor_config
        if image_field is not UNSET:
            field_dict["image_field"] = image_field
        if iou_agreement_threshold is not UNSET:
            field_dict["iou_agreement_threshold"] = iou_agreement_threshold
        if is_benchmark_label_schema is not UNSET:
            field_dict["is_benchmark_label_schema"] = is_benchmark_label_schema
        if is_text_label is not UNSET:
            field_dict["is_text_label"] = is_text_label
        if label_column is not UNSET:
            field_dict["label_column"] = label_column
        if label_descriptions is not UNSET:
            field_dict["label_descriptions"] = label_descriptions
        if label_ordinality is not UNSET:
            field_dict["label_ordinality"] = label_ordinality
        if pdf_url_field is not UNSET:
            field_dict["pdf_url_field"] = pdf_url_field
        if primary_field is not UNSET:
            field_dict["primary_field"] = primary_field

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.create_label_schema_payload_label_descriptions import (
            CreateLabelSchemaPayloadLabelDescriptions,  # noqa: F401
        )
        from ..models.create_label_schema_payload_label_map import (
            CreateLabelSchemaPayloadLabelMap,  # noqa: F401
        )
        from ..models.create_label_schema_payload_label_ordinality import (
            CreateLabelSchemaPayloadLabelOrdinality,  # noqa: F401
        )
        from ..models.extractor_config import ExtractorConfig  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        data_type = DataType(d.pop("data_type"))

        dataset_uid = d.pop("dataset_uid")

        is_multi_label = d.pop("is_multi_label")

        label_map = CreateLabelSchemaPayloadLabelMap.from_dict(d.pop("label_map"))

        name = d.pop("name")

        task_type = TaskType(d.pop("task_type"))

        _allow_overlapping = d.pop("allow_overlapping", UNSET)
        allow_overlapping = UNSET if _allow_overlapping is None else _allow_overlapping

        _description = d.pop("description", UNSET)
        description = UNSET if _description is None else _description

        _entity_origin_uid = d.pop("entity_origin_uid", UNSET)
        entity_origin_uid = UNSET if _entity_origin_uid is None else _entity_origin_uid

        _extractor_config = d.pop("extractor_config", UNSET)
        _extractor_config = UNSET if _extractor_config is None else _extractor_config
        extractor_config: Union[Unset, ExtractorConfig]
        if isinstance(_extractor_config, Unset):
            extractor_config = UNSET
        else:
            extractor_config = ExtractorConfig.from_dict(_extractor_config)

        _image_field = d.pop("image_field", UNSET)
        image_field = UNSET if _image_field is None else _image_field

        _iou_agreement_threshold = d.pop("iou_agreement_threshold", UNSET)
        iou_agreement_threshold = (
            UNSET if _iou_agreement_threshold is None else _iou_agreement_threshold
        )

        _is_benchmark_label_schema = d.pop("is_benchmark_label_schema", UNSET)
        is_benchmark_label_schema = (
            UNSET if _is_benchmark_label_schema is None else _is_benchmark_label_schema
        )

        _is_text_label = d.pop("is_text_label", UNSET)
        is_text_label = UNSET if _is_text_label is None else _is_text_label

        _label_column = d.pop("label_column", UNSET)
        label_column = UNSET if _label_column is None else _label_column

        _label_descriptions = d.pop("label_descriptions", UNSET)
        _label_descriptions = (
            UNSET if _label_descriptions is None else _label_descriptions
        )
        label_descriptions: Union[Unset, CreateLabelSchemaPayloadLabelDescriptions]
        if isinstance(_label_descriptions, Unset):
            label_descriptions = UNSET
        else:
            label_descriptions = CreateLabelSchemaPayloadLabelDescriptions.from_dict(
                _label_descriptions
            )

        _label_ordinality = d.pop("label_ordinality", UNSET)
        _label_ordinality = UNSET if _label_ordinality is None else _label_ordinality
        label_ordinality: Union[Unset, CreateLabelSchemaPayloadLabelOrdinality]
        if isinstance(_label_ordinality, Unset):
            label_ordinality = UNSET
        else:
            label_ordinality = CreateLabelSchemaPayloadLabelOrdinality.from_dict(
                _label_ordinality
            )

        _pdf_url_field = d.pop("pdf_url_field", UNSET)
        pdf_url_field = UNSET if _pdf_url_field is None else _pdf_url_field

        _primary_field = d.pop("primary_field", UNSET)
        primary_field = UNSET if _primary_field is None else _primary_field

        obj = cls(
            data_type=data_type,
            dataset_uid=dataset_uid,
            is_multi_label=is_multi_label,
            label_map=label_map,
            name=name,
            task_type=task_type,
            allow_overlapping=allow_overlapping,
            description=description,
            entity_origin_uid=entity_origin_uid,
            extractor_config=extractor_config,
            image_field=image_field,
            iou_agreement_threshold=iou_agreement_threshold,
            is_benchmark_label_schema=is_benchmark_label_schema,
            is_text_label=is_text_label,
            label_column=label_column,
            label_descriptions=label_descriptions,
            label_ordinality=label_ordinality,
            pdf_url_field=pdf_url_field,
            primary_field=primary_field,
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
