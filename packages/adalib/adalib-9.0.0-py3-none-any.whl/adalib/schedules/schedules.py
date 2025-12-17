import base64
import os

import requests

from .. import adaboard
from ..utils import validate_acl

ALLOWED_CARD_SOURCES = ["lab", "local"]
MAX_FILE_SIZE = 5000000
RUN_STATUS_CODES = {"1": "Pending", "2": "Running", "3": "OK", "4": "Error"}


def create_schedule(
    name: str,
    schedule: str,
    acl_type_view: str = "logged_in",
    acl_list_view: list[str] = [],
    acl_type_logs: str = "logged_in",
    acl_list_logs: list[str] = [],
    acl_type_edit: str = "logged_in",
    acl_list_edit: list[str] = [],
    acl_type_decrypt: str = "logged_in",
    acl_list_decrypt: list[str] = [],
    active: bool = True,
    aux_files: list[dict] = [{"source": "", "target": ""}],
    card_id: int = None,
    cleanup: bool = True,
    inputs: dict = {},
    concurrent: bool = True,
    kernel_id: int = None,
    notebook_file: str = "",
    owner_id: str = "",
    pool: str = "card-runner-low",
    post_run_script: str = "",
    pre_run_script: str = "",
    profile_id: int = None,
    options_ids: list[int] = [],
    runner_id: str = "",
    source: str = "lab",
    timeout: int = 3600,
    timezone: str = "Etc/UTC",
):
    """
    Create a new notebook schedule.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/create_schedule.ipynb) to test this function or build upon it.

    :param name: The schedule's name.
    :type name: str
    :param schedule: The schedule time string in cron format.
    :type schedule: str
    :param acl_type_view: The ACL type for viewing the schedule. Defaults to "logged_in".
    :type acl_type_view: str, optional
    :param acl_list_view: The list of users or groups allowed to view the schedule. Defaults to an empty list.
    :type acl_list_view: list[str], optional
    :param acl_type_logs: The ACL type for viewing the schedule including logs. Defaults to "logged_in".
    :type acl_type_logs: str, optional
    :param acl_list_logs: The list of users or groups allowed to view the schedule including logs. Defaults to an empty list.
    :type acl_list_logs: list[str], optional
    :param acl_type_edit: The ACL type for editing the schedule. Defaults to "logged_in".
    :type acl_type_edit: str, optional
    :param acl_list_edit: The list of users or groups allowed to edit the schedule. Defaults to an empty list.
    :type acl_list_edit: list[str], optional
    :param acl_type_decrypt: The ACL type for editing the schedule and decrypting its secrets. Defaults to "logged_in".
    :type acl_type_decrypt: str, optional
    :param acl_list_decrypt: The list of users or groups allowed to edit the schedule and decrypt its secrets. Defaults to an empty list.
    :type acl_list_decrypt: list[str], optional
    :param active: Flag whether the schedule is active. Defaults to True.
    :type active: bool, optional
    :param aux_files: A list of auxiliary files to include in the schedule.
    :type aux_files: list[dict], optional
    :param card_id: The ID of the card from which to create the schedule. Defaults to None.
    :type card_id: int, optional
    :param cleanup: Flag whether to clean up resources after the schedule. Defaults to True.
    :type cleanup: bool, optional
    :param inputs: A dictionary of input parameters for the schedule. Defaults to an empty dictionary.
    :type inputs: dict, optional
    :param concurrent: Flag whether the schedule can run concurrently. Defaults to True.
    :type concurrent: bool, optional
    :param kernel_id: The ID of the kernel to be used when running the schedule. Defaults to None.
    :type kernel_id: int, optional
    :param notebook_file: The path to the notebook file. Defaults to an empty string.
    :type notebook_file: str, optional
    :param owner_id: The user ID of the person to own the schedule. Defaults to an empty string.
    :type owner_id: str, optional
    :param pool: The execution pool. Defaults to "card-runner-low".
    :type pool: str, optional
    :param post_run_script: A post-run script to execute. Defaults to an empty string.
    :type post_run_script: str, optional
    :param pre_run_script: A pre-run script to execute. Defaults to an empty string.
    :type pre_run_script: str, optional
    :param profile_id: The ID of the Lab profile to use when running the notebook. Defaults to None.
    :type profile_id: int, optional
    :param options_ids: A list of Lab option IDs to use when running the notebook. Defaults to an empty list.
    :type options_ids: list[int], optional
    :param runner_id: The user ID of the person running the notebook schedule. Defaults to an empty string.
    :type runner_id: str, optional
    :param source: The source of the notebook file. Defaults to "lab".
    :type source: str, optional
    :param timeout: The maximum time (in seconds) before killing the run. Defaults to 3600.
    :type timeout: int, optional
    :param timezone: The timezone code for the schedule. Defaults to "Etc/UTC".
    :type timezone: str, optional
    :return: The schedule's ID.
    :rtype: int
    """

    assert (
        card_id or notebook_file
    ), "Either card_id or notebook_file must be provided."
    if notebook_file:
        assert notebook_file.lower().endswith(
            ".ipynb"
        ), "Notebook file must be a .ipynb file."
        assert (
            source.lower() in ALLOWED_CARD_SOURCES
        ), "Files source must be 'lab' or 'local'."
        assert all(
            issubclass(type(x), dict) for x in aux_files
        ), "Auxiliary files must be a list of dictionaries."
        assert all(
            ("source" in d and "target" in d) for d in aux_files
        ), "Auxiliary files must have keys 'source' and 'target'."

    validate_acl(
        "schedule",
        False,
        acl_type_view,
        acl_type_logs,
        acl_type_edit,
        acl_type_decrypt,
    )

    # Collect ACL configuration
    acl_config = [
        {
            "acl_action": "schedule_view",
            "acl_type": acl_type_view,
            "userlist": acl_list_view,
            "grouplist": acl_list_view,
        },
        {
            "acl_action": "schedule_view_logs",
            "acl_type": acl_type_logs,
            "userlist": acl_list_logs,
            "grouplist": acl_list_logs,
        },
        {
            "acl_action": "schedule_edit",
            "acl_type": acl_type_edit,
            "userlist": acl_list_edit,
            "grouplist": acl_list_edit,
        },
        {
            "acl_action": "schedule_edit_privileged",
            "acl_type": acl_type_decrypt,
            "userlist": acl_list_decrypt,
            "grouplist": acl_list_decrypt,
        },
    ]
    # Collect run configuration
    run_config = {
        "inputs": inputs,
        "options_ids": options_ids,
        "profile_id": profile_id,
        "scripts": {
            "pre_run_script": pre_run_script,
            "post_run_script": post_run_script,
        },
    }

    # Add content depending on user input
    content = {}
    if card_id:
        tmp = adaboard.request_adaboard(
            f"cards/{card_id}", params={"incl_content": True}
        ).json()
        content["content"] = tmp["content"]
    else:
        if source.lower() == "lab":
            # Check file size before actually pulling it from the Lab
            try:
                response_props = adaboard.request_adaboard(
                    path="jupyter/files/notebook/content/",
                    params={"path": os.path.dirname(notebook_file)},
                ).json()
                props = [
                    x
                    for x in response_props
                    if x["name"] == os.path.basename(notebook_file)
                ][0]
            except IndexError as e:
                raise IndexError(
                    f"Notebook file '{notebook_file}' not found in the Lab."
                ) from e
            assert (
                props["size"] <= MAX_FILE_SIZE
            ), f"Notebook file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
            nb_file_bin = adaboard.request_adaboard(
                path="jupyter/files/notebook/content/fetch",
                params={"path": notebook_file},
            ).json()["content"]
        else:
            # Check file size before actually opening it
            assert (
                os.path.getsize(notebook_file) <= MAX_FILE_SIZE
            ), f"Notebook file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
            with open(notebook_file, "rb") as f:
                nb_file_bin = base64.b64encode(f.read()).decode("utf-8")
        content["content"] = [
            {
                "content": nb_file_bin,
                "content_name": os.path.basename(notebook_file),
                "contenttype_id": 1,
            }
        ]
    # Auxiliary files
    # Collect all files within the specified paths
    if aux_files[0]["source"]:
        # In the Lab, paths are relative to the user's home directory
        if source.lower() == "lab":
            # Collect all files within the specified paths
            all_aux_files = []
            for aux_file in aux_files:
                # Directories end with "/"; otherwise they are considered files; no nesting allowed
                if aux_file["source"].endswith("/"):
                    dir_cont = adaboard.request_adaboard(
                        path="jupyter/files/notebook/content/",
                        params={"path": aux_file["source"]},
                    ).json()
                    dir_paths = [
                        {
                            "source": x["path"],
                            "target": aux_file["target"],
                            "size": x["size"],
                        }
                        for x in dir_cont
                        if x["type"] == "file"
                    ]
                    all_aux_files.extend(dir_paths)
                else:
                    response_props = adaboard.request_adaboard(
                        path="jupyter/files/notebook/content/",
                        params={"path": os.path.dirname(aux_file["source"])},
                    ).json()
                    file_path = [
                        {
                            "source": x["path"],
                            "target": aux_file["target"],
                            "size": x["size"],
                        }
                        for x in response_props
                        if x["name"] == os.path.basename(aux_file["source"])
                    ]
                    all_aux_files.extend(file_path)
            # Now we have all the files with their paths and sizes in a single list
            for aux_file in all_aux_files:
                # Check file size before actually pulling it from the Lab
                assert (
                    aux_file["size"] <= MAX_FILE_SIZE
                ), f"Auxiliary file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
                # "content" is the binary; "content_name" determines the target folder
                aux_file_bin = adaboard.request_adaboard(
                    path="jupyter/files/notebook/content/fetch",
                    params={"path": aux_file["source"]},
                ).json()["content"]
                aux_file_name = f"{aux_file['target']}{os.path.basename(aux_file['source'])}"
                tmp = {
                    "content": aux_file_bin,
                    "content_name": aux_file_name,
                    "contenttype_id": 2,
                    # "path": aux_file["source"],
                }
                content["content"].append(tmp)

        # In the local machine, paths are absolute; nesting is allowed
        elif source.lower() == "local":
            all_aux_files = []
            for aux_file in aux_files:
                if os.path.isfile(aux_file["source"]):
                    all_aux_files.append(aux_file)
                elif os.path.isdir(aux_file["source"]):
                    for root, dirs, files in os.walk(aux_file["source"]):
                        for file in files:
                            all_aux_files.append(
                                {
                                    "source": f"{root}/{file}",
                                    "target": f"{root}/".replace(
                                        aux_file["source"], aux_file["target"]
                                    ),
                                }
                            )
            # Now we have all the files with their paths in a single list
            for aux_file in all_aux_files:
                # Check file sizes before actually opening them
                assert (
                    os.path.getsize(aux_file["source"]) <= MAX_FILE_SIZE
                ), f"Auxiliary file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
                with open(aux_file["source"], "rb") as f:
                    aux_file_bin = base64.b64encode(f.read()).decode("utf-8")
                # "content" is the binary; "content_name" determines the target folder
                aux_file_name = f"{aux_file['target']}/{os.path.basename(aux_file['source'])}"
                tmp = {
                    "content": aux_file_bin,
                    "content_name": aux_file_name,
                    "contenttype_id": 2,
                }
                content["content"].append(tmp)

    # Build request payload with user options
    payload = {
        "owner_id": owner_id or adaboard.get_user()["user_id"],
        "runner_id": runner_id or adaboard.get_user()["user_id"],
        "name": name,
        "timezone": timezone,
        "cron": schedule,
        "timeout": timeout,
        "pool": pool,
        "active": active,
        "concurrent": concurrent,
        "cleanup": cleanup,
        "acls": acl_config,
        "run_config": run_config,
        "kernel_metadata_id": kernel_id,
    }
    # Attach schedule content to payload
    payload.update(content)

    response = adaboard.request_adaboard(
        "schedules/v2", method=requests.post, json=payload
    ).json()

    return response["id"]


