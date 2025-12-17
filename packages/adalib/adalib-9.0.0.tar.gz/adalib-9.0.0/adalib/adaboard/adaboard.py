import logging

import requests
from adalib_auth import config, keycloak


def build_request_url(path: str) -> str:
    """Build the URL to hit adaboard on.

    :param path: The relative path to hit adaboard on.
    :type path: str
    :return: The complete URL to hit adaboard on.
    :rtype: str
    """
    adalib_config = config.get_config()
    url_scheme = (
        "https://" if adalib_config.ENVIRONMENT == "external" else "http://"
    )
    api_extension = (
        "/adaboard/api" if adalib_config.ENVIRONMENT == "external" else ""
    )
    return (
        url_scheme
        + adalib_config.SERVICES["adaboard-api"]["netloc"]
        + api_extension
        + f"/{path}"
    )


def get_all_pages(api_url: str, params: dict = None) -> list[dict]:
    """
    Fetch all pages of data from a paginated API and return the combined results.

    :param api_url: The base API URL to request data from.
    :type api_url: str
    :param params: Additional query parameters for the API request.
    :type params: dict
    :return: A list of items from all pages.
    :rtype: list[dict]
    """
    all_responses = []
    current_page = 1

    while True:
        if params is None:
            params = {}
        params["page"] = current_page
        params["size"] = 100

        response = request_adaboard(
            path=api_url, method=requests.get, params=params
        ).json()

        all_responses.extend(response.get("items"))
        if response.get("page") >= response.get("pages"):
            break

        current_page += 1

    return all_responses


def get_user(
    include_notification_preferences: bool = False,
) -> dict:
    """Get user data.

    :param user_id: User ID
    :type user_id: str
    :param include_notification_preferences: Flag whether the notification
        preferences should be included
    :type include_notification_preferences: bool
    """
    user = request_adaboard(path="users/self").json()
    notifications = request_adaboard(path="nosy/settings/").json()
    user["notifications"] = notifications

    if include_notification_preferences:
        notification_preferences = request_adaboard(
            path="nosy/preferences/"
        ).json()
        notification_preferences = [
            _unravel_notification(x)
            for x in notification_preferences["preferences"]
        ]
        user["notifications"]["preferences"] = notification_preferences

    return user


def request_adaboard(
    path: str,
    method=requests.get,
    omit_content_type: bool = False,
    **kwargs,
) -> requests.models.Response:
    """Function to hit the adaboard api at the specified url and raise for error on response.

    Note: All kwargs passed are directly sent through to the request function.

    :param path: path to hit adaboard on (base url will be injected automatically)
    :type path: str
    :param method: method to use to query adaboard, defaults to requests.get
    :type method: function, optional
    :return: response from adaboard
    :rtype: response
    """
    # Construct authentication header for adaboard
    adalib_config = config.get_config()
    adaboard_token = keycloak.get_client_token(
        audience_client_id=adalib_config.KEYCLOAK_CLIENTS["adaboard-api"]
    )

    headers = {
        "authorization": f"Bearer {adaboard_token['access_token']}",
        "Accept": "application/json",
    }
    if not omit_content_type:
        headers["Content-Type"] = "application/json"

    request_url = build_request_url(path)

    # Query adaboard and raise for status
    try:
        response = method(request_url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        try:
            error_message = e.response.json()["detail"]
        except ValueError:
            error_message = e.response.text

        logging.error(
            f"""HTTP error occurred: {e} - """
            f"""Error details: {error_message}"""
        )
        raise


def _unravel_notification(notif: dict) -> dict:
    """Helper for parsing the notification preferences."""
    data = notif["name"].split("__")
    for d in data:
        key, value = d.split("=")
        notif[key.lower()] = value
    del notif["name"]
    return notif
