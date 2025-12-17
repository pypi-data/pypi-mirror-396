import base64
import json
import os
import re
from typing import Optional, Union

import requests

from .. import adaboard
from ..keywords import create_keywords
from ..utils import validate_acl

ALLOWED_CARD_SOURCES = ["lab", "local"]
ALLOWED_CARD_TYPES = {"notebook": 1, "voila": 2}
MAX_FILE_SIZE = 5000000


def _create_keywords_if_not_exist(keywords: list[str]) -> dict[str, int]:
    """Helper function to create keywords if they do not exist in the Gallery.

    :param keywords: the list of keywords to be created
    :type keywords: list
    :return: the dictionary of all keywords and their IDs
    :rtype: dict[str, int]
    """
    all_kws = {
        x["keyword"]: x["keyword_id"]
        for x in adaboard.request_adaboard(
            path="keywords", method=requests.get
        ).json()
    }
    for kw in keywords:
        if kw not in all_kws:
            new_kw = create_keywords(new_keywords=kw)[0]
            all_kws[kw] = new_kw["keyword_id"]

    return all_kws


def create_card(  # noqa: C901
    name: str,
    description: str,
    cardtype: str,
    notebook_file: str,
    acl_type_view: str = "public",
    acl_list_view: list[str] = [],
    acl_type_launch: str = "public",
    acl_list_launch: list[str] = [],
    acl_type_edit: str = "public",
    acl_list_edit: list[str] = [],
    aux_files: list[dict[str, str]] = [{"source": "", "target": ""}],
    coauthors: list[str] = [],
    include_kernel: bool = True,
    keywords: list[str] = [],
    picture_id: int = 0,
    reviewers: list[str] = [],
    source: str = "lab",
) -> int:
    """
    Create a card in the AdaLab Gallery. Note that only Notebook and Voilà cards are supported.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/create_card.ipynb) to test this function or build upon it.

    :param name: the name of the card
    :type name: str
    :param description: the card description (tip: supports Markdown)
    :type description: str
    :param cardtype: the type of card (tip: must be "notebook" or "voila")
    :type cardtype: str
    :param notebook_file: the path to the main notebook file to be added to the card
    :type notebook_file: str
    :param acl_type_view: the ACL type for viewing the card, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_view: str, optional
    :param acl_list_view: the list of users/groups allowed to view the card, defaults to []
    :type acl_list_view: list, optional
    :param acl_type_launch: the ACL type for launching the card, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_launch: str, optional
    :param acl_list_launch: the list of users/groups allowed to launch the card, defaults to []
    :type acl_list_launch: list, optional
    :param acl_type_edit: the ACL type for editing the card, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_edit: str, optional
    :param acl_list_edit: the list of users/groups allowed to edit the card, defaults to []
    :type acl_list_edit: list, optional
    :param aux_files: the list of paths to the auxiliary files to be added to the card, defaults to {}
    :type aux_files: dict, optional
    :param coauthors: the other card authors, defaults to []
    :type coauthors: list, optional
    :param include_kernel: whether to link the Notebook with the kernel used during its development, defaults to True
    :type include_kernel: bool, optional
    :param keywords: the keywords related to the card, defaults to [] (tip: must exist in the Gallery)
    :type keywords: list, optional
    :param picture_id: the ID of the picture to be used for the card, defaults to 0
    :type picture_id: int, optional
    :param reviewers: the list of users who will review the card, defaults to []
    :type reviewers: list, optional
    :param source: the source of the card files, defaults to "lab" (tip: must be "lab" or "local")
    :type source: str, optional
    :return: the ID of the card
    :rtype: int
    """

    assert (
        cardtype.lower() in ALLOWED_CARD_TYPES
    ), "Card type must be 'notebook' or 'voila'."
    assert notebook_file.lower().endswith(
        ".ipynb"
    ), "Notebook file must be a .ipynb file."
    assert (
        source.lower() in ALLOWED_CARD_SOURCES
    ), "Files source must be 'lab' or 'local'."
    validate_acl("card", False, acl_type_view, acl_type_launch, acl_type_edit)
    assert all(
        issubclass(type(x), dict) for x in aux_files
    ), "Auxiliary files must be a list of dictionaries."
    assert all(
        ("source" in d and "target" in d) for d in aux_files
    ), "Auxiliary files must have keys 'source' and 'target'."

    cardtype_id = ALLOWED_CARD_TYPES[cardtype.lower()]

    keywords_id = []
    if keywords:
        kws = _create_keywords_if_not_exist(keywords=keywords)
        for kw in keywords:
            keywords_id.append(kws[kw])

    # Main notebook file; read binary from Lab or local machine
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

    if not include_kernel:
        nb_file_dict = json.loads(
            base64.b64decode(nb_file_bin).decode("utf-8")
        )
        nb_file_dict["metadata"]["kernelspec"] = {
            "display_name": "",
            "name": "",
        }
        nb_file_bin = base64.b64encode(
            json.dumps(nb_file_dict).encode("utf-8")
        ).decode("utf-8")

    content = [
        {
            "content": nb_file_bin,
            "content_name": os.path.basename(notebook_file),
            "contenttype_id": 1,
            "path": notebook_file if source.lower() == "lab" else None,
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
                    "path": aux_file["source"],
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

    acl_config = [
        {
            "acl_action": "card_view",
            "acl_type": acl_type_view if acl_type_view else "public",
            "userlist": acl_list_view if acl_type_view == "userlist" else [],
            "grouplist": acl_list_view if acl_type_view == "grouplist" else [],
        },
        {
            "acl_action": "card_launch",
            "acl_type": acl_type_launch if acl_type_launch else "public",
            "userlist": (
                acl_list_launch if acl_type_launch == "userlist" else []
            ),
            "grouplist": (
                acl_list_launch if acl_type_launch == "grouplist" else []
            ),
        },
        {
            "acl_action": "card_edit",
            "acl_type": acl_type_edit if acl_type_edit else "public",
            "userlist": acl_list_edit if acl_type_edit == "userlist" else [],
            "grouplist": acl_list_edit if acl_type_edit == "grouplist" else [],
        },
    ]
    payload = {
        "name": name,
        "description": description,
        "cardtype_id": cardtype_id,
        "author_id": adaboard.get_user()["user_id"],
        "owner_id": adaboard.get_user()["user_id"],
        "image_id": picture_id,
        "keywords": keywords_id,
        "coauthors": coauthors,
        "acls": acl_config,
        "content": content,
        "reviewers": reviewers,
    }

    response = adaboard.request_adaboard(
        path="cards",
        method=requests.post,
        json=payload,
    ).json()

    return response["id"]


def create_card_group(
    name: str,
    description: str,
    cards_id: list[int],
    acl_type_view: str = "public",
    acl_list_view: list[str] = [],
    acl_type_edit: str = "public",
    acl_list_edit: list[str] = [],
    coauthors: list[str] = [],
    keywords: list[str] = [],
    picture_id: int = 0,
    reviewers: list[str] = [],
) -> int:
    """
    Create a card group in the AdaLab Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/create_card_group.ipynb) to test this function or build upon it.

    :param name: the name of the group
    :type name: str
    :param description: description of the group (tip: supports Markdown)
    :type description: str
    :param cards_id: the IDs of the cards to be added to the group, in order of appearance
    :type cards_id: list
    :param acl_type_view: the ACL type for viewing the card group, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_view: str, optional
    :param acl_list_view: the list of users/groups allowed to view the card group, defaults to []
    :type acl_list_view: list, optional
    :param acl_type_launch: the ACL type for launching the card group, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :param acl_type_edit: the ACL type for editing the card group, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_edit: str, optional
    :param acl_list_edit: the list of users/groups allowed to edit the card group, defaults to []
    :type acl_list_edit: list, optional
    :param coauthors: the other group authors, defaults to []
    :type coauthors: list, optional
    :param keywords: the keywords related to the card group, defaults to [] (tip: must exist in the Gallery)
    :type keywords: list, optional
    :param picture_id: the ID of the picture to be used for the card group, defaults to 0
    :type picture_id: int, optional
    :param reviewers: the list of users who will review the card group, defaults to []
    :type reviewers: list, optional
    :return: the ID of the card group
    :rtype: int
    """
    validate_acl("card", False, acl_type_view, acl_type_edit)

    keywords_id = []
    if keywords:
        kws = _create_keywords_if_not_exist(keywords=keywords)
        for kw in keywords:
            keywords_id.append(kws[kw])

    acl_config = [
        {
            "acl_action": "card_view",
            "acl_type": acl_type_view if acl_type_view else "public",
            "userlist": acl_list_view if acl_type_view == "userlist" else [],
            "grouplist": acl_list_view if acl_type_view == "grouplist" else [],
        },
        {
            "acl_action": "card_launch",
            "acl_type": "logged_in",
            "userlist": [],
            "grouplist": [],
        },
        {
            "acl_action": "card_edit",
            "acl_type": acl_type_edit if acl_type_edit else "public",
            "userlist": acl_list_edit if acl_type_edit == "userlist" else [],
            "grouplist": acl_list_edit if acl_type_edit == "grouplist" else [],
        },
    ]

    group_cards = []
    for card_id in cards_id:
        group_cards.append(
            {"card_id": card_id, "order_id": cards_id.index(card_id)}
        )

    payload = {
        "name": name,
        "description": description,
        "cardtype_id": 4,
        "card_group_cards": group_cards,
        "author_id": adaboard.get_user()["user_id"],
        "owner_id": adaboard.get_user()["user_id"],
        "image_id": picture_id,
        "keywords": keywords_id,
        "coauthors": coauthors,
        "acls": acl_config,
        "reviewers": reviewers,
    }

    response = adaboard.request_adaboard(
        path="cards",
        method=requests.post,
        json=payload,
    ).json()

    return response["id"]


def create_url_card(
    name: str,
    description: str,
    remote_url: str,
    url_subtype: str,
    acl_type_view: str = "public",
    acl_list_view: list[str] = [],
    acl_type_launch: str = "public",
    acl_list_launch: list[str] = [],
    acl_type_edit: str = "public",
    acl_list_edit: list[str] = [],
    coauthors: list[str] = [],
    keywords: list[str] = [],
    picture_id: int = 0,
    reviewers: list[str] = [],
) -> int:
    """Create a URL-type card in the AdaLab Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/create_url_card.ipynb) to test this function or build upon it.

    :param name: the name of the card
    :type name: str
    :param description: the card description (tip: supports Markdown)
    :type description: str
    :param remote_url: URL to point the card to
    :type remote_url: str
    :param url_subtype: URL subtype (tip: must exist in the Gallery)
    :type url_subtype: str
    :param acl_type_view: the ACL type for viewing the card, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_view: str, optional
    :param acl_list_view: the list of users/groups allowed to view the card, defaults to []
    :type acl_list_view: list, optional
    :param acl_type_launch: the ACL type for launching the card, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_launch: str, optional
    :param acl_list_launch: the list of users/groups allowed to launch the card, defaults to []
    :type acl_list_launch: list, optional0
    :param acl_type_edit: the ACL type for editing the card, defaults to "public" (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_edit: str, optional
    :param acl_list_edit: the list of users/groups allowed to edit the card, defaults to []
    :type acl_list_edit: list, optional
    :param coauthors: the other card authors, defaults to []
    :type coauthors: list, optional
    :param keywords: the keywords related to the card, defaults to [] (tip: must exist in the Gallery)
    :type keywords: list, optional
    :param picture_id: the ID of the picture to be used for the card, defaults to 0
    :type picture_id: int, optional
    :param reviewers: the list of users who will review the card, defaults to []
    :type reviewers: list, optional
    :return: the ID of the card
    :rtype: int
    """

    validate_acl("card", False, acl_type_view, acl_type_launch, acl_type_edit)

    try:
        url_subtypes = adaboard.request_adaboard(
            "url-card-subtypes", method=requests.get
        ).json()
        url_subtype_id = [
            x["urlcardsubtype_id"]
            for x in url_subtypes
            if x["name"] == url_subtype
        ][0]
    except IndexError as e:
        raise IndexError(
            f"URL subtype '{url_subtype}' not found in the Gallery. Please use an existing URL subtype."
        ) from e

    keywords_id = []
    if keywords:
        kws = _create_keywords_if_not_exist(keywords=keywords)
        for kw in keywords:
            keywords_id.append(kws[kw])

    acl_config = [
        {
            "acl_action": "card_view",
            "acl_type": acl_type_view if acl_type_view else "public",
            "userlist": acl_list_view if acl_type_view == "userlist" else [],
            "grouplist": acl_list_view if acl_type_view == "grouplist" else [],
        },
        {
            "acl_action": "card_launch",
            "acl_type": acl_type_launch if acl_type_launch else "public",
            "userlist": (
                acl_list_launch if acl_type_launch == "userlist" else []
            ),
            "grouplist": (
                acl_list_launch if acl_type_launch == "grouplist" else []
            ),
        },
        {
            "acl_action": "card_edit",
            "acl_type": acl_type_edit if acl_type_edit else "public",
            "userlist": acl_list_edit if acl_type_edit == "userlist" else [],
            "grouplist": acl_list_edit if acl_type_edit == "grouplist" else [],
        },
    ]

    payload = {
        "name": name,
        "description": description,
        "cardtype_id": 3,
        "remote_url": remote_url,
        "url_subtype_id": url_subtype_id,
        "author_id": adaboard.get_user()["user_id"],
        "owner_id": adaboard.get_user()["user_id"],
        "image_id": picture_id,
        "keywords": keywords_id,
        "coauthors": coauthors,
        "acls": acl_config,
        "reviewers": reviewers,
    }

    response = adaboard.request_adaboard(
        "cards", json=payload, method=requests.post
    ).json()

    return response["id"]


def create_url_subtype(
    name: str = "",
    description: str = "",
    picture_id: int = 0,
    protected: bool = False,
) -> int:
    """
    Create a new URL subtype in the AdaLab Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/cards/create_url_subtype.ipynb) to test this function or build upon it.

    :param name: the name of the URL subtype
    :type name: str, optional
    :param description: the description of the URL subtype
    :type description: str, optional
    :param picture_id: the ID of the picture to be used for the card
    :type picture_id: int, optional
    :param protected: whether to protect the URL subtype from deletion, defaults to False
    :type protected: bool, optional
    :return: the ID of the URL subtype
    :rtype: int
    """

    payload = {
        "name": name,
        "description": description,
        "image_id": picture_id,
        "protected": protected,
    }
    response = adaboard.request_adaboard(
        "url-card-subtypes", json=payload, method=requests.post
    ).json()

    return response["id"]


def delete_card(card_id: int) -> None | str:
    """
    Delete a card from the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/delete_card.ipynb) to test this function or build upon it.

    :param card_id: the id of the card to be deleted
    :type card_id: int
    :return: Nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"cards/{card_id}",
        method=requests.delete,
    )

    return None


def delete_card_group(group_id: int) -> None:
    """
    Delete a card group from the AdaLab Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/delete_card_group.ipynb) to test this function or build upon it.

    :param group_id: the ID of the group to be deleted
    :type group_id: int
    """

    adaboard.request_adaboard(
        path=f"cards/{group_id}",
        method=requests.delete,
    )

    return None


def delete_url_subtype(url_subtype_id: int) -> None:
    """
    Delete a URL subtype from the AdaLab Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/cards/delete_url_subtype.ipynb) to test this function or build upon it.

    :param url_subtype_id: the ID of the URL subtype
    :type url_subtype_id: int
    :return: Nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"url-card-subtypes/{url_subtype_id}",
        method=requests.delete,
    )

    return None


