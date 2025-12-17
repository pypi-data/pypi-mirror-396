from datetime import datetime

import requests

from .. import adaboard
from ..utils import validate_acl, validate_volume_mount

PRIVILEGED_ROLES = ["Curator", "PlatformAdmin"]
ALLOWED_CONTAINER_KEYS = [
    "command",
    "environment_variables",
    "max_cpu",
    "max_ram",
    "metadata_id",
    "min_cpu",
    "min_ram",
    "port",
    "volume_mounts",
    "is_primary",
]
ALLOWED_LOG_SOURCES = ["container", "system"]
LOG_SOURCES = {"container": False, "system": True}


def delete_app(app_id: str) -> None:
    """
    Delete a deployed app from AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/delete_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    """

    adaboard.request_adaboard(path=f"apps/{app_id}/", method=requests.delete)
    return None


def deploy_app(
    name: str,
    description: str,
    metadata_id: int,
    url_path_prefix: str,
    stripped_prefix: bool = True,
    port: int = 80,
    environment_variables: dict = {},
    max_cpu: float = 1.0,
    min_cpu: float = 0.0,
    max_ram: int = 500,
    min_ram: int = 20,
    command: str = "",
    acl_type: str = "public",
    acl_list: list[str] = None,
    idp_enabled: bool = False,
    idp_scope: str = "",
    maintainers: list[str] = [],
    volume_mounts: list[dict[str,]] = [],
) -> str:
    """
    Deploy a single-container app to AdaLab from an existing metadata object.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/deploy_app.ipynb) to test this function or build upon it.

    :param name: the app's name
    :type name: str
    :param description: the app's description
    :type description: str
    :param metadata_id: the metadata ID of the container image
    :type metadata_id: int
    :param url_path_prefix: URL endpoint to deploy the app to
    :type url_path_prefix: str
    :param stripped_prefix: whether to strip the apps/{app_url} prefix from the URL, defaults to True
    :type stripped_prefix: bool, optional
    :param port: port to expose the app on, defaults to 80
    :type port: int, optional
    :param environment_variables: environment variables for the container, defaults to {}. Each entry must follow the format {"key": value}
    :type environment_variables: dict, optional
    :param max_cpu: maximum CPU usage allowed (vCPU), defaults to 1.0
    :type max_cpu: float, optional
    :param min_cpu: minimum CPU usage allowed (vCPU), defaults to 0.0
    :type min_cpu: float, optional
    :param max_ram: maximum RAM usage allowed (Mb), defaults to 500
    :type max_ram: int, optional
    :param min_ram: minimum RAM usage allowed (Mb), defaults to 20
    :type min_ram: int, optional
    :param command: command to start up the container, defaults to ""
    :type command: str, optional
    :param acl_type: type of access control list, defaults to "public"
    :type acl_type: str, optional
    :param acl_list: list of users or groups allowed to access the app when acl_type="userlist" or "grouplist", defaults to None. *Note: if acl_type is "userlist" or "grouplist", this parameter is required.*
    :type acl_list: list, optional
    :param idp_enabled: whether to enable IdP token in app headers, defaults to False
    :type idp_enabled: bool, optional
    :param idp_scope: IdP token scope, defaults to ""
    :type idp_scope: str, optional
    :param maintainers: list of users allowed to edit the app, defaults to []
    :type maintainers: list, optional
    :param volume_mounts: list of volume mounts for the container, defaults to []
    :type volume_mounts: list, optional
    :return: the app's ID
    :rtype: str
    """

    # Check that the app configuration is valid
    validate_acl("app", False, acl_type)
    for vm in volume_mounts:
        validate_volume_mount(volume_mount=vm)

    # Build the payload for the request
    payload = {
        "name": name,
        "description": description,
        "containers": [
            {
                "command": command,
                "environment_variables": [
                    {"key": k, "value": v}
                    for k, v in environment_variables.items()
                ],
                "max_cpu": max_cpu,
                "max_ram": max_ram,
                "metadata_id": metadata_id,
                "min_cpu": min_cpu,
                "min_ram": min_ram,
                "port": port,
                "is_primary": True,
                "volume_mounts": volume_mounts,
            }
        ],
        "url_path_prefix": url_path_prefix,
        "acls": [
            {
                "acl_action": "app_open",
                "acl_type": acl_type or "public",
                "userlist": acl_list if acl_type == "userlist" else None,
                "grouplist": acl_list if acl_type == "grouplist" else None,
            }
        ],
        "idp_enabled": idp_enabled,
        "idp_scope": idp_scope,
        "maintainers": maintainers,
        "stripped_prefix": stripped_prefix,
    }

    # Deploy the app
    response = adaboard.request_adaboard(
        path="apps/deploy/", method=requests.post, json=payload
    ).json()

    # Return the ID of the deployed app
    return response["id"]


