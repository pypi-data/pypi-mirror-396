"""Interfaces to interact with the Snorkel REST API.

Most of the functions in the ``snorkelai.sdk.client`` module require a *client context*
object — :mod:`SnorkelSDKContext <snorkelai.sdk.client.ctx.SnorkelSDKContext>` — that points to the Snorkel Flow instance:

.. testcode::

    import snorkelai.sdk.client as sai
    ctx = sai.SnorkelSDKContext.from_endpoint_url()

All the functions under submodules are also available under ``snorkelai.sdk.client``.

Examples
--------
.. testcode::

    import snorkelai.sdk.client as sai
    # get_annotation_sources is available under snorkelai.sdk.client.annotation_sources
    sai.annotation_sources.get_annotation_sources()
    # also available under snorkelai.sdk.client (recommended)
    sai.get_annotation_sources()  # noqa: F405

Since ``snorkelai.sdk.client`` submodules may be reorganized in the future, we recommend accessing functions directly from ``snorkelai.sdk.client`` to minimize the risk of future breaking changes.

Submodules
==========

.. autosummary::
    :toctree: _autosummary
    :template: custom-module-template.rst

    snorkelai.sdk.client.annotation_sources
    snorkelai.sdk.client.connector_configs
    snorkelai.sdk.client.ctx
    snorkelai.sdk.client.external_models
    snorkelai.sdk.client.files
    snorkelai.sdk.client.fm_suite
    snorkelai.sdk.client.secrets
    snorkelai.sdk.client.synthetic
    snorkelai.sdk.client.utils
    snorkelai.sdk.client.users


"""

# from snorkelai.sdk.client.core import *
# We intentionally import functions from client_v3/core.py to client/XXX.py rather than client/core.py
# so that those functions show up in a more appropriate submodule than core because "core" is not clear to end users.
from snorkelai.sdk.client.annotation_sources import *  # noqa: F403
from snorkelai.sdk.client.connector_configs import *  # noqa: F403
from snorkelai.sdk.client.ctx import *  # noqa: F403
from snorkelai.sdk.client.external_models import *  # noqa: F403
from snorkelai.sdk.client.files import *  # noqa: F403
from snorkelai.sdk.client.fm_suite import *  # noqa: F403
from snorkelai.sdk.client.secrets import *  # noqa: F403
from snorkelai.sdk.client.synthetic import *  # noqa: F403
from snorkelai.sdk.client.users import *  # noqa: F403
from snorkelai.sdk.client.utils import *  # noqa: F403