def edit_card(  # noqa: C901
    card_id: int,
    name: str = None,
    description: str = None,
    cardtype: str = None,
    notebook_file: str = None,
    acl_type_view: str = None,
    acl_list_view: list[str] = None,
    acl_type_launch: str = None,
    acl_list_launch: list[str] = None,
    acl_type_edit: str = None,
    acl_list_edit: list[str] = None,
    aux_files: dict[str, str] = None,
    coauthors: list[str] = None,
    keep_aux_files: bool = True,
    keywords: list[str] = None,
    picture_id: int = None,
    reviewers: list[str] = None,
    source: str = "lab",
) -> None:
    """
    Edit a card in the AdaLab Gallery. Note that unspecified fields will not be changed.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/edit_card.ipynb) to test this function or build upon it.

    :param card_id: the ID of the card
    :type card_id: int
    :param name: the new name of the card
    :type name: str, optional
    :param description: the new description of the card (tip: supports Markdown)
    :type description: str, optional
    :param cardtype: the type of card (tip: must be "notebook" or "voila")
    :type cardtype: str, optional
    :param notebook_file: the path to the new main notebook file to be added to the card
    :type notebook_file: str, optional
    :param acl_type_view: the ACL type for viewing the card (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_view: str, optional
    :param acl_list_view: the list of users/groups allowed to view the card
    :type acl_list_view: list, optional
    :param acl_type_launch: the ACL type for launching the card (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_launch: str, optional
    :param acl_list_launch: the list of users/groups allowed to launch the card
    :type acl_list_launch: list, optional
    :param acl_type_edit: the ACL type for editing the card (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_edit: str, optional
    :param acl_list_edit: the list of users/groups allowed to edit the card
    :type acl_list_edit: list, optional
    :param aux_files: the list of paths to the new auxiliary files to be added to the card
    :type aux_files: dict, optional
    :param coauthors: the other card authors
    :type coauthors: list, optional
    :param keep_aux_files: whether to keep the existing auxiliary files or not, defaults to True
    :type keep_aux_files: bool, optional
    :param keywords: the keywords related to the card, defaults to [] (tip: must exist in the Gallery)
    :type keywords: list, optional
    :param picture_id: the ID of the picture to be used for the card
    :type picture_id: int, optional
    :param reviewers: the list of users who will review the card
    :type reviewers: list, optional
    :param source: the source of the card files, defaults to "lab" (tip: must be "lab" or "local")
    :type source: str, optional
    :return: nothing
    :rtype: None
    """
    assert (
        cardtype is None or cardtype.lower() in ALLOWED_CARD_TYPES
    ), "Card type must be 'notebook' or 'voila'."
    assert notebook_file is None or notebook_file.lower().endswith(
        ".ipynb"
    ), "Notebook file must be a .ipynb file."
    assert (
        source.lower() in ALLOWED_CARD_SOURCES
    ), "Files source must be 'lab' or 'local'."

    validate_acl("card", True, acl_type_view, acl_type_launch, acl_type_edit)
    assert aux_files is None or all(
        issubclass(type(x), dict) for x in aux_files
    ), "Auxiliary files must be a list of dictionaries."
    assert aux_files is None or all(
        ("source" in d and "target" in d) for d in aux_files
    ), "Auxiliary files must have keys 'source' and 'target'."

    try:
        cardtype_id = ALLOWED_CARD_TYPES[cardtype.lower()]
    except AttributeError:
        cardtype_id = None

    keywords_id = []
    if keywords:
        kws = _create_keywords_if_not_exist(keywords=keywords)
        for kw in keywords:
            keywords_id.append(kws[kw])

    # Collect new configuration options
    card_config = {
        "name": name,
        "description": description,
        "cardtype_id": cardtype_id,
        "author_id": None,
        "owner_id": None,
        "image_id": picture_id,
        "keywords": keywords_id,
        "coauthors": coauthors,
        "acls": None,
        "content": None,
        "reviewers": reviewers,
    }
    # Fetch old configuration
    old_config = adaboard.request_adaboard(
        path=f"cards/{card_id}", method=requests.get
    ).json()

    # ACLs need to be re-formatted for the PUT request
    old_acls = []
    for tmp in old_config["acls"]:
        if tmp["acl_type"] == "grouplist":
            tmp["grouplist"] = [x["group_id"] for x in tmp["grouplist"]]
        elif tmp["acl_type"] == "userlist":
            tmp["userlist"] = [x["user_id"] for x in tmp["userlist"]]
        else:
            tmp["grouplist"] = []
            tmp["userlist"] = []
        old_acls.append(tmp)
    old_config["acls"] = old_acls
    # Collect the new ACLs
    acl_config = [
        {
            "acl_action": "card_view",
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
            "acl_action": "card_launch",
            "acl_type": (
                acl_type_launch
                if acl_type_launch
                else old_config["acls"][1]["acl_type"]
            ),
            "userlist": (
                acl_list_launch
                if acl_type_launch
                else old_config["acls"][1]["userlist"]
            ),
            "grouplist": (
                acl_list_launch
                if acl_type_launch
                else old_config["acls"][1]["grouplist"]
            ),
        },
        {
            "acl_action": "card_edit",
            "acl_type": (
                acl_type_edit
                if acl_type_edit
                else old_config["acls"][2]["acl_type"]
            ),
            "userlist": (
                acl_list_edit
                if acl_type_edit
                else old_config["acls"][2]["userlist"]
            ),
            "grouplist": (
                acl_list_edit
                if acl_type_edit
                else old_config["acls"][2]["grouplist"]
            ),
        },
    ]
    card_config["acls"] = acl_config
    # Author, coauthors and reviewers need to be re-formatted for the PUT request
    old_author = old_config["author"]["user_id"]
    old_config["author"] = old_author
    old_coauthors = [
        coauthor["user_id"] for coauthor in old_config["coauthors"]
    ]
    old_config["coauthors"] = old_coauthors
    old_reviewers = [
        reviewer["user_id"] for reviewer in old_config["reviewers"]
    ]
    old_config["reviewers"] = old_reviewers
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
                "path": notebook_file if source.lower() == "lab" else None,
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
                    "path": aux_file["source"],
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

    card_config["content"] = content
    # Build request payload combining new and old options
    payload = {
        k: v if v is not None else old_config[k]
        for k, v in card_config.items()
    }
    adaboard.request_adaboard(
        f"cards/{card_id}", method=requests.put, json=payload
    )
    return None


