"""The Keywords sub-package exposes the core integrations of the keywords in the AdaLab Gallery."""

from .keywords import (
    create_keywords,
    delete_keywords,
    delete_keywords_by_id,
    get_keyword_id,
    get_keywords,
    get_keywords_stats,
    merge_keywords,
    rename_keyword,
)

__all__ = [
    "create_keywords",
    "delete_keywords",
    "delete_keywords_by_id",
    "get_keyword_id",
    "get_keywords",
    "get_keywords_stats",
    "merge_keywords",
    "rename_keyword",
]

__title__ = "adalib Keywords"
