"""AdaLab Shared Volumes Module."""

from typing import Optional

import requests
from requests import Response

from adalib.adaboard import request_adaboard

from ..utils import validate_acl


def get_all_volumes(
    include_all: bool = False, allowed_to_mount: bool = True
) -> list[dict[str,]]:
    """Get all AdaLab Shared Volumes currently available.

    :param include_all: If True, return all volumes. If False, return only volumes
        that the user is allowed to view.
    :type include_all: bool
    :param allowed_to_mount: If True, return only volumes that the user is allowed to
        mount. If False, return all volumes.
    :type allowed_to_mount: bool

    :return: List of AdaLab Shared Volumes.
    :rtype: list[dict[str,]]
    """
    params = {"can_mount": allowed_to_mount}
    if not include_all:
        user_id = request_adaboard(path="users/self").json()["user_id"]
        params["user_id"] = user_id

    return request_adaboard("volumes", params=params).json()


def get_volume(volume_id: int) -> dict[str,]:
    """Get a specific AdaLab Shared Volume.

    :param volume_id: The ID of the volume to get.
    :type volume_id: int
    :return: The AdaLab Shared Volume.
    :rtype: dict[str,]
    """
    return request_adaboard(f"volumes/{volume_id}").json()


def get_all_volume_mounts_for_app(app_id: str) -> list[dict[str,]]:
    """Get all AdaLab Shared Volumes mounted to a specific AdaLab App.

    :param app_id: The ID of the AdaLab App.
    :type app_id: str
    :return: List of AdaLab Shared Volume mounts to the AdaLab App.
    :rtype: list[dict[str,]]
    """
    return request_adaboard(
        "volumes/mounts/app", params={"app_id": app_id}
    ).json()


def get_all_volume_mounts_for_user(
    user_id: Optional[str] = None,
) -> list[dict[str,]]:
    """Get all AdaLab Shared Volumes mounted to a specific AdaLab User's Lab.

    :param user_id: The ID of the AdaLab User.
    :type user_id: Optional[str]
    :return: List of AdaLab Shared Volume mounts to the AdaLab User's Lab.
    :rtype: list[dict[str,]]
    """
    params = dict()
    if user_id is not None:
        params["user_id"] = user_id

    return request_adaboard("volumes/mounts/user", params=params).json()


def create_volume(
    name: str,
    description: str,
    size: int,
    view_acl_type: str = "public",
    view_acl_list: list[str] = [],
    mount_acl_type: str = "public",
    mount_acl_list: list[str] = [],
    edit_acl_type: str = "public",
    edit_acl_list: list[str] = [],
) -> int:
    """Create a new AdaLab Shared Volume.

    :param name: The name of the volume.
    :type name: str
    :param description: The description of the volume.
    :type description: str
    :param size: The size of the volume in GB.
    :type size: int
    :param view_acl_type: The ACL type for viewing the volume. Default is "public".
    :type view_acl_type: str
    :param view_acl_list: The list of users or groups that can view the volume.
    :type view_acl_list: list[str]
    :param mount_acl_type: The ACL type for mounting the volume. Default is "public".
    :type mount_acl_type: str
    :param mount_acl_list: The list of users or groups that can mount the volume.
    :type mount_acl_list: list[str]
    :param edit_acl_type: The ACL type for editing the volume. Default is "public".
    :type edit_acl_type: str
    :param edit_acl_list: The list of users or groups that can edit the volume.
    :type edit_acl_list: list[str]

    :return: The ID of the created volume.
    :rtype: int
    """
    validate_acl("volume", False, view_acl_type, mount_acl_type, edit_acl_type)
    assert size >= 1, "Volume size must be at least 1GB"

    acls = [
        {
            "acl_action": "volume_view",
            "acl_type": view_acl_type,
            "userlist": view_acl_list if view_acl_type == "userlist" else [],
            "grouplist": view_acl_list if view_acl_type == "grouplist" else [],
        },
        {
            "acl_action": "volume_mount",
            "acl_type": mount_acl_type,
            "userlist": mount_acl_list if mount_acl_type == "userlist" else [],
            "grouplist": (
                mount_acl_list if mount_acl_type == "grouplist" else []
            ),
        },
        {
            "acl_action": "volume_edit",
            "acl_type": edit_acl_type,
            "userlist": edit_acl_list if edit_acl_type == "userlist" else [],
            "grouplist": edit_acl_list if edit_acl_type == "grouplist" else [],
        },
    ]
    payload = {
        "name": name,
        "description": description,
        "size": size,
        "acls": acls,
    }

    return request_adaboard(
        "volumes", method=requests.post, json=payload
    ).json()["id"]


def mount_volume_to_user_lab(
    volume_id: int,
    mount_path: str,
    user_id: Optional[str] = None,
    read_only: bool = False,
    from_root: bool = False,
) -> Response:
    """Create a new AdaLab Shared Volume mount to a specific AdaLab User's Lab.

    :param volume_id: The ID of the volume to mount.
    :type volume_id: int
    :param mount_path: The path to mount the volume to.
    :type mount_path: str
    :param user_id: The ID of the AdaLab User. If None, the current user is used.
    :type user_id: Optional[str]
    :param read_only: If True, mount the volume as read-only. Default is False.
    :type read_only: bool
    :param from_root: If True, mount the volume from the root. Default is False.
    :type from_root: bool

    :return: The response from the request.
    :rtype: Response
    """
    if user_id is None:
        user_id = request_adaboard(path="users/self").json()["user_id"]

    payload = {
        "mount_path": mount_path,
        "read_only": read_only,
        "from_root": from_root,
        "user_id": user_id,
    }
    return request_adaboard(
        f"volumes/{volume_id}/mount", method=requests.post, json=payload
    )


