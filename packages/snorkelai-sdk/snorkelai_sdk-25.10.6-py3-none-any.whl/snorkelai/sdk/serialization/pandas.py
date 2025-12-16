import base64
import binascii
import pickle
import time
from abc import ABCMeta
from io import BytesIO
from typing import Any, Dict, List, Literal, NamedTuple, Optional, Set, Union, overload

import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype

from snorkelai.sdk.serialization.get_serializable import (
    get_serializable_class,
    get_serialization_types,
    maybe_serialize,
)
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Serialization")

CATEGORICAL_REPEAT_THRESHOLD = 2
SHOULD_SERIALIZE_DTYPES = ["object", "datetime64[ns]"]
RESERVED_SNORKELFLOW_CATEGORY = "__RESERVED_SNORKELFLOW_CATEGORY"


class SerializationError(Exception):
    pass


def _serialize_dataframe_to_parquet(df: pd.DataFrame) -> bytes:
    """Serialize a pandas dataframe into the binary parquet format"""
    buffer = BytesIO()
    df.to_parquet(buffer)
    buffer.seek(0)
    serialized_data = buffer.read()
    return serialized_data


def _deserialize_dataframe_from_parquet(serialized_data: bytes) -> pd.DataFrame:
    """Deserialize a pandas dataframe from the binary parquet format"""
    buffer = BytesIO()
    buffer.write(serialized_data)
    buffer.seek(0)
    df = pd.read_parquet(buffer)
    return df


def serialize_dataframe(
    df: Union[Dict[str, pd.DataFrame], pd.DataFrame], engine: str = "pickle"
) -> str:
    """Encode a dataframe into a JSON-compatible string

    Parameters
    ----------
    df
    engine: either 'pickle' or 'parquet'.
        Use 'pickle' for exchanging a dataframe within the platform (e.g., tdm <-> engine), and
        'parquet' for between the platform and the SDK.
        The former supports more data types (e.g., RichDoc) while the latter is more compatible with different pandas versions.

    Steps:
    asset -> pickle -> base64 str -> ascii str

    - pickleis necessary to convert object to bytes
    - base64 is necessary to convert bytes into a valid string
    - string is required to jsonify (json can't serialize bytes)

    """
    # NOTE: this was created becuase dill has issues with pycapsul types which
    # are used with numpy, and pandas dataframes see: https://github.com/uqfoundation/dill/issues/354
    obj: Any
    if engine == "pickle":
        obj = df
    elif engine == "parquet":
        is_dict = isinstance(df, dict)
        data: Any = {}
        types: Any = {}
        if is_dict:
            for k, v in df.items():
                assert isinstance(v, pd.DataFrame)  # mypy
                types[k] = get_serialization_types(v.iloc[0])
                data[k] = _serialize_dataframe_to_parquet(serialize_dataframe_series(v))
        else:
            assert isinstance(df, pd.DataFrame)  # mypy
            types = get_serialization_types(df.iloc[0]) if not df.empty else {}
            data = _serialize_dataframe_to_parquet(serialize_dataframe_series(df))
        obj = {"data": data, "is_dict": is_dict, "types": types}
    else:
        raise ValueError(f"Unsupported engine: {engine}")

    df_pkl: bytes = pickle.dumps(obj)
    df_pkl_b64: bytes = base64.b64encode(df_pkl)
    df_pkl_ascii: str = df_pkl_b64.decode("ascii")
    return df_pkl_ascii


@overload
def deserialize_dataframe(
    df_pkl_ascii: str, engine: Literal["pickle"] = "pickle"
) -> pd.DataFrame: ...


@overload
def deserialize_dataframe(
    df_pkl_ascii: str, engine: Literal["parquet"] = "parquet"
) -> Union[Dict[str, pd.DataFrame], pd.DataFrame]: ...


def deserialize_dataframe(
    df_pkl_ascii: str, engine: Literal["pickle", "parquet"] = "pickle"
) -> Union[Dict[str, pd.DataFrame], pd.DataFrame]:
    """Decode a serialized dataframe  into a pandas dataframe object.

    Reverses the steps in `serialize_asset()`.
    """
    df_pkl = base64.b64decode(df_pkl_ascii)
    if engine == "pickle":
        df = pickle.loads(df_pkl)
    elif engine == "parquet":
        obj = pickle.loads(df_pkl)
        df_dict = obj["data"]
        types = obj["types"]
        if obj["is_dict"]:
            df = {
                k: deserialize_dataframe_series(
                    _deserialize_dataframe_from_parquet(v), types[k]
                )
                for k, v in df_dict.items()
            }
        else:
            df = deserialize_dataframe_series(
                _deserialize_dataframe_from_parquet(df_dict), types
            )
    else:
        raise ValueError(f"Unsupported engine: {engine}")
    return df