def deploy_multicontainer_app(
    name: str,
    description: str,
    containers: list[dict[str,]],
    url_path_prefix: str,
    acl_type: str = "public",
    acl_list: list[str] = None,
    idp_enabled: bool = False,
    idp_scope: str = "",
    maintainers: list[str] = [],
    stripped_prefix: bool = True,
) -> str:
    """
    Deploy a multi-container app to AdaLab from an existing metadata object.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/deploy_multicontainer_app.ipynb) to test this function or build upon it.

    :param name: the app's name
    :type name: str
    :param description: the app's description
    :type description: str
    :param containers: list of container configurations. Each container must have a "metadata_id" key and can have the following optional keys: "command", "environment_variables", "max_cpu", "max_ram", "min_cpu", "min_ram", "port". Each entry in "environment_variables" must follow the format {"key": value}
    :type containers: list
    :param url_path_prefix: URL endpoint to deploy the app to
    :type url_path_prefix: str
    :param acl_type: type of access control list, defaults to "public"
    :type acl_type: str, optional
    :param acl_list: list of users or groups allowed to access the app when acl_type="userlist" or "grouplist", defaults to None. *Note: if acl_type is "userlist" or "grouplist", this parameter is required.*
    :type acl_list: list, optional
    :param idp_enabled: whether to enable IdP token in app headers, defaults to False
    :type idp_enabled: bool, optional
    :param idp_scope: IdP token scope, defaults to ""
    :type idp_scope: str, optional
    :param maintainers: list of users allowed to edit the app, defaults to []
    :type maintainers: list, optional
    :param stripped_prefix: whether to strip the apps/{app_url} prefix from the URL, defaults to True
    :type stripped_prefix: bool, optional
    :return: the app's ID
    :rtype: str
    """

    # Check that the app configuration is valid
    validate_acl("app", False, acl_type)

    found_primary = False
    for container in containers:
        assert (
            "metadata_id" in container
        ), "Metadata ID of the container is required."
        assert "is_primary" in container, "Primary container flag is required."
        if container["is_primary"]:
            assert not found_primary, "Only one primary container is allowed."
            found_primary = True

        for key in container.keys():
            assert (
                key in ALLOWED_CONTAINER_KEYS
            ), f"Invalid container parameter key: {key}. Allowed keys are {', '.join(ALLOWED_CONTAINER_KEYS)}."

        for vm in container.get("volume_mounts", []):
            validate_volume_mount(volume_mount=vm)

    # Build the payload for the request
    payload = {
        "name": name,
        "description": description,
        "url_path_prefix": url_path_prefix,
        "stripped_prefix": stripped_prefix,
        "acls": [
            {
                "acl_action": "app_open",
                "acl_type": acl_type or "public",
                "userlist": acl_list if acl_type == "userlist" else None,
                "grouplist": acl_list if acl_type == "grouplist" else None,
            }
        ],
        "idp_enabled": idp_enabled,
        "idp_scope": idp_scope,
        "maintainers": maintainers,
    }

    for container in containers:
        container["environment_variables"] = [
            {"key": k, "value": v}
            for k, v in container.get("environment_variables", {}).items()
        ]

    payload["containers"] = containers

    # Deploy the app
    response = adaboard.request_adaboard(
        path="apps/deploy/", method=requests.post, json=payload
    ).json()

    # Return the ID of the deployed app
    return response["id"]