def delete_run(schedule_id: int, run_id: int) -> None:
    """
    Delete a specific schedule run.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/delete_run.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :param run_id: The run's ID.
    :type run_id: int
    :return: Nothing.
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"schedules/v2/runs/{schedule_id}/{run_id}",
        method=requests.delete,
    )


def delete_schedule(schedule_id: int) -> None:
    """
    Delete a specific notebook schedule.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/delete_schedule.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :return: Nothing.
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"schedules/v2/{schedule_id}", method=requests.delete
    )


def edit_schedule(  # noqa: C901
    schedule_id: int,
    name: str = None,
    schedule: str = None,
    acl_type_view: str = None,
    acl_list_view: list[str] = None,
    acl_type_logs: str = None,
    acl_list_logs: list[str] = None,
    acl_type_edit: str = None,
    acl_list_edit: list[str] = None,
    acl_type_decrypt: str = None,
    acl_list_decrypt: list[str] = None,
    active: bool = None,
    aux_files: list[dict] = None,
    cleanup: bool = None,
    inputs: dict = None,
    concurrent: bool = None,
    keep_aux_files: bool = True,
    kernel_id: int = None,
    notebook_file: str = None,
    owner_id: str = None,
    pool: str = None,
    post_run_script: str = None,
    pre_run_script: str = None,
    profile_id: int = None,
    options_ids: list[int] = None,
    runner_id: str = None,
    source: str = "lab",
    timeout: int = None,
    timezone: str = None,
):
    """
    Edit an existing notebook schedule. Note that unspecified fields will not be changed.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/edit_schedule.ipynb) to test this function or build upon it.

    :param name: The name of the schedule. Defaults to None
    :type name: str, optional
    :param schedule: The schedule time string in cron format. Defaults to None
    :type schedule: str, optional
    :param acl_type_view: The ACL type for viewing the schedule. Defaults to None
    :type acl_type_view: str, optional
    :param acl_list_view: The list of users or groups allowed to view the schedule. Defaults to None
    :type acl_list_view: list[str], optional
    :param acl_type_logs: The ACL type for viewing the schedule including logs. Defaults to None
    :type acl_type_logs: str, optional
    :param acl_list_logs: The list of users or groups allowed to view the schedule including logs. Defaults to None
    :type acl_list_logs: list[str], optional
    :param acl_type_edit: The ACL type for editing the schedule. Defaults to None
    :type acl_type_edit: str, optional
    :param acl_list_edit: The list of users or groups allowed to edit the schedule. Defaults to None
    :type acl_list_edit: list[str], optional
    :param acl_type_decrypt: The ACL type for editing the schedule and decrypting its secrets. Defaults to None
    :type acl_type_decrypt: str, optional
    :param acl_list_decrypt: The list of users or groups allowed to edit the schedule and decrypt its secrets. Defaults to None
    :type acl_list_decrypt: list[str], optional
    :param active: Flag whether the schedule is active. Defaults to None
    :type active: bool, optional
    :param aux_files: A list of auxiliary files to include in the schedule. Defaults to None
    :type aux_files: list[dict], optional
    :param card_id: The ID of the card from which to create the schedule. Defaults to None
    :type card_id: int, optional
    :param cleanup: Flag whether to clean up resources after the schedule. Defaults to None
    :type cleanup: bool, optional
    :param inputs: A dictionary of input parameters for the schedule. Defaults to None
    :type inputs: dict, optional
    :param concurrent: Flag whether the schedule can run concurrently. Defaults to None
    :type concurrent: bool, optional
    :param keep_aux_files: Flag whether to keep the existing auxiliary files. Defaults to True
    :type keep_aux_files: bool, optional
    :param kernel_id: The ID of the kernel to be used when running the schedule. Defaults to None
    :type kernel_id: int, optional
    :param notebook_file: The path to the notebook file. Defaults to None
    :type notebook_file: str, optional
    :param owner_id: The user ID of the person to own the schedule. Defaults to None
    :type owner_id: str, optional
    :param pool: The execution pool. Defaults to None
    :type pool: str, optional
    :param post_run_script: A post-run script to execute. Defaults to None
    :type post_run_script: str, optional
    :param pre_run_script: A pre-run script to execute. Defaults to None
    :type pre_run_script: str, optional
    :param profile_id: The ID of the Lab profile to use when running the notebook. Defaults to None
    :type profile_id: int, optional
    :param options_ids: A list of Lab option IDs to use when running the notebook. Defaults to None
    :type options_ids: list[int], optional
    :param runner_id: The user ID of the person running the notebook schedule. Defaults to None
    :type runner_id: str, optional
    :param source: The source of the schedule files. Defaults to "lab"
    :type source: str, optional
    :param timeout: The maximum time (in seconds) before killing the run. Defaults to None
    :type timeout: int, optional
    :param timezone: The timezone code for the schedule. Defaults to None
    :type timezone: str, optional
    :return: Nothing
    :rtype: None
    """
    if notebook_file:
        assert notebook_file.lower().endswith(
            ".ipynb"
        ), "Notebook file must be a .ipynb file."
        assert (
            source.lower() in ALLOWED_CARD_SOURCES
        ), "Files source must be 'lab' or 'local'."
    if aux_files:
        assert all(
            issubclass(type(x), dict) for x in aux_files
        ), "Auxiliary files must be a list of dictionaries."
        assert all(
            ("source" in d and "target" in d) for d in aux_files
        ), "Auxiliary files must have keys 'source' and 'target'."

    validate_acl(
        "schedule",
        True,
        acl_type_view,
        acl_type_logs,
        acl_type_edit,
        acl_type_decrypt,
    )

    # Collect new schedule configuration
    schedule_config = {
        "owner_id": owner_id,
        "runner_id": runner_id,
        "name": name,
        "timezone": timezone,
        "cron": schedule,
        "timeout": timeout,
        "pool": pool,
        "active": active,
        "concurrent": concurrent,
        "cleanup": cleanup,
        "kernel_metadata_id": kernel_id,
    }

    # Fetch old configuration
    tmp = adaboard.request_adaboard(
        f"schedules/v2/{schedule_id}",
        method=requests.get,
        params={"with_content": True},
    ).json()
    tmp.pop("kernel")
    tmp.pop("owner")
    tmp.pop("runner")
    tmp.pop("last_scheduled_ts")
    tmp.pop("next_scheduled_ts")
    # Reformat and load old ACLs
    old_acls = [
        {
            "acl_action": x["acl_action"],
            "acl_type": x["acl"]["acl_type"],
            "userlist": [
                y["user_id"]
                for y in x["acl"]["userlist"]
                if "user_id" in y.keys()
            ],
            "grouplist": [
                y["user_id"]
                for y in x["acl"]["grouplist"]
                if "user_id" in y.keys()
            ],
        }
        for x in tmp["acls"]
    ]

    old_config = tmp
    old_config.update({"acls": old_acls})
    # Update ACLs
    acl_config = [
        {
            "acl_action": "schedule_view",
            "acl_type": (
                acl_type_view
                if acl_type_view
                else old_config["acls"][0]["acl_type"]
            ),
            "userlist": (
                acl_list_view
                if acl_list_view
                else old_config["acls"][0]["userlist"]
            ),
            "grouplist": (
                acl_list_view
                if acl_list_view
                else old_config["acls"][0]["grouplist"]
            ),
        },
        {
            "acl_action": "schedule_view_logs",
            "acl_type": (
                acl_type_logs
                if acl_type_logs
                else old_config["acls"][1]["acl_type"]
            ),
            "userlist": (
                acl_list_logs
                if acl_list_logs
                else old_config["acls"][1]["userlist"]
            ),
            "grouplist": (
                acl_list_logs
                if acl_list_logs
                else old_config["acls"][1]["grouplist"]
            ),
        },
        {
            "acl_action": "schedule_edit",
            "acl_type": (
                acl_type_edit
                if acl_type_edit
                else old_config["acls"][2]["acl_type"]
            ),
            "userlist": (
                acl_list_edit
                if acl_list_edit
                else old_config["acls"][2]["userlist"]
            ),
            "grouplist": (
                acl_list_edit
                if acl_list_edit
                else old_config["acls"][2]["grouplist"]
            ),
        },
        {
            "acl_action": "schedule_edit_privileged",
            "acl_type": (
                acl_type_decrypt
                if acl_type_decrypt
                else old_config["acls"][3]["acl_type"]
            ),
            "userlist": (
                acl_list_decrypt
                if acl_list_decrypt
                else old_config["acls"][3]["userlist"]
            ),
            "grouplist": (
                acl_list_decrypt
                if acl_list_decrypt
                else old_config["acls"][3]["grouplist"]
            ),
        },
    ]
    schedule_config.update({"acls": acl_config})
    # Update run configuration
    run_config = {
        "inputs": inputs if inputs else old_config["run_config"]["inputs"],
        "options_ids": (
            options_ids
            if options_ids is not None
            else old_config["run_config"]["options_ids"]
        ),
        "profile_id": (
            profile_id
            if profile_id is not None
            else old_config["run_config"]["profile_id"]
        ),
        "scripts": {
            "pre_run_script": (
                pre_run_script
                if pre_run_script is not None
                else old_config["run_config"]["scripts"]["pre_run_script"]
            ),
            "post_run_script": (
                post_run_script
                if post_run_script is not None
                else old_config["run_config"]["scripts"]["post_run_script"]
            ),
        },
    }
    schedule_config.update({"run_config": run_config})

    # Update content
    # First, the main Notebook
    if notebook_file:
        if source.lower() == "lab":
            # Check file size before actually pulling it from the Lab
            try:
                response_props = adaboard.request_adaboard(
                    path="jupyter/files/notebook/content/",
                    params={"path": os.path.dirname(notebook_file)},
                ).json()
                props = [
                    x
                    for x in response_props
                    if x["name"] == os.path.basename(notebook_file)
                ][0]
            except IndexError as e:
                raise IndexError(
                    f"Notebook file '{notebook_file}' not found in the Lab."
                ) from e
            assert (
                props["size"] <= MAX_FILE_SIZE
            ), f"Notebook file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
            nb_file_bin = adaboard.request_adaboard(
                path="jupyter/files/notebook/content/fetch",
                params={"path": notebook_file},
            ).json()["content"]
        else:
            # Check file size before actually opening it
            assert (
                os.path.getsize(notebook_file) <= MAX_FILE_SIZE
            ), f"Notebook file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
            with open(notebook_file, "rb") as f:
                nb_file_bin = base64.b64encode(f.read()).decode("utf-8")

        content = [
            {
                "content": nb_file_bin,
                "content_name": os.path.basename(notebook_file),
                "contenttype_id": 1,
            }
        ]
    else:
        content = [
            x for x in old_config["content"] if x["contenttype_id"] == 1
        ]

    # Next, the auxiliary files
    # Start by collecting or ditching the old ones
    if keep_aux_files:
        old_aux_files = [
            x for x in old_config["content"] if x["contenttype_id"] == 2
        ]
        content.extend(old_aux_files)
    # Then, add the new ones
    if aux_files:
        # In the Lab, paths are relative to the user's home directory
        if source.lower() == "lab":
            # Collect all files within the specified paths
            all_aux_files = []
            for aux_file in aux_files:
                # Directories end with "/"; otherwise they are considered files; no nesting allowed
                if aux_file["source"].endswith("/"):
                    dir_cont = adaboard.request_adaboard(
                        path="jupyter/files/notebook/content/",
                        params={"path": aux_file["source"]},
                    ).json()
                    dir_paths = [
                        {
                            "source": x["path"],
                            "target": aux_file["target"],
                            "size": x["size"],
                        }
                        for x in dir_cont
                        if x["type"] == "file"
                    ]
                    all_aux_files.extend(dir_paths)
                else:
                    response_props = adaboard.request_adaboard(
                        path="jupyter/files/notebook/content/",
                        params={"path": os.path.dirname(aux_file["source"])},
                    ).json()
                    file_path = [
                        {
                            "source": x["path"],
                            "target": aux_file["target"],
                            "size": x["size"],
                        }
                        for x in response_props
                        if x["name"] == os.path.basename(aux_file["source"])
                    ]
                    all_aux_files.extend(file_path)
            # Now we have all the files with their paths and sizes in a single list
            for aux_file in all_aux_files:
                # Check file size before actually pulling it from the Lab
                assert (
                    aux_file["size"] <= MAX_FILE_SIZE
                ), f"Auxiliary file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
                # "content" is the binary; "content_name" determines the target folder
                aux_file_bin = adaboard.request_adaboard(
                    path="jupyter/files/notebook/content/fetch",
                    params={"path": aux_file["source"]},
                ).json()["content"]
                aux_file_name = f"{aux_file['target']}{os.path.basename(aux_file['source'])}"
                tmp = {
                    "content": aux_file_bin,
                    "content_name": aux_file_name,
                    "contenttype_id": 2,
                }
                content.append(tmp)

        # In the local machine, paths are absolute; nesting is allowed
        elif source.lower() == "local":
            all_aux_files = []
            for aux_file in aux_files:
                if os.path.isfile(aux_file["source"]):
                    all_aux_files.append(aux_file)
                elif os.path.isdir(aux_file["source"]):
                    for root, dirs, files in os.walk(aux_file["source"]):
                        for file in files:
                            all_aux_files.append(
                                {
                                    "source": f"{root}/{file}",
                                    "target": f"{root}/".replace(
                                        aux_file["source"], aux_file["target"]
                                    ),
                                }
                            )
            # Now we have all the files with their paths in a single list
            for aux_file in all_aux_files:
                # Check file sizes before actually opening them
                assert (
                    os.path.getsize(aux_file["source"]) <= MAX_FILE_SIZE
                ), f"Auxiliary file size exceeds the maximum allowed ({MAX_FILE_SIZE} bytes). Please reduce the size of the file and try again."
                with open(aux_file["source"], "rb") as f:
                    aux_file_bin = base64.b64encode(f.read()).decode("utf-8")
                # "content" is the binary; "content_name" determines the target folder
                aux_file_name = f"{aux_file['target']}/{os.path.basename(aux_file['source'])}"
                tmp = {
                    "content": aux_file_bin,
                    "content_name": aux_file_name,
                    "contenttype_id": 2,
                }
                content.append(tmp)

    schedule_config.update({"content": content})

    # Finally, build the request payload based on new and old configuration
    payload = {
        k: v if v is not None else old_config[k]
        for k, v in schedule_config.items()
    }

    # return payload
    adaboard.request_adaboard(
        f"schedules/v2/{schedule_id}", method=requests.put, json=payload
    )