def edit_card_group(
    group_id: int,
    name: str = None,
    description: str = None,
    cards_id: list[int] = None,
    acl_type_view: str = None,
    acl_list_view: list[str] = None,
    acl_type_edit: str = None,
    acl_list_edit: list[str] = None,
    coauthors: list[str] = None,
    keywords: list[str] = None,
    picture_id: int = None,
    reviewers: list[str] = None,
) -> None:
    """
    Edit a card group in the AdaLab Gallery. Note that the unspecified fields will not be modified.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/edit_card_group.ipynb) to test this function or build upon it.

    :param group_id: the ID of the card group
    :type group_id: int
    :param name: the new name of the card group
    :type name: str, optional
    :param description: the new description of the card group
    :type description: str, optional
    :param cards_id: the IDs of the cards to be added to the group
    :type cards_id: list, optional
    :param acl_type_view: the ACL type for viewing the card group (tip: must be "public", "logged_in", "userlist" or "grouplist"), defaults to None
    :type acl_type_view: str, optional
    :param acl_list_view: the list of users/groups allowed to view the card group
    :type acl_list_view: list, optional
    :param acl_type_edit: the ACL type for editing the card group (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_edit: str, optional
    :param acl_list_edit: the list of users/groups allowed to edit the card group
    :type acl_list_edit: list, optional
    :param coauthors: the other authors of the card group
    :type coauthors: list, optional
    :param keywords: the keywords related to the card group
    :type keywords: list, optional
    :param picture_id: the ID of the new picture to be used for the card group
    :type picture_id: int, optional
    :param reviewers: the list of users who will review the card group
    :type reviewers: list, optional
    """

    validate_acl("card", True, acl_type_view, acl_type_edit)

    keywords_id = []
    if keywords:
        kws = _create_keywords_if_not_exist(keywords=keywords)
        for kw in keywords:
            keywords_id.append(kws[kw])

    # Collect new configuration options
    card_group_config = {
        "name": name,
        "description": description,
        "cardtype_id": 4,
        "card_group_cards": None,
        "author_id": None,
        "owner_id": None,
        "image_id": picture_id,
        "keywords": keywords_id,
        "coauthors": coauthors,
        "acls": None,
        "reviewers": reviewers,
    }
    # Fetch old configuration
    old_config = adaboard.request_adaboard(
        path=f"cards/{group_id}", method=requests.get
    ).json()

    # ACLs need to be re-formatted for the PUT request
    old_acls = []
    for tmp in old_config["acls"]:
        if tmp["acl_type"] == "grouplist":
            tmp["grouplist"] = [x["group_id"] for x in tmp["grouplist"]]
        elif tmp["acl_type"] == "userlist":
            tmp["userlist"] = [x["user_id"] for x in tmp["userlist"]]
        else:
            tmp["grouplist"] = []
            tmp["userlist"] = []
        old_acls.append(tmp)
    old_config["acls"] = old_acls
    # Collect the new ACLs
    acl_config = [
        {
            "acl_action": "card_view",
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
            "acl_action": "card_launch",
            "acl_type": "logged_in",
            "userlist": [],
            "grouplist": [],
        },
        {
            "acl_action": "card_edit",
            "acl_type": (
                acl_type_edit
                if acl_type_edit
                else old_config["acls"][2]["acl_type"]
            ),
            "userlist": (
                acl_list_edit
                if acl_type_edit
                else old_config["acls"][2]["userlist"]
            ),
            "grouplist": (
                acl_list_edit
                if acl_type_edit
                else old_config["acls"][2]["grouplist"]
            ),
        },
    ]
    card_group_config["acls"] = acl_config
    # Author, coauthors and reviewers need to be re-formatted for the PUT request
    old_author = old_config["author"]["user_id"]
    old_config["author"] = old_author
    old_coauthors = [
        coauthor["user_id"] for coauthor in old_config["coauthors"]
    ]
    old_config["coauthors"] = old_coauthors
    old_reviewers = [
        reviewer["user_id"] for reviewer in old_config["reviewers"]
    ]
    old_config["reviewers"] = old_reviewers

    # Update the card group cards
    if cards_id:
        old_config["card_group_cards"] = []
        for card_id in cards_id:
            old_config["card_group_cards"].append(
                {"card_id": card_id, "order_id": cards_id.index(card_id)}
            )

    # Build request payload combining new and old options
    payload = {
        k: v if v is not None else old_config[k]
        for k, v in card_group_config.items()
    }
    adaboard.request_adaboard(
        path=f"cards/{group_id}",
        method=requests.put,
        json=payload,
    )

    return None


