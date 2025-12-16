class AlchemyQLError(Exception):
    """Base class for all exceptions raised by AlchemyQL."""

    pass


class ConfigurationError(AlchemyQLError):
    """Raised when the user provides invalid configuration."""

    pass


class QueryExecutionError(AlchemyQLError):
    """Raised when the query execution fails."""

    pass
