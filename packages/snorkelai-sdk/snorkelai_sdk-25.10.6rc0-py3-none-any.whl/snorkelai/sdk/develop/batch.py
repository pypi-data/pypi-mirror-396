import datetime
import pathlib
import tempfile
from typing import List, Optional, Union, final

import pandas as pd
import requests

from snorkelai.sdk.client_v3.tdm.api.annotation import (
    commit_annotation_commit_dataset_annotation_post,
)
from snorkelai.sdk.client_v3.tdm.api.dataset_batch import (
    add_batch_datasets__dataset_uid__batch_post,
    delete_batch_dataset_batches__dataset_batch_uid__delete,
    export_batches_dataset_batches__dataset_uid__export_batches_get,
    get_batch_dataset_batches__dataset_batch_uid__get,
    get_batch_x_uids_dataset_batches__dataset_batch_uid__x_uids_get,
    update_batch_dataset_batches__dataset_batch_uid__put,
)
from snorkelai.sdk.client_v3.tdm.models.commit_dataset_annotation_params import (
    CommitDatasetAnnotationParams,
)
from snorkelai.sdk.client_v3.tdm.models.create_dataset_batch_payload import (
    CreateDatasetBatchPayload,
)
from snorkelai.sdk.client_v3.tdm.models.dataset_batch import DatasetBatch
from snorkelai.sdk.client_v3.tdm.models.selection_strategy import (
    SelectionStrategy,
)
from snorkelai.sdk.client_v3.tdm.models.update_dataset_batch_params import (
    UpdateDatasetBatchParams,
)
from snorkelai.sdk.client_v3.tdm.types import UNSET, Unset
from snorkelai.sdk.client_v3.utils import get_dataset_metadata
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.develop.label_schema import LabelSchema
from snorkelai.sdk.types.load import DATAPOINT_UID_COL

DEFAULT_LIST_DELIMITER = "|"
DEFAULT_CSV_DELIMITER = ","
DEFAULT_QUOTE_CHAR = '"'
DEFAULT_ESCAPE_CHAR = "\\"


def _get_label_schemas_from_batch_response(b: DatasetBatch) -> List[LabelSchema]:
    if b.label_schemas:
        return [
            LabelSchema.get(int(ls_uid)) for ls_uid in b.label_schemas.to_dict().keys()
        ]
    return []


