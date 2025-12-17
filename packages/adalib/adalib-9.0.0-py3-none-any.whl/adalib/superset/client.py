import logging
import urllib.parse
from json import dumps

import pandas as pd
import requests_oauthlib
import supersetapiclient.base
import supersetapiclient.charts
import supersetapiclient.client
import supersetapiclient.dashboards
import supersetapiclient.databases
import supersetapiclient.datasets
import supersetapiclient.exceptions
import supersetapiclient.saved_queries
from adalib_auth import config, keycloak

from ..exceptions import QueryLimitReached

log = logging.getLogger(__name__)


class RunWrapper:
    """Wrapper for converting results from Superset into pandas dataframes
    seamlessly.
    """

    def __init__(self, data, columns):
        """Init the RunWrapper

        :param data: data to be converted to a dataframe
        :type data: dict
        :param columns: columns describing the types of the dataframe
        :type columns: list
        """
        self._data = data
        self._columns = columns

    def __iter__(self):
        """__iter__ implementation for the RunWrapper

        :return: iterator of the data and columns
        :rtype: iter
        """
        return iter((self._data, self._columns))

    def as_df(self):
        """Converts an SQL query result as returned by Superset to a dataframe.

        :return: dataframe constructed from the data + columns
        :rtype: pandas.DataFrame
        """
        #
        dtypes_map = {
            "STRING": "str",
        }
        colspec = {
            c["name"]: dtypes_map[c["type"]]
            for c in self._columns
            if c["type"] in dtypes_map
        }
        df = pd.DataFrame.from_dict(self._data)
        return df.astype(colspec, errors="ignore")


class ListWrapper:
    """Wrapper for returning query results as a list."""

    def __init__(self, objs, df_cols):
        self._objs = objs
        self._df_cols = df_cols

    def __iter__(self):
        """iterator for the ListWrapper objects.

        :return: an iterator for objects in the class instantiation
        :rtype: list_iterator
        """
        return iter(self._objs)

    def __len__(self):
        """len implementation for the ListWrapper.

        :return: lenght of the list of objects in the class instantiation
        :rtype: int
        """
        return len(self._objs)

    def as_df(self):
        """Converts the ListWrapper input data to a pandas.DataFrame.

        :return: dataframe constructed from the data + columns
        :rtype: pandas.DataFrame
        """
        data = [
            {k: getattr(o, f) for f, k in self._df_cols.items()}
            for o in self._objs
        ]
        df = pd.DataFrame(data=data)
        if len(df) and "id" in self._df_cols:
            df.set_index("id", inplace=True)
        return df


class DbListWrapper(ListWrapper):
    """Wrapper for the ListWrapper for handling databases."""

    def __init__(self, databases, *args, **kwargs):
        self._databases = databases
        super().__init__(*args, **kwargs)

    def as_df(self):
        """Add database name to objects returned as a pandas.DataFrame.

        :return: dataframe constructed from the data + columns
        :rtype: pandas.DataFrame
        """
        db_map = {d.id: d.database_name for d in self._databases}
        db_id_field = {v: k for k, v in self._df_cols.items()}["database_id"]
        for o in self._objs:
            o.database_name = db_map.get(getattr(o, db_id_field))
        return super().as_df()


class ListMixIn:
    """MixIn for converting to a list."""

    DATAFRAME_COLS = {}

    def all(self):
        """returns everything that can be found.

        :return: a list of all objects found
        :rtype: list
        """
        return self.find()

    def find(self, *args, **kwargs):
        """not implemented."""
        raise NotImplementedError()

    def fetch(self, *args, **kwargs):
        """Wrapper for the supersetapiclient.get method returning a SavedQueries/Dashboards/Charts/Datasets/Databases object corresponding to the given id.

        :param id: valid object id
        :type id: int (or castable to int)
        :return: Superset object
        :rtype: supersetapiclient.().SavedQueries/Dashboards/Charts/Datasets/Databases
        """
        try:
            kwargs["id"] = int(kwargs["id"])
            res = self.get(*args, **kwargs)
            return res
        except ValueError:
            raise ValueError("'id' must be of type int, or castable to int.")


class SavedQueries(supersetapiclient.saved_queries.SavedQueries, ListMixIn):
    """Wrapper for saved queries in SuperSet.

    :param supersetapiclient: SavedQueries from the superset api client
    :type supersetapiclient: supersetapiclient.saved_queries.SavedQueries
    :param ListMixIn: mixin for returning superset results as lists
    :type ListMixIn: ListMixIn
    """

    DATAFRAME_COLS = {
        "id": "id",
        "label": "name",
        "description": "description",
        "db_id": "database_id",
        "database_name": "database_name",
        "sql": "sql",
    }

    def find(self, *args, **kwargs):
        """wrapper for the supersetapiclient.find method returning a pandas
        DataFrame object with the found saved queries

        :return: A list wrapper for database objects returned
        :rtype: DbListWrapper
        """
        res = super().find(*args, **kwargs)
        dbs = self.client.databases.all()
        return DbListWrapper(
            objs=res, databases=dbs, df_cols=self.DATAFRAME_COLS
        )


class Dashboards(supersetapiclient.dashboards.Dashboards, ListMixIn):
    """Wrapper for the supersetapiclient for returning dashboards from Superset."""

    DATAFRAME_COLS = {
        "id": "id",
        "dashboard_title": "name",
        "published": "published",
        "changed_on": "changed_on",
        "changed_by_name": "changed_by_name",
    }

    def find(self, *args, **kwargs):
        """wrapper for the supersetapiclient.find method returning a pandas
        DataFrame object with the found dashboards

        :return: list of dashboards
        :rtype: list
        """
        res = super().find(*args, **kwargs)
        return ListWrapper(objs=res, df_cols=self.DATAFRAME_COLS)