def edit_url_card(
    card_id: int,
    name: str = None,
    description: str = None,
    remote_url: str = None,
    url_subtype: str = None,
    acl_type_view: str = None,
    acl_list_view: list[str] = None,
    acl_type_launch: str = None,
    acl_list_launch: list[str] = None,
    acl_type_edit: str = None,
    acl_list_edit: list[str] = None,
    coauthors: list[str] = None,
    keywords: list[str] = None,
    picture_id: int = None,
    reviewers: list[str] = None,
) -> None:
    """
    Edit a card of the URL type in the AdaLab Gallery. Note that unspecified fields will not be changed.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/edit_url_card.ipynb) to test this function or build upon it.

    :param card_id: the ID of the card
    :type card_id: int
    :param name: the new name of the card
    :type name: str, optional
    :param description: the new description of the card (tip: supports Markdown)
    :type description: str, optional
    :param remote_url: _description_, defaults to None
    :type remote_url: str, optional
    :param url_subtype: _description_, defaults to None
    :type url_subtype: str, optional
    :param acl_type_view: the ACL type for viewing the card (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_view: str, optional
    :param acl_list_view: the list of users/groups allowed to view the card
    :type acl_list_view: list, optional
    :param acl_type_launch: the ACL type for launching the card (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_launch: str, optional
    :param acl_list_launch: the list of users/groups allowed to launch the card
    :type acl_list_launch: list, optional
    :param acl_type_edit: the ACL type for editing the card (tip: must be "public", "logged_in", "userlist" or "grouplist")
    :type acl_type_edit: str, optional
    :param acl_list_edit: the list of users/groups allowed to edit the card
    :type acl_list_edit: list, optional
    :param coauthors: _description_, defaults to None
    :param coauthors: the other card authors
    :type coauthors: list, optional
    :param keywords: the keywords related to the card, defaults to [] (tip: must exist in the Gallery)
    :type keywords: list, optional
    :param picture_id: the ID of the picture to be used for the card
    :type picture_id: int, optional
    :param reviewers: the list of users who will review the card
    :type reviewers: list, optional
    :return: nothing
    :rtype: None
    """

    validate_acl("card", True, acl_type_view, acl_type_launch, acl_type_edit)

    try:
        url_subtypes = adaboard.request_adaboard(
            "url-card-subtypes", method=requests.get
        ).json()
        url_subtype_id = [
            x["urlcardsubtype_id"]
            for x in url_subtypes
            if x["name"] == url_subtype
        ][0]
    except IndexError as e:
        raise IndexError(
            f"URL subtype '{url_subtype}' not found in the Gallery. Please use an existing URL subtype."
        ) from e

    keywords_id = []
    if keywords:
        kws = _create_keywords_if_not_exist(keywords=keywords)
        for kw in keywords:
            keywords_id.append(kws[kw])

    # Collect new configuration options
    card_config = {
        "name": name,
        "description": description,
        "cardtype_id": 3,
        "remote_url": remote_url,
        "url_subtype_id": url_subtype_id,
        "author_id": None,
        "owner_id": None,
        "image_id": picture_id,
        "keywords": keywords_id,
        "coauthors": coauthors,
        "acls": None,
        "reviewers": reviewers,
    }
    # Fetch old configuration
    old_config = adaboard.request_adaboard(
        path=f"cards/{card_id}", method=requests.get
    ).json()

    # ACLs need to be re-formatted for the PUT request
    old_acls = []
    for tmp in old_config["acls"]:
        if tmp["acl_type"] == "grouplist":
            tmp["grouplist"] = [x["group_id"] for x in tmp["grouplist"]]
        elif tmp["acl_type"] == "userlist":
            tmp["userlist"] = [x["user_id"] for x in tmp["userlist"]]
        else:
            tmp["grouplist"] = []
            tmp["userlist"] = []
        old_acls.append(tmp)
    old_config["acls"] = old_acls
    # Collect the new ACLs
    acl_config = [
        {
            "acl_action": "card_view",
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
            "acl_action": "card_launch",
            "acl_type": (
                acl_type_launch
                if acl_type_launch
                else old_config["acls"][1]["acl_type"]
            ),
            "userlist": (
                acl_list_launch
                if acl_type_launch
                else old_config["acls"][1]["userlist"]
            ),
            "grouplist": (
                acl_list_launch
                if acl_type_launch
                else old_config["acls"][1]["grouplist"]
            ),
        },
        {
            "acl_action": "card_edit",
            "acl_type": (
                acl_type_edit
                if acl_type_edit
                else old_config["acls"][2]["acl_type"]
            ),
            "userlist": (
                acl_list_edit
                if acl_type_edit
                else old_config["acls"][2]["userlist"]
            ),
            "grouplist": (
                acl_list_edit
                if acl_type_edit
                else old_config["acls"][2]["grouplist"]
            ),
        },
    ]
    card_config["acls"] = acl_config
    # Author, coauthors and reviewers need to be re-formatted for the PUT request
    old_author = old_config["author"]["user_id"]
    old_config["author"] = old_author
    old_coauthors = [
        coauthor["user_id"] for coauthor in old_config["coauthors"]
    ]
    old_config["coauthors"] = old_coauthors
    old_reviewers = [
        reviewer["user_id"] for reviewer in old_config["reviewers"]
    ]
    old_config["reviewers"] = old_reviewers

    # Build request payload combining new and old options
    payload = {
        k: v if v is not None else old_config[k]
        for k, v in card_config.items()
    }
    adaboard.request_adaboard(
        f"cards/{card_id}", method=requests.put, json=payload
    )
    return None


