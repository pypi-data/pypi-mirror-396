import requests
from adalib_auth import config, keycloak

from .. import adaboard

ALLOWED_OCI_PROJECT_TYPES = [
    "adamatics",
    "apps",
    "base_images",
    "kernels",
    "labapps",
]
ALLOWED_METADATA_TYPES = ["app", "base", "internal", "kernel", "lab_app"]

ALLOWED_OCI_SOURCE_TYPES_OPERATIONS = {"lab": "push", "registry": "copy"}
ALLOWED_PUBLISH_LOG_SOURCES = ["publish", "system"]
HARBOR_HOST = "container-registry"
HARBOR_PORT = "80"


def archive_image(metadata_id: int) -> None:
    """
    Archive an image in the Harbor registry. This will archive the OCI image metadata object and works as a soft delete.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/archive_image.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :return: nothing
    :rtype: None
    """

    # Check if image is already archived
    img_metadata = adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}",
    ).json()
    # If not archived, archive it
    if not img_metadata["archived"]:
        payload = {"archived": True}
        adaboard.request_adaboard(
            path=f"registry/metadata/{metadata_id}/archive",
            method=requests.put,
            json=payload,
        )
        return None
    else:
        raise RuntimeError(
            f"Image with metadata ID {metadata_id} is already archived."
        )


def create_image_metadata(
    source_type: str,
    source_repository: str,
    source_tag: str,
    project_name: str,
    repository_name: str,
    tag: str,
    type_id: str,
    name: str,
    description: str,
    username: str,
    cmd: str = "",
    picture_id=1,
) -> dict[str, str | int | bool | dict[str, str]]:
    """
    Create metadata for a specific image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/create_image_metadata.ipynb) to test this function or build upon it.

    :param source_type: the location where the source image is to be pulled from
    :type source_type: str
    :param source_repository: the name of the repository of the source image
    :type source_repository: str
    :param source_tag: the tag of the source image
    :type source_tag: str
    :param project_name: the name of the target project for the image metadata
    :type project_name: str
    :param repository_name: the name of the target repository for the image metadata
    :type: repository_name: str
    :param tag: the tag for the target image metadata
    :type tag: str
    :param type_id: the type of the image
    :type type_id: str
    :param name: the name for the target image metadata
    :type name: str
    :param description: the description for the target image metadata
    :type description: str
    :param username: the current username (tip: check "LOGNAME" environment variable)
    :type username: str
    :param cmd: the startup command for the target image metadata, defaults to ""
    :type cmd: str, optional
    :param picture_id: the ID of the picture for the image, defaults to 1
    :type picture_id: int, optional

    :return: image metadata
    :rtype: dict
    """
    # TODO fix the use of environmental variables here
    adalib_config = config.get_config()

    # Make sure container options are valid
    assert (
        project_name in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only create metadata for images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"
    assert (
        type_id in ALLOWED_METADATA_TYPES
    ), f"Can only create metadata of the type {', '.join([x for x in ALLOWED_METADATA_TYPES])}"
    assert source_type in list(
        ALLOWED_OCI_SOURCE_TYPES_OPERATIONS.keys()
    ), f"""Can only create metadata for images located in {', '.join([x for x in list(
        ALLOWED_OCI_SOURCE_TYPES_OPERATIONS.keys()
    )])}"""

    # Create metadata object in AdaLab
    payload = {
        "sha256": "sha256:00000",
        "oci_image_name": {
            "project": project_name,
            "repository": repository_name,
            "tag": tag,
            "host": f"{HARBOR_HOST}:{HARBOR_PORT}",
        },
        "type": type_id,
        "name": name,
        "description": description,
        "startup_cmd": cmd,
        "image_id": picture_id,
    }

    response_metadata = adaboard.request_adaboard(
        path="registry/metadata", method=requests.post, json=payload
    ).json()

    # Build request payload based on user and default options
    source_project = f"{project_name}_temp"

    payload = {
        "script": "pusher",
        "user_id": username,
        "pool": "internal",
        "cleanup": True,
        "timeout": 3600,
        "run_in_isolation": False,
        "start_podman_sidecar": False,
        "config": {
            "ADABOARD_API_URL": {
                "value": adalib_config.SERVICES["adaboard-api"]["external"],
                "real_value": adalib_config.SERVICES["adaboard-api"][
                    "external"
                ],
            },
            "CONTAINER_METADATA_ID": {
                "value": response_metadata["metadata_id"],
                "real_value": response_metadata["metadata_id"],
            },
            "HARBOR_HOST": {
                "value": HARBOR_HOST,
                "real_value": HARBOR_HOST,
            },
            "HARBOR_NAMESPACE": {
                "value": adalib_config.NAMESPACE,
                "real_value": adalib_config.NAMESPACE,
            },
            "HARBOR_TARGET_PROJECT": {
                "value": response_metadata["oci_image_name"]["project"],
                "real_value": response_metadata["oci_image_name"]["project"],
            },
            "HARBOR_TARGET_REPOSITORY_NAME": {
                "value": response_metadata["oci_image_name"]["repository"],
                "real_value": response_metadata["oci_image_name"][
                    "repository"
                ],
            },
            "HARBOR_TARGET_TAG": {
                "value": response_metadata["oci_image_name"]["tag"],
                "real_value": response_metadata["oci_image_name"]["tag"],
            },
            "KEEP_IMAGES": {"value": True, "real_value": True},
            "NETWORK_HOST": {
                "value": adalib_config.NETWORK_HOST,
                "real_value": adalib_config.NETWORK_HOST,
            },
            "OPERATION": {
                "value": ALLOWED_OCI_SOURCE_TYPES_OPERATIONS[source_type],
                "real_value": ALLOWED_OCI_SOURCE_TYPES_OPERATIONS[source_type],
            },
        },
    }
    if source_type.lower() == "lab":
        payload["config"]["RAW_SOURCE_IMAGE"] = {
            "value": f"{source_repository}:{source_tag}",
            "real_value": f"{source_repository}:{source_tag}",
        }
    elif source_type.lower() == "registry":
        payload["config"]["HARBOR_SOURCE_PROJECT"] = {
            "value": source_project,
            "real_value": source_project,
        }
        payload["config"]["HARBOR_SOURCE_REPOSITORY_NAME"] = {
            "value": source_repository,
            "real_value": source_repository,
        }
        payload["config"]["HARBOR_SOURCE_TAG"] = {
            "value": source_tag,
            "real_value": source_tag,
        }

    # Push image from a source to a target repo in Harbor
    adaboard.request_adaboard(
        path="script_runner/runs/start/", method=requests.post, json=payload
    ).json()

    return adaboard.request_adaboard(
        path=f"registry/metadata/{response_metadata['metadata_id']}",
    ).json()


def edit_image_metadata(
    metadata_id: int,
    new_name: str = "",
    new_description: str = "",
    new_cmd: str = "",
    new_run_id: int = 0,
    new_picture_id: int = 1,
) -> None:
    """
    Edit the metadata of an image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/edit_image_metadata.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :param new_name: the new name of the image, defaults to ""
    :type image_name: str, optional
    :param new_description: the new description of the image, defaults to ""
    :type new_description: str, optional
    :param new_cmd: the new startup command of the image, defaults to ""
    :type new_cmd: str, optional
    :param new_run_id: the new run ID of the image, defaults to 0
    :type new_run_id: int, optional
    :param new_picture_id: the ID of the new picture of the image, defaults to 1
    :type new_picture_id: int, optional
    :return: nothing
    :rtype: None
    """

    # Build request payload based on new and old options
    old_metadata = adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}",
    ).json()

    if not new_name:
        new_name = old_metadata["name"]
    if not new_description:
        new_description = old_metadata["description"]
    if not new_cmd:
        new_cmd = old_metadata["startup_cmd"]
    if not new_run_id:
        new_run_id = old_metadata["run_id"]
    if not new_picture_id:
        new_picture_id = old_metadata["image_id"]

    payload = {
        "name": new_name,
        "description": new_description,
        "startup_cmd": new_cmd,
        "run_id": new_run_id,
        "image_id": new_picture_id,
    }

    # Edit metadata
    adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}",
        method=requests.put,
        json=payload,
    )

    return None


