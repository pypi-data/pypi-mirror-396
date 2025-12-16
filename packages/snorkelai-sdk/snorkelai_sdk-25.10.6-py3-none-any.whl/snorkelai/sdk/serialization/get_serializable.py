# This is a top-level file for serializables. To prevent circular top-level imports, this
# file imports all serializables but not vice-versa. We make it an explicit file instead of
# __init__.py because pytest doesn't execute the __init__.py by default.

from abc import ABCMeta
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from snorkelai.sdk.serialization import serializable
from snorkelai.sdk.utils.logging import get_logger

logger = get_logger("Serialization")

STANDARD_TYPES = (
    pd.CategoricalDtype,
    bool,
    int,
    float,
    np.number,
    str,
    type(None),
    np.bool_,
)

try:
    from snorkelai.sdk.rich_doc_wrapper.rich_doc_wrapper import (
        Ngram,  # noqa: F401
    )
except ImportError:
    logger.debug("Skipping registration for Ngram.")

try:
    from snorkelai.sdk.rich_docs.rich_doc import (  # noqa: F401
        RichDoc,
        RichDocList,
    )
except ImportError:
    logger.debug("Skipping registration for RichDoc extras.")


def get_serializable_class(cls_name: str) -> ABCMeta:
    if cls_name not in serializable.serializables_dict:
        raise ValueError(
            f"Serializable class not found: {cls_name}. Make sure the class file is imported above."
        )
    return serializable.serializables_dict[cls_name]


def cls_is_serializable(cls: type) -> bool:
    return issubclass(cls, serializable.Serializable)


def maybe_serialize(x: Any) -> Any:
    """Conditionally serialize the value to ensure parquet-writability.
    Use serialize_series() if serializing a whole pandas series instead
    of series.map(maybe_serialize) to prevent memory explosion.
    """
    if isinstance(x, STANDARD_TYPES):
        return x
    if cls_is_serializable(type(x)):
        return x.serialize()
    return serializable.B64PICKLE.serialize_val(x)


def get_serialization_types(row: Any) -> Dict[str, str]:
    types = {}
    for col in row.index:
        col_type = get_serialization_type(row[col])
        if col_type is not None:
            types[col] = col_type
    return types


def get_serialization_type(val: Any) -> Optional[str]:
    if isinstance(val, STANDARD_TYPES):
        return None  # No custom type to add.
    elif cls_is_serializable(type(val)):
        return type(val).__name__
    else:
        return serializable.B64PICKLE.__name__
