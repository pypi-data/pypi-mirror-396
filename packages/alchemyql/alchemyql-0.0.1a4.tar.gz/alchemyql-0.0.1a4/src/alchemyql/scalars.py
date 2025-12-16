import base64
from datetime import date, datetime, time
from enum import Enum
from typing import cast

from graphql import (
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLFloat,
    GraphQLInputType,
    GraphQLInt,
    GraphQLScalarType,
    GraphQLString,
)

IntScalar = cast(GraphQLInputType, GraphQLInt)
FloatScalar = cast(GraphQLInputType, GraphQLFloat)
BoolScalar = cast(GraphQLInputType, GraphQLBoolean)
StringScalar = cast(GraphQLInputType, GraphQLString)


BytesScalar = cast(
    GraphQLInputType,
    GraphQLScalarType(
        name="Bytes",
        serialize=lambda v: base64.b64encode(v).decode("ascii")
        if isinstance(v, (bytes, bytearray))
        else None,
        parse_value=lambda v: base64.b64decode(v.encode("ascii")),
    ),
)

JSONScalar = cast(
    GraphQLInputType,
    GraphQLScalarType(
        name="JSON",
        serialize=lambda v: v,
        parse_value=lambda v: v,
    ),
)

TimeScalar = cast(
    GraphQLInputType,
    GraphQLScalarType(
        name="Time",
        serialize=lambda v: v.isoformat() if isinstance(v, time) else None,
        parse_value=lambda v: time.fromisoformat(v),
    ),
)

DateTimeScalar = cast(
    GraphQLInputType,
    GraphQLScalarType(
        name="DateTime",
        serialize=lambda v: v.isoformat() if isinstance(v, datetime) else None,
        parse_value=lambda v: datetime.fromisoformat(v),
    ),
)

DateScalar = cast(
    GraphQLInputType,
    GraphQLScalarType(
        name="Date",
        serialize=lambda v: v.isoformat() if isinstance(v, date) else None,
        parse_value=lambda v: date.fromisoformat(v),
    ),
)


def build_enum_scalar(cls: type[Enum]) -> GraphQLInputType:
    return cast(
        GraphQLInputType,
        GraphQLEnumType(
            name=cls.__name__,
            values={mem.name: GraphQLEnumValue(mem.name) for mem in cls},
        ),
    )


class Order(Enum):
    ASC = "ASC"
    DESC = "DESC"


OrderingEnumScalar = build_enum_scalar(Order)


def convert_to_scalar(column) -> GraphQLInputType:
    py_type = column.type.python_type

    if py_type is int:
        return IntScalar
    elif py_type is bool:
        return BoolScalar
    elif py_type is float:
        return FloatScalar
    elif issubclass(py_type, Enum):
        return build_enum_scalar(py_type)
    elif py_type is datetime:
        return DateTimeScalar
    elif py_type is date:
        return DateScalar
    elif py_type is time:
        return TimeScalar
    elif py_type is dict or py_type is list:
        return JSONScalar
    elif py_type is bytearray or py_type is bytes:
        return BytesScalar
    return StringScalar