@final
class Batch(Base):
    """The Batch object represents an annotation batch in Snorkel Flow. Currently, this
    interface only represents Dataset-level (not Node-level) annotation batches.
    """

    def __init__(
        self,
        name: str,
        uid: int,
        dataset_uid: int,
        label_schemas: List[LabelSchema],
        batch_size: int,
        ts: datetime.datetime,
        x_uids: List[str],
    ):
        """Create a batch object in-memory with necessary properties. This constructor
        should not be called directly, and should instead be accessed through the
        ``create()`` and ``get()`` methods.

        Parameters
        ----------
        name
            The name of the batch
        uid
            The UID for the batch within Snorkel Flow
        dataset_uid
            The UID for the dataset within Snorkel Flow
        label_schemas
            The list of label schemas associated with this batch
        batch_size
            The number of examples in the batch
        ts
            The timestamp at which the batch was created
        x_uids
            The UIDs for the examples in the batch

        """
        self._name = name
        self._uid = uid
        self._dataset_uid = dataset_uid
        self._label_schemas = label_schemas
        self._batch_size = batch_size
        self._ts = ts
        self._x_uids = x_uids

    # ---------------------------
    # BATCH PROPERTIES -- PRIVATE
    # ---------------------------

    # These are all object properties because they shouldn't be set directly by the user
    @property
    def name(self) -> str:
        """The name of the batch."""
        return self._name

    @property
    def uid(self) -> int:
        """The UID for the batch within Snorkel Flow."""
        return self._uid

    @property
    def dataset_uid(self) -> int:
        """The UID for the dataset within Snorkel Flow."""
        return self._dataset_uid

    @property
    def label_schemas(self) -> List[LabelSchema]:
        """The list of label schemas associated with this batch."""
        return self._label_schemas

    @property
    def batch_size(self) -> int:
        """The number of examples in the batch."""
        return self._batch_size

    @property
    def ts(self) -> datetime.datetime:
        """The timestamp at which the batch was created."""
        return self._ts

    @property
    def x_uids(self) -> List[str]:
        """The UIDs for the examples in the batch."""
        return self._x_uids

    # ---------------------------
    # INTERNAL METHODS
    # ---------------------------

    @classmethod
    def _make_batch_from_batch_response(cls, b: DatasetBatch) -> "Batch":
        return Batch(
            uid=b.batch_uid,
            name=b.name or "",
            dataset_uid=b.dataset_uid,
            label_schemas=_get_label_schemas_from_batch_response(b),
            batch_size=b.batch_size,
            ts=b.ts,
            x_uids=get_batch_x_uids_dataset_batches__dataset_batch_uid__x_uids_get(
                b.batch_uid
            ).x_uids,
        )

    # ----------------
    # BATCH OPERATIONS
    # ----------------

    @classmethod
    def create(  # type: ignore[override]
        cls,
        dataset_uid: int,
        name: Optional[str] = None,
        assignees: Optional[List[int]] = None,
        label_schemas: Optional[List[LabelSchema]] = None,
        batch_size: Optional[int] = None,
        randomize: Optional[bool] = False,
        random_seed: Optional[int] = 123,
        selection_strategy: Optional[SelectionStrategy] = None,
        split: Optional[str] = None,
        x_uids: Optional[List[str]] = None,
        filter_by_x_uids_not_in_batch: Optional[bool] = False,
        divide_x_uids_evenly_to_assignees: Optional[bool] = False,
    ) -> List["Batch"]:
        """Create one or more annotation batches for a dataset.

        Typically, Dataset.create_batches() is the recommended entrypoint for
        creating batches.

        Parameters
        ----------
        dataset_uid
            The UID for the dataset within Snorkel Flow
        name
            The name of the batch
        assignees
            The user UIDs for the assignees of the batches
        label_schemas
            The label schemas assigned for the batches
        batch_size
            The size of the batches
        randomize
            Whether to randomize the batches
        random_seed
            The seed for the randomization
        selection_strategy
            The SelectionStrategy for the batches
        split
            The split ("train", "test", or "valid") of the batches
        x_uids
            A list of datapoint uids to create batches from
        filter_by_x_uids_not_in_batch
            Whether to create batches with datapoints not in a batch
        divide_x_uids_evenly_to_assignees
            Whether to divide the datapoints evenly among the provided assignees

        Returns
        -------
        List[Batch]
            The list of created batches

        """
        if not get_dataset_metadata(dataset_uid).mta_enabled:
            raise ValueError(
                f"Multi-task annotation not enabled for dataset with UID {dataset_uid}. Cannot create batch."
            )
        label_schema_uids = [ls.uid for ls in label_schemas] if label_schemas else None
        payload_dict = dict(
            dataset_uid=dataset_uid,
            name=name,
            assignees=assignees,
            label_schema_uids=label_schema_uids,
            batch_size=batch_size,
            randomize=randomize,
            random_seed=random_seed,
            split=split,
            x_uids=x_uids,
            filter_by_unassigned_x_uids=filter_by_x_uids_not_in_batch,
            divide_x_uids_evenly_to_assignees=divide_x_uids_evenly_to_assignees,
        )
        if selection_strategy:
            payload_dict["selection_strategy"] = selection_strategy
        body = CreateDatasetBatchPayload.from_dict(payload_dict)
        batches_resp = add_batch_datasets__dataset_uid__batch_post(
            dataset_uid=dataset_uid, body=body
        )
        batches = [cls._make_batch_from_batch_response(b) for b in batches_resp]
        print(f"Successfully created {len(batches)} batches.")
        return batches

    def commit(
        self, source_uid: int, label_schema_uids: Optional[List[int]] = None
    ) -> None:
        """Commit a source on a batch as ground truth.

        Parameters
        ----------
        source_uid
            The UID for the source on the batch
        label_schema_uids
            The label schema UIDs to commit, defaults to all label schemas if not set

        """
        body = CommitDatasetAnnotationParams(
            dataset_uid=self.dataset_uid,
            source_uid=source_uid,
            batch_uid=self.uid,
            label_schema_uids=(
                [ls.uid for ls in self.label_schemas]
                if label_schema_uids is None
                else label_schema_uids
            ),
        )
        commit_annotation_commit_dataset_annotation_post(body=body)

    @classmethod
    def get(cls, batch_uid: int) -> "Batch":
        """Retrieve an annotation batch by its UID.

        Parameters
        ----------
        batch_uid
            The UID for the batch within Snorkel Flow

        Returns
        -------
        Batch
            The batch object

        """
        try:
            batch_resp = get_batch_dataset_batches__dataset_batch_uid__get(
                dataset_batch_uid=batch_uid
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"No batch found with UID {batch_uid}.") from e
            raise e
        batch = cls._make_batch_from_batch_response(batch_resp)
        print(f"Successfully retrieved batch with UID {batch.uid}.")
        return batch

    @classmethod
    def delete(cls, batch_uid: int) -> None:
        """Delete an annotation batch by its UID.

        Parameters
        ----------
        batch_uid
            The UID for the batch within Snorkel Flow

        """
        try:
            delete_batch_dataset_batches__dataset_batch_uid__delete(
                dataset_batch_uid=batch_uid
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"No batch found with UID {batch_uid}.") from e
            raise e
        print(f"Successfully deleted batch with UID {batch_uid}.")

    def update(
        self,
        name: Optional[str] = None,
        assignees: Optional[List[int]] = None,
        expert_source_uid: Optional[int] = None,
    ) -> None:
        """Update properties of the annotation batch.

        Parameters
        ----------
        name
            The new name of the batch
        assignees
            The user UIDs for the new assignees of the batches
        expert_source_uid
            The UID for the new expert source of the batches

        """
        body = UpdateDatasetBatchParams.from_dict(
            dict(
                batch_name=name,
                assignees=assignees,
                expert_source_uid=expert_source_uid,
            )
        )
        update_batch_dataset_batches__dataset_batch_uid__put(
            dataset_batch_uid=self.uid, body=body
        )
        if name:
            self._name = name
        print("Successfully updated batch.")

    def _fetch_batch_data(
        self,
        selected_fields: Optional[List[str]],
        include_annotations: bool,
        include_ground_truth: bool,
        max_rows: int,
        csv_delimiter: str,
        quote_char: str,
        escape_char: str,
    ) -> bytes:
        """Return bytes representing the zipped export of the batch data."""
        selected_fields_parsed: Union[List[str], Unset] = selected_fields or UNSET
        return export_batches_dataset_batches__dataset_uid__export_batches_get(
            self._dataset_uid,
            batch_uids=[self.uid],
            selected_fields=selected_fields_parsed,
            include_annotations=include_annotations,
            include_ground_truth=include_ground_truth,
            max_datapoints_to_export=max_rows,
            max_chars_per_column=100_000,
            csv_delimiter=csv_delimiter,
            quote_char=quote_char,
            escape_char=escape_char,
            raw=True,
        ).content

    def export(
        self,
        path: Union[str, pathlib.Path],
        selected_fields: Optional[List[str]] = None,
        include_annotations: bool = False,
        include_ground_truth: bool = False,
        max_rows: int = 10_000,
        csv_delimiter: str = DEFAULT_CSV_DELIMITER,
        quote_char: str = DEFAULT_QUOTE_CHAR,
        escape_char: str = DEFAULT_ESCAPE_CHAR,
    ) -> pathlib.Path:
        """Export the batch to a zipped CSV file.

        Parameters
        ----------
        path
            The path to the zipped CSV file. If the path does not end in .zip, it will be
            appended to the path.
        selected_fields
            A list of fields to export. If not set, all fields will be exported.
        include_annotations
            Whether to include annotations in the export
        include_ground_truth
            Whether to include ground truth in the export
        max_rows
            The maximum number of rows to export
        csv_delimiter
            The delimiter to use for CSV fields
        quote_char
            The character to use for quoted fields in the CSV
        escape_char
            The character to use for escaping special characters in the CSV

        Returns
        -------
        pathlib.Path
            The path to the zipped CSV file

        """
        path_obj = path if isinstance(path, pathlib.Path) else pathlib.Path(path)
        if path_obj.is_dir():
            raise ValueError(
                f"Path {path_obj} is a directory. Please provide the full path to the desired destination."
            )
        if not path_obj.parent.exists():
            raise ValueError(
                f"Parent directory {path_obj.parent} does not exist. Please create it first."
            )
        if path_obj.suffix.lower() != ".zip":
            path_obj = path_obj.with_suffix(f"{path_obj.suffix}.zip")
        with open(path_obj, "wb") as f:
            f.write(
                self._fetch_batch_data(
                    selected_fields=selected_fields,
                    include_annotations=include_annotations,
                    include_ground_truth=include_ground_truth,
                    max_rows=max_rows,
                    csv_delimiter=csv_delimiter,
                    quote_char=quote_char,
                    escape_char=escape_char,
                )
            )
        return path_obj

    def get_dataframe(
        self,
        selected_fields: Optional[List[str]] = None,
        include_annotations: bool = False,
        include_ground_truth: bool = False,
        max_rows: int = 10_000,
    ) -> pd.DataFrame:
        """Get a pandas DataFrame representation of the batch.

        Parameters
        ----------
        selected_fields
            A list of fields to include in the DataFrame. If not set, all fields will be included.
        include_annotations
            Whether to include annotations in the DataFrame
        include_ground_truth
            Whether to include ground truth in the DataFrame
        max_rows
            The maximum number of rows to include in the DataFrame

        Returns
        -------
        pd.DataFrame
            The pandas DataFrame representation of the batch

        """
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".zip") as f:
            f.write(
                self._fetch_batch_data(
                    selected_fields=selected_fields,
                    include_annotations=include_annotations,
                    include_ground_truth=include_ground_truth,
                    max_rows=max_rows,
                    csv_delimiter=DEFAULT_CSV_DELIMITER,
                    quote_char=DEFAULT_QUOTE_CHAR,
                    escape_char=DEFAULT_ESCAPE_CHAR,
                )
            )
            f.flush()
            return pd.read_csv(
                f.name,
                compression="zip",
                index_col=DATAPOINT_UID_COL,
                delimiter=DEFAULT_CSV_DELIMITER,
                quotechar=DEFAULT_QUOTE_CHAR,
                escapechar=DEFAULT_ESCAPE_CHAR,
            )
