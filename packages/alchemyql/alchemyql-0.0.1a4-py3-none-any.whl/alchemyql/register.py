from sqlalchemy import inspect

from .errors import ConfigurationError
from .filters import FILTERS
from .models import Order, Table


def validate_field(inspected, field_name: str):
    """
    Validation to check the field exists in the sqlalchemy table.

    This will raise a ConfigurationError exception if the field does not exist.
    """
    column = next((it for it in inspected.columns if field_name == it.key), None)
    if column is None:
        raise ConfigurationError(
            f"Field {field_name} does not exist for {inspected.class_.__name__}"
        )
    return column


def build_fields(
    inspected, include_fields: list[str] | None, exclude_fields: list[str] | None
) -> list[str]:
    """
    Build the list of fields to expose based on include and exclude lists.
    This also validates all requested fields exist.
    """
    fields = []

    if include_fields:
        # Validate the fields requested and add them to the list
        for field in include_fields:
            validate_field(inspected, field)
            fields.append(field)
    else:
        # Add all fields to the list
        fields = [it.key for it in inspected.columns]

    if exclude_fields:
        # Validate the fields requested and remove them from the list
        for field in exclude_fields:
            validate_field(inspected, field)

            if field in fields:
                fields.remove(field)

    return fields


def validate_filter_fields(inspected, field_list: list[str]):
    """
    Validates the fields requested for filtering are valid.
    This checks they exist and the type is supported.
    """
    for field in field_list:
        col = validate_field(inspected, field)

        if col.type.python_type not in FILTERS and not any(
            issubclass(col.type.python_type, it) for it in FILTERS
        ):
            raise ConfigurationError(
                f"Column {field}'s data type of {col.type.python_type} is not supported for filtering!"
            )


def validate_order_fields(
    inspected, field_list: list[str], default: dict[str, Order] | None
):
    """
    Validates the fields requested for ordering and the default order is valid.
    This checks they exist.
    """
    for field in field_list:
        validate_field(inspected, field)

    if default and any(field not in field_list for field in default):
        raise ConfigurationError(
            "Default ordering cannot be done on fields for which ordering is not supported!"
        )


def validate_paginated_fields(enabled: bool, default: int | None, max: int | None):
    """
    Validates the pagination settings make sense (basic sanity checks).

    All checks are ignored if validation is disabled.
    """
    # We dont need to validate if pagination is disabled
    if not enabled:
        return

    if default and default < 1:
        raise ConfigurationError(
            f"Default limit for pagination must be a positive number (value={default})"
        )

    if max and max < 1:
        raise ConfigurationError(
            f"Maximum limit for pagination must be a positive number (value={max})"
        )

    if max and default and max < default:
        raise ConfigurationError(
            f"Maximum limit cannot be smaller than the default limit for pagination ({default=}, {max=})"
        )


def validate_relationships(inspected, relationship_list: list[str] | None):
    """
    Validates the requested relationships to be exposed are valid.

    NOTE: This does not check that the relationship is also registered, this happens during schema generation.
    """
    # We do not need to validate if no relationships requested
    if not relationship_list:
        return

    for rel in relationship_list:
        if rel not in inspected.relationships:
            raise ConfigurationError(
                f"Requested relationship {rel} does not exist for {inspected.class_.__name__}"
            )


def register_transform(
    sqlalchemy_cls,
    graphql_name: str | None,
    description: str | None,
    query: bool,
    include_fields: list[str] | None,
    exclude_fields: list[str] | None,
    relationships: list[str] | None,
    filter_fields: list[str] | None,
    order_fields: list[str] | None,
    default_order: dict[str, Order] | None,
    pagination: bool,
    default_limit: int | None,
    max_limit: int | None,
) -> Table:
    """
    Take the user inputs and convert it to a AlchemyQL table
    """
    inspected = inspect(sqlalchemy_cls)

    fields = build_fields(inspected, include_fields, exclude_fields)
    validate_relationships(inspected, relationships)

    if query:
        validate_filter_fields(inspected, filter_fields or [])
        validate_order_fields(inspected, order_fields or [], default_order)
        validate_paginated_fields(pagination, default_limit, max_limit)
    else:
        filter_fields = []
        order_fields = []
        default_order = None
        pagination = False
        default_limit = None
        max_limit = None

    # Perform initial transformation
    table = Table(
        sqlalchemy_cls=sqlalchemy_cls,
        inspected=inspected,
        graphql_name=(graphql_name or sqlalchemy_cls.__tablename__).lower(),
        description=description or sqlalchemy_cls.__tablename__,
        fields=fields,
        relationships=relationships or [],
        filter_fields=filter_fields or [],
        order_fields=order_fields or [],
        default_order=default_order,
        pagination=pagination,
        default_limit=default_limit,
        max_limit=max_limit,
        query=query,
    )

    return table