def edit_app(
    app_id: str,
    name: str = None,
    description: str = None,
    metadata_id: int = None,
    url_path_prefix: str = None,
    stripped_prefix: bool = None,
    port: int = None,
    environment_variables: dict = None,
    max_cpu: float = None,
    min_cpu: float = None,
    max_ram: int = None,
    min_ram: int = None,
    command: str = None,
    acl_type: str = None,
    acl_list: list[str] = None,
    idp_enabled: bool = None,
    idp_scope: str = None,
    maintainers: list[str] = None,
    volume_mounts: list[dict[str,]] = None,
) -> None:
    """
    Edit a single-container app's configuration.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/edit_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :param name: the app's name, defaults to None (old one)
    :type name: str, optional
    :param description: the app's description, defaults to None (old one)
    :type description: str, optional
    :param metadata_id: the ID of the metadata object, defaults to None (old one)
    :type metadata_id: int, optional
    :param url_path_prefix: URL endpoint to deploy the app to, defaults to None (old one)
    :type url_path_prefix: str, optional
    :param stripped_prefix: whether to strip the apps/{app_url} prefix from the URL, defaults to None (old one)
    :type stripped_prefix: bool, optional
    :param port: the port where the app is served from, defaults to None (old one)
    :type port: int, optional
    :param replicas: number of replicas to deploy, defaults to None (old one)
    :type replicas: int, optional
    :param environment_variables: environment variables to pass to the app, defaults to None (old one)
    :type environment_variables: dict, optional
    :param max_cpu: maximum CPU usage allowed (vCPU), defaults to None (old one)
    :type max_cpu: float, optional
    :param min_cpu: minimum CPU usage allowed (vCPU), defaults to None (old one)
    :type min_cpu: float, optional
    :param max_ram: maximum RAM usage allowed (Mb), defaults to None (old one)
    :type max_ram: int, optional
    :param min_ram: minimum RAM usage allowed (Mb), defaults to None (old one)
    :type min_ram: int, optional
    :param command: command to start up the app, defaults to None (old one)
    :type command: str, optional
    :param acl_type: type of access control list, defaults to None (old one)
    :type acl_type: str, optional
    :param acl_list: list of users or groups allowed to access the app when acl_type="userlist" or "grouplist", defaults to None
    :type acl_list: list, optional
    :param idp_enabled: whether to enable IdP token in app headers, defaults to None (old one)
    :type idp_enabled: bool, optional
    :param idp_scope: IdP token scope, defaults to None (old one)
    :type idp_scope: str, optional
    :param maintainers: list of users allowed to edit the app, defaults to None (old one)
    :type maintainers: list, optional
    :param volume_mounts: list of volume mounts for the container, defaults to []
    :type volume_mounts: list, optional
    :return: nothing
    :rtype: None
    """

    # Collect configuration options
    environment_variables = environment_variables or dict()
    validate_acl("app", True, acl_type)

    if volume_mounts is not None:
        for vm in volume_mounts:
            validate_volume_mount(volume_mount=vm)

    if acl_type in ["userlist", "grouplist"]:
        assert (
            acl_list is not None
        ), "ACL type is userlist or grouplist but acl_list was not specified."

    acls = None
    if acl_type is not None:
        acls = [
            {
                "acl_action": "app_open",
                "acl_type": acl_type,
                "userlist": acl_list if acl_type == "userlist" else None,
                "grouplist": acl_list if acl_type == "grouplist" else None,
            }
        ]

    app_config = {
        "name": name,
        "description": description,
        "containers": [
            {
                "command": command,
                "environment_variables": (
                    [
                        {"key": k, "value": v}
                        for k, v in environment_variables.items()
                    ]
                    or None
                ),
                "max_cpu": max_cpu,
                "max_ram": max_ram,
                "metadata_id": metadata_id,
                "min_cpu": min_cpu,
                "min_ram": min_ram,
                "port": port,
                "is_primary": True,
                "volume_mounts": volume_mounts,
            }
        ],
        "url_path_prefix": url_path_prefix,
        "acls": acls,
        "idp_enabled": idp_enabled,
        "idp_scope": idp_scope,
        "maintainers": maintainers,
        "stripped_prefix": stripped_prefix,
    }

    # Fetch old configuration
    old_config = adaboard.request_adaboard(
        path=f"apps/{app_id}/info/", method=requests.get
    ).json()

    # Build request payload combining new and old options
    containers = [
        {
            k: v if v is not None else old_config["containers"][0][k]
            for k, v in app_config["containers"][0].items()
        }
    ]
    payload = {
        k: v if v is not None else old_config[k] for k, v in app_config.items()
    }
    payload["containers"] = containers

    adaboard.request_adaboard(
        path=f"apps/{app_id}/update/", method=requests.put, json=payload
    )

    return None


