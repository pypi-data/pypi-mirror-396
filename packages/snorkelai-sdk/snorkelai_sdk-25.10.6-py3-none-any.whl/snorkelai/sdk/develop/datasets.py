import io
import json
import os
import uuid
from functools import wraps
from typing import Any, Callable, Dict, List, Literal, Optional, Union, final, overload

import pandas as pd
import requests
from fsspec.utils import infer_storage_options

from snorkelai.sdk.client_v3.tdm import models
from snorkelai.sdk.client_v3.tdm.api.dataset_batch import (
    get_batches_for_dataset_datasets__dataset_uid__batches_get,
)
from snorkelai.sdk.client_v3.tdm.api.dataset_ground_truth import (
    get_dataset_ground_truth_dataset_ground_truth_get,
    import_dataset_ground_truth_dataset__dataset_uid__ingest_ground_truth_post,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    create_dataset as create_dataset_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    delete_dataset as delete_dataset_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    edit_dataset,
    fetch_dataset_dataframes_datasets__dataset_uid__dataframes_get,
)
from snorkelai.sdk.client_v3.tdm.api.datasets import (
    get_datasets as get_datasets_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.datasources import (
    delete_datasource as delete_datasource_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.datasources import (
    ingest_datasource_datasets__dataset_uid__data_sources_post,
    list_dataset_datasources_datasets__dataset_uid__data_sources_get,
    put_datasource_data_sources__datasource_uid__put,
    upload_datasource_datasets__dataset_uid__upload_post,
)
from snorkelai.sdk.client_v3.tdm.api.datasources import (
    swap_datasource_datasets__dataset_uid__datasources__datasource_uid__swap_post as swap_datasource_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.label_schemas import (
    list_label_schemas_label_schemas_get,
)
from snorkelai.sdk.client_v3.tdm.models.base_dataset import BaseDataset as TDMDataset
from snorkelai.sdk.client_v3.tdm.models.body_upload_datasource_datasets_dataset_uid_upload_post import (
    BodyUploadDatasourceDatasetsDatasetUidUploadPost,
)
from snorkelai.sdk.client_v3.tdm.models.data_frame_response import DataFrameResponse
from snorkelai.sdk.client_v3.tdm.models.ground_truth_df_model import GroundTruthDFModel
from snorkelai.sdk.client_v3.tdm.models.import_dataset_ground_truth_params import (
    ImportDatasetGroundTruthParams,
)
from snorkelai.sdk.client_v3.tdm.models.ingest_and_swap_datasource_payload import (
    IngestAndSwapDatasourcePayload,
)
from snorkelai.sdk.client_v3.tdm.models.put_datasource import PutDatasource
from snorkelai.sdk.client_v3.tdm.models.remove_dataset_request import (
    RemoveDatasetRequest,
)
from snorkelai.sdk.client_v3.tdm.models.remove_datasource_request import (
    RemoveDatasourceRequest,
)
from snorkelai.sdk.client_v3.tdm.models.selection_strategy import SelectionStrategy
from snorkelai.sdk.client_v3.tdm.models.single_data_source_ingestion_request import (
    SingleDataSourceIngestionRequest,
)
from snorkelai.sdk.client_v3.tdm.types import UNSET, File, Unset
from snorkelai.sdk.client_v3.utils import (
    DEFAULT_WORKSPACE_UID,
    IdType,
    _wrap_in_unset,
    get_dataset_metadata,
    get_workspace_uid,
    poll_job_status,
)
from snorkelai.sdk.context.ctx import SnorkelSDKContext
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.develop.batch import Batch
from snorkelai.sdk.develop.label_schema import LabelSchema
from snorkelai.sdk.extraction.span import SpanCols
from snorkelai.sdk.serialization.pandas import serialize_dataframe
from snorkelai.sdk.types.load import (
    DATAPOINT_UID_COL,
)

ITER_CHUNK_SIZE = 128 * 1024 * 1024  # 128MB
LABEL_COLUMN_NAME = "label"


def _require_mta_enabled(func: Callable) -> Callable:
    # Decorator for Dataset functions that require multi-task annotation to be enabled

    @wraps(func)
    def _wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        self._check_mta_enabled()
        return func(self, *args, **kwargs)

    return _wrapper


@final
class Dataset(Base):
    """The Dataset object represents a dataset in Snorkel Flow.

    ===================
    Datasets Quickstart
    ===================

    In this quickstart, we will create a Dataset and upload a file to that Dataset as a data source. We will then show how you might go about
    ingesting that data into the platform.

    We will need the following imports

    .. testcode::

        from snorkelai.sdk.develop import Dataset
        import snorkelai.sdk.client as sai
        import pandas as pd
        ctx = sai.SnorkelSDKContext.from_endpoint_url()

    We will begin by creating a new Dataset.

    .. doctest::

        >>> contracts_dataset = Dataset.create("contracts-dataset")
        Successfully created dataset contracts-dataset with UID 0 in workspace 0

    Next, we will attempt to save a file to the Dataset as a data source. This file will be in S3.
    File upload will initially fail because this file contains null values.

    .. doctest::

        >>> contracts_dataset.create_datasource("s3://snorkel-contracts-dataset/dev.parquet", uid_col="uid", split="train")
        UserInputError: Errors...

    In this particular example, we decide we don't care about these rows, so we can use Pandas to edit the file and remove the null values. We can then re-upload the data, this time
    uploading the DataFrame directly without needing to save it to a file again. In some other cases, you may want to either edit those null cells or fix them in your upstream data pipeline.

    .. doctest::

        >>> df = pd.read_parquet("s3://snorkel-contracts-dataset/dev.parquet")
        >>> df = df.dropna()
        >>> contracts_dataset.create_datasource(df, uid_col="uid", split="train")
        +0.07s Starting data ingestion
        +1.85s Ingesting data
        +2.05s Data ingestion complete


    To verify that has worked correctly, we can view this Dataset's data sources.

    .. doctest::

        >>> contracts_dataset.datasources
        [{'datasource_uid': 668,...}]


    ================
    Dataset Concepts
    ================

    --------
    Datasets
    --------
    Datasets are how your data is represented in Snorkel Flow. Snorkel Flow projects always begin with a single Dataset.
    Datasets bring external data into Snorkel Flow and help manage that data once it has been ingested. Datasets are composed
    of individual chunks of data, called **data sources**, and provides an interface for managing individual data sources.

    ------------
    Data Sources
    ------------
    Data sources are the individual chunks of data that make up a Dataset. A data source can be a file you upload from local storage,
    a file located in a remote (S3, MinIO, etc.) storage service, or an in-memory Pandas DataFrame. Data sources shouldn't be touched directly,
    but should be managed by interfacing with their parent Dataset. The best way to deal
    with data sources is to treat them as blocks of data, which can be added and removed but only occasionally changed. Data sources can be given
    names during their creation, but are usually referred to using a data source UID, an integer ID assigned to each data source when it is created.

    --------------------
    Derived Data Sources
    --------------------
    When an application is created using a dataset, Snorkel Flow
    will create a *derived* data source for each data source in the dataset. Derived data sources are intermediate representations of data that track the lineage of the data as it is being processed and are associated with only one application. Note that some operations, such as changing the split of a data source, don't propagate to any of the derived data source once they are derived, and vice versa. Derived data sources are viewable in the Snorkel Flow UI on the "View Data Sources" button, accessible from the "Develop" screen of an application.

    --------------
    Modifying Data
    --------------
    In general, data sources should be treated as immutable. This means that you should avoid modifying the underlying data source once it has been uploaded.
    If your goal is to filter out rows, add feature columns, or remove feature columns, you should use an `Operator <https://docs.snorkel.ai/docs/user-guide/app-setup/operators/operators-transform-and-process-your-data>`_ to do so.
    Alternatively, you can modify your data upstream of Snorkel and create a new Dataset with your edited data.

    The Python SDK provides limited support for specific one-off operations on data sources. Sometimes you might need to reformat the data in an existing
    column to make it compatible with processing logic. In this case, you can use the ``dataset.update_datasource_data`` method to swap out an existing data source for a new one with the updated data. However,
    be aware that this is an irreversible change, and updating data in this way is an expensive operation that will require all downstream applications to be refreshed.

    ------
    Splits
    ------
    Data sources belong to *splits*. Splits help dictate how the data will be used in the model development process. Data sources allocated to the
    **train** split will be used for model training and labeling function development. Data sources allocated to the **valid** split will be used to validate
    models iteratively and to perform error analysis. Data sources allocated to the **test** split will be used to evaluate the final model. Data source splits
    may be updated as needed, but be aware that model metrics and labeling function performance will change based on how the splits are allocated.


    ----------------------
    Data Upload Guardrails
    ----------------------

    When you upload data to Snorkel Flow, it must pass a series of safety checks to ensure that the data is valid and safe to
    load into the platform. These checks include:

        * **Number of rows**: A single data source should not exceed 10 million rows. If your data source exceeds this limit, you should split it into multiple data sources before uploading.

        * **Column memory**: The average memory usage of a single column must be under 20MB across all columns in your data source. For performance, the average column memory usage should be under 5MB. If your data source exceeds this limit, you should split it into multiple data sources before uploading.

        * **Null values**: Snorkel Flow will not permit data to be uploaded if any null values exist in that data source. If you have null values in your data, you might want to clean them up with the Pandas ``fillna()`` method before uploading.

        * **Unique integer index**: Snorkel Flow requires that each data source have a unique integer index column. The values in this index must be unique among all datasources in the Dataset. The values must also be unique, non-negative integers. If your Dataset does not already have this stable index column, you must create one before uploading.

        * **Consistent schema**: All data sources in a single Dataset should have the same columns. All columns that are in multiple data sources must have the same type. If you have columns that exist in some data sources but not others, you may see unexpected behavior in downstream tasks.

    -------------
    Fetching UIDs
    -------------
    Methods in the ``Dataset`` class will sometimes require a UID parameter. This is the unique identifier for the Dataset within Snorkel Flow.
    The Dataset UID can be retrieved by calling ``.uid`` on a Dataset object. Data source methods will sometimes require a data source UID, which can
    be retrieved by printing out the datasources by calling ``my_dataset.datasources``. The data source UID is the ``datasource_uid`` field in the returned dictionary.


    """

    def __init__(self, name: str, uid: int, mta_enabled: bool):
        """Create a dataset object in-memory with necessary properties. This constructor should not be called directly,
        and should instead be accessed through the ``create()`` and ``get()`` methods

        Parameters
        ----------
        name
            The human-readable name of the dataset. Must be unique within the workspace
        uid
            The unique integer identifier for the dataset within Snorkel Flow
        mta_enabled
            Whether or not multi-task annotation is enabled for this dataset

        """
        self._name = name
        self._uid = uid
        self._mta_enabled = mta_enabled
        self._datasources: List[Dict[str, Any]] = []

    # -----------------------------
    # DATASET PROPERTIES -- PRIVATE
    # -----------------------------

    # These are all object properties because they shouldn't be set directly by the user
    @property
    def name(self) -> str:
        """The human-readable name of the dataset."""
        return self._name

    @property
    def uid(self) -> int:
        """The unique integer identifier for the dataset within Snorkel Flow."""
        return self._uid

    @property
    def mta_enabled(self) -> bool:
        """Whether or not multi-task annotation is enabled for this dataset."""
        return self._mta_enabled

    @property
    def datasources(self) -> List[Dict[str, Any]]:
        """A list of data sources and associated metadata belonging to this Dataset."""
        self._datasources = self._refresh_datasource_list()
        return self._datasources

    @property
    def label_schemas(self) -> List[LabelSchema]:
        """A list of label schemas belonging to this Dataset."""
        return self._refresh_label_schema_list()

    @property
    def batches(self) -> List[Batch]:
        """A list of batches belonging to this Dataset."""
        self._batches = self._refresh_batch_list()
        return self._batches

    # --------------
    # HELPER METHODS
    # --------------

    def _refresh_datasource_list(self) -> List[Dict[str, Any]]:
        """A helper function to refresh the list of datasources associated with this dataset, since
        this may fall out of sync on the client-side when we upload a file

        Returns
        -------
        List[Dict[str, Any]]
            A list of datasources associated with this dataset

        """
        response = list_dataset_datasources_datasets__dataset_uid__data_sources_get(
            self.uid
        )
        return [v.to_dict() for v in response]

    def _repr_dataset_datasources(self) -> List[Dict[str, Any]]:
        """Datasource objects retrieved from the backend have somewhat esoteric representations
        that may not be interpretable for end-users. This function reformats the fetched data to
        make it more palatable

        Returns
        -------
        str
            A friendly representation of the datasources associated with this dataset

        """
        parsed_datasources = [
            {
                "datasource_uid": d.get("datasource_uid", None),
                "datasource_name": d.get("datasource_name", None),
                "split": d.get("split", None),
                "internal_config": d.get("config", None),
            }
            for d in self.datasources
        ]
        return parsed_datasources

    def _refresh_label_schema_list(self) -> List[LabelSchema]:
        """Helper function to refresh the list of label schemas associated with this
        dataset, since this may fall out of sync on the client-side new label schemas
        are created.

        Returns
        -------
        List[LabelSchema]
            A list of label schemas associated with this dataset

        """
        label_schema_resp = list_label_schemas_label_schemas_get(dataset_uid=self.uid)
        return [LabelSchema.get(ls.label_schema_uid) for ls in label_schema_resp]

    def _refresh_batch_list(self) -> List[Batch]:
        """Helper function to refresh the list of batches associated with this dataset,
        since this may fall out of sync on the client-side new batches are created.

        Returns
        -------
        List[Batch]
            A list of batches associated with this dataset

        """
        batch_resp = get_batches_for_dataset_datasets__dataset_uid__batches_get(
            dataset_uid=self.uid
        )
        return [Batch.get(b.batch_uid) for b in batch_resp]

    def _check_mta_enabled(self) -> None:
        if not self.mta_enabled:
            raise ValueError(
                "Multi-task annotation is not enabled for this dataset. To enable it, use the ``enable_mta`` flag when creating the dataset."
            )

    def __repr__(self) -> str:
        """Prints out a user-friendly representation of the Dataset"""
        return json.dumps(
            dict(
                name=self.name,
                uid=self.uid,
                datasources=self._repr_dataset_datasources(),
            ),
            indent=2,
        )

    def _maybe_upload_file(self, path: str) -> str:
        """If the path is a local file, upload it to the platform and return the remote path."""
        protocol = infer_storage_options(path).get("protocol")

        if protocol == "file":
            # Upload a local file to the platform
            with open(path, "rb") as f:
                file = File(
                    payload=f,
                    file_name=os.path.basename(path),
                    mime_type="application/octet-stream",
                )

                res = upload_datasource_datasets__dataset_uid__upload_post(
                    dataset_uid=self.uid,
                    body=BodyUploadDatasourceDatasetsDatasetUidUploadPost(
                        file=file,
                    ),
                )
            path = res.minio_path

        return path

    @classmethod
    def _df_tmpfile_wrapper(
        cls, f: Callable, df: pd.DataFrame, dataset_uid: int, *args: Any, **kwargs: Any
    ) -> Any:
        """A wrapper function that takes in a function that is meant to apply to a file.
        Uploads dataframe to minio, gets that file name, and then calls the function on that file name.

        Parameters
        ----------
        f : Callable
            A function that returns a dataframe.
            The "Callable" type hint does not allow variadic arguments, but the function should take
            a path to a file as its first argument, followed by any other arguments.
        args : Any
            Arguments to pass to the function
        kwargs : Any
            Keyword arguments to pass to the function

        Returns
        -------
        Any
            The result of calling the function on the uploaded dataframe

        """
        if not all(isinstance(col, str) for col in df.columns):
            msg = (
                "All column names must be strings when uploading a DataFrame. Please change the following column names: "
                + ", ".join(
                    [str(col) for col in df.columns if not isinstance(col, str)]
                )
            )
            raise ValueError(msg)
        file = File(
            payload=io.BytesIO(df.to_parquet(engine="pyarrow", index=False)),
            file_name=f"{uuid.uuid4()}.parquet",
            mime_type="application/vnd.apache.parquet",
        )
        # Upload the df as a file and get the path
        res = upload_datasource_datasets__dataset_uid__upload_post(
            dataset_uid=dataset_uid,
            body=BodyUploadDatasourceDatasetsDatasetUidUploadPost(
                file=file,
            ),
        )
        minio_path = res.minio_path

        return f(minio_path, *args, **kwargs)

    # ------------------
    # DATASET OPERATIONS
    # ------------------

    def update(self, name: str = "") -> None:
        """Update the metadata for this dataset. Only updating the name of this Dataset is currently supported.
        The new name for the dataset must be unique within the workspace.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get(dataset="my-dataset")
            >>> my_dataset.update(name="my-new-dataset")
            Successfully renamed dataset with UID 0 to my-new-dataset

        Parameters
        ----------
        name
            The new name for this dataset
        """
        if name:
            edit_dataset(self.uid, body=models.UpdateDatasetParams(name=name))
            self._name = name
            print(f"Renamed dataset with UID {self.uid} to {self.name}")
        else:
            raise ValueError("Must provide a non-empty new name for this dataset")

    @classmethod
    def create(cls, dataset_name: str, enable_mta: bool = True) -> "Dataset":
        """Creates and registers a new Dataset object. A Dataset object organizes and collects files and other sources
        of data for use in Snorkel Flow. A Dataset is restricted to a particular workspace, so only users
        in that workspace will be able to access that Dataset. Datasets must be initialized with a unique name

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.create(dataset_name="my-dataset")
            Successfully created dataset my-dataset with UID 0 in workspace 0

        Parameters
        ----------
        dataset_name
            A name for the Dataset. This name must be unique within the workspace
        enable_mta
            Whether to enable multi-task annotation for this dataset. Enabled by default.

        Returns
        -------
        Dataset
            A Dataset object that can be used to interact with the dataset in Snorkel Flow

        """
        workspace_name = SnorkelSDKContext.get_global().workspace_name
        workspace_uid = (
            DEFAULT_WORKSPACE_UID
            if workspace_name is None
            else get_workspace_uid(workspace_name)
        )
        body = TDMDataset(name=dataset_name, workspace_uid=workspace_uid)
        dataset_res = create_dataset_autogen(body=body, enable_mta=enable_mta)

        if dataset_res.metadata and not isinstance(
            dataset_res.metadata.enable_mta, Unset
        ):
            enable_mta = dataset_res.metadata.enable_mta

        dataset_obj = cls(
            uid=dataset_res.dataset_uid,
            name=dataset_res.name,
            mta_enabled=enable_mta,
        )
        print(
            f"Successfully created dataset {dataset_obj.name} with UID {dataset_obj.uid}."
        )
        return dataset_obj

    @classmethod
    def get(cls, dataset: Union[str, int]) -> "Dataset":
        """Fetches an already-created Dataset from Snorkel Flow and returns a Dataset object
        that can be used to interact with files and data

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            Successfully retrieved dataset my-dataset with UID 0 in workspace 0.

        Parameters
        ----------
        dataset
            Either the name or UID of the dataset. A list of all accessible datasets can be retrieved with ``Dataset.list()``

        Returns
        -------
        Dataset
            A Dataset object that can be used to interact with files and data in Snorkel Flow.

        """
        dataset_metadata = get_dataset_metadata(dataset)
        dataset_obj = cls(
            uid=dataset_metadata.uid,
            name=dataset_metadata.name,
            mta_enabled=dataset_metadata.mta_enabled,
        )
        print(
            f"Successfully retrieved dataset {dataset_metadata.name} with UID {dataset_metadata.uid}."
        )
        return dataset_obj

    @classmethod
    def delete(cls, dataset: IdType, force: bool = False) -> None:
        """Delete a dataset based on the provided identifier

        The operation will fail if any applications use this Dataset

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> Dataset.delete("my-dataset")
            Successfully deleted dataset my-dataset with UID 0.

        Parameters
        ----------
        dataset
            Name or UID of the dataset to delete
        force
            If True, delete any applications using the Dataset as well

        """
        dataset_metadata = get_dataset_metadata(dataset)
        job_id = delete_dataset_autogen(
            dataset_uid=dataset_metadata.uid, body=RemoveDatasetRequest(force=force)
        ).job_id
        poll_job_status(job_id)
        print(
            f"Successfully deleted dataset {dataset_metadata.name} with UID {dataset_metadata.uid}."
        )

    def get_dataframe(
        self,
        split: Optional[str] = None,
        max_rows: Optional[int] = 10,
        target_columns: Optional[List[str]] = None,
        datasource_uid: Optional[int] = None,
        use_source_index: bool = True,
    ) -> pd.DataFrame:
        """Read the Dataset's data into an in-memory Pandas DataFrame. If only a subset of columns are required, they can be specified with ``target_columns``. Note that
        changes to the DataFrame will not be reflected in the Dataset. To change the actual data in the dataset, you must
        swap out the relevant data sources.

        .. note::
            By default, only 10 rows are read for memory safety. This limit can
            be increased by setting ``max_rows`` to a larger value, but this can be computationally intensive and may lead to
            unstable behavior.

        .. note::
            By default, we will return the original index column name the data source was uploaded with.
            However, certain SDK workflows might require an internal representation of the index column, such as the ``snorkelai.sdk.develop.Deployment.execute`` function.
            If you run into issues because of this, run ``dataset.get_dataframe`` with the ``use_source_index`` parameter set to ``False``.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            >>> df = my_dataset.get_dataframe(target_columns=["a", "b"])
            <pd.DataFrame object with 10 rows and columns a, b>
            >>> df = my_dataset.get_dataframe(datasource_uid=0, max_rows=None)
            <pd.DataFrame object with 100 rows and columns a, b, c>

        Parameters
        ----------
        split
            The data split to load, by default None (all splits). Other options are "train", "valid", and "test".
        max_rows
            The maximum number of rows to read, by default 10. Use ``max_rows=None`` to fetch all rows. Warning: setting this to a large value can be computationally intensive and may lead to unstable behavior
        target_columns
            A list of desired data columns, in case not all columns are required, by default None
        datasource_uid
            Fetch a dataframe from a particular ``datasource_uid``. A list of all datasource UIDs can be retrieved with ``Dataset().datasources``.
            This can't be used with ``split``.
        use_source_index
            If true, returns the index column that the data source was originally uploaded with. If false, returns the Snorkel Flow internal column name. True by default.

        Returns
        -------
        pd.DataFrame
            A Pandas DataFrame object displaying the data in this dataset

        """
        # Note that we tell the server to stream the response, but the client downloads the entire response at once (i.e., not streaming).
        # In the future, we can have iter_dataframes that streams the response and returns one chunk at a time.
        res = fetch_dataset_dataframes_datasets__dataset_uid__dataframes_get(
            dataset_uid=self.uid,
            limit=_wrap_in_unset(max_rows),
            offset=0,
            split=_wrap_in_unset(split),
            datasource_uid=_wrap_in_unset(datasource_uid),
            streaming=True,  # Tell the server to stream responses.
            raw=True,
        )
        all_records: List[Dict[str, Any]] = []

        if isinstance(res, requests.Response):
            iter_lines = res.iter_lines(chunk_size=ITER_CHUNK_SIZE, decode_unicode=True)
        else:
            # This is for testing where response is of httpx.Response, which doesn't take in those arguments.
            iter_lines = res.iter_lines()

        for line in iter_lines:
            # The response is a NDJSON (newline-delimited JSON) stream.
            df_res = DataFrameResponse.from_dict(json.loads(line))
            all_records.extend(item.to_dict() for item in df_res.data)
        if not all_records:
            return pd.DataFrame()
        df = pd.DataFrame(all_records)
        if use_source_index:
            uid_col = self.datasources[0]["config"]["uid_col"]
            df = df.rename(columns={SpanCols.CONTEXT_UID: uid_col})
        df = df.set_index(DATAPOINT_UID_COL)
        df = df if target_columns is None else df[target_columns]
        return df

    @staticmethod
    def list() -> List["Dataset"]:
        """Get a list of all Datasets. The returned list includes the Dataset UID, the Dataset name, and additional metadata
        used to keep track of the Dataset's properties.

        Examples
        --------
        .. doctest::

            >>> Dataset.list()
            [
                {
                    "name": "test-csv-str",
                    "uid": 116,
                    "datasources": []
                },
                ...
            ]

        Returns
        -------
        List[Dataset]
            List of all dataset objects

        """
        workspace_name = SnorkelSDKContext.get_global().workspace_name
        workspace_uid = (
            UNSET if workspace_name is None else get_workspace_uid(workspace_name)
        )
        return [
            Dataset.get(ds.dataset_uid)
            for ds in get_datasets_autogen(name=UNSET, workspace_uid=workspace_uid)
        ]

    # ---------------------------------------------------------
    # Below are methods for working with individual datasources
    # ---------------------------------------------------------

    def _create_datasource_from_file(
        self,
        filepath: str,
        uid_col: Optional[str] = None,
        name: Optional[str] = None,
        split: Optional[str] = "train",
        sync: Optional[bool] = True,
        run_datasource_checks: bool = True,
    ) -> Union[str, int]:
        filetype = filepath.rsplit(".", 1)[-1].upper()
        filepath = self._maybe_upload_file(filepath)

        body = SingleDataSourceIngestionRequest(
            path=filepath,
            source_type=filetype,
            run_async=True,
            split=UNSET if split is None else split,
            uid_col=_wrap_in_unset(uid_col),
            name=name if name is not None else os.path.basename(filepath),
            run_datasource_checks=run_datasource_checks,
            load_to_model_nodes=True,
            # Hardcode the reader_kwargs until we support non-file data sources in SDK or users ask for the ability to change it.
            reader_kwargs='{"sample": false}',
        )

        job_id = ingest_datasource_datasets__dataset_uid__data_sources_post(
            dataset_uid=self.uid, body=body
        )["job_id"]

        if sync:
            response = poll_job_status(job_id)
            detail = response.get("detail") or {}
            if detail.get("warning"):
                print(detail["warning"])
            self._datasources = self._refresh_datasource_list()
            return detail.get("datasource_uids", [None])[0]
        else:
            return job_id

    @overload
    def create_datasource(
        self,
        data: Union[str, pd.DataFrame],
        uid_col: Optional[str] = None,
        name: Optional[str] = None,
        split: str = "train",
        sync: Literal[True] = True,
        run_checks: bool = True,
    ) -> int: ...

    @overload
    def create_datasource(
        self,
        data: Union[str, pd.DataFrame],
        uid_col: Optional[str] = None,
        name: Optional[str] = None,
        split: str = "train",
        *,
        sync: Literal[False],
        run_checks: bool = True,
    ) -> str: ...

    def create_datasource(
        self,
        data: Union[str, pd.DataFrame],
        uid_col: Optional[str] = None,
        name: Optional[str] = None,
        split: str = "train",
        sync: bool = True,
        run_checks: bool = True,
    ) -> Union[str, int]:
        """Creates a new data source withing the Dataset from either a filepath or a Pandas DataFrame.

        If you provide a filepath: A file can be a CSV or Parquet file that either exists in the local filesystem, or is
        accessible via an S3-compatible API (such as MinIO, or AWS S3). Files
        must have a stable integer index column that is unique across all data sources in the dataset.

        If you provide a DataFrame: The DataFrame must have a unique integer column that does not contain duplicates across other sources of data. All DataFrame column names must be strings.

        The data must pass all validation checks to be registered as a valid data source. If a DataFrame fails to pass all data validation checks, the upload will fail and the data source will not be registered.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            >>> my_dataset.create_datasource("my_data.csv", uid_col="id", split="train")
            +0.07s Starting data ingestion
            +1.85s Ingesting data
            +2.05s Data ingestion complete
            1 # UID of the datasource

            >>> my_dataset.create_datasource(df, uid_col="id", name="dataframe-data", split="train")
            +0.07s Starting data ingestion
            +1.85s Ingesting data
            +2.05s Data ingestion complete
            1

        Parameters
        ----------
        data
            Either:
            - A path to a file in the local filesystem, or a path to an S3-compatible API, by default None. If filepath is not provided, a DataFrame must be provided instead
            - A Pandas DataFrame, by default None. If df is not provided, a filepath must be provided instead
        uid_col
            Name of the UID column for this data. The values in this column must be unique non-negative integers that are not duplicated across files.
            If not specified, the UID column will be generated in the server side.
        name
            The name to give this data source. If not provided, the name of the file will be used, by default None. Adding a name is strongly recommended when uploading a DataFrame
        split
            The name of the data split this data belongs to, by default Splits.train
        sync
            Whether execution should be blocked by this function, by default True. Note that Dataset().datasources may not be updated immediately if sync=False
        run_checks
            Whether we should run datasource checks. Recommended for safety, by default True

        Returns
        -------
        Union[str, int]
            If sync is True, returns the integer UID of the datasource. If sync is False, returns a job ID that can be monitored with ``sai.poll_job_id``

        """
        if isinstance(data, str):
            return self._create_datasource_from_file(
                data,
                uid_col,
                split=split,
                name=name,
                sync=sync,
                run_datasource_checks=run_checks,
            )
        elif isinstance(data, pd.DataFrame):
            return self._df_tmpfile_wrapper(
                self._create_datasource_from_file,
                data,
                self.uid,
                uid_col,
                split=split,
                name=name,
                sync=sync,
                run_datasource_checks=run_checks,
            )
        else:
            msg = "The ``data`` parameter must be either a valid filepath or a Pandas DataFrame."
            raise ValueError(msg)

    def delete_datasource(
        self, datasource_uid: int, force: bool = False, sync: bool = True
    ) -> Optional[str]:
        """Delete a data source. Calling delete_datasource will fully remove the data source from the dataset.

        .. warning::
            The operation will not be permitted if any applications are using the data source to avoid breaking downstream applications.
            If you are sure you want to delete the data source, use the flag ``force=True`` to override this check. This function may take a while.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            >>> my_dataset.delete_datasource(1)
            Successfully deleted datasource with UID 1.


        Parameters
        ----------
        datasource_uid
            UID of the data source to delete. See all datasources for this dataset by viewing self.datasources.
        force
            boolean allowing one to force deletion of a datasource even if that
            datasource has dependent assets (ground truth, annotations, etc), by default false
        sync
            Poll job status and block until complete, by default true

        Returns
        -------
        Optional[str]
            Optionally returns job_id if sync mode is turned off

        """
        job_id = delete_datasource_autogen(
            dataset_uid=self.uid,
            datasource_uid=datasource_uid,
            body=RemoveDatasourceRequest(force=force),
        ).job_id
        if sync:
            poll_job_status(job_id)
            self._datasources = self._refresh_datasource_list()
            return None
        else:
            return job_id

    @_require_mta_enabled
    def create_label_schema(
        self,
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
    ) -> LabelSchema:
        """Create a label schema associated with this dataset.

        This is the recommended entrypoint for creating label schemas.

        Parameters
        ----------
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
        return LabelSchema.create(
            dataset_uid=self.uid,
            name=name,
            data_type=data_type,
            task_type=task_type,
            multi_label=multi_label,
            label_map=label_map,
            description=description,
            label_column=label_column,
            label_descriptions=label_descriptions,
            primary_field=primary_field,
            is_text_label=is_text_label,
            allow_overlapping=allow_overlapping,
        )

    @_require_mta_enabled
    def create_batches(
        self,
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
    ) -> List[Batch]:
        """Create annotation batches for this dataset.

        This is the recommended entrypoint for creating batches.

        Parameters
        ----------
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
        return Batch.create(
            dataset_uid=self.uid,
            name=name,
            assignees=assignees,
            label_schemas=label_schemas,
            batch_size=batch_size,
            randomize=randomize,
            random_seed=random_seed,
            selection_strategy=selection_strategy,
            split=split,
            x_uids=x_uids,
            filter_by_x_uids_not_in_batch=filter_by_x_uids_not_in_batch,
            divide_x_uids_evenly_to_assignees=divide_x_uids_evenly_to_assignees,
        )

    def update_datasource_split(self, datasource_uid: int, split: str) -> List[int]:
        """Change the split of a data source that has already been uploaded to the dataset. This will impact how the data source is used in all
        future applications.

        .. warning::
            This will only impact the Dataset's data source, and not existing derived data sources. To change the split within applications that have already
            been created, find the node's derived data source UID by clicking on "Develop" > "View Data Sources" in the Snorkel Flow UI and use the ``sai.update_datasource`` function.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            >>> my_dataset.datasources
            [{"datasource_uid": 1, "datasource_name": "test.csv", "split": "train"}]
            >>> my_dataset.update_datasource_split(1, "train")
            [123, 456, 789]

        Parameters
        ----------
        datasource_uid
            The integer UID corresponding to the data source you wish to update. You can see a list of all data sources for this dataset by viewing self.datasources.
        split
            The new split to assign to this data source. Must be one of "train", "test", or "valid".

        Returns
        -------
        List[int]
            Returns a list of model nodes that have been impacted by changing the split.

        """
        return put_datasource_data_sources__datasource_uid__put(
            datasource_uid, body=PutDatasource(split=split)
        ).tasks

    def update_datasource_data(
        self,
        old_datasource_uid: int,
        new_data: Union[str, pd.DataFrame],
        sync: bool = True,
    ) -> None:
        """This function allows you to replace the data of an existing data source with new data. This function
        can be used if you find an error in an existing value in a data source, or if you need to update values due
        to changes in your upstream data pipeline. This function requires that all row indexes in the new data source
        match the row indexes of the old data source. Additionally, all columns must have the same name and the same type.

        If your goal is to change the number of columns, the number of rows, or the type of a column, you should
        consider using an `Operator <https://docs.snorkel.ai/docs/user-guide/app-setup/operators/operators-transform-and-process-your-data>`_ instead.

        .. warning::
            This is a potentially dangerous operation, and may take a while to run. For safety, this will always run data source checks
            on the new data source. Applications and models that use the data source
            being replaced may become temporarily unavailable as computations are re-run over the new data, and might report different behavior.
            If you are unsure how to use this function, contact a Snorkel representative.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            >>> my_dataset.datasources
            [{"datasource_uid": 1, "datasource_name": "test.csv", "split": "train"}]
            >>> df = my_dataset.get_dataframe(datasource_uid=1, max_rows=None)
            >>> df
            |   |   a |   b |   c        |
            |  0|   1 |   0 | bad_path.pdf|
            >>> df.iloc[0, 2] = "good_path.pdf"
            >>> my_dataset.update_datasource_data(1, df)
            Successfully replaced data in datasource with UID 1.

        Parameters
        ----------
        old_datasource_uid
            The UID of the data source you want to swap out. You can see a list of all data sources for this dataset by viewing self.datasources.
        new_data
            Either (1) A path to a file in the local filesystem, or a path to an S3-compatible API, by default None. If filepath is not provided, a DataFrame must be provided instead,
            or (2) A Pandas DataFrame, by default None. If df is not provided, a filepath must be provided instead.
            The columns and UIDs of the new data must exactly match that of the data being replaced. Use ``dataset.get_dataframe(datasource_uid=old_datasource_uid)`` to see the existing data.
        sync
            Poll job status and block until all jobs are complete, by default True

        Returns
        -------
        Optional[str]
            Returns a Job ID that can be polled if sync is False. Otherwise returns None

        Raises
        ------
        ValueError
            If the data provided is neither a valid file path or a valid Pandas DataFrame

        """
        if isinstance(new_data, str):
            new_datasource_path = self._maybe_upload_file(new_data)
            self._update_datasource_data(
                new_datasource_path, old_datasource_uid, sync=sync
            )
        elif isinstance(new_data, pd.DataFrame):
            self._df_tmpfile_wrapper(
                self._update_datasource_data,
                new_data,
                dataset_uid=self.uid,
                old_datasource_uid=old_datasource_uid,
                sync=sync,
            )
        else:
            msg = "The ``new_data`` parameter must be either a valid filepath or a Pandas DataFrame."
            raise ValueError(msg)

    def _update_datasource_data(
        self, path: str, old_datasource_uid: int, sync: bool = True
    ) -> None:
        job_id = swap_datasource_autogen(
            dataset_uid=self.uid,
            datasource_uid=old_datasource_uid,
            body=IngestAndSwapDatasourcePayload(new_datasource_path=path),
        ).job_id
        if sync:
            poll_job_status(job_id)
            self._datasources = self._refresh_datasource_list()

    @_require_mta_enabled
    def get_ground_truth(
        self,
        label_schema_uid: int,
        user_format: bool = True,
    ) -> pd.DataFrame:
        """Get the ground truth for a given label schema.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> my_dataset = Dataset.get("my-dataset")
            >>> df = my_dataset.get_ground_truth(1, user_format=True)
            >>> df
                                    label
                __DATAPOINT_UID
                doc::1              POSITIVE
                doc::2              NEGATIVE
                doc::3              NEGATIVE
                doc::4              POSITIVE


        Parameters
        ----------
        label_schema_uid
            The UID of the label schema to get the ground truth from.
        user_format
            Return the ground truth in user format if True, otherwise return the raw label values.


        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with x_uid as index, and ground truth labels in column 'label'

        """
        label_schema = LabelSchema.get(label_schema_uid)
        if label_schema.dataset_uid != self.uid:
            raise ValueError(
                f"Label schema {label_schema_uid} is not in dataset {self.uid}"
            )

        ground_truths = get_dataset_ground_truth_dataset_ground_truth_get(
            dataset_uid=self.uid,
            label_schema_uids=[label_schema_uid],
            user_formatted=user_format,
        )
        df = pd.DataFrame(columns=[DATAPOINT_UID_COL, LABEL_COLUMN_NAME])

        for ground_truth in ground_truths:
            x_uid = ground_truth.x_uid
            for label in ground_truth.labels:
                # Since we are only searching for one label schema, there should only be one label
                # Simply use the first one.
                if label.label_schema_uid == label_schema_uid:
                    df.loc[len(df)] = [x_uid, label.label]
                    break

        return df.set_index(DATAPOINT_UID_COL)

    @_require_mta_enabled
    def add_ground_truth(
        self,
        label_schema_uid: int,
        data: pd.DataFrame,
        user_format: bool = True,
        sync: bool = True,
    ) -> Optional[str]:
        """Add ground truth to a given label schema.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import Dataset
            >>> from snorkelai.sdk.client_v3.utils import poll_job_status
            >>> my_dataset = Dataset.get("my-dataset")
            >>> df = pd.DataFrame(
            >>>    {
            >>>        "label": ["POSITIVE", "NEGATIVE", "NEGATIVE", "POSITIVE"],
            >>>        "__DATAPOINT_UID": ["doc::1", "doc::2", "doc::3", "doc::4"],
            >>>    }
            >>> )
            >>> job_uid = my_dataset.add_ground_truth(
            >>>    label_schema_uid=1,
            >>>     data=df,
            >>>     user_format=True,
            >>>     sync=False)
            >>> poll_job_status(job_uid)


        Parameters
        ----------
        label_schema_uid
            The UID of the label schema to add the ground truth to.
        data
            A pandas DataFrame with x_uid as index, and ground truth labels in column 'label'
        user_format
            True if ground truth labels in data in user format, otherwise they should be raw label values.
        sync
            Whether execution should be blocked by this function, by default True.

        Returns
        -------
        Optional[str]
            The job ID of the ground truth job. None if sync is true.

        """
        label_schema = LabelSchema.get(label_schema_uid)
        if label_schema.dataset_uid != self.uid:
            raise ValueError(
                f"Label schema {label_schema_uid} is not in dataset {self.uid}"
            )

        # TODO(ENG-39436): Add validation for all the labels in data
        if LABEL_COLUMN_NAME not in data.columns:
            raise ValueError(
                f"Input DataFrame must contain a '{LABEL_COLUMN_NAME}' column."
            )

        response = (
            import_dataset_ground_truth_dataset__dataset_uid__ingest_ground_truth_post(
                dataset_uid=self.uid,
                body=ImportDatasetGroundTruthParams(
                    label_schema_uid=label_schema_uid,
                    df=GroundTruthDFModel(
                        serialized_df=serialize_dataframe(data, engine="parquet"),
                        label_col=LABEL_COLUMN_NAME,
                    ),
                    convert_to_raw_format=user_format,
                    run_async=True,
                ),
            )
        )

        job_uid: Optional[str] = (
            None if isinstance(response.job, Unset) else response.job
        )

        if sync and job_uid:
            poll_job_status(job_uid)
            return None

        return job_uid