def get_all_schedules(include_inactive: bool = False) -> list[dict]:
    """
    Retrieve a list of schedules for all users.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_all_schedules.ipynb) to test this function or build upon it.

    :param include_inactive: Flag whether inactive schedules should be included. Defaults to False.
    :type include_inactive: bool, optional
    :return: A list of notebook schedules in dictionary form.
    :rtype: list[dict]
    """

    all_schedules = adaboard.get_all_pages(
        "schedules/v2", params={"only_active": not include_inactive}
    )
    clean_schedules = [__extract_schedule_data(x) for x in all_schedules]
    return clean_schedules


def get_card_schedules(
    card_id: int, include_inactive: bool = False
) -> list[dict]:
    """
    Retrieve a list of schedules for a specific card.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_card_schedules.ipynb) to test this function or build upon it.

    :param card_id: The card's ID.
    :type card_id: int
    :param include_inactive: Flag whether inactive schedules should be included. Defaults to False.
    :type include_inactive: bool, optional
    :return: A list of notebook schedules in dictionary form.
    :rtype: list[dict]
    """

    all_schedules = adaboard.get_all_pages(
        "schedules/v2",
        params={"only_active": not include_inactive},
    )

    cards_schedules = [
        __extract_schedule_data(x)
        for x in all_schedules
        if x["card_id"] == card_id
    ]

    return cards_schedules


