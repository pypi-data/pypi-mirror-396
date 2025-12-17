"""The Superset sub-package exposes the core integrations with the Superset data platform connected to AdaLab."""

from .client import OAuthSupersetClient


def get_client(token=None):
    """Create a client for communicating with the Superset API

    :param token: An OAuth token valid for authenticating with the Superset API.
                  Optional if we're running in JupyterHub
    :return: authenticated Superset client
    :rtype: OAuthSupersetClient
    """
    return OAuthSupersetClient(oauth_token=token)


_superset_client = get_client()

databases = _superset_client.databases
datasets = _superset_client.datasets
saved_queries = _superset_client.saved_queries
charts = _superset_client.charts
dashboards = _superset_client.dashboards
