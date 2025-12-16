import warnings
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union, final

import requests

from snorkelai.sdk.client_v3.tdm.api.label_schemas import (
    copy_label_schema_label_schemas__label_schema_uid__post,
)
from snorkelai.sdk.client_v3.tdm.api.label_schemas import (
    create_label_schema_label_schemas_post as create_label_schema_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.label_schemas import (
    delete_label_schema as delete_label_schema_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.label_schemas import (
    list_label_schemas_label_schemas_get as get_label_schemas_autogen,
)
from snorkelai.sdk.client_v3.tdm.models.copy_label_schema_payload import (
    CopyLabelSchemaPayload,
)
from snorkelai.sdk.client_v3.tdm.models.create_label_schema_payload import (
    CreateLabelSchemaPayload,
)
from snorkelai.sdk.client_v3.tdm.models.data_type import DataType
from snorkelai.sdk.client_v3.tdm.models.task_type import TaskType
from snorkelai.sdk.client_v3.utils import get_dataset_metadata, poll_job_status
from snorkelai.sdk.context.ctx import SnorkelSDKContext
from snorkelai.sdk.develop.base import Base


def _get_label_schema_uid_from_name(name: str) -> int:
    label_schema_resp = get_label_schemas_autogen(name=name)
    if len(label_schema_resp) == 0:
        raise ValueError(f"No label schema found with name  {name}")
    if len(label_schema_resp) > 1:
        raise ValueError(
            f"Multiple label schemas found with name {name}: {[ls.name for ls in label_schema_resp]}"
        )
    return label_schema_resp[0].label_schema_uid


def _parse_enum_with_error_handling(n: str, E: Type[Enum]) -> Enum:
    try:
        return E(n)
    except ValueError as e:
        raise ValueError(
            f"{n} is not a valid {E.__name__}. Valid values are {[e.value for e in E]}."
        ) from e


@final
class LabelSchema(Base):
    """The LabelSchema object represents a label schema in Snorkel Flow. Currently,
    this interface only represents Dataset-level (not Node-level) label schemas.
    """

    def __init__(
        self,
        name: str,
        uid: int,
        dataset_uid: int,
        label_map: Dict[str, int],
        description: Optional[str],
        is_text_label: bool = False,
    ):
        """Create a label schema object in-memory with necessary properties.
        This constructor should not be called directly, and should instead be accessed
        through the ``create()`` and ``get()`` methods

        Parameters
        ----------
        name
            The name of the label schema
        uid
            The UID for the label schema within Snorkel Flow
        dataset_uid
            The UID for the dataset within Snorkel Flow
        label_map
            The label map of the label schema
        description
            The description of the label schema
        is_text_label
            Whether the label schema is a text label schema

        """
        self._name = name
        self._uid = uid
        self._dataset_uid = dataset_uid
        self._label_map: Dict[str, int] = label_map
        self._description = description
        self._is_text_label = is_text_label

    # ----------------------------------
    # LABEL SCHEMA PROPERTIES -- PRIVATE
    # ----------------------------------

    # These are all object properties because they shouldn't be set directly by the user
    @property
    def name(self) -> str:
        """The name of the label schema."""
        return self._name

    @property
    def uid(self) -> int:
        """The UID for the label schema within Snorkel Flow."""
        return self._uid

    @property
    def dataset_uid(self) -> int:
        """The UID for the dataset within Snorkel Flow."""
        return self._dataset_uid

    @property
    def is_text_label(self) -> bool:
        """Whether the label schema is a text label schema."""
        return self._is_text_label

    @property
    def label_map(self) -> Dict[str, int]:
        """The label map of the label schema."""
        self._refresh_attributes()
        return self._label_map

    @property
    def description(self) -> Optional[str]:
        """The description of the label schema."""
        self._refresh_attributes()
        return self._description

    def _refresh_attributes(self) -> None:
        label_schema_resp = get_label_schemas_autogen(label_schema_uid=self.uid)
        if len(label_schema_resp) == 0:
            raise ValueError(f"No label schema found with UID {self.uid}")
        self._label_map = label_schema_resp[0].label_map.to_dict()
        self._description = label_schema_resp[0].description or None

    # -----------------------
    # LABEL SCHEMA OPERATIONS
    # -----------------------

    @classmethod
    def create(
        cls,
        dataset_uid: int,
        name: str,
        data_type: str,
        task_type: str,
        label_map: Union[Dict[str, int], List[str]],
        multi_label: bool = False,
        description: Optional[str] = None,
        label_column: Optional[str] = None,
        label_descriptions: Optional[Dict[str, str]] = None,
        primary_field: Optional[str] = None,
        is_text_label: bool = False,
        allow_overlapping: Optional[bool] = None,
    ) -> "LabelSchema":
        """Create a label schema for a dataset.

        Typically, Dataset.create_label_schema() is the recommended entrypoint for
        creating label schemas.

        Parameters
        ----------
        dataset_uid
            The UID for the dataset within Snorkel Flow
        name
            The name of the label schema
        data_type
            The data type of the label schema
        task_type
            The task type of the label schema
        label_map
            A dictionary mapping label names to their integer values, or a list of label names
        multi_label
            Whether the label schema is a multi-label schema, by default False
        description
            A description of the label schema, by default None
        label_column
            The name of the column that contains the labels, by default None
        label_descriptions
            A dictionary mapping label names to their descriptions, by default None
        primary_field
            The primary field of the label schema, by default None
        is_text_label
            Whether the label schema is a text label schema, by default False
        allow_overlapping
            Enable overlapping labels at the same token position. Defaults to None. Sequence tagging only.

        Returns
        -------
        LabelSchema
            The label schema object

        """
        if not get_dataset_metadata(dataset_uid).mta_enabled:
            raise ValueError(
                f"Multi-task annotation not enabled for dataset with UID {dataset_uid}. Cannot create label schema."
            )
        if isinstance(label_map, dict):
            label_map_dict = label_map
            if -1 not in label_map_dict.values():
                label_map_dict["UNKNOWN"] = -1
        else:
            if "UNKNOWN" in label_map:
                label_map.remove("UNKNOWN")
                warnings.warn("Removing UNKNOWN from label map", stacklevel=1)
            label_map_dict = {k: i for i, k in enumerate(label_map)}
            label_map_dict["UNKNOWN"] = -1
        if multi_label:
            # Multi-label schemas should not include UNKNOWN label otherwise the backend endpoint will fail.
            label_map_dict = {k: v for k, v in label_map_dict.items() if v != -1}

        body = CreateLabelSchemaPayload.from_dict(
            dict(
                dataset_uid=dataset_uid,
                name=name,
                data_type=_parse_enum_with_error_handling(data_type, DataType),
                task_type=_parse_enum_with_error_handling(task_type, TaskType),
                is_multi_label=multi_label,
                label_map=label_map_dict,
                description=description,
                label_column=label_column,
                label_descriptions=label_descriptions or {},
                primary_field=primary_field,
                is_text_label=is_text_label,
                allow_overlapping=allow_overlapping,
            )
        )
        label_schema_response = create_label_schema_autogen(body=body)
        label_schema = cls.get(label_schema_response.label_schema_uid)
        print(
            f"Successfully created label schema {label_schema.name} with UID {label_schema.uid}."
        )
        return label_schema

    @classmethod
    def get(cls, label_schema: Union[str, int]) -> "LabelSchema":
        """Retrieve a label schema by name or UID.

        Parameters
        ----------
        label_schema
            The name or UID of the label schema

        Returns
        -------
        LabelSchema
            The label schema object

        Raises
        ------
        ValueError
            If no label schema is found with the given name or UID

        """
        SnorkelSDKContext.get_global().workspace_name  # noqa: B018
        if isinstance(label_schema, str):
            label_schema_uid = _get_label_schema_uid_from_name(label_schema)
        else:
            label_schema_uid = label_schema
        label_schema_resp = get_label_schemas_autogen(label_schema_uid=label_schema_uid)
        if len(label_schema_resp) == 0:
            raise ValueError(f"No label schema found with UID {label_schema_uid}")
        label_schema_obj = cls(
            uid=label_schema_resp[0].label_schema_uid,
            name=label_schema_resp[0].name,
            dataset_uid=label_schema_resp[0].dataset_uid,
            label_map=label_schema_resp[0].label_map.to_dict(),
            description=label_schema_resp[0].description or None,
            is_text_label=label_schema_resp[0].is_text_label or False,
        )
        return label_schema_obj

    @classmethod
    def delete(cls, label_schema: Union[str, int]) -> None:
        """Delete a label schema by name or UID.

        Parameters
        ----------
        label_schema
            The name or UID of the label schema

        """
        if isinstance(label_schema, str):
            label_schema_uid = _get_label_schema_uid_from_name(label_schema)
        else:
            label_schema_uid = label_schema
        try:
            delete_label_schema_autogen(label_schema_uid=label_schema_uid)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(
                    f"No label schema found with UID {label_schema_uid}"
                ) from e
            elif e.response.status_code == 400:
                if "Cannot delete a label schema with associated" in e.response.text:
                    raise ValueError(e.response.text) from e
            else:
                raise e
        print(f"Successfully deleted label schema with UID {label_schema_uid}.")

    def copy(
        self,
        name: str,
        description: Optional[str] = None,
        label_map: Optional[Dict[str, int]] = None,
        label_descriptions: Optional[Dict[str, str]] = None,
        updated_label_schema: Optional[Dict[str, str]] = None,
    ) -> "LabelSchema":
        """Copy a label schema.

        Parameters
        ----------
        name
            The name of the new label schema
        description
            The description of the new label schema
        label_map
            The label map of the new label schema
        label_descriptions
            The label descriptions of the new label schema
        updated_label_schema
            The update mapping to apply to the new label schema. This is a dictionary
            mapping label names for the current label schema to those for the new label
            schema. If a label for the current label schema is removed, it is mapped
            to None. Examples:
            1. Rename "old_1" to "new_1" and remove "old_2": {"old_1": "new_1", "old_2": None}
            2. Merge "old_1" and "old_2" to "new_1": {"old_1": "new_1", "old_2": "new_1"}
            3. Split "old_1" to "new_1" and "new_2", and keep assets labeled as "old_1" at "new_1": {"old_1": "new_1"}
            4. Add "new_3": None (no change to the existing assets)

        Returns
        -------
        LabelSchema
            The new label schema object

        """
        payload_dict: Dict[str, Optional[Union[str, Dict[str, Any]]]] = dict(
            name=name,
            description=description,
        )
        if label_map is not None:
            payload_dict["label_map"] = label_map
        if label_descriptions is not None:
            payload_dict["label_descriptions"] = label_descriptions
        if updated_label_schema is not None:
            payload_dict["updated_label_schema"] = updated_label_schema
        body = CopyLabelSchemaPayload.from_dict(payload_dict)
        job_id = copy_label_schema_label_schemas__label_schema_uid__post(
            label_schema_uid=self.uid, body=body
        )
        resp = poll_job_status(job_id)
        return LabelSchema.get(resp["detail"]["label_schema_uid"])

    def update(self) -> None:
        """Update of a label schema is not implemented."""
        raise NotImplementedError("Not implemented")