def edit_url_subtype(
    url_subtype_id: int,
    name: str = None,
    description: str = None,
    picture_id: int = None,
    protected: bool = None,
) -> None:
    """
    Edit a URL subtype in the AdaLab Gallery. Note that unspecified fields will not be changed.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/cards/edit_url_subtype.ipynb) to test this function or build upon it.

    :param url_subtype_id: the ID of the URL subtype
    :type url_subtype_id: int
    :param name: the new name of the URL subtype
    :type name: str, optional
    :param description: the new description of the URL subtype
    :type description: str, optional
    :param picture_id: the ID of the picture to be used for the URL subtype
    :type picture_id: int, optional
    :param protected: whether to protect the URL subtype from deletion, defaults to False
    :type protected: bool, optional
    :return: nothing
    :rtype: None
    """

    # Collect new configuration options
    url_subtype_config = {
        "name": name,
        "description": description,
        "image_id": picture_id,
        "protected": protected,
    }
    # Fetch old configuration
    tmp = adaboard.request_adaboard(
        path="url-card-subtypes", method=requests.get
    ).json()

    old_config = [x for x in tmp if x["urlcardsubtype_id"] == url_subtype_id][
        0
    ]

    # Build request payload combining new and old options
    payload = {
        k: v if v is not None else old_config[k]
        for k, v in url_subtype_config.items()
    }
    adaboard.request_adaboard(
        f"url-card-subtypes/{url_subtype_id}",
        method=requests.put,
        json=payload,
    )
    return None


