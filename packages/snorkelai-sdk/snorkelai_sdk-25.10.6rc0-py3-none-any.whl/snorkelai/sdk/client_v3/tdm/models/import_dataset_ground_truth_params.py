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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    # fmt: off
    from ..models.ground_truth_df_model import GroundTruthDFModel  # noqa: F401
    from ..models.ground_truth_file_model import GroundTruthFileModel  # noqa: F401
    from ..models.ground_truth_raw_model import GroundTruthRawModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="ImportDatasetGroundTruthParams")


@attrs.define
class ImportDatasetGroundTruthParams:
    """
    Attributes:
        label_schema_uid (int):
        convert_to_raw_format (Union[Unset, bool]):  Default: False.
        df (Union[Unset, GroundTruthDFModel]):
        file (Union[Unset, GroundTruthFileModel]):
        is_context (Union[Unset, bool]):  Default: False.
        merge_type (Union[Unset, str]):  Default: 'FROM'.
        raw (Union[Unset, GroundTruthRawModel]):
        replace_abstain_with_negative (Union[Unset, bool]):  Default: False.
        run_async (Union[Unset, bool]):  Default: False.
        skip_missing (Union[Unset, bool]):  Default: False.
        skip_unknown (Union[Unset, bool]):  Default: False.
    """

    label_schema_uid: int
    convert_to_raw_format: Union[Unset, bool] = False
    df: Union[Unset, "GroundTruthDFModel"] = UNSET
    file: Union[Unset, "GroundTruthFileModel"] = UNSET
    is_context: Union[Unset, bool] = False
    merge_type: Union[Unset, str] = "FROM"
    raw: Union[Unset, "GroundTruthRawModel"] = UNSET
    replace_abstain_with_negative: Union[Unset, bool] = False
    run_async: Union[Unset, bool] = False
    skip_missing: Union[Unset, bool] = False
    skip_unknown: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.ground_truth_df_model import GroundTruthDFModel  # noqa: F401
        from ..models.ground_truth_file_model import GroundTruthFileModel  # noqa: F401
        from ..models.ground_truth_raw_model import GroundTruthRawModel  # noqa: F401
        # fmt: on
        label_schema_uid = self.label_schema_uid
        convert_to_raw_format = self.convert_to_raw_format
        df: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.df, Unset):
            df = self.df.to_dict()
        file: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_dict()
        is_context = self.is_context
        merge_type = self.merge_type
        raw: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.raw, Unset):
            raw = self.raw.to_dict()
        replace_abstain_with_negative = self.replace_abstain_with_negative
        run_async = self.run_async
        skip_missing = self.skip_missing
        skip_unknown = self.skip_unknown

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label_schema_uid": label_schema_uid,
            }
        )
        if convert_to_raw_format is not UNSET:
            field_dict["convert_to_raw_format"] = convert_to_raw_format
        if df is not UNSET:
            field_dict["df"] = df
        if file is not UNSET:
            field_dict["file"] = file
        if is_context is not UNSET:
            field_dict["is_context"] = is_context
        if merge_type is not UNSET:
            field_dict["merge_type"] = merge_type
        if raw is not UNSET:
            field_dict["raw"] = raw
        if replace_abstain_with_negative is not UNSET:
            field_dict["replace_abstain_with_negative"] = replace_abstain_with_negative
        if run_async is not UNSET:
            field_dict["run_async"] = run_async
        if skip_missing is not UNSET:
            field_dict["skip_missing"] = skip_missing
        if skip_unknown is not UNSET:
            field_dict["skip_unknown"] = skip_unknown

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.ground_truth_df_model import GroundTruthDFModel  # noqa: F401
        from ..models.ground_truth_file_model import GroundTruthFileModel  # noqa: F401
        from ..models.ground_truth_raw_model import GroundTruthRawModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        label_schema_uid = d.pop("label_schema_uid")

        _convert_to_raw_format = d.pop("convert_to_raw_format", UNSET)
        convert_to_raw_format = (
            UNSET if _convert_to_raw_format is None else _convert_to_raw_format
        )

        _df = d.pop("df", UNSET)
        _df = UNSET if _df is None else _df
        df: Union[Unset, GroundTruthDFModel]
        if isinstance(_df, Unset):
            df = UNSET
        else:
            df = GroundTruthDFModel.from_dict(_df)

        _file = d.pop("file", UNSET)
        _file = UNSET if _file is None else _file
        file: Union[Unset, GroundTruthFileModel]
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = GroundTruthFileModel.from_dict(_file)

        _is_context = d.pop("is_context", UNSET)
        is_context = UNSET if _is_context is None else _is_context

        _merge_type = d.pop("merge_type", UNSET)
        merge_type = UNSET if _merge_type is None else _merge_type

        _raw = d.pop("raw", UNSET)
        _raw = UNSET if _raw is None else _raw
        raw: Union[Unset, GroundTruthRawModel]
        if isinstance(_raw, Unset):
            raw = UNSET
        else:
            raw = GroundTruthRawModel.from_dict(_raw)

        _replace_abstain_with_negative = d.pop("replace_abstain_with_negative", UNSET)
        replace_abstain_with_negative = (
            UNSET
            if _replace_abstain_with_negative is None
            else _replace_abstain_with_negative
        )

        _run_async = d.pop("run_async", UNSET)
        run_async = UNSET if _run_async is None else _run_async

        _skip_missing = d.pop("skip_missing", UNSET)
        skip_missing = UNSET if _skip_missing is None else _skip_missing

        _skip_unknown = d.pop("skip_unknown", UNSET)
        skip_unknown = UNSET if _skip_unknown is None else _skip_unknown

        obj = cls(
            label_schema_uid=label_schema_uid,
            convert_to_raw_format=convert_to_raw_format,
            df=df,
            file=file,
            is_context=is_context,
            merge_type=merge_type,
            raw=raw,
            replace_abstain_with_negative=replace_abstain_with_negative,
            run_async=run_async,
            skip_missing=skip_missing,
            skip_unknown=skip_unknown,
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
