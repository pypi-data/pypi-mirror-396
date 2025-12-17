"""The Apps sub-package exposes the core integrations of the deployed apps in AdaLab."""

from .apps import (
    delete_app,
    deploy_app,
    deploy_multicontainer_app,
    edit_app,
    edit_multicontainer_app,
    get_all_apps,
    get_app,
    get_app_id,
    get_app_logs,
    get_apps_by_author,
    get_apps_status,
    get_container_idx,
    restart_app,
    start_app,
    stop_app,
)

__all__ = [
    "delete_app",
    "deploy_app",
    "deploy_multicontainer_app",
    "edit_app",
    "edit_multicontainer_app",
    "get_all_apps",
    "get_app",
    "get_app_id",
    "get_app_logs",
    "get_apps_by_author",
    "get_apps_status",
    "get_container_idx",
    "restart_app",
    "start_app",
    "stop_app",
]
__title__ = "adalib Apps"
