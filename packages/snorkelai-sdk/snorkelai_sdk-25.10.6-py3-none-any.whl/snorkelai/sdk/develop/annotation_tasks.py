import re
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional, TypeVar, Union, cast, final

import attrs
import pandas as pd
from requests import HTTPError

from snorkelai.sdk.client_v3.tdm.api.annotation import (
    get_annotations_dataset_annotations_get,
)
from snorkelai.sdk.client_v3.tdm.api.annotation import (
    import_annotations_dataset_annotations_post as import_annotations,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    add_assignees_to_annotation_task_annotation_tasks__annotation_task_uid__assignees_post as add_assignees_to_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    add_x_uids_to_annotation_task_annotation_tasks__annotation_task_uid__x_uids_post as add_x_uids_to_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    create_annotation_task_datasets__dataset_uid__annotation_tasks_post as create_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    delete_annotation_task_annotation_tasks__annotation_task_uid__delete as delete_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    delete_assignees_from_annotation_task_annotation_tasks__annotation_task_uid__assignees_delete as delete_assignees_from_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    delete_x_uids_from_annotation_task_annotation_tasks__annotation_task_uid__x_uids_delete as delete_x_uids_from_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    fetch_annotation_task_dataframes_annotation_tasks__annotation_task_uid__dataframes_get as fetch_annotation_task_dataframes,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    get_annotation_task_annotation_tasks__annotation_task_uid__get as get_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    get_annotation_task_assignees_annotation_tasks__annotation_task_uid__assignees_get as get_annotation_task_assignees,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    get_annotation_tasks_datasets__dataset_uid__annotation_tasks_get as get_annotation_tasks_for_dataset,
)
from snorkelai.sdk.client_v3.tdm.api.annotation_tasks import (
    update_annotation_task_annotation_tasks__annotation_task_uid__put as update_annotation_task,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    fetch_dataset_by_uid_datasets__dataset_uid__get as fetch_dataset_by_uid,
)
from snorkelai.sdk.client_v3.tdm.api.label_schemas import (
    list_label_schemas_label_schemas_get as get_label_schemas,
)
from snorkelai.sdk.client_v3.tdm.api.users import (
    get_list_workspaced_users_workspaced_users_get as get_users,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AddAssigneesToAnnotationTaskParams,
    CreateAnnotationTaskParams,
    CreateDatasetAnnotationParams,
    DataPointSelectionParams,
    DataPointStatus,
    DeleteAssigneesFromAnnotationTaskParams,
    FetchedDatasetAnnotation,
    ImportDatasetAnnotationsParams,
    UpdateAnnotationTaskParams,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AnnotationForm as AnnotationFormModel,
)
from snorkelai.sdk.client_v3.tdm.models import (
    AnnotationTask as AnnotationTaskApiModel,
)
from snorkelai.sdk.client_v3.tdm.models.create_dataset_annotation_params_metadata import (
    CreateDatasetAnnotationParamsMetadata,
)
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.client_v3.utils import (
    IdType,
    _unwrap_unset,
    _wrap_in_unset,
    get_dataset_uid,
)
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.types.load import (
    ANNOTATION_TASK_STATUS_COL,
    ASSIGNEES_COL,
    DATAPOINT_UID_COL,
    X_UID_COL,
)

logger = getLogger(__name__)

# Extract field names from FetchedDatasetAnnotation model
ANNOTATION_FIELD_NAMES = {
    field.name for field in attrs.fields(FetchedDatasetAnnotation)
}
CREATE_ANNOTATION_FIELD_NAMES_REQ: set[str] = {
    field.name
    for field in attrs.fields(CreateDatasetAnnotationParams)
    if field.default == attrs.NOTHING
}
CREATE_ANNOTATION_FIELD_NAMES_OPT: set[str] = {
    field.name
    for field in attrs.fields(CreateDatasetAnnotationParams)
    if field.default != attrs.NOTHING
}

T = TypeVar("T")


class LabelSchemaGroup:
    """A group of related label schemas to be shown together in the annotation form."""

    def __init__(
        self, name: str, description: Optional[str], label_schema_uids: List[int]
    ):
        """
        Parameters
        ----------
        name
            The name of the label schema group
        description
            A description of the label schema group, by default None
        label_schema_uids
            List of label schema UIDs in this group
        """
        self.name = name
        self.description = description
        self.label_schema_uids = label_schema_uids


class AnnotationForm:
    """Represents the annotation form with grouped and individual label schemas for a specific annotation task."""

    def __init__(
        self,
        grouped_label_schemas: Optional[List[LabelSchemaGroup]] = None,
        individual_label_schemas: Optional[List[int]] = None,
    ):
        """
        Parameters
        ----------
        grouped_label_schemas
            Groups of related label schemas that should be shown together, by default None
        individual_label_schemas
            Individual label_schema_uids not in any group, by default None
        """
        self.grouped_label_schemas = (
            grouped_label_schemas if grouped_label_schemas is not None else []
        )
        self.individual_label_schemas = (
            individual_label_schemas if individual_label_schemas is not None else []
        )


