from logging import getLogger
from typing import Any, Dict, List, Optional, Sequence, Union, cast, final

from requests import HTTPError

from snorkelai.sdk.client_v3.tdm.api.slices import (
    add_xuids_to_slice_dataset__dataset_uid__add_xuids__slice_uid__post as add_xuids_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.slices import (
    create_slice_dataset__dataset_uid__slice_post as create_slice_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.slices import (
    delete_slice_dataset__dataset_uid__slice__slice_uid__delete as delete_slice_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.slices import (
    get_slice_membership_dataset__dataset_uid__slice__slice_uid__membership_get as get_slice_membership_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.slices import (
    get_slices_dataset__dataset_uid__slices_get as get_slices_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.slices import (
    remove_xuids_from_slice_dataset__dataset_uid__remove_xuids__slice_uid__post as remove_xuids_autogen,
)
from snorkelai.sdk.client_v3.tdm.api.slices import (
    update_slice_dataset__dataset_uid__slice__slice_uid__put as update_slice_autogen,
)
from snorkelai.sdk.client_v3.tdm.models.modify_slice_request import (
    ModifySliceRequest,
)
from snorkelai.sdk.client_v3.tdm.models.slice_config import SliceConfig
from snorkelai.sdk.client_v3.tdm.models.slice_creation_request import (
    SliceCreationRequest,
)
from snorkelai.sdk.client_v3.tdm.models.slice_template_graph import (
    SliceTemplateGraph as GenSliceTemplateGraph,
)
from snorkelai.sdk.client_v3.tdm.models.slice_template_graph_templates_item import (
    SliceTemplateGraphTemplatesItem,
)
from snorkelai.sdk.client_v3.tdm.models.update_slice_request import (
    UpdateSliceRequest,
)
from snorkelai.sdk.client_v3.tdm.types import Unset
from snorkelai.sdk.client_v3.utils import IdType, get_dataset_uid
from snorkelai.sdk.develop.base import Base

logger = getLogger(__name__)


def _get_template_graph_from_slice_config(
    slice_config: Optional[SliceConfig],
) -> GenSliceTemplateGraph:
    if slice_config is None or isinstance(slice_config, Unset):
        return GenSliceTemplateGraph(templates=[], graph=[])

    transform_config = getattr(slice_config, "transform_config", {})
    transform_type = getattr(slice_config, "transform_type", "")
    slice_config_dict = {
        "transform_config": transform_config,
        "transform_type": transform_type,
    }
    return GenSliceTemplateGraph(
        templates=[SliceTemplateGraphTemplatesItem.from_dict(slice_config_dict)],
        graph=["$AND", 0],
    )


def _convert_templates_to_slice_config_templates_item(
    templates: Sequence[Union[Dict, SliceTemplateGraphTemplatesItem]],
) -> List[SliceTemplateGraphTemplatesItem]:
    """Convert a dictionary template to a SliceTemplateGraphTemplatesItem to make sure templates are of SliceTemplateGraphTemplatesItem."""
    if templates is None:
        return []
    return [
        (
            SliceTemplateGraphTemplatesItem.from_dict(template)
            if isinstance(template, dict)
            else template
        )
        for template in templates
    ]


@final
class Slice(Base):
    """
    Represents a slice within a Snorkel dataset for identifying and managing subsets of datapoints.

    A slice is a logical subset of datapoints within a dataset that can be created either manually
    by adding specific datapoints, or programmatically using slicing functions defined through
    templates and configurations. Slices are essential for data analysis, model evaluation,
    and targeted data operations within Snorkel workflows.

    Key capabilities:

    - Manual datapoint management through add/remove operations
    - Programmatic datapoint identification using configurable slicing functions

    This class provides methods for creating, retrieving, updating, and managing slice membership.
    Slice objects should not be instantiated directly - use the ``create()`` or ``get()``
    class methods instead.

    Read more in `Using data slices <https://docs.snorkel.ai/docs/user-guide/data-management/using-data-slices>`_.

    Using the ``Slice`` class requires the following import:

    .. testcode::

        from snorkelai.sdk.develop import Slice
    """

    def __init__(
        self,
        dataset: IdType,
        slice_uid: int,
        name: str,
        description: Optional[str] = None,
        templates: Optional[List[Dict[str, Any]]] = None,
        graph: Optional[List[Any]] = None,
    ):
        """Create a Slice object in-memory with necessary properties.
        This constructor should not be called directly, and should instead be accessed
        through the ``create()`` and ``get()`` methods

        Parameters
        ----------
        dataset
            The UID or name for the dataset within Snorkel
        slice_uid
            The UID for the slice within Snorkel
        name
            The name of the slice
        description
            The description of the slice
        templates
            Configuration defining slicing functions for programmatic datapoint identification.
        graph
            A representation of the slicing function's structure.
        """
        self._dataset_uid = get_dataset_uid(dataset)
        self._slice_uid = slice_uid
        self._name = name
        self._description = description
        self._templates = templates
        self._graph = graph

    # ----------------------------------
    # SLICE PROPERTIES -- PRIVATE
    # ----------------------------------

    # These are all object properties because they shouldn't be set directly by the user

    @property
    def slice_uid(self) -> int:
        """Return the UID of the slice"""
        return self._slice_uid

    @property
    def uid(self) -> int:
        """Return the UID of the slice"""
        return self._slice_uid

    @property
    def dataset_uid(self) -> int:
        """Return the UID of the dataset that the slice belongs to"""
        return self._dataset_uid

    @property
    def name(self) -> str:
        """Return the name of the slice"""
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Return the description of the slice"""
        return self._description

    # -----------------------
    # SLICE OPERATIONS
    # -----------------------

    @classmethod
    def create(
        cls,
        dataset: IdType,
        name: str,
        description: str = "",
        templates: Optional[List[Dict[str, Any]]] = None,
        graph: Optional[List[Any]] = None,
    ) -> "Slice":
        """Creates a slice for a dataset.

        Slices are used to identify a subset of datapoints in a dataset.
        You can add datapoints to a slice manually, or if you define a config, you can add datapoints programmatically.
        Slice membership can contain both manual and programmatic identified datapoints.

        Parameters
        ----------
        dataset
            The UID or name for the dataset within Snorkel.
        name
            The name of the slice.
        description
            A description of the slice, by default the empty string.
        templates
            A list of template dictionaries, by default None, you can reference the schema in the ``template`` module for constructing
            these templates. These templates are used to define the Slicing Function for the slice,
            allowing it to programmatically add datapoints to the slice membership.
        graph
            A representation of the slicing function's structure, by default None.

        Returns
        -------
        Slice
            The slice object.

        Raises
        ------
        ValueError
            If the dataset doesn't exist or cannot be found by name/UID.
        ValueError
            If the slice name is a reserved name or already exists for the dataset.
        ValueError
            If there are other validation or server errors during slice creation.

        Examples
        --------
        Example 1
        ^^^^^^^^^

        Create a simple slice without templates:

        .. testcode::

            from snorkelai.sdk.develop import Slice
            slice = Slice.create(
                dataset=1,
                name="my_slice",
                description="A slice for testing purposes"
            )

        Example 2
        ^^^^^^^^^

        Create a slice from a keyword template. This example creates a slice containing all datapoints with the string ``capital`` in the ``Instruction`` field:

        .. testcode::

            from snorkelai.sdk.develop import Slice
            from snorkelai.sdk.utils.graph import DEFAULT_GRAPH
            from snorkelai.templates.keyword_template import KeywordTemplateSchema

            keyword_template = KeywordTemplateSchema(
                operator="CONTAINS",
                keywords=["capital"],
                field="Instruction",
                case_sensitive=False,
                tokenize=True,
            )
            template_config_dict = {
                **keyword_template.to_dict(),
                "template_type": "keyword"
            }
            slice = Slice.create(
                dataset=1,
                name="slice_name",
                description="description",
                templates=[
                    {
                        "transform_type": "dataset_template_filter",
                        "config": {
                            "transform_config_type": "template_filter_schema",
                            "filter_type": "text_template",
                            "filter_config_type": "dataset_text_template",
                            "dataset_uid": 1,
                            "template_config": template_config_dict,
                         },
                    },
                    ],
                graph=DEFAULT_GRAPH,
            )
        """
        dataset_uid = get_dataset_uid(dataset)
        body = SliceCreationRequest(
            dataset_uid=dataset_uid,
            display_name=name,
            description=description,
        )
        if templates:
            converted_templates = _convert_templates_to_slice_config_templates_item(
                templates
            )
            template_graph = GenSliceTemplateGraph(
                templates=converted_templates,
                graph=graph if graph is not None else [],
            )
            body.template_graph = template_graph

        try:
            slice_uid = create_slice_autogen(dataset_uid=dataset_uid, body=body)
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e

        slice_obj = cls.get(dataset=dataset, slice=slice_uid)
        print(
            f"Successfully created slice {slice_obj.name} with UID {slice_obj.slice_uid}."
        )
        return slice_obj

    @classmethod
    def get(cls, dataset: IdType, slice: IdType) -> "Slice":
        """Retrieves a slice by UID or name.

        Parameters
        ----------
        dataset
            The UID or name for the dataset within Snorkel.
        slice
            The UID or name of the slice.

        Returns
        -------
        Slice
            The slice object.

        Raises
        ------
        ValueError
            If no slice is found with the given UID or name.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            slice = Slice.get(dataset=1, slice=20)
        """
        if not slice:
            raise TypeError("Slice must be either a UID or a name")
        dataset_uid = get_dataset_uid(dataset)

        # TODO ENG-29964 add a get request for slice_uid
        slice_resp = get_slices_autogen(dataset_uid=dataset_uid)
        for s in slice_resp:
            if int(s.slice_uid) == slice or s.display_name == slice:
                slice_config = SliceConfig(**s.config.to_dict()) if s.config else None
                transform_graph = _get_template_graph_from_slice_config(slice_config)
                slice_obj = Slice(
                    slice_uid=int(s.slice_uid),
                    name=s.display_name,
                    dataset=dataset_uid,
                    description=s.description or "",
                    templates=(
                        [template.to_dict() for template in transform_graph.templates]
                        if transform_graph.templates is not None
                        else None
                    ),
                    graph=transform_graph.graph,
                )
                return slice_obj
        raise ValueError(f"Slice with name {slice} not found")

    @classmethod
    def list(
        cls,
        dataset: IdType,
    ) -> List["Slice"]:
        """Retrieves all slices for a dataset.

        Parameters
        ----------
        dataset
            The UID or name for the dataset within Snorkel.

        Returns
        -------
        List[Slice]
            A list of all the slices available for that dataset.

        Raises
        ------
        ValueError
            If no dataset is found with the given id.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            slices = Slice.list(dataset=1)
        """
        print(f"Retrieving slices for dataset {dataset}.")
        dataset_uid = get_dataset_uid(dataset)
        slice_resp = get_slices_autogen(dataset_uid=dataset_uid)

        def _to_template_graph_config(
            s_config: Optional[Union[Dict[str, Any], SliceConfig, Unset]]
        ) -> Optional[GenSliceTemplateGraph]:
            if not s_config or isinstance(s_config, Unset):
                return None
            if isinstance(s_config, SliceConfig):
                sc = s_config
            else:
                sc = SliceConfig(**s_config)
            tg = _get_template_graph_from_slice_config(sc)
            return tg

        result = []
        for slice in slice_resp:
            template_graph_config = _to_template_graph_config(slice.config)
            slice_obj = Slice(
                slice_uid=int(slice.slice_uid),
                name=slice.display_name,
                dataset=dataset_uid,
                description=slice.description or "",
                templates=(
                    [template.to_dict() for template in template_graph_config.templates]
                    if template_graph_config is not None
                    else None
                ),
                graph=(
                    template_graph_config.graph
                    if template_graph_config is not None
                    else None
                ),
            )
            result.append(slice_obj)
        return result

    def add_x_uids(self, x_uids: List[str]) -> None:
        """Adds datapoints to a slice.

        Parameters
        ----------
        x_uids
            List of UIDs of the datapoints you want to add to the slice.

        Raises
        ------
        Exception
            If other server errors occur during the operation.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            slice = Slice.get(dataset=1, slice=20)
            slice.add_x_uids(["uid1", "uid2", "uid3"])
        """
        try:
            add_xuids_autogen(
                dataset_uid=self.dataset_uid,
                slice_uid=self.slice_uid,
                body=ModifySliceRequest(x_uids=x_uids),
            )
            print(f"Successfully added {len(x_uids)} datapoints to slice {self.name}.")
        except HTTPError as e:
            raise Exception(e.response.json()["detail"]) from e

    def remove_x_uids(self, x_uids: List[str]) -> None:
        """Removes datapoints from a slice.

        Parameters
        ----------
        x_uids
            List of UIDs of the datapoints you want to remove from the slice.

        Raises
        ------
        Exception
            If other server errors occur during the operation.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            slice = Slice.get(dataset=1, slice=20)
            slice.remove_x_uids(["uid1", "uid2", "uid3"])
        """
        try:
            remove_xuids_autogen(
                dataset_uid=self.dataset_uid,
                slice_uid=self.slice_uid,
                body=ModifySliceRequest(x_uids=x_uids),
            )
            print(
                f"Successfully removed {len(x_uids)} datapoints from slice {self.name}."
            )
        except HTTPError as e:
            raise Exception(e.response.json()["detail"]) from e

    def get_x_uids(self) -> List[str]:
        """Retrieves the UIDs of the datapoints in the slice.

        Returns
        -------
        List[str]
            List of UIDs of the datapoints in the slice.

        Raises
        ------
        Exception
            If other server errors occur during the operation.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            slice = Slice.get(dataset=1, slice=20)
            x_uids = slice.get_x_uids()
        """
        try:
            slice_xuids = get_slice_membership_autogen(
                dataset_uid=self.dataset_uid,
                slice_uid=self.slice_uid,
            )
        except HTTPError as e:
            raise Exception(e.response.json()["detail"]) from e
        return slice_xuids

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        templates: Optional[List[Dict[str, Any]]] = None,
        graph: Optional[List[str]] = None,
    ) -> None:
        """Updates the slice properties.

        Parameters
        ----------
        name
            The new name for the slice, by default None.
        description
            The new description for the slice, by default None.
        templates
            A list of template dictionaries for the slice, by default None.
        graph
            A list of strings representing the graph structure for the slice, by default None.

        Raises
        ------
        ValueError
            If there are other errors during slice update.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            slice = Slice.get(dataset=1, slice=20)
            slice.update(name="new_name", description="updated description")
        """
        try:
            slice_model_dict: Dict[str, Any] = {
                "dataset_uid": self.dataset_uid,
                "display_name": name if name is not None else self.name,
                "description": cast(
                    Union[Unset, str],
                    description if description is not None else self.description,
                ),
            }

            if templates is not None:
                converted_templates = _convert_templates_to_slice_config_templates_item(
                    templates
                )
                slice_model_dict["template_graph"] = GenSliceTemplateGraph(
                    templates=converted_templates,
                    graph=graph if graph is not None else [],
                )

            # Create a SliceCreationRequest object
            slice_model = SliceCreationRequest(**slice_model_dict)

            update_request = UpdateSliceRequest(slice_=slice_model)
            updated_slice = update_slice_autogen(
                dataset_uid=self.dataset_uid,
                slice_uid=self.slice_uid,
                body=update_request,
            )

            if name is not None:
                self._name = name
            if description is not None:
                self._description = description
            if not isinstance(updated_slice.config, Unset):
                template_graph = _get_template_graph_from_slice_config(
                    updated_slice.config
                )
                self._templates = (
                    [template.to_dict() for template in template_graph.templates]
                    if template_graph.templates is not None
                    else None
                )
                self._graph = template_graph.graph

        except HTTPError as e:
            msg = "Failed to update slice"
            logger.exception(msg)
            raise ValueError(msg) from e

    @classmethod
    def delete(cls, dataset: IdType, slice_uid: int) -> None:
        """Deletes a slice from a dataset.

        Parameters
        ----------
        dataset
            The UID or name for the dataset within Snorkel.
        slice_uid
            The UID of the slice to delete.

        Raises
        ------
        ValueError
            If the dataset or slice doesn't exist or cannot be found by UID.
        ValueError
            If there are other validation or server errors during slice deletion.

        Example
        -------
        .. testcode::

            from snorkelai.sdk.develop import Slice
            Slice.delete(dataset=1, slice_uid=20)
        """
        dataset_uid = get_dataset_uid(dataset)
        try:
            delete_slice_autogen(
                dataset_uid=dataset_uid,
                slice_uid=slice_uid,
            )
            print(f"Successfully deleted slice with UID {slice_uid}.")
        except HTTPError as e:
            raise ValueError(e.response.json()["detail"]) from e
