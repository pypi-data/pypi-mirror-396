import base64
import json
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Union

import pandas as pd

serializables_dict: Dict[str, Type["Serializable"]] = {}


class Serializable(ABC):
    """Interface for types that have a custom serialization / deserialization function."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Define init subclass to register all subclasses in serializables_dict."""
        super().__init_subclass__(**kwargs)
        serializables_dict[cls.__name__] = cls

    @abstractmethod
    def serialize(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, serialized: str) -> Any:
        raise NotImplementedError


class B64PICKLE(Serializable):
    """Special pickle wrapper for non-serializable non-(int/float/str) classes."""

    def __init__(self, val: Any):
        self.val = val

    # Default serialization for non-serializable non-(int, str, float) classes.
    # must be the inverse of deserialize method below.
    @classmethod
    def serialize_val(cls, val: Any) -> str:
        return base64.b64encode(pickle.dumps(val)).decode()

    @classmethod
    def deserialize(cls, serialized: str) -> Any:
        """Deserialize instance to string."""
        return pickle.loads(base64.b64decode(serialized))


# BEGIN Deprecated
# Classes below are for back-compat with older files (ds_schema_version <= 3).
# Do not use for new data, and delete this block when we force upgrade to a
# ds_schema_version >= 4.
class JSON(Serializable):
    """Special wrapper for lists / dicts."""

    def __init__(self, val: Union[List[Any], Dict[str, Any]]):
        self.val = val

    @classmethod
    def deserialize(cls, serialized: str) -> Any:
        """Deserialize instance to string."""
        return json.loads(serialized)


class Timestamp(Serializable):
    """Special wrapper for pd.Timestamp."""

    def __init__(self, val: pd.Timestamp):
        self.val = val

    @classmethod
    def deserialize(cls, serialized: str) -> pd.Timestamp:
        """Deserialize string to pd.Timestamp."""
        return pd.Timestamp(serialized)


# END Deprecated
