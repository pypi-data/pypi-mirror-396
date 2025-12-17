"""General module for custom exceptions."""


class QueryLimitReached(ValueError):
    """Exception to signal that the limit of queries in Superset has been
    reached.

    :param ValueError: The ValueError of the exception
    :type ValueError: ValueError
    """

    pass