def update_volume(
    volume_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    size: Optional[int] = None,
    view_acl_type: Optional[str] = None,
    view_acl_list: list[str] = [],
    mount_acl_type: Optional[str] = None,
    mount_acl_list: list[str] = [],
    edit_acl_type: Optional[str] = None,
    edit_acl_list: list[str] = [],
) -> Response:
    """Update an AdaLab Shared Volume.

    :param volume_id: The ID of the volume to update.
    :type volume_id: int
    :param name: The new name of the volume.
    :type name: Optional[str]
    :param description: The new description of the volume.
    :type description: Optional[str]
    :param size: The new size of the volume in GB.
    :type size: Optional[int]
    :param view_acl_type: The new ACL type for viewing the volume.
    :type view_acl_type: Optional[str]
    :param view_acl_list: The new list of users or groups that can view the volume.
    :type view_acl_list: list[str]
    :param mount_acl_type: The new ACL type for mounting the volume.
    :type mount_acl_type: Optional[str]
    :param mount_acl_list: The new list of users or groups that can mount the volume.
    :type mount_acl_list: list[str]
    :param edit_acl_type: The new ACL type for editing the volume.
    :type edit_acl_type: Optional[str]
    :param edit_acl_list: The new list of users or groups that can edit the volume.
    :type edit_acl_list: list[str]

    :return: The response from the request.
    :rtype: Response
    """
    old_volume = get_volume(volume_id=volume_id)

    # Build ACLs payload
    old_acls = old_volume["acls"]
    acls = []

    for _acl_type, _acl_list, _acl_action in [
        (view_acl_type, view_acl_list, "volume_view"),
        (mount_acl_type, mount_acl_list, "volume_mount"),
        (edit_acl_type, edit_acl_list, "volume_edit"),
    ]:
        if _acl_type is not None:
            validate_acl("volume", False, _acl_type)
            acls.append(
                {
                    "acl_action": _acl_action,
                    "acl_type": _acl_type,
                    "userlist": _acl_list if _acl_type == "userlist" else [],
                    "grouplist": _acl_list if _acl_type == "grouplist" else [],
                }
            )
        else:
            old_view_acl = [
                x for x in old_acls if x["acl_action"] == _acl_action
            ][0]
            acls.append(
                {
                    "acl_action": old_view_acl["acl_action"],
                    "acl_type": old_view_acl["acl_type"],
                    "userlist": [
                        x["user_id"] for x in old_view_acl["userlist"]
                    ],
                    "grouplist": [
                        x["group_id"] for x in old_view_acl["grouplist"]
                    ],
                }
            )

    payload = {
        "name": name or old_volume["name"],
        "description": description or old_volume["description"],
        "size": size or old_volume["size"],
        "acls": acls,
    }
    return request_adaboard(
        f"volumes/{volume_id}", method=requests.put, json=payload
    )


def update_mounted_volume_to_user_lab(
    volume_id: int,
    user_id: Optional[str] = None,
    mount_path: Optional[str] = None,
    read_only: bool = False,
    from_root: bool = False,
) -> Response:
    """Update an AdaLab Shared Volume mount to a specific AdaLab User's Lab.

    :param volume_id: The ID of the volume to update.
    :type volume_id: int
    :param user_id: The ID of the AdaLab User. If None, the current user is used.
    :type user_id: Optional[str]
    :param mount_path: The new path to mount the volume to.
    :type mount_path: Optional[str]
    :param read_only: If True, mount the volume as read-only. Default is False.
    :type read_only: bool
    :param from_root: If True, mount the volume from the root. Default is False.
    :type from_root: bool

    :return: The response from the request.
    :rtype: Response
    """
    if user_id is None:
        user_id = request_adaboard(path="users/self").json()["user_id"]

    all_user_mounts = get_all_volume_mounts_for_user(user_id=user_id)
    spums = [x for x in all_user_mounts if x["volume_id"] == volume_id]
    assert len(spums) == 1, "User is not mounted to this volume"
    old_user_mount = spums[0]

    payload = {
        "mount_path": mount_path or old_user_mount["mount_path"],
        "read_only": read_only or old_user_mount["read_only"],
        "from_root": from_root or old_user_mount["from_root"],
        "user_id": user_id,
    }
    return request_adaboard(
        f"volumes/{volume_id}/mount", method=requests.put, json=payload
    )


def delete_volume(volume_id: int) -> Response:
    """Delete an AdaLab Shared Volume.

    :param volume_id: The ID of the volume to delete.
    :type volume_id: int
    :return: The response from the request.
    :rtype: Response
    """
    return request_adaboard(f"volumes/{volume_id}", method=requests.delete)


def unmount_volume_from_user_lab(
    volume_id: int, user_id: Optional[str] = None
) -> Response:
    """Unmount an AdaLab Shared Volume from a specific AdaLab User's Lab.

    :param volume_id: The ID of the volume to unmount.
    :type volume_id: int
    :param user_id: The ID of the AdaLab User. If None, the current user is used.
    :type user_id: Optional[str]

    :return: The response from the request.
    :rtype: Response
    """
    if user_id is None:
        user_id = request_adaboard(path="users/self").json()["user_id"]

    return request_adaboard(
        f"volumes/{volume_id}/mount",
        method=requests.delete,
        params={"user_id": user_id},
    )