def get_all_metadata(
    include_archived: bool = False,
) -> list[dict[str, str | int | bool | dict[str, str]]]:
    """
    Get metadata for all images in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_all_metadata.ipynb) to test this function or build upon it.

    :param include_archived: whether to include archived images, defaults to False
    :type include_archived: bool, optional
    :return: metadata for all images
    :rtype: list
    """
    response = adaboard.request_adaboard(
        path="registry/metadata", params={"get_archived": False}
    ).json()
    if include_archived:
        res_archived = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": True}
        ).json()
        response.extend(res_archived)

    return response


def get_image_digest(metadata_id: str) -> str:
    """
    Get the digest of an image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_image_digest.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :return: image digest for the remote image
    :rtype: str
    """

    response = adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}",
    ).json()

    return response["sha256"]


def get_image_id(project_name: str, repository_name: str, tag: str) -> int:
    """
    Get the ID of an image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_image_id.ipynb) to test this function or build upon it.

    :param project_name: the name of the project the image belongs to
    :type project_name: str
    :param repository_name: the name of the image repository
    :type: repository_name: str
    :param tag: the tag of the specific image
    :type tag: str
    :return: image ID
    :rtype: int
    """
    # Make sure image options are valid
    assert (
        project_name in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only list IDs for images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"

    # Get all images from the repository, page by page
    all_images = adaboard.get_all_pages(
        api_url=f"registry/{project_name}/{repository_name}/images/v2/"
    )
    # Find the specific image and return its ID
    for image in all_images:
        if image["tags"][0] == tag:
            return image["id"]

    raise ValueError(
        f"Could not find image with tag {tag} in repository {repository_name}"
    )


def get_image_metadata(
    metadata_id: int,
) -> dict[str, str | int | bool | dict[str, str]]:
    """
    Get metadata for a specific image in the Harbor registry based on its ID.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_image_metadata.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :return: image metadata
    :rtype: dict
    """

    response = adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}",
    ).json()

    return response


