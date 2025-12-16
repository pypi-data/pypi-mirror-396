import sys
from typing import List, Optional, cast, final

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

from requests.exceptions import HTTPError, RequestException

from snorkelai.sdk.client_v3.tdm.api.users import (
    create_user_users_post,
    get_list_workspaced_users_workspaced_users_get,
    remove_user_users__user_uid__delete,
    reset_password_reset_password_post,
    update_user_email_users__user_uid__email_put,
    update_user_role_users__user_uid__role_put,
    update_user_timezone_users__user_uid__timezone_put,
    update_user_users__user_uid__put,
    update_user_view_users__user_uid__default_view_put,
)
from snorkelai.sdk.client_v3.tdm.models import (
    CreateUserRequest,
    ResetPasswordParams,
    UpdateUserEmail,
    UpdateUserPayload,
    UpdateUserRole,
    UpdateUserTimezone,
    UpdateUserView,
)
from snorkelai.sdk.client_v3.tdm.models.update_superadmin_action import (
    UpdateSuperadminAction,
)
from snorkelai.sdk.client_v3.tdm.models.user_role import UserRole as UserRoleGen
from snorkelai.sdk.client_v3.tdm.models.user_view import UserView as UserViewGen
from snorkelai.sdk.client_v3.tdm.types import UNSET
from snorkelai.sdk.client_v3.utils import IdType, get_workspace_uid
from snorkelai.sdk.develop.base import Base
from snorkelai.sdk.utils.http_errors import parse_http_error_detail

DEACTIVATED_SUFFIX = " (deactivated)"


class UserRole(StrEnum):
    ADMIN = "admin"
    LABELER = "labeler"
    REVIEWER = "reviewer"
    STANDARD = "standard"
    SUPERADMIN = "superadmin"


class UserView(StrEnum):
    ANNOTATION = "annotation"
    STANDARD = "standard"