class CompressedDataFrameRows(NamedTuple):
    data: List[Dict[str, Any]]
    compressed_data: Dict[str, List[Any]]


def dataframe_to_dict(
    df: pd.DataFrame,
    compress: bool = False,
    duplicate_ratio_threshold: Optional[float] = 1.25,
    memory_usage_bytes_threshold: Optional[int] = 100_000,
) -> CompressedDataFrameRows:
    """compress:                       If True, run the compression algo, otherwise just do df.to_dict
    duplicate_ratio_threshold:      If a column has a duplication ratio over this value, compress it. Ratio is # of values / # of unique values
                                    If set to None, no ratio threshold is used
    memory_usage_bytes_threshold:   If a column's memory usage is higher than the threshold, compress it.
                                    If set to None, memory usage of column is ignored

    Note: If both thresholds are set, both most be fulfilled in order for column to be compressed.

    Returns
    -------
    List of DF rows. Compressed columns will have their values replaced with an integer
    A dictionary of column names to list of values. The integer mentioned above points to the index in the array

    TODO: Provide an implementation of decompression. Currently only the UI has to decompress, so no Python implementation has been made.

    """
    # Use dictionary as an ordered set
    compressed_data: Dict[str, Dict[str, int]] = {}
    if compress:
        # Two criteria for compressing:
        # - Significant memory usage (100KB+)
        # - Significant duplication ratio (each row duplicated on average at least 1.25 times)
        for column, memory in df.memory_usage(deep=True, index=False).items():
            logger.info(f"{column}: {memory} {memory_usage_bytes_threshold}")
            if (
                memory_usage_bytes_threshold is not None
                and memory < memory_usage_bytes_threshold
            ):
                continue
            try:
                unique_values = df[column].unique()
            except TypeError as e:
                # TODO: Think of another way to deal with columns containing unhashable types
                #       like lists and dicts. Just json.dumps them now?
                if str(e).startswith("unhashable type:"):
                    logger.warning(
                        f"Column {column} takes significant memory and is unhashable"
                    )
                    continue
            if (
                duplicate_ratio_threshold is not None
                and len(df) / len(unique_values) < duplicate_ratio_threshold
            ):
                continue
            compressed_data[column] = {  # type: ignore[index]
                unique_value: idx for idx, unique_value in enumerate(unique_values)
            }

    data = df.to_dict(orient="records")

    # Convert values in pointers for compressed columns
    for column, column_data in compressed_data.items():
        for row in data:
            row[column] = column_data[row[column]]

    final_compressed_data = {
        column: list(column_data) for column, column_data in compressed_data.items()
    }
    return CompressedDataFrameRows(data, final_compressed_data)  # type: ignore[arg-type]


def serialize_dataframe_series(
    df: pd.DataFrame,
    coerce_object_as_category: bool = False,
    categorical_repeat_threshold: float = CATEGORICAL_REPEAT_THRESHOLD,
    all_string_cols: Optional[Set[str]] = None,
    only_coerce: bool = False,
) -> pd.DataFrame:
    """If all_string_cols is not set, will perform expensive type-check of expensive columns
    This is fine if not performing multiple operations that need to check whether object column is string-type.

    If only_coerce is True, then we assume the input df is already serialized, and we only convert columns
    between object and categorical as necessary (call coerce_object_series_as_category on each column) if
    coerce_object_as_category is True.
    """
    start_time = time.time()

    serialized_columns = []
    to_assign = {}
    for col in df.columns:
        series = df[col]
        if not only_coerce and not _series_is_arrow_compatible(
            col, series, all_string_cols
        ):
            series = serialize_series(series)
        if coerce_object_as_category:
            series = coerce_object_series_as_category(
                series, categorical_repeat_threshold
            )
            if series.dtype.name == "category":
                serialized_columns.append(series.name)
        to_assign[col] = series
    df = df.assign(**to_assign)
    if time.time() - start_time > 1:
        logger.info(f"Serialized dataframe in {time.time() - start_time} seconds")
    # Store serialized columns in DF metadata
    df.attrs["serialized_columns"] = serialized_columns
    return df


