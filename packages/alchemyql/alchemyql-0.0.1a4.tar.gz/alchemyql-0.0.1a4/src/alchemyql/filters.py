from datetime import date, datetime, time
from enum import Enum
from typing import Callable, cast

from graphql import (
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLList,
)

from .scalars import (
    BoolScalar,
    DateScalar,
    DateTimeScalar,
    FloatScalar,
    IntScalar,
    StringScalar,
    TimeScalar,
)

IntFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="IntFilter",
        fields=lambda: {
            "eq": GraphQLInputField(IntScalar),
            "ne": GraphQLInputField(IntScalar),
            "gt": GraphQLInputField(IntScalar),
            "ge": GraphQLInputField(IntScalar),
            "lt": GraphQLInputField(IntScalar),
            "le": GraphQLInputField(IntScalar),
            "in": GraphQLInputField(GraphQLList(IntScalar)),
        },
    ),
)

FloatFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="FloatFilter",
        fields=lambda: {
            "eq": GraphQLInputField(FloatScalar),
            "ne": GraphQLInputField(FloatScalar),
            "gt": GraphQLInputField(FloatScalar),
            "ge": GraphQLInputField(FloatScalar),
            "lt": GraphQLInputField(FloatScalar),
            "le": GraphQLInputField(FloatScalar),
            "in": GraphQLInputField(GraphQLList(FloatScalar)),
        },
    ),
)

BoolFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="BoolFilter",
        fields=lambda: {
            "eq": GraphQLInputField(BoolScalar),
            "ne": GraphQLInputField(BoolScalar),
        },
    ),
)

StringFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="StringFilter",
        fields=lambda: {
            "eq": GraphQLInputField(StringScalar),
            "ne": GraphQLInputField(StringScalar),
            "contains": GraphQLInputField(StringScalar),
            "startswith": GraphQLInputField(StringScalar),
            "endswith": GraphQLInputField(StringScalar),
            "in": GraphQLInputField(GraphQLList(StringScalar)),
        },
    ),
)

DateTimeFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="DateTimeFilter",
        fields=lambda: {
            "eq": GraphQLInputField(DateTimeScalar),
            "ne": GraphQLInputField(DateTimeScalar),
            "gt": GraphQLInputField(DateTimeScalar),
            "ge": GraphQLInputField(DateTimeScalar),
            "lt": GraphQLInputField(DateTimeScalar),
            "le": GraphQLInputField(DateTimeScalar),
            "in": GraphQLInputField(GraphQLList(DateTimeScalar)),
        },
    ),
)

DateFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="DateFilter",
        fields=lambda: {
            "eq": GraphQLInputField(DateScalar),
            "ne": GraphQLInputField(DateScalar),
            "gt": GraphQLInputField(DateScalar),
            "ge": GraphQLInputField(DateScalar),
            "lt": GraphQLInputField(DateScalar),
            "le": GraphQLInputField(DateScalar),
            "in": GraphQLInputField(GraphQLList(DateScalar)),
        },
    ),
)

TimeFilter = cast(
    GraphQLInputObjectType,
    GraphQLInputObjectType(
        name="TimeFilter",
        fields=lambda: {
            "eq": GraphQLInputField(TimeScalar),
            "ne": GraphQLInputField(TimeScalar),
            "gt": GraphQLInputField(TimeScalar),
            "ge": GraphQLInputField(TimeScalar),
            "lt": GraphQLInputField(TimeScalar),
            "le": GraphQLInputField(TimeScalar),
            "in": GraphQLInputField(GraphQLList(TimeScalar)),
        },
    ),
)


def build_enum_filter(cls: GraphQLEnumType) -> GraphQLInputObjectType:
    return cast(
        GraphQLInputObjectType,
        GraphQLInputObjectType(
            name=f"{cls.name}_filter",
            fields=lambda: {
                "eq": GraphQLInputField(cls),
                "ne": GraphQLInputField(cls),
                "in": GraphQLInputField(GraphQLList(cls)),
            },
        ),
    )


FILTERS: dict[type, Callable[[GraphQLInputType], GraphQLInputObjectType]] = {
    int: lambda _: IntFilter,
    str: lambda _: StringFilter,
    bool: lambda _: BoolFilter,
    float: lambda _: FloatFilter,
    Enum: lambda field: build_enum_filter(cast(GraphQLEnumType, field)),
    datetime: lambda _: DateTimeFilter,
    date: lambda _: DateFilter,
    time: lambda _: TimeFilter,
}