def edit_multicontainer_app(
    app_id: str,
    name: str = None,
    description: str = None,
    containers: list[dict[str,]] = None,
    url_path_prefix: str = None,
    acl_type: str = None,
    acl_list: list[str] = None,
    idp_enabled: bool = None,
    idp_scope: str = None,
    stripped_prefix: bool = None,
) -> None:
    """
    Edit a multi-container app's configuration.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/edit_multicontainer_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :param name: the app's name, defaults to None (old one)
    :type name: str, optional
    :param description: the app's description, defaults to None (old one)
    :type description: str, optional
    :param containers: list of container configurations, defaults to None (old one)
    :type containers: list, optional
    :param url_path_prefix: URL endpoint to deploy the app to, defaults to None (old one)
    :type url_path_prefix: str, optional
    :param acl_type: type of access control list, defaults to None (old one)
    :type acl_type: str, optional
    :param acl_list: list of users or groups allowed to access the app when acl_type="userlist" or "grouplist", defaults to None (old one)
    :type acl_list: list, optional
    :param idp_enabled: whether to enable IdP token in app headers, defaults to None (old one)
    :type idp_enabled: bool, optional
    :param idp_scope: IdP token scope, defaults to None (old one)
    :type idp_scope: str, optional
    :param stripped_prefix: whether to strip the apps/{app_url} prefix from the URL, defaults to None (old one)
    :type stripped_prefix: bool, optional
    :return: nothing
    :rtype: None
    """
    validate_acl("app", True, acl_type)
    if acl_type in ["userlist", "grouplist"]:
        assert (
            acl_list is not None
        ), "ACL type is userlist or grouplist but acl_list was not specified."

    acls = None
    if acl_type is not None:
        acls = [
            {
                "acl_action": "app_open",
                "acl_type": acl_type,
                "userlist": acl_list if acl_type == "userlist" else None,
                "grouplist": acl_list if acl_type == "grouplist" else None,
            }
        ]

    # Collect configuration options
    app_config = {
        "name": name,
        "description": description,
        "containers": containers,
        "url_path_prefix": url_path_prefix,
        "acls": acls,
        "idp_enabled": idp_enabled,
        "idp_scope": idp_scope,
        "stripped_prefix": stripped_prefix,
    }

    # Check that the container configurations are valid
    if containers:
        found_primary = False
        for container in containers:
            assert (
                "metadata_id" in container
            ), "Metadata ID of the container is required."
            assert (
                "is_primary" in container
            ), "Primary container flag is required."
            if container["is_primary"]:
                assert (
                    not found_primary
                ), "Only one primary container is allowed."
                found_primary = True

            for key in container.keys():
                assert (
                    key in ALLOWED_CONTAINER_KEYS
                ), f"Invalid container parameter key: {key}. Allowed keys are {', '.join(ALLOWED_CONTAINER_KEYS)}."

            for vm in container.get("volume_mounts", []):
                validate_volume_mount(volume_mount=vm)

            container["environment_variables"] = [
                {"key": k, "value": v}
                for k, v in container.get(
                    "environment_variables", dict()
                ).items()
            ]

    # Fetch old configuration
    old_config = adaboard.request_adaboard(
        path=f"apps/{app_id}/info/", method=requests.get
    ).json()
    payload = {
        k: v if v is not None else old_config[k] for k, v in app_config.items()
    }
    adaboard.request_adaboard(
        path=f"apps/{app_id}/update/", method=requests.put, json=payload
    )

    return None


