import requests

from .. import adaboard


def create_keywords(
    new_keywords: str | list[str],
) -> list[dict[str, str | int]]:
    """
    Add a new keyword to the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/keywords/create_keywords.ipynb) to test this function or build upon it.

    :param new_keyword: name (or names) of the keywords to be added
    :type new_keyword: str or list
    :return: a list of dictionaries with the new keyword ids
    :rtype: list
    """

    if not isinstance(new_keywords, list):
        new_keywords = [new_keywords]

    new_keyword_ids = []
    for new_keyword in new_keywords:
        payload = {"keyword": new_keyword}
        response = adaboard.request_adaboard(
            path="keywords",
            method=requests.post,
            json=payload,
        ).json()

        new_keyword_ids.append(
            {"keyword": new_keyword, "keyword_id": response["id"]}
        )
    return new_keyword_ids


def delete_keywords(keywords: str | list[str]) -> None:
    """
    Delete keywords from the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/keywords/delete_keywords.ipynb) to test this function or build upon it.

    :param keywords: keywords to be deleted (tip: all names must be valid, otherwise the process fails)
    :type keywords: str or list
    :return: Nothing
    :rtype: None
    """

    if not isinstance(keywords, list):
        keywords = [keywords]

    keyword_ids = []
    for keyword in keywords:
        kw_id = get_keyword_id(keyword=keyword)
        keyword_ids.append(str(kw_id))
    delete_keywords_by_id(keyword_ids=keyword_ids)

    return None


def delete_keywords_by_id(keyword_ids: str | list[str]) -> None:
    """
    Delete keywords from the Gallery based on their ids.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/keywords/delete_keywords_by_id.ipynb) to test this function or build upon it.

    :param keyword_ids: ids of the keywords to be deleted (tip: all ids must be valid, otherwise the process fails)
    :type keyword_ids: str or list
    :return: Nothing
    :rtype: None
    """

    if not isinstance(keyword_ids, list):
        keyword_ids = [keyword_ids]

    payload = {"keyword_ids": keyword_ids}
    adaboard.request_adaboard(
        path="keywords",
        method=requests.delete,
        json=payload,
    )

    return None


def get_keyword_id(keyword: str) -> int | None:
    """
    Find the ID for a specific keyword.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/keywords/get_keyword_id.ipynb) to test this function or build upon it.

    :param keyword: name of the keyword
    :type keyword: str
    :return: id of the keyword, or None if keyword not found
    :rtype: int or None
    """

    kws = get_keywords()
    for kw in kws:
        if keyword == kw["keyword"]:
            return kw["keyword_id"]
    return None


def get_keywords() -> list[dict[str, str | int]]:
    """
    Get information about all keywords in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/keywords/get_keywords.ipynb) to test this function or build upon it.

    :return: list of dictionaries with keywords data
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="keywords",
        method=requests.get,
    ).json()

    return response


def get_keywords_stats() -> list[dict[str, str | int]]:
    """
    Get utilization statistics for the keywords in the Gallery.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/user/keywords/get_keywords_stats.ipynb) to test this function or build upon it.

    :return: list of dictionaries with keywords stats
    :rtype: list
    """

    response = adaboard.request_adaboard(
        path="keywords/statistics",
        method=requests.get,
    ).json()

    return response


def merge_keywords(keywords: list[str], new_keyword: str) -> int:
    """
    Merge several keywords into a single one.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/keywords/merge_keywords.ipynb) to test this function or build upon it.

    :param keywords: keywords to be merged
    :type keywords: list
    :param new_keyword: name of the new keyword (note: it can be one of the keywords to be merged)
    :type new_keyword: str
    :return: the new keyword's ID
    :rtype: int
    """

    keyword_ids = []
    for keyword in keywords:
        kw_id = get_keyword_id(keyword=keyword)
        keyword_ids.append(kw_id)

    payload = {"keyword_ids": keyword_ids, "new_keyword": new_keyword}
    response = adaboard.request_adaboard(
        path="keywords/merge",
        method=requests.put,
        json=payload,
    ).json()

    return response["id"]


def rename_keyword(keyword: str, new_keyword: str) -> int | str:
    """
    Rename a keyword.

    Use the [example Jupyter Notebook](https://github.com/adamatics/adalib_example_notebooks/blob/main/admin/keywords/rename_keyword.ipynb) to test this function or build upon it.

    :param keyword: the keyword to be renamed
    :type keyword: str
    :param new_keyword: name of the new keyword
    :type new_keyword: str
    :return: new keyword's id
    :rtype: int
    """

    keyword_id = get_keyword_id(keyword=keyword)
    payload = {"keyword_ids": [keyword_id], "new_keyword": new_keyword}
    response = adaboard.request_adaboard(
        path="keywords/merge",
        method=requests.put,
        json=payload,
    ).json()

    return response["id"]
