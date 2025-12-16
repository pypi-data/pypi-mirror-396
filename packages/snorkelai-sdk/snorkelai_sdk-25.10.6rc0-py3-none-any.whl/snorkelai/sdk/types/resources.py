from enum import Enum


class ResourceState(Enum):
    """Enum to capture state of a resource (e.g. application, model, training set)
    in the database.

    This lets us reserve a uid for an incomplete resource (e.g. a training set)
    inside a large transaction without prematurely committing the transaction or
    polluting GET query results.

    This can also be used to mark things as deleted without the cascading delete
    itself being a long blocking call (and actual deletion can be part of a cron job).
    """

    # Do not change values here without a migration since we store the ints in DB.
    CREATED = 0
    READY = 1
    DELETED = 2
