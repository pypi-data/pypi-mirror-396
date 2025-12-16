from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    cast,
)

from snorkelai.sdk.utils.graph import AND, DEFAULT_GRAPH, OR, Graph


class FilterBase(ABC):
    """Abstract base class for SDK filters."""

    type: str

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the filter to a dictionary that can be serialized to JSON.
        Concrete filters must implement this method.
        """


# Operators align with server constants:
# - StringFilterOperator: "matches", "contains"
# - NumericFilterOperator: "==", "!=", ">", "<", ">=", "<="
FieldStringOperator = Literal["matches", "contains"]
FieldNumericOperator = Literal["==", "!=", ">", "<", ">=", "<="]
FieldOperator = Union[FieldStringOperator, FieldNumericOperator]

SliceOperator = Literal["is", "is not"]


@dataclass(frozen=True)
class FieldFilter(FilterBase):
    """Field filter for dataset fields.

    Required fields:
    - field: the column name
    - operator: one of {"matches", "contains", "==", "!=", ">", "<", ">=", "<="}
    - value: str or float depending on the field type
    """

    field: str
    operator: FieldOperator
    value: Union[str, float]
    type: Literal["field"] = "field"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the filter to a dictionary that can be serialized to JSON.
        Includes the filter type, field, operator, and value.
        """
        return {
            "type": self.type,
            "field": self.field,
            "operator": self.operator,
            "value": self.value,
        }


@dataclass(frozen=True)
class GroundTruthFilter(FilterBase):
    """Ground truth filter.

    Required fields:
    - label_schema_uids: list of label schema ids
    - voted: voted label value
    - vote_type: optional (used for multi-label spaces)
    """

    label_schema_uids: List[int]
    voted: str
    vote_type: Optional[str] = None
    type: Literal["ground_truth"] = "ground_truth"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the filter to a dictionary that can be serialized to JSON.
        Includes the filter type, label schema uids, voted label value, and vote type.
        """
        payload: Dict[str, Any] = {
            "type": self.type,
            "label_schema_uids": self.label_schema_uids,
            "voted": self.voted,
        }
        if self.vote_type is not None:
            payload["vote_type"] = self.vote_type
        return payload


@dataclass(frozen=True)
class SliceFilter(FilterBase):
    """Slice membership filter.

    Required fields:
    - slice_uid: the slice identifier
    - operator: one of {"is", "is not"}
    """

    slice_uid: int
    operator: SliceOperator
    type: Literal["slice"] = "slice"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the filter to a dictionary that can be serialized to JSON.
        Includes the filter type, slice uid, and operator.
        """
        return {
            "type": self.type,
            "slice_uid": self.slice_uid,
            "operator": self.operator,
        }


