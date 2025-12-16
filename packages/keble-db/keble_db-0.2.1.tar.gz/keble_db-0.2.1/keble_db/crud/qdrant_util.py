from typing import Literal, Optional, cast

from qdrant_client.conversions.common_types import Filter

from ..schemas import QueryBase


def cleanse_query_for_search(
    query: Optional[QueryBase | dict], offset_type: Literal["int", "str"] = "int"
) -> Filter | None:
    if query is None:
        return None
    elif isinstance(query, dict):
        query = QueryBase(**query)
    if offset_type == "int":
        assert query.offset is None or isinstance(query.offset, int), (
            "[Db] Offset must be int in Qdrant searching"
        )
    elif offset_type == "str":
        assert query.offset is None or isinstance(query.offset, str), (
            "[Db] Offset must be id (str) in Qdrant querying"
        )
    assert query.id is None, (
        "[Db] QueryBase's 'id' key should not being use for similarity search in qdrant"
    )
    assert query.ids is None, (
        "[Db] QueryBase's 'ids' key should not being use for similarity search in qdrant"
    )
    assert query.order_by is None, (
        "[Db] QueryBase's 'order_by' key should not being use for similarity search in qdrant"
    )
    assert query.filters is None or isinstance(query.filters, dict), (
        "[Db] Query.filters only accept dict of qdrant query"
    )

    base = query.filters if query.filters is not None else {}

    # forbidden id and ids in filters
    if "id" in base:
        raise AssertionError(
            "[Db] You should not include 'id' in your QueryBase.filters when searching Qdrant"
        )
    if "ids" in base:
        raise AssertionError(
            "[Db] You should not include 'ids' in your QueryBase.filters when searching Qdrant"
        )
    return cast(Filter, base)