def get_pool_stats() -> list[dict[str, int | str | list]]:
    """
    Retrieve statistics about all run pools.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_pool_stats.ipynb) to test this function or build upon it.
    """

    return adaboard.request_adaboard(
        path="schedules/v2/runs/stats", method=requests.get
    ).json()


def get_run_info(schedule_id: int, run_id: int) -> dict:
    """
    Retrieve information about a specific run.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_run_info.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :param run_id: The run's ID.
    :type run_id: int
    :return: Information about the run.
    :rtype: dict
    """

    run_info = adaboard.request_adaboard(
        f"schedules/v2/runs/{schedule_id}/{run_id}",
    ).json()
    run_info.pop("user")
    run_info["status"] = RUN_STATUS_CODES[str(run_info["status"])]
    return run_info


def get_run_logs(schedule_id: int, run_id: int) -> dict:
    """
    Retrieve the execution and system logs of a specific run.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_run_logs.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :param run_id: The run's ID.
    :type run_id: int
    :return: Information about the run.
    :rtype: dict
    """

    return adaboard.request_adaboard(
        f"schedules/v2/runs/{schedule_id}/{run_id}/logs",
    ).json()


def get_runs_overview(
    schedule_id: int = None, owner_id: int = None
) -> list[dict]:
    """
    Retrieve a list of all schedule runs.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_runs_overview.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID. Defaults to all.
    :type schedule_id: int, optional
    :param owner_id: The schedule's owner ID. Defaults to all.
    :type owner_id: int, optional
    """

    all_runs = adaboard.get_all_pages(
        "schedules/v2/runs/overview",
        params={"user_id": owner_id, "schedule_id": schedule_id},
    )
    try:
        all_runs.pop("owner_image_id")
        for runs in all_runs:
            for run in runs["runs"]:
                run["status"] = RUN_STATUS_CODES[str(run["status"])]
    except (TypeError, KeyError):
        pass
    return all_runs