class FilterConfig:
    """
    Represents a composable filter configuration.

    This class maintains:
      - `_filters`: a list of individual `FilterBase` objects, each representing a single filter condition.
      - `_graph`: a structure (either an integer index, a nested list, or an operator node) describing how these filters are combined using boolean logic.
        - If there is only one filter, `_graph` is set to `0` (the index of the filter in `_filters`).
        - For multiple filters, `_graph` can be a nested list representing logical operations (e.g., `["$AND", 0, 1]` to combine the first and second filters with AND).
        - Each integer in the graph refers to the index of a filter in the `_filters` list.
        - Currently, only the AND operator is supported, but the structure allows for future extension to other boolean operators and more complex logical expressions.
    """

    _filters: List[FilterBase]
    _graph: Optional[Graph]

    def __init__(
        self, filters: Optional[List[FilterBase]] = None, graph: Optional[Graph] = None
    ) -> None:
        """
        Parameters
        ----------
        filters
            Optional initial list of filters to include in this configuration.
        graph
            Optional graph describing how the provided filters are combined. If not
            provided, a default graph is used for a single filter and `None` otherwise.
        """
        self._filters = list(filters or [])
        if graph is not None:
            self._graph = graph
        elif len(self._filters) == 0:
            self._graph = None
        elif len(self._filters) == 1:
            self._graph = DEFAULT_GRAPH
        else:
            self._graph = None

    @staticmethod
    def from_filter(filter_obj: FilterBase) -> FilterConfig:
        """
        Parameters
        ----------
        filter_obj
            A single filter to wrap into a configuration.

        Returns
        -------
        FilterConfig
            A configuration containing the provided filter and a default graph.
        """
        return FilterConfig([filter_obj], DEFAULT_GRAPH)

    @property
    def filters(self) -> List[FilterBase]:
        """
        Returns
        -------
        list
            A copy of the filters contained in this configuration.
        """
        return list(self._filters)

    def to_json(
        self,
    ) -> str:
        """Build a JSON string for the filter config using only each filter's schema and the graph.

        Returns
        -------
        str
            A JSON string representing the filter configuration.
        """
        return json.dumps(
            {
                "filters": [f.to_dict() for f in self._filters],
                "graph": self._graph,
            }
        )

    @staticmethod
    def _unwrap_singleton_or(node: Graph) -> Graph:
        """
        Unwrap an OR node that contains a single integer child.

        If `node` is of the form `[OR, <int>]`, the method returns the integer child
        to simplify the graph. Otherwise, the node is returned unchanged.

        Parameters
        ----------
        node
            Graph node to examine and possibly unwrap.

        Returns
        -------
        Graph
            The unwrapped child index or the original node if no unwrapping applies.
        """
        if (
            isinstance(node, list)
            and len(node) == 2
            and node[0] == OR
            and isinstance(node[1], int)
        ):
            return node[1]
        return node

    @staticmethod
    def _merge_and_nodes(left: Graph, right: Graph) -> Graph:
        """
        Merge two graph nodes under a single AND node, flattening nested ANDs.

        This builds a single list representation `[AND, ...children]` by recursively
        pulling up children of any encountered AND nodes, preventing nested AND
        structures.

        Parameters
        ----------
        left
            Left graph node to merge.
        right
            Right graph node to merge.

        Returns
        -------
        Graph
            A flattened AND node combining both inputs.
        """
        merged_children: List[Any] = []

        def append(node: Graph) -> None:
            """
            Parameters
            ----------
            node
                A graph node to append into `merged_children`; flattens AND nodes recursively.
            """
            if isinstance(node, list) and len(node) > 0 and node[0] == AND:
                for child in cast(List[Graph], node[1:]):
                    append(child)
            else:
                merged_children.append(node)

        append(left)
        append(right)
        return [AND] + merged_children

    @staticmethod
    def _compose_and(
        left_filters: List[FilterBase],
        left_graph: Optional[Graph],
        right_filters: List[FilterBase],
        right_graph: Optional[Graph],
    ) -> Tuple[List[FilterBase], Optional[Graph]]:
        """
        Compose two filter sets and their graphs using a logical AND.

        - Normalizes missing graphs to `DEFAULT_GRAPH` when a side has filters.
        - Shifts indices in the right graph by the size of the left filters so
          that indices continue to point at the correct filters.
        - Unwraps singleton OR nodes to avoid unnecessary OR wrappers.
        - Merges the two graphs under a flattened AND using `_merge_and_nodes`.

        Parameters
        ----------
        left_filters
            Filters on the left-hand side.
        left_graph
            Graph describing how `left_filters` are combined (or `None`).
        right_filters
            Filters on the right-hand side.
        right_graph
            Graph describing how `right_filters` are combined (or `None`).

        Returns
        -------
        Tuple[List[FilterBase], Optional[Graph]]
            The combined filters and the composed graph.
        """
        if not left_filters:
            return list(right_filters), right_graph
        if not right_filters:
            return list(left_filters), left_graph

        normalized_left: Graph = left_graph if left_graph is not None else DEFAULT_GRAPH
        normalized_right: Graph = (
            right_graph if right_graph is not None else DEFAULT_GRAPH
        )
        offset = len(left_filters)
        transformed_right: Graph = FilterConfig._transform_graph_indices(
            normalized_right, offset
        )
        left_node: Graph = FilterConfig._unwrap_singleton_or(normalized_left)
        right_node: Graph = FilterConfig._unwrap_singleton_or(transformed_right)
        combined_graph: Graph = FilterConfig._merge_and_nodes(left_node, right_node)
        return list(left_filters) + list(right_filters), combined_graph

    def __and__(self, other: Union[FilterBase, FilterConfig]) -> FilterConfig:
        """
        Return a new configuration that is the logical AND of `self` and `other`.

        The `other` argument may be a single `FilterBase` (which will be wrapped
        into a `FilterConfig`) or another `FilterConfig`.

        Parameters
        ----------
        other
            A `FilterBase` or `FilterConfig` to combine with this configuration.

        Returns
        -------
        FilterConfig
            A new configuration representing the conjunction of both operands.

        Examples
        --------
        Combine a single filter and a `FilterConfig` using `&`:

        >>> f_text = FieldFilter(field="text", operator="contains", value="error")
        >>> f_score = FieldFilter(field="score", operator=">=", value=0.9)
        >>> cfg = FilterConfig.from_filter(f_text) & f_score
        >>> isinstance(cfg, FilterConfig)
        True

        Combine two `FilterConfig` objects:

        >>> left = FilterConfig.from_filter(f_text)
        >>> right = FilterConfig.from_filter(f_score)
        >>> combined = left & right
        >>> isinstance(combined, FilterConfig)
        True
        """
        if isinstance(other, FilterConfig):
            right_cfg = other
        elif isinstance(other, FilterBase):
            right_cfg = FilterConfig.from_filter(other)
        else:
            raise TypeError("Unsupported type for FilterConfig composition")
        combined_filters, combined_graph = FilterConfig._compose_and(
            self._filters,
            self._graph,
            right_cfg._filters,
            right_cfg._graph,
        )
        return FilterConfig(combined_filters, combined_graph)

    def __iand__(self, other: Union[FilterBase, FilterConfig]) -> FilterConfig:
        """
        In-place logical AND composition with `other`.

        Updates this instance's filters and graph. The `other` argument may be a
        single `FilterBase` or another `FilterConfig`.

        Parameters
        ----------
        other
            A `FilterBase` or `FilterConfig` to compose with this configuration.

        Returns
        -------
        FilterConfig
            The updated configuration (i.e., `self`).

        Examples
        --------
        In-place composition using `&=`:

        >>> cfg = FilterConfig.from_filter(FieldFilter(field="text", operator="contains", value="error"))
        >>> cfg &= FieldFilter(field="score", operator=">=", value=0.9)
        >>> isinstance(cfg, FilterConfig)
        True
        """
        if isinstance(other, FilterConfig):
            right_cfg = other
        elif isinstance(other, FilterBase):
            right_cfg = FilterConfig.from_filter(other)
        else:
            raise TypeError("Unsupported type for FilterConfig composition")
        combined_filters, combined_graph = FilterConfig._compose_and(
            self._filters,
            self._graph,
            right_cfg._filters,
            right_cfg._graph,
        )
        self._filters = combined_filters
        self._graph = combined_graph
        return self

    @staticmethod
    def _transform_graph_indices(input_graph: Graph, offset: int) -> Graph:
        """
        Shift all integer indices in `input_graph` by `offset`.

        Traverses the graph recursively and adds `offset` to every integer index,
        preserving non-integer tokens like operator markers and nested list
        structure.

        Parameters
        ----------
        input_graph
            Graph whose indices should be shifted.
        offset
            Amount to add to every integer index in the graph.

        Returns
        -------
        Graph
            A new graph with all indices shifted by the given offset.
        """
        if isinstance(input_graph, int):
            return input_graph + offset
        if isinstance(input_graph, list):
            result: List[Any] = []
            for item in input_graph:
                if isinstance(item, int):
                    result.append(item + offset)
                elif isinstance(item, list):
                    result.append(
                        FilterConfig._transform_graph_indices(cast(Graph, item), offset)
                    )
                else:
                    result.append(item)
            return result
        return input_graph

    def __eq__(self, other: object) -> bool:
        """
        Determine structural equality between two configurations.

        Two configurations are considered equal if their filter lists (after
        converting each filter to JSON) are the same length and, when their graphs
        are compared structurally (treating `None` as `DEFAULT_GRAPH`), the nodes
        at corresponding positions reference equal filters and have identical
        shapes/operators.

        Parameters
        ----------
        other
            The object to compare against.

        Returns
        -------
        bool
            True if both configurations are structurally equivalent, otherwise False.
        """
        if not isinstance(other, FilterConfig):
            return False
        left_filters = [f.to_dict() for f in self._filters]
        right_filters = [f.to_dict() for f in other._filters]
        if len(left_filters) != len(right_filters):
            return False

        def dfs_compare(left_node: Graph, right_node: Graph) -> bool:
            """
            Parameters
            ----------
            left_node
                A node from the left-hand-side graph.
            right_node
                A node from the right-hand-side graph.

            Returns
            -------
            bool
                Whether the two graphs represent equivalent filter structures.
            """
            if isinstance(left_node, int) and isinstance(right_node, int):
                if left_node >= len(left_filters) or right_node >= len(right_filters):
                    return False
                return left_filters[left_node] == right_filters[right_node]
            if isinstance(left_node, list) and isinstance(right_node, list):
                if len(left_node) != len(right_node):
                    return False
                return all(
                    dfs_compare(cast(Graph, l), cast(Graph, r))
                    for l, r in zip(left_node, right_node)
                )
            return False

        lg: Graph = self._graph if self._graph is not None else DEFAULT_GRAPH
        rg: Graph = other._graph if other._graph is not None else DEFAULT_GRAPH
        return dfs_compare(lg, rg)
