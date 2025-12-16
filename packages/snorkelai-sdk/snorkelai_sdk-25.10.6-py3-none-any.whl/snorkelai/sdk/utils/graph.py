import json
import urllib
from typing import Any, Dict, List, Union

# A specification of how to combine one or more templates into an LFCondition
# Note: This type signature is an oversimplification; e.g., does not show recursion
Graph = Union[int, List[Any]]
"""
TODO: Make it more clear in graphs where blocks are (e.g., is AND combining two
templates in one block or two singleton blocks)

TODO: Normalize grammar so that all graphs expressible in the backend are supported by
the frontend

GRAMMAR:
   $GRAPH -> $BOOL
   $BOOL -> $OR $BOOL ... $BOOL
   $BOOL -> $AND $BOOL ... $BOOL
   $BOOL -> $NOT $BOOL
   $BOOL -> $IS $BOOL
   $BOOL -> [int] ->  # Evaluate template on x to create a bool
EXAMPLE GRAPHS:
- [“$IS”, 0]
   - The minimal/default graph (e.g., if none is passed)
   - The graph for a single template
- [“$NOT”, 0]
- [“$AND”, 0, 1]
- [“$AND”, [“$OR”, 0, 1], [“$NOT”, 2]]
   - e.g., “span is right of 'executed' or 'signed' and not right of 'amended'”
"""
AND = "$AND"
OR = "$OR"
IS = "$IS"
NOT = "$NOT"

DEFAULT_GRAPH = [OR, 0]
MAX_GRAPH_DEPTH = 3  # AND/OR to combine blocks, AND/OR inside blocks to combine builders, and NOT on each builder.


def parse_uri_encoded_object(config: str) -> Dict[str, Any]:
    message = urllib.parse.unquote(config)
    return json.loads(message)