class Chart(supersetapiclient.charts.Chart):
    """Wrapper for the supersetapiclient chart."""

    def iframe(self, width: int = 600, height: int = 400) -> str:
        """Returns a chart as an iframe to be rendered in a notebook.

        :param width: width of the iframe
        :type width: int
        :param height: height of the iframe
        :type height: int

        :return: an iframe containing the chart to be rendered
        :rtype: str
        """
        base_url = self._parent.client.external_host
        form_data = urllib.parse.quote(dumps(self.params))
        return f"""\
<iframe
  width="{width}"
  height="{height}"
  seamless
  frameBorder="0"
  scrolling="no"
  src="{base_url}/superset/explore/?form_data={form_data}&standalone=1&height={height}"
>
</iframe>
"""

    def embed(self, width: int = 600, height: int = 400) -> None:
        """when called from a notebook, displays the chart in an iframe.

        :param width: width of the iframe, defaults to 600
        :type width: int, optional
        :param height: height of the iframe, defaults to 400
        :type height: int, optional
        """
        from IPython.display import HTML, display

        display(HTML(self.iframe(width=width, height=height)))


class Charts(supersetapiclient.charts.Charts, ListMixIn):
    """Wrapper for the supersetapiclient charts."""

    base_object = Chart
    DATAFRAME_COLS = {
        "id": "id",
        "slice_name": "name",
        "description": "description",
        "datasource_type": "datasource_type",
        "datasource_id": "datasource_id",
        "viz_type": "viz_type",
    }

    def find(self, *args, **kwargs):
        """wrapper for the supersetapiclient.find method returning a pandas
        DataFrame object with the found charts

        :return: list of charts
        :rtype: list
        """
        res = super().find(*args, **kwargs)
        return ListWrapper(objs=res, df_cols=self.DATAFRAME_COLS)


class Datasets(supersetapiclient.datasets.Datasets, ListMixIn):
    """Wrapper for the supersetapiclient datasets."""

    DATAFRAME_COLS = {
        "id": "id",
        "table_name": "name",
        "description": "description",
        "kind": "kind",
        "sql": "sql",
        "database_id": "database_id",
        "database_name": "database_name",
        "schema": "schema",
    }

    def find(self, *args, **kwargs):
        """wrapper for the supersetapiclient.find method returning a pandas
        DataFrame object with the found datasets

        :return: list of datasets
        :rtype: list
        """
        res = super().find(*args, **kwargs)
        dbs = self.client.databases.all()
        return DbListWrapper(
            objs=res, databases=dbs, df_cols=self.DATAFRAME_COLS
        )


class Databases(supersetapiclient.databases.Databases, ListMixIn):
    """Wrapper for the supersetapiclient databases."""

    DATAFRAME_COLS = {
        "id": "id",
        "database_name": "name",
    }

    def find(self, *args, **kwargs):
        """wrapper for the supersetapiclient.find method returning a pandas
        DataFrame object with the found databases

        :return: list of databases
        :rtype: list
        """
        res = super().find(*args, **kwargs)
        return ListWrapper(objs=res, df_cols=self.DATAFRAME_COLS)


class OAuthSupersetClient(supersetapiclient.client.SupersetClient):
    """Class to handle OAuth2 login to Superset for a programmatic client."""

    dashboards_cls = Dashboards
    charts_cls = Charts
    datasets_cls = Datasets
    databases_cls = Databases
    saved_queries_cls = SavedQueries

    def __init__(self, *args, **kwargs):
        """requires and OAuth token valid for authenticating with the Superset API."""
        adalib_config = config.get_config()
        self.oauth_token = kwargs.pop("oauth_token", None)

        self.external_host = adalib_config.SERVICES["superset"]["external"]
        self.internal_host = adalib_config.SERVICES["superset"]["url"]
        kwargs["host"] = (
            self.external_host
            if adalib_config.ENVIRONMENT == "external"
            else self.internal_host
        )
        super().__init__(*args, **kwargs)

    def authenticate(self):
        """
        Authenticate with OAuth using our KeyCloak setup. We want to defer authentication to this point, to allow
        creating a client instance without triggering any requests.

        If no token is given, and we're in a JupyterHub context where we have a JupyterHub API token, then we can
        translate that token to a Superset token using Keycloak token exchange.

        :return: authentication response as json
        :rtype: json
        """
        adalib_config = config.get_config()
        if not self.oauth_token:
            self.oauth_token = keycloak.get_client_token(
                audience_client_id=adalib_config.KEYCLOAK_CLIENTS["superset"]
            )
        session = requests_oauthlib.OAuth2Session(token=self.oauth_token)
        response = session.post(
            self.login_endpoint,
            json={
                "provider": "oauth",
                "refresh": "true",
            },
        )
        response.raise_for_status()
        return response.json()

    def run(self, *args, **kwargs):
        """Runs a query against the Superset API

        :raises QueryLimitReached: if the query limit is reached against the API
        :return: a pandas.DataFrame with the results of the query
        :rtype: RunWrapper
        """
        try:
            columns, data = super().run(*args, **kwargs)
        except supersetapiclient.exceptions.QueryLimitReached as e:
            raise QueryLimitReached(*e.args)
        return RunWrapper(columns=columns, data=data)

    @property
    def _sql_endpoint(self) -> str:
        """returns the sql query endpoint from the Superset API

        :return: url endpoint for executing sql queries
        :rtype: str
        """
        return self.join_urls(self.base_url, "execute_sql_json/")
