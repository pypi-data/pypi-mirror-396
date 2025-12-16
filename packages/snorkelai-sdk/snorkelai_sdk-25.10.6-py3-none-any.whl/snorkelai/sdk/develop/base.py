from typing import Any, Protocol

from typing_extensions import Self


class Base(Protocol):
    """Base protocol that all SDK classes, representing an entity, e.g., Dataset, Benchmark, etc, should implement for consistency."""

    @classmethod
    def create(cls, *args: Any, **kwargs: Any) -> Self:
        """Creates a new entity instance in the server and returns an object that represents it.

        Parameters
        ----------
        args
            Positional arguments
        kwargs
            Keyword arguments

        Returns
        -------
        Self
            The created object
        """

    @classmethod
    def get(cls, *args: Any, **kwargs: Any) -> Self:
        """Returns an object that represents an entity instance identified by UID or name.


        Parameters
        ----------
        args
            Positional arguments
        kwargs
            Keyword arguments

        Returns
        -------
        Self
            The object
        """

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Update the entity instance in the server and updates the object in place if needed.

        Parameters
        ----------
        args
            Positional arguments
        kwargs
            Keyword arguments

        Returns
        -------

        """

    @classmethod
    def delete(cls, *args: Any, **kwargs: Any) -> None:
        """Deletes an entity instance in the server.

        Parameters
        ----------
        args
            Positional arguments
        kwargs
            Keyword arguments
        """

    @property
    def uid(self) -> int:
        """Returns the unique identifier (UID) of the entity instance.

        Returns
        -------
        int
            The UID of the entity instance
        """