def get_schedule(
    schedule_id: int,
) -> dict[str, str | int | bool | list | dict]:
    """
    Retrieve a specific notebook schedule.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_schedule.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :return: A list of notebook schedules in dictionary form.
    :rtype: list[dict]
    """

    schedule = adaboard.request_adaboard(
        path=f"schedules/v2/{schedule_id}", method=requests.get
    ).json()
    clean_schedule = __extract_schedule_data(schedule)
    return clean_schedule


def get_schedule_id(name: str, owner_id: str) -> list[int]:
    """
    Find the ID of a specific schedule.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_schedule_id.ipynb) to test this function or build upon it.

    :param name: The schedule's name.
    :type name: str
    :param owner_id: The schedule's owner ID.
    :type owner_id: str
    :return: A list of schedule IDs that match the search parameters.
    :rtype: list[int]
    """

    all_schedules = adaboard.get_all_pages(
        "schedules/v2",
        params={"owner_id": owner_id},
    )

    schedule_id = [
        x["schedule_id"]
        for x in all_schedules
        if x["owner_id"] == owner_id and x["name"] == name
    ]
    if not schedule_id:
        raise ValueError(
            f"No schedule found with name '{name}' from user '{owner_id}'."
        )
    return schedule_id


def get_user_schedules(
    user_id: str = "", include_inactive: bool = False
) -> list[dict]:
    """
    Retrieve a list of schedules for a specific user.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/get_user_schedules.ipynb) to test this function or build upon it.

    :param user_id: The user's ID. Defaults to the current user.
    :type user_id: str, optional
    :param include_inactive: Flag whether inactive schedules should be included. Defaults to False.
    :type include_inactive: bool, optional
    :return: A list of notebook schedules in dictionary form.
    :rtype: list[dict]
    """
    user_id = user_id or adaboard.get_user()["user_id"]

    get_user_schedules = adaboard.get_all_pages(
        "schedules/v2",
        params={"user_id": user_id, "only_active": not include_inactive},
    )
    clean_schedules = [__extract_schedule_data(x) for x in get_user_schedules]
    return clean_schedules


