from dataclasses import dataclass
from enum import Enum, auto


class Order(Enum):
    ASC = auto()
    DESC = auto()


@dataclass
class Table:
    # fmt: off

    # Table details
    sqlalchemy_cls  : type 
    inspected       : type
    graphql_name    : str
    description     : str

    # Fields Details
    fields          : list[str]
    relationships   : list[str]

    # Filtering Details
    filter_fields   : list[str]

    # Ordering Details
    order_fields    : list[str]
    default_order   : dict[str, Order] | None

    # Pagination Details
    pagination      : bool
    default_limit   : int | None
    max_limit       : int | None

    # Querying Details
    query           : bool

    # fmt: on