@final
class AnnotationTask(Base):
    """
    Represents an annotation task within a Snorkel dataset for managing annotation workflows.

    An annotation task defines a set of datapoints that need to be annotated, along with
    the annotation form, user assignments, and task configuration. This class provides
    methods for creating, retrieving, updating, and managing annotation tasks.

    AnnotationTask objects should not be instantiated directly - use the ``create()`` or
    ``get()`` class methods instead.
    """

    def __init__(
        self,
        name: str,
        annotation_task_uid: int,
        dataset_uid: int,
        created_by_user_uid: int,
        created_at: datetime,
        description: Optional[str] = None,
        annotation_form: Optional[AnnotationForm] = None,
        x_uids: Optional[List[str]] = None,
    ):
        """Create an AnnotationTask object in-memory with necessary properties.
        This constructor should not be called directly, and should instead be accessed
        through the ``create()`` and ``get()`` methods.

        Parameters
        ----------
        name
            The name of the annotation task
        annotation_task_uid
            The unique identifier for the annotation task
        dataset_uid
            The UID of the dataset that the annotation task belongs to
        created_by_user_uid
            The UID of the user who created the annotation task
        created_at
            The timestamp when the annotation task was created
        description
            A description of the annotation task, by default None
        annotation_form
            The annotation form associated with the task, by default None
        x_uids
            List of datapoint UIDs in this annotation task, by default None
        """
        self._name = name
        self._annotation_task_uid = annotation_task_uid
        self._dataset_uid = dataset_uid
        self._created_by_user_uid = created_by_user_uid
        self._created_at = created_at
        self._description = description
        self._annotation_form = (
            annotation_form if annotation_form is not None else AnnotationForm()
        )
        self._x_uids = x_uids or []

    # ----------------------------------
    # ANNOTATION TASK PROPERTIES
    # ----------------------------------

    @property
    def uid(self) -> int:
        """Return the UID of the annotation task"""
        return self._annotation_task_uid

    @property
    def name(self) -> str:
        """Return the name of the annotation task"""
        return self._name

    @property
    def dataset_uid(self) -> int:
        """Return the UID of the dataset that the annotation task belongs to"""
        return self._dataset_uid

    @property
    def description(self) -> Optional[str]:
        """Return the description of the annotation task"""
        return self._description

    @property
    def created_by_user_uid(self) -> int:
        """Return the UID of the user who created the annotation task"""
        return self._created_by_user_uid

    @property
    def created_at(self) -> datetime:
        """Return the creation timestamp of the annotation task"""
        return self._created_at

    @property
    def annotation_form(self) -> AnnotationForm:
        """Return the annotation form of the annotation task"""
        return self._annotation_form

    @property
    def x_uids(self) -> List[str]:
        """Return the list of datapoint UIDs in this annotation task"""
        return self._x_uids

    @property
    def label_schema_uids(self) -> List[int]:
        """Return the list of label schema UIDs associated with this annotation task."""
        label_schema_uids = set(self.annotation_form.individual_label_schemas)
        for group in self.annotation_form.grouped_label_schemas:
            label_schema_uids.update(group.label_schema_uids)
        return list(label_schema_uids)

    # ----------------------------------
    # CONVERSION METHODS
    # ----------------------------------
    @staticmethod
    def _from_response_model(
        annotation_task: AnnotationTaskApiModel,
    ) -> "AnnotationTask":
        """Convert an API model to an AnnotationTask SDK object.

        Parameters
        ----------
        annotation_task
            The API model annotation task to convert

        Returns
        -------
        AnnotationTask
            The converted SDK annotation task object
        """
        # Convert the API model's AnnotationForm to our SDK's AnnotationForm
        annotation_form = None
        if annotation_task.annotation_form:
            grouped_label_schemas = []
            if (
                annotation_task.annotation_form.grouped_label_schemas
                and annotation_task.annotation_form.grouped_label_schemas is not UNSET
            ):
                for group in annotation_task.annotation_form.grouped_label_schemas:
                    group_description: Optional[str] = _unwrap_unset(
                        group.description, None
                    )
                    label_schema_uids: List[int] = _unwrap_unset(
                        group.label_schema_uids, cast(List[int], [])
                    )
                    grouped_label_schemas.append(
                        LabelSchemaGroup(
                            name=group.name,
                            description=group_description,
                            label_schema_uids=label_schema_uids,
                        )
                    )

            individual_label_schemas = (
                annotation_task.annotation_form.individual_label_schemas
                if (
                    annotation_task.annotation_form.individual_label_schemas
                    and annotation_task.annotation_form.individual_label_schemas
                    is not UNSET
                )
                else []
            )

            annotation_form = AnnotationForm(
                grouped_label_schemas=grouped_label_schemas,
                individual_label_schemas=individual_label_schemas,
            )

        # Extract values and handle UNSET types properly
        task_description: Optional[str] = _unwrap_unset(
            annotation_task.description, None
        )
        x_uids: List[str] = _unwrap_unset(annotation_task.x_uids, cast(List[str], []))

        return AnnotationTask(
            name=annotation_task.name,
            annotation_task_uid=annotation_task.annotation_task_uid,
            dataset_uid=annotation_task.dataset_uid,
            created_by_user_uid=annotation_task.created_by_user_uid,
            created_at=annotation_task.created_at,
            description=task_description,
            annotation_form=annotation_form,
            x_uids=x_uids,
        )

    # ----------------------------------
    # CRUD OPERATIONS
    # ----------------------------------
    @classmethod
    def create(
        cls,
        dataset_uid: int,
        name: str,
        description: Optional[str] = None,
    ) -> "AnnotationTask":
        """Create an annotation task.

        .. note::

            This method only accepts `dataset_uid`, `name`, and `description` as parameters.
            Other properties (such as annotation form, datapoint UIDs, and questions) can be set later through
            other methods.


        Parameters
        ----------
        dataset_uid
            The UID of the dataset for the annotation task
        name
            The name of the annotation task
        description
            A description of the annotation task, by default None

        Returns
        -------
        AnnotationTask
            The created annotation task object
        """
        annotation_task_params = CreateAnnotationTaskParams(
            # Since as mentioned above, we are not passing annotation_form intentionally, we can just assume empty ones.
            annotation_form=AnnotationFormModel(),
            description=_wrap_in_unset(description),
            name=name,
        )

        try:
            created_annotation_task = create_annotation_task(
                dataset_uid=dataset_uid,
                body=annotation_task_params,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        return cls.get(created_annotation_task.annotation_task_uid)

    @classmethod
    def get(cls, annotation_task_uid: int) -> "AnnotationTask":
        """Get an annotation task by UID.

        Parameters
        ----------
        annotation_task_uid
            The UID of the annotation task to retrieve

        Returns
        -------
        AnnotationTask
            The annotation task object
        """
        try:
            annotation_task = get_annotation_task(annotation_task_uid)
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        return cls._from_response_model(annotation_task)

    @classmethod
    def list(cls, dataset: IdType) -> List["AnnotationTask"]:
        """List all annotation tasks for a given dataset.

        Parameters
        ----------
        dataset
            The dataset UID or dataset object to list annotation tasks for

        Returns
        -------
        List[AnnotationTask]
            A list of annotation task objects
        """
        try:
            dataset_uid = get_dataset_uid(dataset)
            api_tasks = get_annotation_tasks_for_dataset(dataset_uid)
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        # Convert API models to AnnotationTask SDK objects
        return [cls._from_response_model(task) for task in api_tasks]

    @classmethod
    def delete(cls, annotation_task_uid: int) -> None:
        """Delete an annotation task.

        Parameters
        ----------
        annotation_task_uid
            The UID of the annotation task to delete
        """
        try:
            delete_annotation_task(annotation_task_uid=annotation_task_uid)
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update an annotation task.

        Parameters
        ----------
        name
            The new name for the annotation task, by default None
        description
            The new description for the annotation task, by default None
        """
        update_body = UpdateAnnotationTaskParams(
            annotation_task_uid=self.uid,
            name=_wrap_in_unset(name),
            description=_wrap_in_unset(description),
        )

        try:
            update_annotation_task(annotation_task_uid=self.uid, body=update_body)

            # Update the in-memory object properties after successful API call
            if name is not None:
                self._name = name
            if description is not None:
                self._description = description

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    # ----------------------------------
    # DATA FRAME OPERATIONS
    # ----------------------------------
    def get_dataframe(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> pd.DataFrame:
        """Fetch the dataset columns for all the datapoints in an annotation task.

        Parameters
        ----------
        limit
            The max number of rows to return. If None, all rows will be returned.
        offset
            Rows will be returned starting at this index.

        Returns
        -------
        pd.DataFrame
            DataFrame containing the dataset data
        """
        try:
            response = fetch_annotation_task_dataframes(
                annotation_task_uid=self.uid,
                dataset_uid=self.dataset_uid,
                limit=_wrap_in_unset(limit),
                offset=offset,
                include_x_uids=True,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        # Do not include annotation data
        excluded_columns = [ANNOTATION_TASK_STATUS_COL, ASSIGNEES_COL]
        df = pd.DataFrame([item.to_dict() for item in response.data])
        if not df.empty:
            df = df.drop(columns=excluded_columns)
            df = df.rename(columns={X_UID_COL: DATAPOINT_UID_COL})
            df = df.set_index(DATAPOINT_UID_COL)

        return df

    def get_annotation_status(self, user_format: bool = True) -> pd.DataFrame:
        """Fetch the task columns (assignees, status) for all the datapoints in an annotation task.

        Parameters
        ----------
        user_format
            If True, assignee names are returned instead of uids

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns: x_uid (this is the index), assignees (list of user UIDs or usernames), status (str)
            The DataFrame will have one row per datapoint in the annotation task

            Example:
                Data Point ID    Assignee(s)         Status
                ----------       ----------          ----------
                doc::1           [101, 102]          IN_ANNOTATION
                doc::2           [103]               READY_FOR_REVIEW
                doc::3           [101, 104]          COMPLETED
                doc::4           []                  NEEDS_ASSIGNEES
        """
        x_uids = self.x_uids

        if len(x_uids) == 0:
            return pd.DataFrame(columns=["assignees", "status"]).rename_axis(
                DATAPOINT_UID_COL
            )

        try:
            response = fetch_annotation_task_dataframes(
                annotation_task_uid=self.uid,
                dataset_uid=self.dataset_uid,
                include_x_uids=True,
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        records = [item.to_dict() for item in response.data]
        full_df = pd.DataFrame(records)
        if full_df.empty:
            df = pd.DataFrame(
                [
                    {
                        DATAPOINT_UID_COL: x_uid,
                        "assignees": [],
                        "status": DataPointStatus.NEEDS_ASSIGNEES,
                    }
                    for x_uid in x_uids
                ]
            ).set_index(DATAPOINT_UID_COL)
            df.index.name = DATAPOINT_UID_COL
            return df

        # Extract only the columns we need
        status_data = []

        df_by_x_uid = {
            row[DATAPOINT_UID_COL]: row for row in full_df.to_dict(orient="records")
        }

        for x_uid in x_uids:
            row = df_by_x_uid.get(x_uid)

            # In case the x_uid is missing in the fetched dataframe, we assume unassigned status and no assignees
            if row is None:
                status_data.append(
                    {
                        DATAPOINT_UID_COL: x_uid,
                        "assignees": [],
                        "status": DataPointStatus.NEEDS_ASSIGNEES,
                    }
                )
                continue

            status_data.append(
                {
                    DATAPOINT_UID_COL: x_uid,
                    "assignees": (
                        row["__ASSIGNEES"]
                        if isinstance(row["__ASSIGNEES"], list)
                        else []
                    ),
                    "status": str(row["__STATUS"]),
                }
            )

        df = pd.DataFrame(status_data)
        df = df.set_index(DATAPOINT_UID_COL)

        if user_format:
            try:
                dataset_response = fetch_dataset_by_uid(self.dataset_uid)

                workspace_uid = dataset_response.workspace_uid
                if workspace_uid is UNSET:
                    raise ValueError("Dataset is missing a valid workspace UID")
                assert isinstance(workspace_uid, int)  # mypy

                users_response = get_users(
                    workspace_uid=workspace_uid, include_inactive=True
                )
                uid_to_username = {
                    user.user_uid: user.username for user in users_response
                }

                df["assignees"] = df["assignees"].apply(
                    lambda assignee_list: (
                        [
                            uid_to_username.get(uid, f"unknown_user_{uid}")
                            for uid in assignee_list
                        ]
                        if assignee_list
                        else []
                    )
                )
            except HTTPError as e:
                # If we can't fetch users, fall back to UIDs
                logger.warning(
                    "Could not fetch necessary info for mapping user names. Falling back to user UIDs.",
                    exc_info=True,
                )

        return df

    # ----------------------------------
    # ANNOTATION OPERATIONS
    # ----------------------------------

    def _get_annotation_df_column_names(self) -> List[str]:
        """Get all possible column names for the annotation DataFrame."""
        replacements = {
            "label_schema": "label_schema_uid",
            "source": "source_uid",
        }
        removals = {
            "x_uid",
            "annotation_uid",
            "split",
            "batch_uid",
        }  # these are always in the index or excluded
        columns = [
            replacements.get(col, col)
            for col in ANNOTATION_FIELD_NAMES
            if col not in removals
        ]

        return columns

    def _convert_annotation_dict_to_model(
        self, dict_annotations: List[Dict], user_format: bool
    ) -> List[CreateDatasetAnnotationParams]:
        """Convert a dictionary representation of an annotation to the API model.

        Parameters
        ----------
        dict_annotations
            A list of dictionaries containing annotation parameters
        user_format
            True if annotations labels are in user format, otherwise they must be raw label values.

        Returns
        -------
        List[CreateDatasetAnnotationParams]
            The converted annotations
        """
        converted_annotations = []
        required_fields, optional_fields = (
            CREATE_ANNOTATION_FIELD_NAMES_REQ,
            CREATE_ANNOTATION_FIELD_NAMES_OPT,
        )

        for annotation_dict in dict_annotations:
            try:
                # Handle metadata conversion if present
                processed_dict = annotation_dict.copy()
                if "metadata" in processed_dict:
                    if processed_dict["metadata"] is None:
                        # Convert None to UNSET because CreateDatasetAnnotationParams does not accept None for metadata
                        processed_dict["metadata"] = UNSET
                    elif isinstance(processed_dict["metadata"], dict):
                        # Convert dict to CreateDatasetAnnotationParamsMetadata
                        processed_dict["metadata"] = (
                            CreateDatasetAnnotationParamsMetadata.from_dict(
                                processed_dict["metadata"]
                            )
                        )

                converted_annotations.append(
                    CreateDatasetAnnotationParams(
                        **processed_dict,
                        annotation_task_uid=self.uid,
                        convert_to_raw_format=user_format,
                    )
                )
            except TypeError as e:
                error_msg = str(e)

                # Check for missing required arguments
                if "missing" in error_msg.lower() and "required" in error_msg.lower():
                    # Try to extract the missing field name from the error message
                    missing_field = None
                    for field in required_fields:
                        if field in error_msg:
                            missing_field = field
                            break

                    if missing_field:
                        raise ValueError(
                            f"Missing required field '{missing_field}' in annotation: {annotation_dict}. "
                            f"Required fields: {required_fields}. Optional fields: {optional_fields}."
                        ) from e
                    else:
                        raise ValueError(
                            f"Missing required field in annotation: {annotation_dict}. "
                            f"Required fields: {required_fields}. Optional fields: {optional_fields}. "
                            f"Error: {error_msg}"
                        ) from e
                # Check for unexpected keyword arguments
                elif "unexpected keyword argument" in error_msg.lower():
                    # Extract the unexpected field name from the error message
                    # Format: "got an unexpected keyword argument 'field_name'"

                    match = re.search(r"unexpected keyword argument '(\w+)'", error_msg)
                    unexpected_field = match.group(1) if match else "unknown"

                    all_valid_fields = required_fields | optional_fields
                    annotation_fields = set(annotation_dict.keys())
                    unexpected_fields = annotation_fields - all_valid_fields

                    raise ValueError(
                        f"Unexpected field(s) {list(unexpected_fields)} in annotation: {annotation_dict}. "
                        f"Valid fields are - Required: {required_fields}, Optional: {optional_fields}. "
                        f"Remove the unexpected field(s) from your annotation data."
                    ) from e
                else:
                    # Handle other type errors (invalid field types, etc.)
                    raise ValueError(
                        f"Invalid field type in annotation: {annotation_dict}. "
                        f"Required fields: {required_fields}. Optional fields: {optional_fields}. "
                        f"Error: {error_msg}"
                    ) from e
            except Exception as e:
                # Handle other validation errors
                error_msg = str(e)
                raise ValueError(
                    f"Validation failed for annotation: {annotation_dict}. "
                    f"Required fields: {required_fields}. Optional fields: {optional_fields}. "
                    f"Error: {error_msg}"
                ) from e
        return converted_annotations

    def _convert_dataframe_to_model(
        self, df: pd.DataFrame, user_format: bool
    ) -> List[CreateDatasetAnnotationParams]:
        """Convert a DataFrame representation of annotations to the API model.

        Parameters
        ----------
        df
            A pandas DataFrame containing annotation data

        user_format
            True if annotations labels are in user format, otherwise they must be raw label values.


        Returns
        -------
        List[CreateDatasetAnnotationParams]
            The converted annotations
        """
        dict_annotations = (
            df.where(pd.notnull(df), None)  # needed because we can't JSON serialize NaN
            .reset_index(
                drop=True
            )  # needed to avoid issues with index being included as a field in the dict
            .to_dict(orient="records")
        )
        return self._convert_annotation_dict_to_model(
            dict_annotations, user_format=user_format
        )

    def _convert_all_annotation_types(
        self,
        annotations: Union[pd.DataFrame, List[Dict]],
        user_format: bool,
    ) -> List[CreateDatasetAnnotationParams]:
        """Convert a list of Annotation objects to the API model.

        Parameters
        ----------
        annotations
            A list of Annotation objects

        user_format
            True if annotations labels are in user format, otherwise they must be raw label values.

        Returns
        -------
        List[CreateDatasetAnnotationParams]
            The converted annotations
        """
        # Type dispatch to call the appropriate conversion method
        if isinstance(annotations, pd.DataFrame):
            converted_annotations = self._convert_dataframe_to_model(
                annotations, user_format=user_format
            )
        elif isinstance(annotations, list) and len(annotations) > 0:
            try:
                casted_annotations = cast(List[Dict], annotations)
            except TypeError as e:
                first_item = annotations[0] if annotations else None
                raise ValueError(
                    f"Unsupported annotation type in list: {type(first_item)}. "
                    "Expected Dict objects."
                ) from e
            converted_annotations = self._convert_annotation_dict_to_model(
                casted_annotations, user_format=user_format
            )
        elif isinstance(annotations, list) and len(annotations) == 0:
            # Empty list - nothing to add
            return []
        else:
            raise ValueError(
                f"Unsupported annotations type: {type(annotations)}. "
                "Expected pandas.DataFrame or List[Dict]."
            )
        return converted_annotations

    def add_annotations(
        self, annotations: Union[pd.DataFrame, List[Dict]], user_format: bool = True
    ) -> None:
        """Add annotations to an annotation task.

        Parameters
        ----------
        annotations
            Annotations to add to the task. Can be provided in one of two formats:

            1. **DataFrame**: A pandas DataFrame with annotation data
            2. **List of Dicts**: A list of dictionaries with annotation parameters

        user_format
            True if annotation labels in data are in user format, otherwise they must be raw label values.

        Examples
        --------

        **DataFrame Input:**

        >>> import pandas as pd
        >>> df = pd.DataFrame([
        ...     {
        ...         'x_uid': 'doc::1',
        ...         'dataset_uid': 1001,
        ...         'label_schema_uid': 101,
        ...         'label': 'positive',
        ...         'metadata': {'confidence': 0.95},
        ...         'freeform_text': None
        ...     },
        ...     {
        ...         'x_uid': 'doc::2',
        ...         'dataset_uid': 1001,
        ...         'label_schema_uid': 101,
        ...         'label': 'negative',
        ...         'metadata': {'confidence': 0.87},
        ...         'freeform_text': None
        ...     }
        ... ])
        >>> annotation_task.add_annotations(df)

        **List of Dictionaries Input:**

        >>> annotations_list = [
        ...     {
        ...         'x_uid': 'doc::3',
        ...         'dataset_uid': 1002,
        ...         'label_schema_uid': 102,
        ...         'label': {'spans': [[0, 10, 'PERSON'], [15, 25, 'ORG']]},
        ...         'metadata': {'annotator': 'user_123'},
        ...         'freeform_text': None
        ...     },
        ...     {
        ...         'x_uid': 'doc::4',
        ...         'dataset_uid': 1002,
        ...         'label_schema_uid': 103,
        ...         'label': {},  # Empty for text annotations
        ...         'metadata': {},
        ...         'freeform_text': 'This document discusses climate change impacts.'
        ...     }
        ... ]
        >>> annotation_task.add_annotations(annotations_list)


        **Dictionaries of different label types:**

        >>> # Single-choice classification
        >>> single_choice = [{'x_uid': 'doc::6', 'dataset_uid': 1003, 'label_schema_uid': 101, 'label': 'category_a'}]
        >>>
        >>> # Multi-choice classification
        >>> multi_choice = [{'x_uid': 'doc::7', 'dataset_uid': 1003, 'label_schema_uid': 102, 'label': ['tag1', 'tag2', 'tag3']}]
        >>>
        >>> # Sequence tagging (NER)
        >>> sequence_tags = [{'x_uid': 'doc::8', 'dataset_uid': 1003, 'label_schema_uid': 103, 'label': [[0, 5, 'B-PER'], [6, 15, 'B-LOC']]}]
        >>>
        >>> # Text annotation (freeform)
        >>> text_annotation = [{'x_uid': 'doc::9', 'dataset_uid': 1003, 'label_schema_uid': 104, 'label': {}, 'freeform_text': 'User feedback here'}]
        >>>
        >>> annotation_task.add_annotations(single_choice)
        >>> annotation_task.add_annotations(multi_choice)
        >>> annotation_task.add_annotations(sequence_tags)
        >>> annotation_task.add_annotations(text_annotation)

        Notes
        -----
        - All annotations must belong to label schemas associated with this annotation task
        - The `x_uid` must correspond to datapoints in the task's dataset
        - For text-based labels (`is_text_label=True`), use `freeform_text` instead of `label`
        - For structured labels, use the `label` field with appropriate format for the label type
        - Metadata is optional and can contain arbitrary key-value pairs
        - Timestamps (`ts`) are auto-generated if not provided

        Raises
        ------
        ValueError
            If annotation format is invalid or contains missing required fields
        UserInputError
            If x_uid is empty or label_schema_uid is not associated with this task
        """
        converted_annotations: List[CreateDatasetAnnotationParams] = (
            self._convert_all_annotation_types(annotations, user_format=user_format)
        )
        if not converted_annotations or len(converted_annotations) == 0:
            return

        try:
            import_params = ImportDatasetAnnotationsParams(
                dataset_uid=self.dataset_uid,
                annotations=converted_annotations,
            )
            import_annotations(body=import_params)
        except HTTPError as e:
            raise ValueError(
                f"Error importing annotations: {e.response.json()['detail']}"
            ) from e

    def get_annotations(
        self,
        user_format: bool = True,  # if True, convert raw label value to label names
        # the following parameters are used to filter the results
        user_uids: Optional[List[int]] = None,
        label_schema_uids: Optional[List[int]] = None,
        source_uids: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """Get annotations from an annotation task, filtered by the uids specified.

        Parameters
        ----------
        user_format
            If True, convert raw label value to label names
        user_uids
            List of user UIDs to filter annotations by, by default None
        label_schema_uids
            List of label schema UIDs to filter annotations by, by default None
        source_uids
            List of source UIDs to filter annotations by, by default None

        Returns
        -------
        pd.DataFrame
            DataFrame containing the filtered annotations with label values transformed to label names if user_format is True
        """
        response = get_annotations_dataset_annotations_get(
            dataset_uid=self.dataset_uid,
            user_uids=user_uids if user_uids is not None else UNSET,
            label_schema_uids=(
                label_schema_uids
                if label_schema_uids is not None
                else self.label_schema_uids
            ),
            x_uids=self.x_uids if self.x_uids else UNSET,
            annotation_task_uids=[self.uid],
            user_formatted_label=user_format,
        )

        expected_columns = self._get_annotation_df_column_names()

        # Flatten and filter annotations in one pass
        filtered_annotations = [
            (label_schema_group.label_schema_uid, annotation)
            for label_schema_group in response.annotations_grouped_by_label_schema
            for annotation in label_schema_group.annotations
            if source_uids is None or annotation.source.source_uid in source_uids
        ]

        # Early exit if no data after filtering
        if not filtered_annotations:
            df = pd.DataFrame(columns=expected_columns)
            df.index = pd.MultiIndex.from_tuples(
                [], names=[DATAPOINT_UID_COL, "annotation_uid"]
            )
            return df

        # Extract data using vectorized operations - single pass through annotations
        label_schema_uid_tuples, annotation_tuples = zip(*filtered_annotations)

        # Build all columns directly without intermediate dictionaries
        x_uids = [ann.x_uid for ann in annotation_tuples]
        annotation_uids = [ann.annotation_uid for ann in annotation_tuples]

        # Build column data using vectorized list comprehensions
        column_data = {}
        for column_name in expected_columns:
            if column_name == "label_schema_uid":
                column_data[column_name] = list(label_schema_uid_tuples)
            elif column_name == "source_uid":
                column_data[column_name] = [
                    (
                        ann.source.source_uid
                        if hasattr(ann, "source") and ann.source
                        else None
                    )
                    for ann in annotation_tuples
                ]
            elif column_name == "metadata":
                # Special handling for metadata to convert empty objects to None for pd.isna() compatibility
                column_data[column_name] = [
                    (
                        getattr(ann, column_name, None)
                        if hasattr(ann, column_name)
                        and getattr(ann, column_name, UNSET) is not UNSET
                        and getattr(ann, column_name, None) is not None
                        and (
                            # Check if metadata has any actual content
                            not hasattr(
                                getattr(ann, column_name), "additional_properties"
                            )
                            or bool(getattr(ann, column_name).additional_properties)
                        )
                        else None
                    )
                    for ann in annotation_tuples
                ]
            else:
                # Direct field extraction with UNSET handling
                column_data[column_name] = [
                    (
                        getattr(ann, column_name, None)
                        if hasattr(ann, column_name)
                        and getattr(ann, column_name, UNSET) is not UNSET
                        else None
                    )
                    for ann in annotation_tuples
                ]

        df = pd.DataFrame(
            column_data,
            index=pd.MultiIndex.from_arrays(
                [x_uids, annotation_uids], names=[DATAPOINT_UID_COL, "annotation_uid"]
            ),
        )

        return df

    # ----------------------------------
    # DATA POINT OPERATIONS
    # ----------------------------------
    def add_datapoints(self, x_uids: List[str]) -> None:
        """Add datapoints to the annotation task.

        Parameters
        ----------
        x_uids
            List of datapoint UIDs to add to the annotation task
        """
        params = DataPointSelectionParams(
            include_x_uids=x_uids,
        )

        try:
            response = add_x_uids_to_annotation_task(
                annotation_task_uid=self.uid,
                body=params,
            )
            failed = response.failed_x_uids
            added_xuids: List[str] = _unwrap_unset(response.added_x_uids, [])

            # Update the in-memory object properties after successful API call
            self._x_uids = list(set(self._x_uids).union(added_xuids))

            if failed and len(failed) > 0:
                failure_message = f"The following datapoints could not be added to annotation task {self.name}: {failed}"
                logger.warning(failure_message)
                print(failure_message)

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    def remove_datapoints(self, x_uids: List[str]) -> None:
        """Remove datapoints from the annotation task.

        Parameters
        ----------
        x_uids
            List of datapoint UIDs to remove from the annotation task
        """
        params = DataPointSelectionParams(
            include_x_uids=x_uids,
        )

        try:
            delete_x_uids_from_annotation_task(
                annotation_task_uid=self.uid,
                body=params,
            )

            # Update the in-memory object properties after successful API call
            self._x_uids = list(set(self._x_uids) - set(x_uids))

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    # ----------------------------------
    # USER OPERATIONS
    # ----------------------------------

    def _get_user_uids_from_users(self, users: List[IdType]) -> List[int]:
        """Convert a list of users (UIDs or usernames) to a list of user UIDs.

        Parameters
        ----------
        users
            List of users. Can be user UIDs (int) or usernames (str).

        Returns
        -------
        List[int]
            List of normalized user UIDs

        Raises
        ------
        ValueError
            If username is not found in workspace or invalid user type is provided
        """
        # Get workspace user mappings
        _, username_to_uid = self._get_workspace_user_mappings()

        # Normalize input users to a list of integer UIDs
        normalized_user_uids: List[int] = []
        for user_id in users:
            if isinstance(user_id, int):
                normalized_user_uids.append(user_id)
            elif isinstance(user_id, str):
                # It's a username, convert to UID
                if user_id not in username_to_uid:
                    raise ValueError(f"Username '{user_id}' not found in workspace")
                normalized_user_uids.append(username_to_uid[user_id])
            else:
                raise ValueError(
                    f"Invalid user type: {type(user_id)}. Expected int (UID) or str (username)"
                )

        return normalized_user_uids

    def _get_workspace_user_mappings(self) -> tuple[Dict[int, str], Dict[str, int]]:
        """Get workspace user mappings for UID-to-username and username-to-UID conversion.

        Returns
        -------
        tuple[Dict[int, str], Dict[str, int]]
            A tuple containing (uid_to_username, username_to_uid) mappings

        Raises
        ------
        ValueError
            If dataset is missing a valid workspace UID
        """
        # Get workspace users to create bidirectional mapping
        dataset_response = fetch_dataset_by_uid(self.dataset_uid)
        workspace_uid = dataset_response.workspace_uid
        if workspace_uid is UNSET:
            raise ValueError("Dataset is missing a valid workspace UID")
        assert isinstance(workspace_uid, int)  # mypy

        users_response = get_users(workspace_uid=workspace_uid, include_inactive=True)

        # Create bidirectional mappings
        uid_to_username = {user.user_uid: user.username for user in users_response}
        username_to_uid = {user.username: user.user_uid for user in users_response}

        return uid_to_username, username_to_uid

    def add_assignees(self, users: List[IdType], x_uids: List[str]) -> None:
        """Assign all of the listed users to the listed datapoints in the annotation task.

        Parameters
        ----------
        users
            List of users to assign to the datapoints. Can be user UIDs (int) or usernames (str).
        x_uids
            List of datapoint UIDs to assign the users to

        Raises
        ------
        ValueError
            If users or x_uids are empty, or if user input is invalid

        Examples
        --------
        Add assignees using user UIDs:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.add_assignees(users=[101, 102, 103], x_uids=["doc::1", "doc::2", "doc::3"])

        Add assignees using usernames:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.add_assignees(users=["alice", "bob", "charlie"], x_uids=["doc::1", "doc::2", "doc::3"])

        Add assignees using mixed usernames and UIDs:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.add_assignees(users=["alice", 102, "charlie"], x_uids=["doc::1", "doc::2", "doc::3"])
        """
        if not users:
            raise ValueError("users cannot be empty")
        if not x_uids:
            raise ValueError("x_uids cannot be empty")

        try:
            # Convert users (usernames/UIDs) to normalized user UIDs
            normalized_user_uids = self._get_user_uids_from_users(users)

            params = AddAssigneesToAnnotationTaskParams(
                user_uids=normalized_user_uids,
                include_x_uids=x_uids,
            )

            add_assignees_to_annotation_task(
                annotation_task_uid=self.uid,
                body=params,
            )
            logger.info(
                f"Successfully added {len(normalized_user_uids)} assignees to {len(x_uids)} datapoints "
                f"in annotation task {self.name}"
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    def remove_assignees(
        self, users: Optional[List[IdType]] = None, x_uids: Optional[List[str]] = None
    ) -> None:
        """Remove all of the listed users from the listed datapoints in the annotation task.

        If both users and x_uids are None, it will remove all assignees from all datapoints in the task.
        This is a non-destructive operation -- it removes the assignments but retains the annotations.

        Parameters
        ----------
        users
            A list of users to remove from listed datapoints, by default None.
            Can be user UIDs (int) or usernames (str). If None, all users assigned
            to listed datapoints will be removed from those datapoints.
        x_uids
            A list of the x_uids of datapoints to remove users from, by default None.
            If None, listed users will be removed from all the datapoints they are assigned to.

        Raises
        ------
        ValueError
            If fetching or deleting assignments fails

        Examples
        --------
        Remove specific users from specific datapoints using UIDs:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.remove_assignees(users=[101, 102], x_uids=["doc::1", "doc::2"])

        Remove specific users from specific datapoints using usernames:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.remove_assignees(users=["alice", "bob"], x_uids=["doc::1", "doc::2"])

        Remove specific users from specific datapoints using mixed identifiers:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.remove_assignees(users=["alice", 102], x_uids=["doc::1", "doc::2"])

        Remove specific users from all datapoints they are assigned to:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.remove_assignees(users=["alice", "bob"])

        Remove all users from specific datapoints:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.remove_assignees(x_uids=["doc::1", "doc::2"])

        Remove all assignees from all datapoints in the task:

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.remove_assignees()
        """
        try:
            # If users is None, we need to get all assigned users
            if users is None:
                assignees_response = get_annotation_task_assignees(
                    annotation_task_uid=self.uid
                )

                # Extract all unique user UIDs from the assignments
                all_user_uids = set()
                if (
                    assignees_response.assignments is not UNSET
                    and assignees_response.assignments
                ):
                    assignments_dict = assignees_response.assignments.to_dict()
                    for assigned_users in assignments_dict.values():
                        if isinstance(assigned_users, list):
                            all_user_uids.update(assigned_users)

                normalized_user_uids = list(all_user_uids)

                # If there are no assignees, nothing to remove
                if not normalized_user_uids:
                    logger.info(
                        f"No assignees found in annotation task {self.name}, "
                        "nothing to remove"
                    )
                    return
            else:
                # Convert users (usernames/UIDs) to normalized user UIDs
                normalized_user_uids = self._get_user_uids_from_users(users)

            # Prepare the parameters
            params = DeleteAssigneesFromAnnotationTaskParams(
                user_uids=normalized_user_uids,
            )

            # Handle x_uids parameter
            if x_uids is None:
                # Remove from all datapoints
                params.is_select_all = True
            else:
                # Remove from specific datapoints
                params.include_x_uids = x_uids

            delete_assignees_from_annotation_task(
                annotation_task_uid=self.uid,
                body=params,
            )

            user_count = len(normalized_user_uids)
            datapoint_info = (
                f"all datapoints in task {self.name}"
                if x_uids is None
                else f"{len(x_uids)} datapoints"
            )
            logger.info(
                f"Successfully removed {user_count} assignees from {datapoint_info} "
                f"in annotation task {self.name}"
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    def list_user_assignments(
        self, users: List[IdType], user_format: bool = True
    ) -> Dict[IdType, List[str]]:
        """Get user assignments in an annotation task.

        Parameters
        ----------
        users
            List of users to fetch annotation assignments for. Can be user UIDs (int) or usernames (str).
        user_format
            If true, return user names as keys; if false, return user UIDs as keys

        Returns
        -------
        Dict[str | int, List[str]]
            A dictionary with user keys (names if user_format is True, UIDs otherwise) and values containing
            lists of datapoint_uids that the user is assigned to

            Example::

                assignments = {
                    "Dr Bubbles": ["doc::1", "doc::2"],
                    "Rebekah": ["doc::5"],
                    "Hiromu": [],
                }

        Raises
        ------
        ValueError
            If user_uids is empty or if fetching assignments fails

        Examples
        --------
        Get assignments using user UIDs, returning usernames as keys:

        .. doctest::

            >>> from snorkelai.sdk.develop import AnnotationTask
            >>> task = AnnotationTask.get(annotation_task_uid=123)
            >>> assignments = task.list_user_assignments(users=[101, 102, 103])
            >>> # Returns dictionary with usernames as keys
            >>> # {'alice': ['doc::1', 'doc::2'], 'bob': ['doc::3'], 'charlie': []}

        Get assignments using usernames, returning usernames as keys:

        .. doctest::

            >>> from snorkelai.sdk.develop import AnnotationTask
            >>> task = AnnotationTask.get(annotation_task_uid=123)
            >>> assignments = task.list_user_assignments(users=['alice', 'bob', 'charlie'])
            >>> # Returns dictionary with usernames as keys
            >>> # {'alice': ['doc::1', 'doc::2'], 'bob': ['doc::3'], 'charlie': []}

        Get assignments using user UIDs, returning UIDs as keys:

        .. doctest::

            >>> from snorkelai.sdk.develop import AnnotationTask
            >>> task = AnnotationTask.get(annotation_task_uid=123)
            >>> assignments = task.list_user_assignments(users=[101, 102], user_format=False)
            >>> # Returns dictionary with user UIDs as keys
            >>> # {101: ['doc::1', 'doc::2'], 102: ['doc::3']}

        Get assignments using mixed input (usernames and UIDs):

        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            assignments = task.list_user_assignments(users=['alice', 102, 'charlie'])
        """
        if not users:
            raise ValueError("users cannot be empty")

        try:
            # Get workspace user mappings and convert users to UIDs
            uid_to_username, _ = self._get_workspace_user_mappings()
            normalized_user_uids = self._get_user_uids_from_users(users)

            # Fetch all assignments for the annotation task
            assignees_response = get_annotation_task_assignees(
                annotation_task_uid=self.uid
            )

            # Initialize result dictionary with all requested users having empty lists
            result: Dict[IdType, List[str]] = {}
            for user_uid in normalized_user_uids:
                user_key: IdType
                if user_format:
                    user_key = uid_to_username.get(user_uid, f"unknown_user_{user_uid}")
                else:
                    user_key = user_uid
                result[user_key] = []

            # Early return if no assignments exist
            if (
                assignees_response.assignments is UNSET
                or not assignees_response.assignments
            ):
                logger.info(
                    f"No assignments found for {len(normalized_user_uids)} users "
                    f"in annotation task {self.name}"
                )
                return result

            # Invert the mapping: from {x_uid: [user_uids]} to {user: [x_uids]}
            assignments_dict = assignees_response.assignments.to_dict()
            for x_uid, assigned_user_uids in assignments_dict.items():
                if not isinstance(assigned_user_uids, list):
                    continue

                for assigned_user_uid in assigned_user_uids:
                    # Only include if this user was requested
                    if assigned_user_uid not in normalized_user_uids:
                        continue

                    user_key_result: IdType
                    if user_format:
                        user_key_result = uid_to_username.get(
                            assigned_user_uid, f"unknown_user_{assigned_user_uid}"
                        )
                    else:
                        user_key_result = assigned_user_uid
                    result[user_key_result].append(x_uid)

            logger.info(
                f"Successfully fetched assignments for {len(normalized_user_uids)} users "
                f"in annotation task {self.name}"
            )

            return result

        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

    # ----------------------------------
    # LABEL SCHEMA OPERATIONS
    # ----------------------------------
    def add_label_schemas(self, label_schema_uids: List[int]) -> None:
        """Add label schemas to the annotation task.

        Label schemas will be displayed in the order in which they are added.

        Parameters
        ----------
        label_schema_uids
            List of label schema UIDs to add to the annotation task

        Raises
        ------
        ValueError
            If label_schema_uids is empty, label schemas are not existing in the dataset or if updating the annotation task fails
        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import AnnotationTask
            task = AnnotationTask.get(annotation_task_uid=123)
            task.add_label_schemas(label_schema_uids=[1, 2, 3])
        """
        if not label_schema_uids:
            raise ValueError("label_schema_uids cannot be empty")

        # Validate that all provided label schema UIDs exist on the dataset
        try:
            dataset_label_schemas = get_label_schemas(dataset_uid=self.dataset_uid)
            valid_label_schema_uids = {
                ls.label_schema_uid for ls in dataset_label_schemas
            }

            invalid_uids = [
                uid for uid in label_schema_uids if uid not in valid_label_schema_uids
            ]

            if invalid_uids:
                err_msg = (
                    f"The following label schema UIDs do not exist on dataset "
                    f"{self.dataset_uid}: {invalid_uids}"
                )
                raise ValueError(err_msg)

            # Get the current individual label schemas and append the new ones
            current_individual_schemas = list(
                self._annotation_form.individual_label_schemas
            )
            updated_individual_schemas = current_individual_schemas + label_schema_uids

            # Create the annotation form with updated individual label schemas
            annotation_form = AnnotationFormModel(
                individual_label_schemas=updated_individual_schemas
            )

            # Update the annotation task with the new annotation form
            params = UpdateAnnotationTaskParams(
                annotation_task_uid=self.uid, annotation_form=annotation_form
            )

            annotation_task = update_annotation_task(
                annotation_task_uid=self.uid, body=params
            )

            # Update the in-memory object after successful API call
            self._annotation_form.individual_label_schemas = _unwrap_unset(
                annotation_task.annotation_form.individual_label_schemas,
                [],
            )

            logger.info(
                f"Successfully added {len(label_schema_uids)} label schemas "
                f"to annotation task {self.name}"
            )
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