def expose_card(card_id: int) -> None:
    """
    Expose (un-hide) a specific card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/expose_card.ipynb) to test this function or build upon it.

    :param card_id: the id of the card to be exposed
    :type card_id: int
    :return: Nothing
    :rtype: None
    """

    set_card_visibility(
        card_id=card_id,
        new_status="exposed",
    )

    return None


def get_cards(
    card_type: str = "all",
    url_subtype: str = "all",
    head: Optional[int] = None,
    search_phrase: Optional[str] = None,
    group_category: Optional[str] = None,
    only_hidden: bool = False,
    only_exposed: bool = False,
) -> list[list[int | str | bool]]:
    """
    Gets all cards registered in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/get_cards.ipynb) to test this function or build upon it.

    :param card_type: The type of cards to return, defaults to "all".
    Available values are "all", "notebook", "voila", "url" and "kernel".
    :type card_type: str
    :return: a list with the main info of all cards in the Gallery
    :rtype: list
    """
    card_types = {
        x["key"]: [x["cardtype_id"]]
        for x in adaboard.request_adaboard(path="cardtypes").json()
    }
    card_types["all"] = None
    allowed_groups = [
        "favorited",
        "authored",
        "coauthored",
        "owned",
        "reviewed",
        "unreviewed",
        "approved",
        "reviewer",
        "involved",
    ]

    assert not (
        card_type != "url" and url_subtype != "all"
    ), """The 'url_subtype' parameter is only available when 'card_type' is set to 'url'."""
    url_subtypes = {
        x["name"]: [x["urlcardsubtype_id"]]
        for x in adaboard.request_adaboard(
            "url-card-subtypes", method=requests.get
        ).json()
    }
    url_subtypes["all"] = None
    assert (
        card_type in card_types
    ), f"Card type must be one of {', '.join(card_types.keys())}"
    assert (
        url_subtype in url_subtypes
    ), f"URL subtype must be one of {', '.join(url_subtypes.keys())}"
    if head is not None:
        assert (
            1 <= head <= 100
        ), "The 'head' parameter must be between 1 and 100."

    filter_options = {"url_subtypes": url_subtypes[url_subtype]}
    if url_subtype == "all":
        filter_options = {"cardtypes": card_types[card_type]}

    if search_phrase is not None:
        filter_options["phrase"] = search_phrase

    if group_category is not None:
        assert (
            group_category in allowed_groups
        ), f"Group category must be one of {', '.join(allowed_groups)}"
        filter_options["groups"] = [group_category]

    if only_hidden:
        filter_options["visibility"] = [True]

    if only_exposed:
        filter_options["visibility"] = [False]

    if head is None:
        all_cards = adaboard.get_all_pages(
            api_url="cards",
            params={"filter_options": json.dumps(filter_options)},
        )
    else:
        all_cards = adaboard.request_adaboard(
            "cards",
            params={
                "filter_options": json.dumps(filter_options),
                "size": head,
            },
        ).json()["items"]

    return [
        [
            x.get("card_id"),
            x.get("cardtype").get("key"),
            (x.get("url_subtype", dict()) or dict()).get("name"),
            x.get("reviewed"),
            not x.get("hidden"),
            x.get("name"),
            ", ".join(
                [str(x["card_id"]) for x in (x.get("card_group_cards") or [])]
            ),
            x.get("author").get("name"),
        ]
        for x in all_cards
    ]


