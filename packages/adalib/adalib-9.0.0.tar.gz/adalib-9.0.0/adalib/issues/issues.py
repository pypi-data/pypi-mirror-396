import datetime as dt

import requests

from .. import adaboard


def create_issue(card_id: int, message: str, username: str) -> int:
    """
    Create a new issue for a specific card in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/issues/create_issue.ipynb) to test this function or build upon it.

    :param card_id: id of the card to assign the issue to
    :type card_id: int
    :param message: message of the new issue
    :type message: str
    :param username: the current username (tip: check "LOGNAME" environment variable)
    :type username: str
    :return: id of the new issue
    :rtype: int
    """

    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    payload = {
        "card_id": card_id,
        "message": message,
        "reported_by": username,
        "reported_date": timestamp,
        "status": "new",
    }
    response = adaboard.request_adaboard(
        path="cardissues",
        method=requests.post,
        json=payload,
    ).json()

    return response["id"]


def get_issue_data(
    issue_id: int,
) -> dict[
    str,
    int
    | str
    | dict[str, str | int]
    | list[dict[str, int | str | dict[str, int | str]]],
]:
    """
    Get contents and information of a specific issue.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/issues/get_issue_data.ipynb) to test this function or build upon it.

    :param issue_id: id of the issue whose info is to be fetched
    :type issue_id: int
    :return: dictionary with the issue's detailed info
    :rtype: dict
    """

    response = adaboard.request_adaboard(
        path=f"cardissues/{issue_id}", method=requests.get
    ).json()

    return response


def get_issues() -> list[dict[str, int | str | dict[str, str | int]]]:
    """
    Get all the card issues registered in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/issues/get_issues.ipynb) to test this function or build upon it.

    :return: list of dictionaries with issues' main info
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="cardissues", method=requests.get
    ).json()

    return response


def update_issue(
    issue_id: int, new_status: str = "", comment: str = ""
) -> int:
    """
    Update issue content (status, comments).
    Note that only one of the fields can be updated at a time.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/issues/update_issue.ipynb) to test this function or build upon it.

    :param issue_id: the id of the issue to be updated
    :type issue_id: int
    :param new_status: status to be set
    :type new_status: str
    :param comment: comment to be added
    :type comment: str
    :return: id of the issue update
    :rtype: int
    """

    if comment and not new_status:
        payload = {
            "comment": comment,
            "history_type": "comment",
        }
    elif new_status and not comment:
        assert new_status.lower() in [
            "new",
            "in progress",
            "in_progress",
            "solved",
            "ignored",
        ], "Invalid status!"
        payload = {
            "new_status": new_status.lower().replace(" ", "_"),
            "comment": "",
            "history_type": "new_status",
        }
    else:
        return "Only one field can be updated at a time!"

    response = adaboard.request_adaboard(
        path=f"cardissues/{issue_id}",
        method=requests.put,
        json=payload,
    ).json()

    return response["id"]
