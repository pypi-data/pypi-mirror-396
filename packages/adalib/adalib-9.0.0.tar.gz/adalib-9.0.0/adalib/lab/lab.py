import base64
from datetime import datetime
from typing import Optional

import requests
from adalib_auth import config

from .. import adaboard

ALLOWED_GIT_TYPES = ["ssh", "https", "public"]
ALLOWED_BUILD_LOG_SOURCES = ["build", "system"]
ALLOWED_LAB_LOG_SOURCES = ["user", "system"]
ALLOWED_OCI_PROJECT_TYPES = ["apps", "kernels", "base_images"]
HARBOR_HOST = "container-registry"
HARBOR_PORT = "80"
LOG_SOURCES = {"user": False, "system": True}


def build_image_from_git(
    git_url: str,
    file_path: str,
    image_name: str,
    image_tag: str,
    image_type: str,
    branch: str = "",
    build_args: dict[str, str] = {},
    commit: str = "",
    git_creds: dict[str, str] = {},
    project_name: str = "",
    timeout: int = 3600,
) -> int:
    """
    Build a container image from a container file in a Git repository.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/build_image_from_git.ipynb) to test this function or build upon it.

    :param git_url: full URL of Git repository containing the container file
    :type git_url: str
    :param file_path: path to the container file in the Git repository
    :type file_path: str
    :param image_name: the name of the target image
    :type image_name: str
    :param image_tag: the tag of the target image
    :type image_tag: str
    :param image_type: the type of the image
    :type image_type: str
    :param branch: the branch of the Git repository to use, defaults to default
    :type branch: str, optional
    :param build_args: additional build arguments to pass build process, defaults to {}
    :type build_args: dict, optional
    :param commit: the commit hash of the Git repository to use, defaults to ""
    :type commit: str, optional
    :param git_creds: credentials to authenticate to the Git repository. For SSH, use keys "PRIVATE_KEY_FILE" and "PASSWORD". For HTTPS, use keys "USERNAME" and "PASSWORD".
    :type git_creds: dict, optional
    :param project_name: the name of the project to link the image to, defaults to image_name
    :type project_name: str, optional
    :param timeout: the maximum time (in seconds) to wait for the build to complete, defaults to 3600
    :type timeout: int, optional
    :return: the run ID of the build process
    :rtype: int
    """

    adalib_config = config.get_config()
    # Check that the specified project is valid
    assert (
        image_type in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only build images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"
    # Check that only branch or commit is specified
    assert not (
        bool(branch) and bool(commit)
    ), "Cannot specify both 'branch' and 'commit'"
    # Check that the file path is valid
    file_name = file_path.split("/")[-1]
    assert ("dockerfile" in file_name.lower()) or (
        "containerfile" in file_name.lower()
    ), "The file path must point at a 'Dockerfile' or 'Containerfile' type of file."
    # Figure out git type
    if git_creds:
        if list(git_creds.keys()) == ["PRIVATE_KEY_FILE", "PASSWORD"]:
            git_type = "ssh"
        elif list(git_creds.keys()) == ["USERNAME", "PASSWORD"]:
            git_type = "https"
        else:
            raise KeyError(
                "Dictionary with git credentials has the wrong keys. For SSH, use 'PRIVATE_KEY_FILE' and 'PASSWORD'. For HTTPS, use 'USERNAME' and 'PASSWORD'."
            )
    else:
        git_type = "public"

    # Build request payload with the specified parameters
    # Prepare build arguments
    build_args = ";;".join([f"{k}={v}" for k, v in build_args.items()])

    # Collect parameters into payload
    payload = {
        "script": "builder",
        "user_id": adaboard.get_user()["user_id"],
        "pool": "internal",
        "cleanup": True,
        "timeout": timeout,
        "run_in_isolation": False,
        "start_podman_sidecar": False,
        "config": {
            "HARBOR_CURATED_PROJECT": {
                "real_value": image_type,
                "value": image_type,
            },
            "HARBOR_HOST": {
                "real_value": HARBOR_HOST,
                "value": HARBOR_HOST,
            },
            "HARBOR_HUMAN_READABLE_REPOSITORY_NAME": {
                "real_value": project_name or image_name,
                "value": project_name or image_name,
            },
            "HARBOR_NAMESPACE": {
                "real_value": adalib_config.NAMESPACE,
                "value": adalib_config.NAMESPACE,
            },
            "HARBOR_PROJECT": {
                "real_value": f"{image_type}_temp",
                "value": f"{image_type}_temp",
            },
            "HARBOR_REPOSITORY_NAME": {
                "real_value": image_name,
                "value": image_name,
            },
            "HARBOR_TAG": {
                "real_value": image_tag,
                "value": image_tag,
            },
            "IMAGE_BUILD_ARGS": {
                "real_value": build_args,
                "value": build_args,
            },
            "IMAGE_CONTAINERFILE_LOCATION": {
                "real_value": file_path,
                "value": file_path,
            },
            "NETWORK_HOST": {
                "real_value": adalib_config.NETWORK_HOST,
                "value": adalib_config.NETWORK_HOST,
            },
        },
    }

    # Add Git credentials to payload based on Git type
    if git_type.lower() == "ssh":
        git_url = git_url.replace("https://", "git@").replace(".com/", ".com:")
        git_config = [
            {
                "GIT_URL": {"real_value": git_url, "value": git_url},
                "GIT_SSH_PRIVATE_KEY_FILE": {
                    "real_value": git_creds["PRIVATE_KEY_FILE"],
                    "value": git_creds["PRIVATE_KEY_FILE"],
                },
                "GIT_SSH_PASSWORD": {
                    "real_value": git_creds["PASSWORD"],
                    "value": git_creds["PASSWORD"],
                },
            },
        ]
    elif git_type.lower() == "https":
        git_config = [
            {
                "GIT_URL": {"real_value": git_url, "value": git_url},
                "GIT_USERNAME": {
                    "real_value": git_creds["USERNAME"],
                    "value": git_creds["USERNAME"],
                },
                "GIT_PASSWORD": {
                    "real_value": git_creds["PASSWORD"],
                    "value": git_creds["PASSWORD"],
                },
            },
        ]
    elif git_type.lower() == "public":
        git_config = [
            {
                "GIT_URL": {"real_value": git_url, "value": git_url},
            },
        ]

    # Use specific branch or commit
    if branch:
        git_config[0]["GIT_BRANCH"] = {"real_value": branch, "value": branch}
    elif commit:
        git_config[0]["GIT_COMMIT"] = {"real_value": commit, "value": commit}

    # Add Git configuration to payload
    for item in git_config:
        payload["config"].update(item)

    # Trigger the build and get the run ID
    response_build = adaboard.request_adaboard(
        path="script_runner/runs/start/",
        method=requests.post,
        json=payload,
    ).json()

    return response_build["id"]


def build_image_from_lab(
    file_path: str,
    image_name: str,
    image_tag: str,
    image_type: str,
    project_name: str = "",
    build_args: dict[str, str] = {},
    timeout: int = 3600,
) -> int:
    """
    Build a container image from a container file in the Lab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/build_image_from_lab.ipynb) to test this function or build upon it.

    :param file_path: path to the container file in the Lab
    :type file_path: str
    :param image_name: the name of the target image
    :type image_name: str
    :param image_tag: the tag of the target image
    :type image_tag: str
    :param image_type: the type of the image
    :type image_type: str
    :param project_name: the name of the project to link the image to, defaults to image_name
    :type project_name: str, optional
    :param build_args: additional build arguments to pass build process, defaults to {}
    :type build_args: dict, optional
    :param timeout: the maximum time (in seconds) to wait for the build to complete, defaults to 3600
    :type timeout: int, optional
    :return: the run ID of the build process
    :rtype: int
    """

    adalib_config = config.get_config()
    # Check that the specified project is valid
    assert (
        image_type in ALLOWED_OCI_PROJECT_TYPES
    ), f"Can only build images that are of the type {', '.join([x for x in ALLOWED_OCI_PROJECT_TYPES])}"

    # Get the context and file name from the full path
    ctxt_path = file_path.split("/")[0]
    file_name = file_path.split("/")[-1]

    assert ("dockerfile" in file_name.lower()) or (
        "containerfile" in file_name.lower()
    ), "The file path must point at a 'Dockerfile' or 'Containerfile' type of file."

    # Build request payload with the specified parameters
    build_args = ";;".join([f"{k}={v}" for k, v in build_args.items()])

    payload = {
        "script": "builder",
        "user_id": adaboard.get_user()["user_id"],
        "pool": "internal",
        "cleanup": True,
        "timeout": timeout,
        "run_in_isolation": False,
        "start_podman_sidecar": False,
        "config": {
            "GIT_LOCATION": {
                "real_value": ctxt_path,
                "value": ctxt_path,
            },
            "HARBOR_CURATED_PROJECT": {
                "real_value": image_type,
                "value": image_type,
            },
            "HARBOR_HOST": {
                "real_value": HARBOR_HOST,
                "value": HARBOR_HOST,
            },
            "HARBOR_HUMAN_READABLE_REPOSITORY_NAME": {
                "real_value": project_name or image_name,
                "value": project_name or image_name,
            },
            "HARBOR_NAMESPACE": {
                "real_value": adalib_config.NAMESPACE,
                "value": adalib_config.NAMESPACE,
            },
            "HARBOR_PROJECT": {
                "real_value": f"{image_type}_temp",
                "value": f"{image_type}_temp",
            },
            "HARBOR_REPOSITORY_NAME": {
                "real_value": image_name,
                "value": image_name,
            },
            "HARBOR_TAG": {
                "real_value": image_tag,
                "value": image_tag,
            },
            "IMAGE_BUILD_ARGS": {
                "real_value": build_args,
                "value": build_args,
            },
            "IMAGE_CONTAINERFILE_LOCATION": {
                "real_value": file_name,
                "value": file_name,
            },
            "NETWORK_HOST": {
                "real_value": adalib_config.NETWORK_HOST,
                "value": adalib_config.NETWORK_HOST,
            },
        },
    }

    # Trigger the build and get the run ID
    response_build = adaboard.request_adaboard(
        path="script_runner/runs/start/",
        method=requests.post,
        json=payload,
    ).json()

    return response_build["id"]


def delete_files(paths: list[str]) -> None:
    """
    Delete files or folders in the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/delete_files.ipynb) to test this function or build upon it.

    :param paths: paths to the files to delete, relative to the user's home directory
    :type paths: list
    :return: nothing
    :rtype: None
    """

    # Build request payload with the specified information
    payload = {"operation": "delete", "paths": paths}

    # Delete the files
    adaboard.request_adaboard(
        path="jupyter/files/notebook/content/",
        method=requests.patch,
        json=payload,
    )

    return None


def download_file(file_path: str, target_path: str) -> None:
    """
    Download a file from the user's Lab environment and save it to a specific location.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/download_file.ipynb) to test this function or build upon it.

    :param file_path: path to the file in the Lab environment, including file name and extension, relative to the user's home directory (/home/<username>)
    :type file_path: str
    :param target_path: path to save the file to, including file name and extension, relative to the current working directory
    :type target_path: str
    :return: nothing
    :rtype: None
    """

    # Get the file, base64 encoded
    response = adaboard.request_adaboard(
        path="jupyter/files/notebook/content/fetch", params={"path": file_path}
    ).json()

    # Decode the file to get the binary
    file_bytes = base64.b64decode(response["content"])

    # Write the file to the target path
    with open(target_path, "wb") as out_file:
        out_file.write(file_bytes)

    return None


def get_available_kernels() -> (
    list[dict[str, str | int | bool | dict[str, str]]]
):
    """
    Get a list of available kernel images in the Harbor registry.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_available_kernels.ipynb) to test this function or build upon it.

    :return: a list of available kernels
    :rtype: list
    """

    # Get metadata for all images
    response = adaboard.request_adaboard(path="registry/metadata").json()

    # Filter-out non-kernel images
    return [x for x in response if x["type"] == "kernel"]


def get_build_logs(
    build_id: int, source: str = "build"
) -> list[dict[str, str]]:
    """
    Get the build or system logs of an image build process.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_build_logs.ipynb) to test this function or build upon it.

    :param build_id: the run ID of the build process
    :type build_id: int
    :param source: the source of the logs, either "build" or "system", defaults to "build"
    :type source: str, optional
    :return: build logs
    :rtype: list
    """

    assert (
        source in ALLOWED_BUILD_LOG_SOURCES
    ), f"Log source must be one of {', '.join([x for x in ALLOWED_BUILD_LOG_SOURCES])}"

    response_raw = adaboard.request_adaboard(
        path=f"script_runner/runs/{build_id}/logs/"
    ).json()
    response = response_raw["log"]

    if source == "build":
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


def get_build_status(
    build_id: int,
) -> str:
    """
    Get the status of a build process.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_build_status.ipynb) to test this function or build upon it.

    :param build_id: the run ID of the build process
    :type build_id: int
    :return: the status of the build process
    :rtype: str
    """

    response_statuses = adaboard.request_adaboard(path="runner/status/").json()

    response_run = adaboard.request_adaboard(
        path=f"script_runner/runs/{build_id}/"
    ).json()

    return response_statuses[str(response_run["status"])]


def get_config_options() -> (
    list[dict[str, int | str | list[dict[str, str | int | bool]]]]
):
    """
    Get the available Lab configuration options for the user.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_config_options.ipynb) to test this function or build upon it.

    :return: list of existing Lab configuration options
    :rtype: list
    """

    response = adaboard.request_adaboard(path="jupyter/system/options").json()

    return response


def get_installed_kernels() -> list[dict[str, str | int]]:
    """
    Get a list of the kernels that are installed in the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_installed_kernels.ipynb) to test this function or build upon it.

    :return: a list of installed kernels
    :rtype: list
    """

    response = adaboard.request_adaboard(path="jupyter/kernelspecs").json()

    return response


def get_kernel_metadata_id(kernel_name: str, kernel_tag: str) -> int:
    """
    Get the metadata ID of the object corresponding to a specific kernel image.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_kernel_metadata_id.ipynb) to test this function or build upon it.

    :param kernel_name: the name of the repository containing the kernel image
    :type kernel_name: str
    :param kernel_tag: the tag of the kernel image
    :type kernel_tag: str
    :return: the metadata ID of the kernel image
    :rtype: int
    """

    # Get metadata for all images
    response = adaboard.request_adaboard(path="registry/metadata").json()

    # Filter-out non-kernel images
    kernel_images = [x for x in response if x["type"] == "kernel"]

    # Return the metadata ID of the specified kernel image, if it exists
    try:
        return [
            x["metadata_id"]
            for x in kernel_images
            if x["oci_image_name"]["repository"] == kernel_name
            and x["oci_image_name"]["tag"] == kernel_tag
        ][0]
    except IndexError:
        raise ValueError(
            f"Kernel image {kernel_name}:{kernel_tag} does not exist."
        )


def get_lab_files(path: str) -> list[dict[str, str | int]]:
    """
    Get a list of the files under a directory in the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_lab_files.ipynb) to test this function or build upon it.

    :param path: path to list the files from, relative to the user's home directory (/home/<username>)
    :type path: str
    :return: files in the directory
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="jupyter/files/notebook/content/", params={"path": path}
    ).json()

    return response


def get_lab_images() -> list[dict[str, str]]:
    """
    Get a list of container images present in the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_lab_images.ipynb) to test this function or build upon it.

    :return: a list of available images
    :rtype: list
    """

    response = adaboard.request_adaboard(path="registry/jupyter_images").json()

    return response


def get_lab_logs(
    from_date: str = "", to_date: str = "", source: str = "user"
) -> list[dict[str, str]]:
    """
    Get the logs of the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_lab_logs.ipynb) to test this function or build upon it.

    :param from_date: the start date for the logs, in ISO format (YYYY-MM-DDTHH:mm:ss+HH:mm), defaults to ""
    :type from_date: str, optional
    :param to_date: the end date for the logs, in ISO format (YYYY-MM-DDTHH:mm:ss+HH:mm), defaults to ""
    :type to_date: str, optional
    :param source: the source of the logs, either "user" or "system", defaults to "user"
    :type source: str, optional
    :return: Lab logs
    :rtype: list
    """

    # Check that the specified source is valid
    assert (
        source in ALLOWED_LAB_LOG_SOURCES
    ), f"Log source must be one of {', '.join([x for x in ALLOWED_LAB_LOG_SOURCES])}"

    params = {"system": LOG_SOURCES[source]}
    # Check that the date format is correct
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
        path="jupyter/server/v2/logs", params=params
    ).json()

    return response


def get_lab_status(metrics: bool = True, options: bool = True) -> dict[
    str,
    str
    | dict[str, float]
    | list[dict[str, str | int | float | dict[str, str | int | bool]]],
]:
    """
    Get configuration and status information about the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/get_lab_status.ipynb) to test this function or build upon it.

    :param metrics: whether to fetch Lab metrics, defaults to True
    :type metrics: bool, optional
    :param options: whether to fetch Lab options, defaults to True
    :type options: bool, optional
    :return: Lab information
    :rtype: dict
    """

    response = adaboard.request_adaboard(
        path="jupyter/server",
        params={"metrics": metrics, "options": options},
    ).json()

    return response


def install_kernel(
    metadata_id: int,
    name: str,
    include_notebook: bool = True,
) -> None:
    """
    Install a kernel into the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/install_kernel.ipynb) to test this function or build upon it.

    :param metadata_id: the metadata ID of the kernel to install
    :type metadata_id: int
    :param name: name to be given to the installed kernel
    :type name: str
    :param include_notebook: whether to include a dummy notebook file with the kernel, defaults to True
    :type include_notebook: bool, optional
    :return: nothing
    :rtype: None
    """

    # Build request payload with the specified information
    payload = {
        "display_name": name + " (published)",
        "metadata_id": metadata_id,
        "include_dummy_notebook": include_notebook,
    }

    # Install kernel and check response
    adaboard.request_adaboard(
        path="jupyter/kernelspecs", method=requests.post, json=payload
    ).json()

    return None


def move_file(old_path: str, new_path: str) -> None:
    """
    Move a file or folder in the user's Lab environment.  Note that this operation can also be used to rename a file or folder.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/move_file.ipynb) to test this function or build upon it.

    :param old_path: path to the file to move, including file name and extension, relative to the user's home directory
    :type old_path: str
    :param new_path: new path to save the file to, including file name and extension, relative to the user's home directory
    :type new_path: str
    :return: nothing
    :rtype: None
    """

    # Build request payload with the specified information
    payload = {
        "operation": "rename",
        "old_path": old_path,
        "new_path": new_path,
    }

    # Rename the file
    adaboard.request_adaboard(
        path="jupyter/files/notebook/content/",
        method=requests.patch,
        json=payload,
    )

    return None


def stop_lab() -> None:
    """
    Stop the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/stop_lab.ipynb) to test this function or build upon it.

    :return: nothing
    :rtype: None
    """

    response = adaboard.request_adaboard(
        path="jupyter/server", method=requests.delete
    ).json()

    assert (
        response["message"] == "OK"
    ), "The Lab environment could not be stopped."

    return None


def uninstall_kernel(name: str) -> None:
    """
    Uninstall a kernel from the user's Lab environment.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/uninstall_kernel.ipynb) to test this function or build upon it.

    :param name: the name of the kernel to uninstall
    :type name: str
    :return: nothing
    :rtype: None
    """

    response = adaboard.request_adaboard(
        path=f"jupyter/kernelspecs/{name}", method=requests.delete
    ).json()

    assert response["message"] == "OK", "The kernel could not be uninstalled."

    return None


def who_am_i() -> dict[str, str]:
    """
    Get information about the current user.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/lab/who_am_i.ipynb) to test this function or build upon it.

    :return: information about the current user
    :rtype: dict
    """

    response = adaboard.request_adaboard(path="users/self").json()

    return response


def convert_token_to_value(token: str) -> Optional[str]:
    """
    Convert a Lab Configuration token into the true decrypted value from the user input.

    :param token: the token to convert
    :type token: str
    :return: the true decrypted value of the token
    :rtype: str
    """
    response = adaboard.request_adaboard(
        path="jupyter/system/user_input_value", params={"token": token}
    ).json()
    return response.get("value")