def get_card_contents(
    card_id: int, incl_content: bool = False
) -> dict[str, Union[str, list[dict]]]:
    """
    Gets the contents of a specific card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/get_card_contents.ipynb) to test this function or build upon it.

    :param card_id: the id of the card to be fetched
    :type card_id: int
    :return: a dictionary with the different fields in the card
    :rtype: dict
    """

    response = adaboard.request_adaboard(
        path=f"cards/{card_id}", params={"incl_content": incl_content}
    ).json()

    return_struct = {
        "Author": response.get("author").get("name"),
        "Owner": response.get("owner").get("name"),
        "Co-Authors": [x.get("name") for x in response.get("coauthors")],
        "Card Type": response.get("cardtype").get("key"),
        "Name": response.get("name"),
        "Description": response.get("description"),
        "Keywords": [x["keyword"] for x in response.get("keywords")],
        "Exposed": not response["hidden"],
        "Reviewed": response["reviewed"],
        "Created at": response.get("created_date"),
        "Updated at": response.get("updated_date"),
        "Reviewers": [x.get("name") for x in response.get("reviewers")],
        "Reviewers Completed": [
            x.get("name") for x in response.get("reviewers_complete")
        ],
        "URL": response.get("remote_url"),
        "URL type": (response.get("url_subtype") or dict()).get("name"),
        "Cards in Group": [
            x.get("card_id") for x in response.get("card_group_cards")
        ],
        "Kernel ID": (response.get("card_kernel") or dict()).get(
            "metadata_id"
        ),
        "# Launches": response.get("usage_count").get("usage_count"),
        "Contents": [],
        "Permissions - Allowed to Launch": response.get("permissions").get(
            "allowed_delete"
        ),
        "Permissions - Allowed to Edit": response.get("permissions").get(
            "allowed_edit"
        ),
    }

    for contents in response.get("content"):
        content = base64.b64decode(contents.get("content"))
        contents["content"] = content
        return_struct.get("Contents").append(contents)

    return return_struct


def get_card_issues(
    card_id: int,
) -> list[dict[str, int | str | dict[str, str | int]]]:
    """
    Get the issues related to a specific card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/get_card_issues.ipynb) to test this function or build upon it.

    :param card_id: the id of the card whose issues are to be fetched
    :type card_id: int
    :return: list of dictionaries with issues content and metadata
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path=f"cards/{card_id}/issues", method=requests.get
    ).json()

    return response


def get_card_types() -> list[dict[str, Union[int, str, bool]]]:
    """
    List all the card types in the Gallery and their main information.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/get_card_types.ipynb) to test this function or build upon it.

    :return: list of card-types dictionaries
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="cardtypes",
        method=requests.get,
    ).json()

    return response


def get_card_types_stats() -> list[dict[str, str | int]]:
    """
    Get the statistics of the card types in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/get_card_types_stats.ipynb) to test this function or build upon it.

    :return: list of card-types-info dictionaries
    :rtype: list
    """
    response = adaboard.request_adaboard(
        path="cardtypes/statistics", method=requests.get
    ).json()

    return response


def get_url_subtypes() -> list[dict[str, str | int | bool]]:
    """
    Get the URL subtypes available in the AdaLab Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/get_url_subtypes.ipynb) to test this function or build upon it.

    :return: list with information about existing URL subtypes
    :rtype: list[dict[str, str | int | bool]]
    """

    response = adaboard.request_adaboard(
        path="url-card-subtypes",
        method=requests.get,
    ).json()

    return response