def start_run(schedule_id: int) -> int:
    """
    Trigger a run of a specific notebook schedule.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/start_run.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :return: Schedule run's ID
    :rtype: int
    """

    res = adaboard.request_adaboard(
        f"schedules/v2/runs/{schedule_id}/trigger", method=requests.post
    ).json()

    return res["id"]


def stop_run(schedule_id: int, run_id: int) -> None:
    """
    Stop a specific run of a notebook schedule.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/schedules/stop_run.ipynb) to test this function or build upon it.

    :param schedule_id: The schedule's ID.
    :type schedule_id: int
    :param run_id: The run's ID.
    :type run_id: int
    :return: Nothing.
    :rtype: None
    """

    adaboard.request_adaboard(
        f"schedules/v2/runs/{schedule_id}/{run_id}/stop", method=requests.post
    ).json()


def __extract_schedule_data(raw_data: dict) -> dict:
    """
    Helper function to discard the unnecessary fields from the raw schedule data.

    :param raw_data: Raw schedule data.
    :type raw_data: dict
    :return: Clean schedule data
    :rtype: dict
    """

    raw_data.pop("owner")
    raw_data.pop("runner")
    raw_data.pop("kernel")
    acls = [
        {
            "acl_action": x["acl_action"],
            "acl_type": x["acl"]["acl_type"],
            "userlist": [
                y["user_id"]
                for y in x["acl"]["userlist"]
                if "user_id" in y.keys()
            ],
            "grouplist": [
                y["user_id"]
                for y in x["acl"]["grouplist"]
                if "user_id" in y.keys()
            ],
        }
        for x in raw_data["acls"]
    ]
    raw_data["acls"] = acls
    return raw_data
