from typing import Dict, List

import pandas as pd

from snorkelai.sdk.client_v3.tdm.api.slices import (
    get_slice_membership_dataset__dataset_uid__slice__slice_uid__membership_get,
    get_slices_dataset__dataset_uid__slices_get,
)


def _get_slice_membership_series(dataset_uid: int) -> pd.Series:
    """Return the slices for the given dataset as a Pandas Series.

    Examples
    --------
    ::

        >>> sai.get_slices(dataset_uid=1)
        x_uid
        doc::10005          [slice0, slice1]
        doc::10006                [slice1]
        doc::10007                [slice2]
        doc::10009                [slice1]
        doc::10012          [slice0, slice2]
        doc::10052                [slice1]
        Name: slices, dtype: object

    Parameters
    ----------
    dataset_uid
        UID of the dataset whose slices are returned

    Returns
    -------
    pd.Series
        A pandas Series containing a list of slices

    """
    slice_list = get_slices_dataset__dataset_uid__slices_get(dataset_uid=dataset_uid)

    slice_dict: Dict[str, List[str]] = {}
    for slice in slice_list:
        x_uids = (
            get_slice_membership_dataset__dataset_uid__slice__slice_uid__membership_get(
                dataset_uid=dataset_uid, slice_uid=slice["id"]
            )
        )
        for x_uid in x_uids:
            if x_uid not in slice_dict:
                slice_dict[x_uid] = []
            slice_dict[x_uid].append(slice["display_name"])

    se_slices = pd.Series(slice_dict)
    return se_slices