def get_all_apps() -> (
    list[dict[str, str | int | bool | dict[str, str] | list[str]]]
):
    """
    Get information for all the apps deployed in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_all_apps.ipynb) to test this function or build upon it.

    :return: list with all the information of each app
    :rtype: list
    """

    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response = adaboard.request_adaboard(
        path="apps/all/", method=requests.get, params={"all": include_all}
    ).json()

    return response


def get_app(
    app_id: str,
) -> dict[str, str | int | bool | dict[str, str] | list[str]]:
    """
    Get the information of a specific deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: app's information
    :rtype: dict
    """

    response = adaboard.request_adaboard(
        path=f"apps/{app_id}/info/", method=requests.get
    ).json()

    return response


def get_app_id(
    app_name: str = "", author_id: str = "", app_url: str = ""
) -> str:
    """
    Get the ID of a deployed app in AdaLab. Either app_url, or app_name and author_id, must be specified.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_app_id.ipynb) to test this function or build upon it.

    :param app_name: name of the app, defaults to ""
    :type app_name: str, optional
    :param author_id: author of the app, defaults to ""
    :type author_id: str, optional
    :param app_url: endpoint of the app's URL, defaults to ""
    :type app_url: str, optional
    :return: the app's ID
    :rtype: str
    """

    # Check that enough information is provided to find the app
    assert (
        app_name and author_id
    ) or app_url, (
        "Either app_url, or app_name and author_id, must be specified."
    )
    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response = adaboard.request_adaboard(
        path="apps/all/", method=requests.get, params={"all": include_all}
    ).json()

    # Return the ID of the requested app
    try:
        if app_url:
            return [
                app["app_id"]
                for app in response
                if app["url_path_prefix"] == app_url
            ][0]
        else:
            return [
                app["app_id"]
                for app in response
                if app["name"] == app_name and app["user_id"] == author_id
            ][0]
    except IndexError:
        raise ValueError("No app found with the specified parameters.")


def get_app_logs(
    app_id: str,
    container_image_name: str = "",
    container_metadata_id: int = 0,
    container_primary: bool = True,
    container_idx: int = 0,
    from_date: str = "",
    to_date: str = "",
    source: str = "container",
) -> str | list[dict[str, str]]:
    """
    Get the container or system logs of a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_app_logs.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :param container_image_name: name of the container image to get logs from
    :type container_image_name: str, optional
    :param container_metadata_id: the metadata ID of the container image to get logs from, defaults to 0
    :type container_metadata_id: int, optional
    :param container_primary: whether to get logs from the primary container, defaults to True
    :type container_primary: bool, optional
    :param container_idx: index of the container to get logs from, defaults to 0
    :type container_idx: int, optional
    :param from_date: start date for the logs, defaults to ""
    :type from_date: str, optional
    :param to_date: end date for the logs, defaults to ""
    :type to_date: str, optional
    :param source: source of the logs, either "container" or "system", defaults to "container"
    :type source: str, optional
    :return: deployment logs
    :rtype: str
    """

    assert (
        source in ALLOWED_LOG_SOURCES
    ), f"Log source must be one of {', '.join([x for x in ALLOWED_LOG_SOURCES])}."
    assert not (
        container_image_name and container_metadata_id and container_idx
    ), "Either container image name, container metadata ID or index must be specified."
    assert not (
        container_image_name and container_metadata_id
    ), "Only one container image identifier allowed."

    # If container name provided, get the index in the app
    if container_image_name and not container_primary:
        tmp = get_app(app_id)
        app_mdata_id = [
            container["metadata_id"] for container in tmp["containers"]
        ]
        imgs = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": False}
        ).json()
        img_names = [
            {"name": img["name"], "metadata_id": img["metadata_id"]}
            for img in imgs
            if img["name"] == container_image_name
        ]
        cnt_mdata_id = [
            img["metadata_id"]
            for img in img_names
            if img["metadata_id"] in app_mdata_id
        ]
        assert not (len(cnt_mdata_id) == 0), "Container not found in app."
        assert not (
            len(cnt_mdata_id) > 1
        ), "Multiple container images found with the same name."
        container_idx = [
            idx
            for idx, cnt in enumerate(tmp["containers"])
            if cnt["metadata_id"] in cnt_mdata_id
        ][0]

    if container_metadata_id and not container_primary:
        tmp = get_app(app_id)
        app_mdata_id = [
            container["metadata_id"] for container in tmp["containers"]
        ]
        cnt_mdata_id = [
            idx
            for idx, x in enumerate(app_mdata_id)
            if x == container_metadata_id
        ]
        assert not (len(cnt_mdata_id) == 0), "Container not found in app."
        assert not (
            len(cnt_mdata_id) > 1
        ), "Multiple containers found with the same container image metadata ID."
        container_idx = cnt_mdata_id[0]

    if container_primary:
        tmp = get_app(app_id=app_id)
        for idx, container in enumerate(tmp["containers"]):
            if container["is_primary"]:
                container_idx = idx
                break

    params = {"container_idx": container_idx, "system": LOG_SOURCES[source]}

    # Check that the date format is correct and update the request
    if from_date:
        try:
            datetime.fromisoformat(from_date)
        except ValueError:
            raise AssertionError(
                "Date must be in ISO format (YYYY-MM-DDTHH:mm:ss+HH:mm)."
            )
        params["start_dt"] = from_date
    if to_date:
        try:
            datetime.fromisoformat(to_date)
        except ValueError:
            raise AssertionError(
                "Date must be in ISO format (YYYY-MM-DDTHH:mm:ss+HH:mm)."
            )
        params["end_dt"] = to_date

    response = adaboard.request_adaboard(
        path=f"apps/v2/{app_id}/logs", method=requests.get, params=params
    ).json()

    return response


