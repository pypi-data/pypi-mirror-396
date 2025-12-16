import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import pandas as pd

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext


@dataclass
class _KV:
    key: str
    val: Any

    def __str__(self) -> str:
        return f"{self.key}={self.val}"

    def __repr__(self) -> str:
        return f"{self.key}={self.val}"


@dataclass
class _Event:
    timestamp: datetime.datetime
    event_type: str


def _indented(s: str, indent: int) -> str:
    return "|   " * indent + s


class _Trace:
    def __init__(self) -> None:
        self.start: datetime.datetime = datetime.datetime.min
        self.subtraces: List[Union[_Event, _Trace]] = []

    def lines(
        self, indent: int = 0, start: Optional[datetime.datetime] = None
    ) -> List[str]:
        start = start or self.start
        lines = []
        for t in self.subtraces:
            if isinstance(t, _Event):
                lines.append(
                    _indented(
                        f"+{t.timestamp - start} {t.event_type} {t.timestamp}", indent
                    )
                )
            elif isinstance(t, _Trace):
                lines.extend(t.lines(indent=indent + 1, start=start))
            else:
                continue
        return lines


class _TraceTree:
    def __init__(self) -> None:
        self.start: datetime.datetime = datetime.datetime.min
        self.node_key: _KV = _KV(key="default", val="default")
        self.node_meta: List[_KV] = []
        self.subtrees: Sequence[Union[_Trace, _TraceTree]] = []

    def lines(self, indent: int = 0) -> List[str]:
        lines = [_indented(f"{self.node_key} {self.node_meta or ''}", indent)]
        for t in sorted(self.subtrees, key=lambda x: x.start):
            lines.extend(t.lines(indent=indent + 1))
        return lines

    def pprint(self) -> None:
        print("\n".join(self.lines()))


def _make_trace(
    events: List[_Event],
    event_type_idx: Optional[Dict[str, List[int]]] = None,
    idx_offset: int = 0,
) -> _Trace:
    if event_type_idx is None:
        event_type_idx = defaultdict(list)
        for i, e in enumerate(events):
            event_type_idx[e.event_type].append(i)

    t = _Trace()
    t.subtraces = []
    i = 0
    while i < len(events):
        e = events[i]
        if i == 0:
            t.start = e.timestamp
        t.subtraces.append(e)
        if e.event_type.endswith("_start"):
            matching_event_type = e.event_type[: -len("_start")] + "_end"
            match_idxs = event_type_idx.get(matching_event_type, [])
            if match_idxs:
                match_idx = match_idxs[0] - idx_offset
                event_type_idx[matching_event_type] = match_idxs[1:]
                t.subtraces.append(
                    _make_trace(
                        events[i + 1 : match_idx],
                        event_type_idx=event_type_idx,
                        idx_offset=idx_offset + i + 1,
                    )
                )
                i = match_idx
                continue
        i += 1
    return t


def _make_trace_tree(
    df: pd.DataFrame, groupby: List[Tuple[str, List[str]]]
) -> Sequence[Union[_Trace, _TraceTree]]:
    if not groupby:
        df = df.sort_values(by=["timestamp"])
        events: List[_Event] = []
        for i, row in df.iterrows():
            events.append(
                _Event(
                    timestamp=datetime.datetime.strptime(
                        row["timestamp"], "%Y-%m-%d-%H-%M-%S-%f"
                    ),
                    event_type=row["event_type"],
                )
            )
        return [_make_trace(events)]

    col, meta_cols = groupby[0]
    df_groupby = df.groupby([col])
    trees: List[_TraceTree] = []
    for g in df_groupby.groups:
        t = _TraceTree()
        t.node_key = _KV(key=col, val=g)
        group = df_groupby.get_group(g)
        node_meta: List[_KV] = []
        for c in meta_cols:
            c_meta = group[c].dropna().unique().tolist()
            node_meta.append(_KV(key=c, val=",".join(c_meta)))
        t.node_meta = node_meta
        t.subtrees = _make_trace_tree(group, groupby[1:])
        start: Optional[datetime.datetime] = None
        for subt in t.subtrees:
            if start is None or subt.start < start:
                start = subt.start
        assert start is not None
        t.start = start
        trees.append(t)
    return trees


def _get_job_trace(job_id: str, time_range_minutes: Optional[int] = None) -> _TraceTree:
    root = _TraceTree()
    root.node_key = _KV(key="root", val="root")
    params = {}
    if time_range_minutes:
        params["time_range_minutes"] = time_range_minutes
    param_str = "&".join(f"{k}={v}" for k, v in params.items())

    # TODO: change below call to api.fetch_event_metrics_events__job_id__get()
    #       when corresponding unit test created
    ctx = SnorkelSDKContext.get_global()
    response = ctx.tdm_client.get(f"events/{job_id}?{param_str}")
    if len(response) == 0:
        return root
    df = pd.DataFrame(response)
    df = df.drop(columns=["_time", "_measurement", "_value", "metric_type"])
    groupby_columns: List[Tuple[str, List[str]]] = [
        ("req_id", []),
        ("job_id", ["job_type", "task_name"]),
    ]

    root.subtrees = _make_trace_tree(df, groupby_columns)
    return root


def print_job_trace(job_id: str, time_range_minutes: Optional[int] = None) -> None:
    """Prints a breakdown of job events given request id

    Parameters
    ----------
    job_id
        The job id of the job to break down.
    time_range_minutes
        Look at jobs in past `time_range_minutes` minutes.

    """
    _get_job_trace(job_id, time_range_minutes=time_range_minutes).pprint()