def get_image_metadata_id(
    project_name: str, repository_name: str, tag: str
) -> int:
    """
    Get the metadata ID for a specific image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_image_metadata_id.ipynb) to test this function or build upon it.

    :param project_name: the name of the project the image belongs to
    :type project_name: str
    :param repository_name: the name of the image repository
    :type: repository_name: str
    :param tag: the tag of the specific image
    :type tag: str
    :return: image metadata ID
    :rtype: int
    """

    # Make sure image options are valid
    assert (
        project_name in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only list metadata IDs for images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"

    # Get metadata for all images
    response = adaboard.request_adaboard(
        path="registry/metadata", params={"get_archived": False}
    ).json()
    res_archived = adaboard.request_adaboard(
        path="registry/metadata", params={"get_archived": True}
    ).json()
    response.extend(res_archived)

    # Find the specific image and return its metadata
    for image in response:
        if (
            image["oci_image_name"]["project"] == project_name
            and image["oci_image_name"]["repository"] == repository_name
            and image["oci_image_name"]["tag"] == tag
        ):
            return image["metadata_id"]

    raise ValueError(
        f"Could not find image with tag {tag} in repository {repository_name}"
    )


def get_project_repositories(project_name: str) -> list[str]:
    """
    Get all image repositories under a given project name.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_project_repositories.ipynb) to test this function or build upon it.

    :param project_name: the name of the project to list images from
    :type project_name: str
    :return: list of existing images under a given project name
    :rtype: list
    """

    # Make sure project options are valid
    assert (
        project_name in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only list images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"

    # Get all repositories from the project, page by page
    all_images = adaboard.get_all_pages(
        api_url=f"registry/{project_name}/v2/repositories/"
    )

    return [x["name"] for x in all_images]


def get_project_stats(project_name: str) -> list[dict[str, str | int]]:
    """
    Get statistics for a specific project in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_project_stats.ipynb) to test this function or build upon it.

    :param project_name: the name of the project to get stats from
    :type project_name: str
    :return: usage statistics for a given project
    :rtype: list
    """

    # Make sure project options are valid
    assert (
        project_name in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only show stats of projects that are {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"

    # Get all repositories from the project, page by page
    all_images = adaboard.get_all_pages(
        api_url=f"registry/{project_name}/v2/repositories/"
    )

    # Compile and return statistics
    return [
        {"repository": x["name"], "count": x["image_amount"]}
        for x in all_images
    ]


def get_projects(include_archived: bool = False) -> list[str]:
    """
    Get a list of the projects in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_projects.ipynb) to test this function or build upon it.

    :param include_archived: whether to include archived projects
    :type include_archived: bool
    :return: list of existing projects
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="registry/metadata", params={"get_archived": False}
    ).json()
    if include_archived:
        res_archived = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": True}
        ).json()
        response.extend(res_archived)

    projects = [x["oci_image_name"]["project"] for x in response]

    return list(set(projects))


def get_publish_logs(
    metadata_id: int, source: str = "publish"
) -> list[dict[str, str]]:
    """
    Get the publish or system logs of an image publishing process.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_publish_logs.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :param source: the source of the logs, either "build" or "publish", defaults to "publish"
    :type source: str, optional
    :return: build logs
    :rtype: list
    """

    assert (
        source in ALLOWED_PUBLISH_LOG_SOURCES
    ), f"Log source must be one of {', '.join([x for x in ALLOWED_PUBLISH_LOG_SOURCES])}"

    # Get run ID of the publishing process
    try:
        mdata = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": False}
        ).json()
        mdata_archived = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": True}
        ).json()
        mdata.extend(mdata_archived)
        publish_id = [
            x["run_id"] for x in mdata if x["metadata_id"] == metadata_id
        ][0]
    except IndexError:
        raise ValueError(
            f"Could not find metadata with ID {metadata_id} in the registry."
        )

    response_raw = adaboard.request_adaboard(
        path=f"script_runner/runs/{publish_id}/logs/"
    ).json()
    response = response_raw["log"]

    if source == "publish":
        logs = [
            {
                "time": res["timestamp"],
                "input": res["input"],
                "output": res["output"].replace(res["input"], ""),
            }
            for res in response
            if res["type"] == "command"
        ]
    elif source == "system":
        logs = [
            {"time": res["timestamp"], "message": res["output"]}
            for res in response
            if res["type"] == "system"
        ]

    return logs


def get_repositories_by_author(
    author_id: str,
    include_archived: bool = False,
) -> list[str]:
    """
    Get a list of the repositories in the Harbor registry by author ID.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_repositories_by_author.ipynb) to test this function or build upon it.

    :param author_id: the ID of the author to list repositories from
    :type author_id: str
    :param include_archived: whether to include archived images, defaults to False
    :type include_archived: bool, optional
    :return: list of existing repositories from a given author
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="registry/metadata", params={"get_archived": False}
    ).json()
    if include_archived:
        res_archived = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": True}
        ).json()
        response.extend(res_archived)

    author_repos = [x["name"] for x in response if x["user_id"] == author_id]

    return list(set(author_repos))


def get_repositories_by_type(
    type_id: str, include_archived: bool = False
) -> list[str]:
    """
    Get a list of the repositories in the Harbor registry by image type.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_repositories_by_type.ipynb) to test this function or build upon it.

    :param type: type of image
    :type type: str
    :param include_archived: whether to include archived images, defaults to False
    :type include_archived: bool, optional
    :return: list of existing repositories of a given type
    :rtype: list
    """

    # Make sure image options are valid
    assert (
        type_id in ALLOWED_METADATA_TYPES
    ), f"Can only get repositories of the type {', '.join([x for x in ALLOWED_METADATA_TYPES])}"

    response = adaboard.request_adaboard(
        path="registry/metadata", params={"get_archived": False}
    ).json()
    if include_archived:
        res_archived = adaboard.request_adaboard(
            path="registry/metadata", params={"get_archived": True}
        ).json()
        response.extend(res_archived)

    type_repos = [x["name"] for x in response if x["type"] == type_id]

    return list(set(type_repos))


def get_repository_tags(project_name: str, repository_name: str) -> list[str]:
    """
    Get all tags of an image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_repository_tags.ipynb) to test this function or build upon it.

    :param project_name: the name of the project the image belongs to
    :type project_name: str
    :param repository_name: the name of the image repository
    :type: repository_name: str
    :return: list of existing image tags
    :rtype: list
    """

    # Make sure repository options are valid
    assert (
        project_name in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only list tags for images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"

    # Get all images from the repository, page by page
    all_images = adaboard.get_all_pages(
        api_url=f"registry/{project_name}/{repository_name}/images/v2/"
    )

    return [response["tags"][0] for response in all_images]


def get_types() -> list[str]:
    """
    Get a list of the image types in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/get_types.ipynb) to test this function or build upon it.

    :return: list of existing types
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="registry/metadata",
    ).json()

    types = [x["type"] for x in response]

    return list(set(types))


def request_harbor(
    path: str,
    method=requests.get,
    **kwargs,
) -> requests.models.Response:
    """
    Function to request the registry API at the specified URL.

    Raises on errors from the HTTP calls.

    Note: All kwargs passed are directly sent through to the request function.

    :param path: path to query the registry on (base url will be injected
                 automatically)
    :type path: str
    :param method: method to use to query harbor, defaults to requests.get
    :type method: function, optional
    :return: response from harbor
    :rtype: response
    """
    # Construct authentication header for harbor
    adalib_config = config.get_config()
    harbor_token = keycloak.get_client_token(
        audience_client_id=adalib_config.KEYCLOAK_CLIENTS["harbor"]
    )

    headers = {
        "authorization": f"Bearer {harbor_token['id_token']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Query harbor and raise for status
    constructed_url = (
        f"{adalib_config.SERVICES['harbor']['url']}/api/v2.0/{path}"
    )
    response = method(constructed_url, headers=headers, **kwargs)
    response.raise_for_status()

    return response


def restore_image(metadata_id: int) -> None:
    """
    Restore a previously-archived image in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/restore_image.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :return: nothing
    :rtype: None
    """

    # Check if image is already visible
    img_metadata = adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}",
    ).json()

    # If not visible, restore it
    if img_metadata["archived"]:
        payload = {"archived": False}
        adaboard.request_adaboard(
            path=f"registry/metadata/{metadata_id}/archive",
            method=requests.put,
            json=payload,
        )
        return None
    else:
        raise RuntimeError(
            f"Image with metadata ID {metadata_id} is already visible."
        )


def update_image_state(metadata_id: str) -> str:
    """
    Update the "ready" state of an image based on its status in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/harbor/update_image_state.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the image
    :type metadata_id: int
    :return: the updated "ready" state of the image
    :rtype: str
    """

    response = adaboard.request_adaboard(
        path=f"registry/metadata/{metadata_id}/ready", method=requests.put
    ).json()

    return response["ready"]