def get_apps_by_author(
    author_id: str,
) -> list[dict[str, str | int | bool | dict[str, str] | list[str]]]:
    """
    Get information for all the apps deployed in AdaLab by a specific author.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_apps_by_author.ipynb) to test this function or build upon it.

    :param author_id: the ID of the app's author
    :type author_id: str
    :return: list with all the information of each app
    :rtype: list
    """

    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response = adaboard.request_adaboard(
        path="apps/all/", method=requests.get, params={"all": include_all}
    ).json()

    return [app for app in response if app["user_id"] == author_id]


def get_apps_status() -> dict[str, str]:
    """
    Get the status of all the apps deployed in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_apps_status.ipynb) to test this function or build upon it.

    :return: dictionary with the status of each app
    :rtype: dict
    """

    # Get status report for all apps
    response_stats = adaboard.request_adaboard(
        path="apps/status/", method=requests.get
    ).json()

    # If the user is privileged enough, get all apps
    response_roles = adaboard.request_adaboard(path="users/self").json()
    include_all = any(
        role in PRIVILEGED_ROLES
        for role in response_roles["roles"]["adaboard"]
    )
    # Get the list of all apps
    response_apps = adaboard.request_adaboard(
        path="apps/all/", method=requests.get, params={"all": include_all}
    ).json()

    # Build dictionary with the status of each app
    apps_status = [
        {
            "name": app["name"],
            "author": app["user_id"],
            "URL": app["url_path_prefix"],
            "status": response_stats[str(app["status"])],
        }
        for app in response_apps
    ]
    return apps_status


def get_container_idx(app_id: str, metadata_id: int) -> int:
    """Get the index of a specific container of a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/get_container_idx.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :param metadata_id: the metadata ID of the container
    :type metadata_id: int
    :return: the index of the container in the app
    :rtype: int
    """

    response = adaboard.request_adaboard(
        path=f"apps/{app_id}/info/", method=requests.get
    ).json()

    for idx, container in enumerate(response["containers"]):
        if container["metadata_id"] == metadata_id:
            return idx

    assert False, "No container found with the specified metadata ID."


def restart_app(app_id: str) -> None:
    """
    Restart a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/restart_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"apps/{app_id}/restart/", method=requests.put
    )
    return None


def start_app(app_id: str) -> None:
    """
    Start a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/start_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"apps/{app_id}/start/", method=requests.put
    )

    return None


def stop_app(app_id: str) -> None:
    """
    Stop a deployed app in AdaLab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/apps/stop_app.ipynb) to test this function or build upon it.

    :param app_id: the app's ID
    :type app_id: str
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(path=f"apps/{app_id}/stop/", method=requests.put)
    return None