def hide_card(card_id: int) -> None:
    """
    Hide a specific card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/hide_card.ipynb) to test this function or build upon it.

    :param card_id: the id of the card to be hidden
    :type card_id: int
    :return: Nothing
    :rtype: None
    """

    set_card_visibility(card_id=card_id, new_status="hidden")

    return None


def launch_card(
    card_id: int, start_lab: bool = True, lab_config: dict = {}
) -> str:
    """
    Launch a card from the Gallery into the user's Lab.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/launch_card.ipynb) to test this function or build upon it.

    :param card_id: the ID of the card to be launched
    :type card_id: int
    :param start_lab: whether to also start the Lab when launching the card, defaults to True. Note that the Lab must be stopped for this to have any effect
    :type start_lab: bool, optional
    :param lab_config: desired configuration for the Lab environment. It can be set up either passing the IDs of the values for each configuration type, or by choosing one of the user's Lab profiles. Defaults to None (i.e., uses the user's default Lab profile). Can
    :type lab_config: dict, optional
    :return: URL/path to Notebook file in the user's Lab
    :rtype: str
    """

    # Check whether the chosen configuration is valid
    if lab_config:
        assert list(lab_config.keys()) == ["options"] or list(
            lab_config.keys()
        ) == [
            "profile_id"
        ], "Configuration must be a list of IDs with key 'options', or a value with key 'profile_id'."
        if list(lab_config.keys()) == ["options"]:
            config_opts = adaboard.request_adaboard(
                path="jupyter/system/options"
            ).json()
            tmp = []
            for item in [x["configuration_type_options"] for x in config_opts]:
                tmp.extend(item)
            config_opts_ids = [x["id"] for x in tmp]
            for id in lab_config["options"]:
                assert (
                    id in config_opts_ids
                ), "Invalid configuration option ID."
        elif list(lab_config.keys()) == ["profile_id"]:
            config_profiles = adaboard.request_adaboard(
                path="jupyter/system/configurationprofiles"
            ).json()
            config_profiles_ids = [x["id"] for x in config_profiles]
            assert (
                lab_config["profile_id"] in config_profiles_ids
            ), "Invalid configuration profile ID."

    payload = {
        "start_lab": start_lab,
        "lab_configuration": lab_config,
    }
    response = adaboard.request_adaboard(
        path=f"cards/{card_id}/launch", method=requests.post, json=payload
    ).json()

    card_path = response["message"]

    # Set up the card kernel
    # Get the main Notebook
    nb_path = card_path[card_path.find("/gallery") + 1 :]
    response = adaboard.request_adaboard(
        path="jupyter/files/notebook/content/fetch", params={"path": nb_path}
    ).json()
    nb_file_dict = json.loads(
        base64.b64decode(response["content"]).decode("utf-8")
    )

    # Check if the kernel is custom
    kernel_pattern = re.compile(r"^(kp|kt)(\d+)$")
    kernel_match = kernel_pattern.match(
        nb_file_dict["metadata"]["kernelspec"]["name"]
    )
    if kernel_match:
        # Check if the kernel linked to the card is installed. If not, install it
        id_dict = {}
        kernels = adaboard.request_adaboard(path="jupyter/kernelspecs").json()
        if kernel_match.group(1) == "kp":
            kernel_metadata_id = int(kernel_match.group(2))
            try:
                [x for x in kernels if x["metadata_id"] == kernel_metadata_id][
                    0
                ]
            except IndexError:
                id_dict = {"metadata_id": kernel_metadata_id}
        elif kernel_match.group(1) == "kt":
            kernel_run_id = int(kernel_match.group(2))
            try:
                [x for x in kernels if x["run_id"] == kernel_run_id][0]
            except IndexError:
                id_dict = {"run_id": kernel_run_id}
        # If the kernel is not installed and it exists, install it
        if id_dict:
            payload = {
                "display_name": nb_file_dict["metadata"]["kernelspec"][
                    "display_name"
                ],
                "include_dummy_notebook": False,
                "start_options": {"start_lab": False, "lab_configuration": {}},
            }
            payload.update(id_dict)
            adaboard.request_adaboard(
                path="jupyter/kernelspecs",
                method=requests.post,
                json=payload,
            )

    return card_path


def set_card_visibility(card_id: int, new_status: str) -> None:
    """
    Set the visibility status of a specific card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/set_card_visibility.ipynb) to test this function or build upon it.

    :param card_id: the id of the card whose visibility is to be set
    :type card_id: int
    :param new_status: visibility to be set
    :type new_status: str
    :return: Nothing
    :rtype: None
    """

    assert new_status.lower() in [
        "exposed",
        "hidden",
    ], "Status must be 'exposed' or 'hidden'"

    status_dict = {"exposed": "false", "hidden": "true"}
    new_status = new_status.lower()
    payload = {"hidden": status_dict[new_status]}
    adaboard.request_adaboard(
        path=f"cards/{card_id}/hidden", method=requests.put, json=payload
    )

    return None


def toggle_card_favorite(card_id: int) -> str:
    """
    Toggle the favorite status of a card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/toggle_card_favorite.ipynb) to test this function or build upon it.

    :param card_id: the id of the card whose status is to be toggled
    :type card_id: int
    :return: a message describing new status
    :rtype: str
    """

    response = adaboard.request_adaboard(
        path=f"favorite/{card_id}", method=requests.post
    ).json()

    return response["message"]


def toggle_card_review(card_id: int) -> None:
    """
    Toggle the review status of a card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/cards/toggle_card_review.ipynb) to test this function or build upon it.

    :param card_id: the id of the card whose status is to be toggled
    :type card_id: int
    :return: nothing
    :rtype: None
    """

    adaboard.request_adaboard(
        path=f"cards/{card_id}/review", method=requests.put
    )

    return None