def serialize_series(series: pd.Series) -> pd.Series:
    """Serialize the pandas series so that it can be written by parquet

    Usage for Dask: ddf[col] = ddf[col].map_partitions(serialize_series, meta=("", ddf[col].dtype))
    Usage for Pandas: df[col] = serialize_series(df[col])

    coerce_object_as_category sets an object as categorial object
    """
    # Do a series of steps to minimize accidental memory explosion.
    # Memory explosion happens when a pandas Series consists of mostly duplicate
    # values gets map() called on it. Imagine the following:
    # x = {large object}
    # series = pd.Series([x] * 1000)
    # The actual memory usage of the series is not 1000 * x, just x, because the series
    # just has a bunch of pointers at the original object.
    # If you call something like
    # new_series = series.map(json.dumps)
    # The memory "explodes" because a new object is being created for every row (no shared
    # memory pointer)

    # To avoid memory explosion, we cache the serialized value based on the memory address of the value

    # NOTE: There is an assumption that calling maybe_serialize on the same object will always
    #       yield the same result

    cache: Dict[int, Any] = {}

    def _fetch_from_cache(x: Any) -> Any:
        x_id = id(x)

        # This is a lazy implementation of dict.setdefault
        if x_id not in cache:
            cache[x_id] = maybe_serialize(x)

        return cache[x_id]

    # We use id() of the value as the cache key since some objects like sets are unhashable
    return series.map(_fetch_from_cache)


def coerce_object_series_as_category(
    series: pd.Series,
    categorical_repeat_threshold: float = CATEGORICAL_REPEAT_THRESHOLD,
) -> pd.Series:
    # We need to set categorical to large string columns to force dictionary encoding in PyArrow
    # Only do so if the average repeat is 2 or more
    unique_count = series.map(id).nunique()
    if unique_count == 0:
        return series
    repeat_ratio = len(series) / unique_count
    if series.dtype.name == "object" and repeat_ratio >= categorical_repeat_threshold:
        series.replace({np.nan: None}, inplace=True)

        categories = get_categories(series)

        series = series.astype(CategoricalDtype(categories=categories, ordered=False))
    elif (
        series.dtype.name == "category" and repeat_ratio < categorical_repeat_threshold
    ):
        series = series.astype(series.cat.categories.dtype)
    return series


def deserialize_dataframe_series(
    df: pd.DataFrame, types: Dict[str, str]
) -> pd.DataFrame:
    for col in df.columns.intersection(list(types)):
        cls = get_serializable_class(types[col])
        try:
            df[col] = deserialize_series(df[col], cls)
        except (binascii.Error, TypeError) as e:
            raise SerializationError(
                f"Could not deserialize some values in '{col}'. Please make sure all values in the column are of the same type."
            ) from e
        except SerializationError as e:
            raise SerializationError(
                f"Could not deserialize column '{col}' in dataframe"
            ) from e
    return df


def deserialize_series(series: pd.Series, cls: ABCMeta) -> pd.Series:
    """Usage for Dask: ddf[col] = ddf[col].map_partitions(deserialize_series, cls, meta=("", object))
    Usage for Pandas: df[col] = deserialize_series(df[col], cls)
    """
    cache: Dict[int, Any] = {}
    cls_deserialize_fn = cls.deserialize  # type: ignore

    def _fetch_from_cache(x: Any) -> Any:
        if x is None or (isinstance(x, (float, np.float64)) and np.isnan(x)):
            return x
        x_id = id(x)

        # This is a lazy implementation of dict.setdefault
        if x_id not in cache:
            try:
                cache[x_id] = cls_deserialize_fn(x)
            except (binascii.Error, TypeError) as e:
                raise e
            except Exception as e:
                raise SerializationError(
                    f"Could not deserialize id '{x_id}' with data '{x}'"
                ) from e

        return cache[x_id]

    series = series.astype(object)
    series = series.map(_fetch_from_cache)

    return series


def _series_is_arrow_compatible(
    col_name: str, series: pd.Series, all_string_cols: Optional[Set[str]] = None
) -> bool:
    dtype = series.dtype.name
    # No need to serialize non-object categorical columns
    if dtype == "category":
        if series.cat.categories.dtype.name not in SHOULD_SERIALIZE_DTYPES:
            return True
    # No need to serialize non-object columns
    elif dtype not in SHOULD_SERIALIZE_DTYPES:
        return True

    # No need to serialize columns that are known to be all strings
    if all_string_cols is not None and col_name in all_string_cols:
        return True
    # No need to serialize columns that are all strings
    return bool(is_all_string_series(series))


def is_all_string_series(series: pd.Series) -> bool:
    """Check whether column is all strings and no other types"""
    # First check if dtype is object to avoid expensive type-check across all rows
    return (
        series.dtype == "object"
        and np.vectorize(lambda x: isinstance(x, str), otypes=[bool])(series).all()
    )


def get_categories(series: pd.Series) -> List[str]:
    # here, we assume the series is serialized, so construct a set instead of using pandas.unique()
    categories = list({cat for cat in series if not pd.isna(cat)})

    # There is a dask specific bug when used with PyArrow on an empty categorical column
    # throws Categorical categories cannot be null. This does not happen with Pandas or with fastparquet.
    # Thus we need to append a RESERVED_SNORKELFLOW_CATEGORY which is just a dummy placeholder
    if not categories:
        categories.append(RESERVED_SNORKELFLOW_CATEGORY)

    return categories
