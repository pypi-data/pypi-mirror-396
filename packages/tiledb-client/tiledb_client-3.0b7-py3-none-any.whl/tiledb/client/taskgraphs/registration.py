import json
from typing import Any, Dict, Optional, Union

import urllib3

import tiledb
from tiledb.client import assets
from tiledb.client import client
from tiledb.client import rest_api
from tiledb.client._common import json_safe
from tiledb.client._common import utils
from tiledb.client.taskgraphs import builder
from tiledb.client.teamspaces import Teamspace


class TaskGraphError(tiledb.TileDBError):
    """Raised when a task graph can not be registered, retrieved, or executed."""


class TaskGraphRegistrar(assets._AssetCreator):
    """Registers a task graph to a path or to a folder.

    The asset creation pattern is implemented in the base class.

    """

    def __init__(self):
        super().__init__(
            client.build(
                rest_api.RegisteredTaskGraphsApi
            ).register_registered_task_graph
        )

    def call_api_method(self, workspace, teamspace, path, request):
        """Adapt arguments for the underlying API method."""
        self.api_method(
            workspace,
            teamspace,
            path,
            graph=json_safe.Value(request),
        )


def register(
    graph: builder.TaskGraphBuilder,
    path: Union[object, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Registers the graph constructed by the TaskGraphBuilder.

    Parameters
    ----------
    graph : TaskGraphBuilder
        The graph to be registered.
    path : str or object
        The TileDB path at which the object is to be registered. May be
        a path relative to a teamspace, a `Folder` or `Asset` instance,
        or an absolute "tiledb" URI. If the path to a folder is
        provided, the name of the function will be appended to form
        a full asset path.
    teamspace : Teamspace or str, optional
        The teamspace to which the object will be registered, specified
        by object or id. If not provided, the `path` parameter is
        queried for a teamspace id.

    """
    teamspace_id, path_id = assets._normalize_ids(teamspace, path)
    registrar = TaskGraphRegistrar()
    try:
        registrar.create(
            path_id,
            teamspace_id,
            graph._tdb_to_json(graph.name),
            graph.name,
        )
    except assets.AssetCreatorError as exc:
        raise TaskGraphError("Failed to register task graph.") from exc


def load(
    path: Union[object, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> Dict[str, Any]:
    """Retrieves a task graph from the server.

    Parameters
    ----------
    path : str or object
        The TileDB path at which the object is registered. May be
        a path relative to a teamspace, an `Asset` instance,
        or an absolute "tiledb" URI.
    teamspace : Teamspace or str, optional
        The teamspace to which the object is registered, specified
        by object or id. If not provided, the `path` parameter is
        queried for a teamspace id.

    Returns
    -------
    dict
        A representation of a task graph.

    """
    teamspace_id, path_id = assets._normalize_ids(teamspace, path)
    api_client = client.build(rest_api.RegisteredTaskGraphsApi)

    result: urllib3.HTTPResponse = api_client.get_registered_task_graph(
        client.get_workspace_id(),
        teamspace_id,
        path_id,
        _preload_content=False,
    )
    try:
        return json.loads(result.data)
    finally:
        utils.release_connection(result)


def update(
    graph: builder.TaskGraphBuilder,
    path: Union[object, str],
    *,
    teamspace: Optional[Union[Teamspace, str]] = None,
) -> None:
    """Updates a registered task graph.

    Parameters
    ----------
    graph : TaskGraphBuilder
        The replacement graph.
    path : str or object
        The TileDB path at which the object is registered. May be
        a path relative to a teamspace, an `Asset` instance,
        or an absolute "tiledb" URI.
    teamspace : Teamspace or str, optional
        The teamspace to which the object is registered, specified
        by object or id. If not provided, the `path` parameter is
        queried for a teamspace id.

    """
    teamspace_id, path_id = assets._normalize_ids(teamspace, path)
    api_client = client.build(rest_api.RegisteredTaskGraphsApi)
    api_client.update_registered_task_graph(
        client.get_workspace_id(),
        teamspace_id,
        path_id,
        graph=json_safe.Value(graph._tdb_to_json()),
    )
