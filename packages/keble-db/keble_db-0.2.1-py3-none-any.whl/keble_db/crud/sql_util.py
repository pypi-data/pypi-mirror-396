from typing import Any, List, Optional, Union, cast

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BinaryExpression
from sqlmodel import and_

from ..schemas import QueryBase


class SqlQueryParsed(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    where: Optional[Union[BinaryExpression, Any]]


def parse_query_for_first(model, query: Optional[QueryBase]) -> SqlQueryParsed:
    where_list = __parse_ids(model, query) + __parse_filters(model, query=query)
    return SqlQueryParsed(where=_build_where(where_list))


def parse_query_for_list(model, query: Optional[QueryBase]) -> SqlQueryParsed:
    if query is None:
        return SqlQueryParsed(where=None)
    where_list = __parse_ids(model, query) + __parse_filters(model, query=query)
    assert query.offset is None or isinstance(query.offset, int), (
        "[Db] Offset must be int"
    )
    return SqlQueryParsed(where=_build_where(where_list))


def _build_where(where_list: List[BinaryExpression]) -> Optional[BinaryExpression]:
    if len(where_list) == 0:
        return None
    if len(where_list) > 1:
        return cast(BinaryExpression, and_(*where_list))
    return where_list[0]


def __parse_ids(model, query: Optional[QueryBase]) -> List[BinaryExpression]:
    if query is None:
        return []
    where: List[BinaryExpression] = []
    if query.id is not None:
        where.append(model.id == query.id)
    if query.ids is not None:
        where.append(model.id.in_(query.ids))
    return where


def __parse_filters(
    model,  # noqa
    query: Optional[QueryBase],
) -> List[BinaryExpression]:
    if query is None or query.filters is None or len(query.filters) == 0:
        return []
    assert not isinstance(query.filters, dict), (
        "[Db] Query.filters only accept list of expression for SQL query"
    )
    return query.filters