@final
class User(Base):
    """
    User management class for Snorkel SDK.

    This class provides methods to create, retrieve, update, and delete users within Snorkel Flow.
    Each user is assigned a role that determines their permissions, and users are organized within workspaces.
    """

    _uid: int
    _username: str
    _email: Optional[str]
    _role: UserRole
    _timezone: Optional[str]
    _is_superadmin: bool
    _is_active: bool
    _default_view: UserView

    def __init__(
        self,
        uid: int,
        username: str,
        role: UserRole,
        default_view: UserView,
        email: Optional[str] = None,
        timezone: Optional[str] = None,
        is_superadmin: bool = False,
        is_active: bool = True,
    ):
        """Create a user object in-memory with necessary properties. This constructor should not be called directly,
        and should instead be accessed through the ``create()``, ``get()``, and ``list()`` methods

        Parameters
        ----------
        uid
            The unique integer identifier for the user within Snorkel Flow
        username
            The username of the user
        role
            The role assigned to the user. Defaults to UserRole.standard if not set.
        default_view
            The default view preference for the user. Defaults to UserView.standard if not set.
        email
            The email address of the user
        timezone
            The timezone preference for the user
        is_superadmin
            Whether the user has superadmin privileges. Defaults to False if not set.
        is_active
            Whether the user account is active. Defaults to True if not set.
        """
        self._uid = uid
        self._username = username
        self._email = email
        self._role = role
        self._timezone = timezone
        self._is_superadmin = is_superadmin
        self._is_active = is_active
        self._default_view = default_view

    @property
    def uid(self) -> int:
        """The unique integer identifier for the user within Snorkel Flow"""
        return self._uid

    @property
    def username(self) -> str:
        """The username of the user"""
        return self._username

    @property
    def email(self) -> Optional[str]:
        """The email address of the user"""
        return self._email

    @property
    def role(self) -> UserRole:
        """The role assigned to the user"""
        return self._role

    @property
    def timezone(self) -> Optional[str]:
        """The timezone preference for the user."""
        return self._timezone

    @property
    def is_superadmin(self) -> bool:
        """Whether the user has superadmin privileges"""
        return self._is_superadmin

    @property
    def is_active(self) -> bool:
        """Whether the user account is active"""
        return self._is_active

    @property
    def default_view(self) -> UserView:
        """The default view preference for the user"""
        return self._default_view

    @staticmethod
    def _resolve_workspace_uid(workspace: Optional[IdType]) -> int:
        """Resolve workspace identifier to workspace UID.

        Parameters
        ----------
        workspace
            Workspace UID (int) or workspace name (str). If None, uses the default workspace.

        Returns
        -------
        int
            The resolved workspace UID
        """
        if workspace is None:
            return get_workspace_uid("default")
        elif isinstance(workspace, str):
            return get_workspace_uid(workspace)
        else:
            return workspace

    @classmethod
    def create(
        cls,
        username: str,
        password: str,
        role: Optional[UserRole] = None,
        email: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> "User":
        """
        Create a new user.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import User, UserRole
            >>> new_user = User.create(username='jane_smith', password='SecurePass123!', role=UserRole.REVIEWER)
            User jane_smith has been created with UID 42.
            >>> new_user.username
            'jane_smith'

        Parameters
        ----------
        username
            Username for the new user
        password
            Password for the new user (minimum 12 characters with at least 3 character types)
        role
            User role - 'standard', 'admin', 'reviewer', 'labeler', or 'superadmin'. Defaults to 'standard'.
        email
            Email address for the user
        timezone
            IANA timezone (e.g., 'America/Sao_Paulo', 'UTC', 'Europe/London').

        Returns
        -------
        User
            The created User object
        """
        try:
            create_request = CreateUserRequest(
                username=username,
                password=password,
                role=UserRoleGen(role.value) if role is not None else UNSET,
                email=email if email is not None else UNSET,
            )

            response = create_user_users_post(body=create_request)
            user_uid = response.user_uid

            if timezone:
                timezone_payload = UpdateUserTimezone(timezone=timezone)
                response = update_user_timezone_users__user_uid__timezone_put(
                    user_uid=user_uid, body=timezone_payload
                )

            print(f"User {username} has been created with UID {user_uid}.")

            email_value = cast(
                Optional[str], None if response.email is UNSET else response.email
            )
            timezone_value = cast(
                Optional[str], None if response.timezone is UNSET else response.timezone
            )

            return cls(
                uid=response.user_uid,
                username=response.username,
                role=UserRole(response.role.value),
                default_view=UserView(response.default_view.value),
                email=email_value,
                timezone=timezone_value,
                is_superadmin=(response.role == UserRoleGen.SUPERADMIN),
                is_active=response.is_active,
            )

        except HTTPError as exc:
            error_detail = parse_http_error_detail(exc)
            msg = f"Failed to create user {username}: {error_detail}"
            raise ValueError(msg) from None
        except RequestException as exc:
            error_msg = str(exc) if exc.args else "Network error"
            msg = f"Failed to create user {username}: {error_msg}"
            raise ValueError(msg) from exc

    @classmethod
    def list(
        cls,
        include_inactive: bool = False,
        include_superadmins: bool = False,
        workspace: Optional[IdType] = None,
    ) -> List["User"]:
        """
        List all users in a workspace with optional filters.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import User
            >>> users = User.list()
            >>> users[0].username
            'john_doe'

            >>> inactive_users = User.list(include_inactive=True)
            >>> all_users = User.list(include_superadmins=True, workspace="my-workspace")

        Parameters
        ----------
        include_inactive
            Include inactive/deleted users in the results
        include_superadmins
            Include superadmin users in the results
        workspace
            Workspace UID (int) or workspace name (str). If None, uses the default workspace.

        Returns
        -------
        List[User]
            List of User objects matching the filter criteria
        """
        try:
            workspace_uid = cls._resolve_workspace_uid(workspace)

            users = get_list_workspaced_users_workspaced_users_get(
                workspace_uid=workspace_uid,
                include_inactive=include_inactive,
            )

            user_list: List[User] = []

            for user_data in users:
                if not include_superadmins and user_data.is_superadmin:
                    continue

                email = cast(
                    Optional[str],
                    None if user_data.email is UNSET else user_data.email,
                )
                timezone = cast(
                    Optional[str],
                    None if user_data.timezone is UNSET else user_data.timezone,
                )
                user_obj = cls(
                    uid=user_data.user_uid,
                    username=user_data.username,
                    role=UserRole(user_data.role.value),
                    default_view=UserView(user_data.default_view.value),
                    email=email,
                    timezone=timezone,
                    is_superadmin=user_data.is_superadmin,
                    is_active=user_data.is_active,
                )
                user_list.append(user_obj)

            return user_list
        except HTTPError as exc:
            error_detail = parse_http_error_detail(exc)
            msg = f"Failed to list users: {error_detail}"
            raise ValueError(msg) from None
        except RequestException as exc:
            error_msg = str(exc) if exc.args else "Network error"
            msg = f"Failed to list users: {error_msg}"
            raise ValueError(msg) from exc

    @classmethod
    def get(cls, user: IdType, workspace: Optional[IdType] = None) -> "User":
        """
        Get a user by UID or username.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import User
            >>> user = User.get("john_doe")
            >>> user.username
            'john_doe'
            >>> user.uid
            42
            >>> user.email
            'john.doe@example.com'

            >>> user = User.get(42, workspace="my-workspace")
            >>> user.username
            'jane_smith'

        Parameters
        ----------
        user
            User UID (int) or username (str)
        workspace
            Workspace UID (int) or workspace name (str). If None, uses the default workspace.

        Returns
        -------
        User
            The user object with all user information

        Raises
        ------
        ValueError
            If the user is not found in the specified workspace, or if there is a
            network error or HTTP error during the request.
        """
        try:
            workspace_uid = cls._resolve_workspace_uid(workspace)

            users = get_list_workspaced_users_workspaced_users_get(
                workspace_uid=workspace_uid,
                include_inactive=True,
            )
            for user_data in users:
                if isinstance(user, int):
                    match_found = user_data.user_uid == user
                else:
                    api_username = user_data.username
                    match_found = (
                        api_username == user
                        or api_username == f"{user}{DEACTIVATED_SUFFIX}"
                    )

                if match_found:
                    email = cast(
                        Optional[str],
                        None if user_data.email is UNSET else user_data.email,
                    )
                    timezone = cast(
                        Optional[str],
                        None if user_data.timezone is UNSET else user_data.timezone,
                    )

                    role = UserRole(user_data.role.value)
                    default_view = UserView(user_data.default_view.value)

                    return cls(
                        uid=user_data.user_uid,
                        username=user_data.username,
                        role=role,
                        default_view=default_view,
                        email=email,
                        timezone=timezone,
                        is_superadmin=user_data.is_superadmin,
                        is_active=user_data.is_active,
                    )

            raise ValueError(f"User {user} was not found.")
        except HTTPError as exc:
            error_detail = parse_http_error_detail(exc)
            msg = f"Failed to get user {user}: {error_detail}"
            raise ValueError(msg) from None
        except RequestException as exc:
            error_msg = str(exc) if exc.args else "Network error"
            msg = f"Failed to get user {user}: {error_msg}"
            raise ValueError(msg) from exc

    @classmethod
    def reset_password(cls, user: IdType, new_password: str) -> None:
        """
        Reset any user's password without requiring old password.

        Accepts user UID (int) or username (str).

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import User
            >>> User.reset_password("john_doe", "NewSecurePass123!")
            Password for user john_doe has been reset.

            >>> User.reset_password(42, "AnotherPass456!")
            Password for user 42 has been reset.

        Parameters
        ----------
        user
            User UID (int) or username (str)
        new_password
            New password to set for the user

        Raises
        ------
        ValueError
            If the user is not found, or if there is a network error or HTTP error
            during the request.
        """
        user_obj = cls.get(user)
        try:
            reset_params = ResetPasswordParams(
                username=user_obj.username, new_password=new_password
            )
            reset_password_reset_password_post(body=reset_params)
            print(f"Password for user {user} has been reset.")
        except HTTPError as exc:
            error_detail = parse_http_error_detail(exc)
            msg = f"Failed to reset password for user {user}: {error_detail}"
            raise ValueError(msg) from None
        except RequestException as exc:
            error_msg = str(exc) if exc.args else "Network error"
            msg = f"Failed to reset password for user {user}: {error_msg}"
            raise ValueError(msg) from exc

    @classmethod
    def delete(cls, user: IdType) -> None:
        """
        Delete a user by UID or username.

        This performs a soft delete: sets is_active=False and clears email.
        Use list(include_inactive=True) to view deleted users.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import User
            >>> User.delete("john_doe")
            User john_doe has been deleted.

            >>> User.delete(42)
            User 42 has been deleted.

        Parameters
        ----------
        user
            User UID (int) or username (str)

        Raises
        ------
        ValueError
            If the user is not found, or if there is a network error or HTTP error
            during the request.
        """
        user_obj = cls.get(user)
        try:
            remove_user_users__user_uid__delete(user_uid=user_obj.uid)
            print(f"User {user} has been deleted.")
        except HTTPError as exc:
            error_detail = parse_http_error_detail(exc)
            msg = f"Failed to delete user {user}: {error_detail}"
            raise ValueError(msg) from None
        except RequestException as exc:
            error_msg = str(exc) if exc.args else "Network error"
            msg = f"Failed to delete user {user}: {error_msg}"
            raise ValueError(msg) from exc

    def update(
        self,
        email: Optional[str] = None,
        role: Optional[UserRole] = None,
        timezone: Optional[str] = None,
        is_superadmin: Optional[bool] = None,
        default_view: Optional[UserView] = None,
    ) -> None:
        """
        Update user properties.

        Examples
        --------
        .. doctest::

            >>> from snorkelai.sdk.develop import User
            >>> user = User.get("john_doe")
            >>> user.update(email="john.doe@example.com")
            User john_doe (UID: 42) has been updated.
            >>> user.email
            'john.doe@example.com'

            >>> user.update(timezone="America/New_York")
            User john_doe (UID: 42) has been updated.
            >>> user.timezone
            'America/New_York'

        Parameters
        ----------
        email
            Email address for the user
        role
            User role - 'standard', 'admin', 'reviewer', 'labeler', or 'superadmin'
        timezone
            IANA timezone (e.g., 'America/Sao_Paulo', 'UTC', 'Europe/London')
        is_superadmin
            Whether the user should be a superadmin
        default_view
            Default view for the user

        Note
        ----
        To deactivate a user (set is_active=False), use User.delete() which performs a soft delete.
        """
        try:
            response = None

            if email is not None:
                email_payload = UpdateUserEmail(email=email)
                response = update_user_email_users__user_uid__email_put(
                    user_uid=self._uid, body=email_payload
                )
                self._email = cast(
                    Optional[str], None if response.email is UNSET else response.email
                )

            if role is not None:
                role_payload = UpdateUserRole(role=UserRoleGen(role.value))
                response = update_user_role_users__user_uid__role_put(
                    user_uid=self._uid, body=role_payload
                )
                self._role = UserRole(response.role.value)
                self._is_superadmin = response.role == UserRoleGen.SUPERADMIN

            if is_superadmin is not None:
                action = (
                    UpdateSuperadminAction.ASSIGN
                    if is_superadmin
                    else UpdateSuperadminAction.REMOVE
                )
                superadmin_payload = UpdateUserPayload(update_superadmin=action)
                update_user_users__user_uid__put(
                    user_uid=self._uid, body=superadmin_payload
                )
                self._is_superadmin = is_superadmin
                if is_superadmin:
                    self._role = UserRole.SUPERADMIN

            if timezone is not None:
                timezone_payload = UpdateUserTimezone(timezone=timezone)
                response = update_user_timezone_users__user_uid__timezone_put(
                    user_uid=self._uid, body=timezone_payload
                )
                self._timezone = cast(
                    Optional[str],
                    None if response.timezone is UNSET else response.timezone,
                )

            if default_view is not None:
                view_payload = UpdateUserView(
                    default_view=UserViewGen(default_view.value)
                )
                response = update_user_view_users__user_uid__default_view_put(
                    user_uid=self._uid, body=view_payload
                )
                self._default_view = UserView(response.default_view.value)

            if any(
                param is not None
                for param in [email, role, timezone, is_superadmin, default_view]
            ):
                print(f"User {self._username} (UID: {self._uid}) has been updated.")

        except HTTPError as exc:
            error_detail = parse_http_error_detail(exc)
            msg = f"Failed to update user {self._username}: {error_detail}"
            raise ValueError(msg) from None
        except RequestException as exc:
            error_msg = str(exc) if exc.args else "Network error"
            msg = f"Failed to update user {self._username}: {error_msg}"
            raise ValueError(msg) from exc
