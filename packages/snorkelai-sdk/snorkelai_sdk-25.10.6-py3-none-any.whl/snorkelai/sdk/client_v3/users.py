from typing import Any, Dict

from snorkelai.sdk.client_v3.tdm.api.users import (
    get_list_users_users_get,
    reset_password_reset_password_post,
)
from snorkelai.sdk.client_v3.tdm.models.reset_password_params import ResetPasswordParams
from snorkelai.sdk.client_v3.utils import IdType


def reset_password(username: str, new_password: str) -> None:
    """Reset the password for the specified user to the specified new password.

    This functionality is only available to administrators as determined by the
    API key of the caller.

    Parameters
    ----------
    username
        Username of the user whose password you wish to reset
    new_password
        The new password value you wish to set for this user

    """
    params = ResetPasswordParams(username=username, new_password=new_password)
    reset_password_reset_password_post(body=params)


def get_user(user: IdType) -> Dict[str, Any]:
    """Get a user info by its username or user_uid.

    Example
    -------

    .. doctest::

        >>> sai.get_user("username")
        {
            'username': 'username',
            'user_uid': 4,
            'default_view': 'standard',
            'role': 'standard',
            'is_active': True,
            'is_locked': False,
            'email': None,
            'timezone': None,
            'is_superadmin': False
        }

    Parameters
    ----------
    user
        A valid Snorkel Flow user's username or user_uid

    Returns
    -------
    Dict[str, Any]
        The user info corresponding to the provided username/user_uid

    """
    users = get_list_users_users_get()
    if isinstance(user, str):
        for _user in users:
            if _user.username == user:
                return _user.to_dict()
        raise ValueError(f"Unable to find a user with username: {user}")
    else:
        for _user in users:
            if _user.user_uid == user:
                return _user.to_dict()
        raise ValueError(f"Unable to find a user with user_uid: {user}")
