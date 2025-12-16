from typing import Any, Dict, List, Optional, Tuple, Union

from keble_db.schemas import QueryBase

_OPERATOR_MAP = {
    "$gt": ">",
    "$gte": ">=",
    "$lt": "<",
    "$lte": "<=",
    "$in": "IN",
    "$contains": "CONTAINS",
    "$startswith": "STARTS WITH",
    "$endswith": "ENDS WITH",
}


def _normalize_query(query: Optional[QueryBase | dict]) -> Optional[QueryBase]:
    if query is None or isinstance(query, QueryBase):
        return query
    return QueryBase(**query)


def _param_name(idx: int) -> str:
    return f"p{idx}"


def build_where_clause(
    query: Optional[QueryBase | dict],
    *,
    alias: str = "n",
    id_field: str = "id",
    use_internal_id: bool = False,
) -> Tuple[str, Dict[str, Any]]:
    query = _normalize_query(query)
    if query is None:
        return "", {}

    clauses: List[str] = []
    params: Dict[str, Any] = {}
    idx = 0

    # Handle id/ids
    def _id_expr(val):
        if use_internal_id:
            # Prefer elementId for internal id lookups to avoid deprecated id(n)
            return f"elementId({alias})"
        return f"{alias}.{id_field}"

    if query.id is not None:
        pname = _param_name(idx)
        idx += 1
        if use_internal_id:
            params[pname] = str(query.id)
            clause_parts = [f"{_id_expr(query.id)} = ${pname}"]
            # also allow stored property with id_field to match the same value
            clause_parts.append(f"{alias}.{id_field} = ${pname}")
            int_name = None
            try:
                int_val = int(str(query.id))
                int_name = _param_name(idx)
                idx += 1
                params[int_name] = int_val
            except (TypeError, ValueError):
                int_val = None
            if int_name:
                clause_parts.append(f"id({alias}) = ${int_name}")
            clauses.append("(" + " OR ".join(clause_parts) + ")")
        else:
            clauses.append(f"{_id_expr(query.id)} = ${pname}")
            params[pname] = query.id

    if query.ids is not None:
        pname = _param_name(idx)
        idx += 1
        # choose expression based on type of ids
        sample = query.ids[0] if len(query.ids) > 0 else None
        expr = _id_expr(sample)
        if use_internal_id:
            params[pname] = [str(v) for v in query.ids]
            clause_parts = [f"{expr} IN ${pname}", f"{alias}.{id_field} IN ${pname}"]
            int_vals: List[int] = []
            for v in query.ids:
                try:
                    int_vals.append(int(str(v)))
                except (TypeError, ValueError):
                    continue
            if int_vals:
                pname_int = _param_name(idx)
                idx += 1
                params[pname_int] = int_vals
                clause_parts.append(f"id({alias}) IN ${pname_int}")
            clauses.append("(" + " OR ".join(clause_parts) + ")")
        else:
            clauses.append(f"{expr} IN ${pname}")
            params[pname] = query.ids

    # Handle filters
    if query.filters is not None:
        assert isinstance(query.filters, dict), (
            "[Db] Query.filters for Neo4j must be a dict mapping property to value or operator dict"
        )
        for field, raw_val in query.filters.items():
            if isinstance(raw_val, dict):
                for op, val in raw_val.items():
                    assert op in _OPERATOR_MAP, (
                        f"[Db] Unsupported operator '{op}' in Neo4j filters"
                    )
                    pname = _param_name(idx)
                    idx += 1
                    if op == "$in":
                        assert isinstance(val, (list, tuple)), (
                            "[Db] $in operator expects list/tuple"
                        )
                        clauses.append(f"{alias}.{field} {_OPERATOR_MAP[op]} ${pname}")
                    else:
                        clauses.append(f"{alias}.{field} {_OPERATOR_MAP[op]} ${pname}")
                    params[pname] = val
            else:
                pname = _param_name(idx)
                idx += 1
                clauses.append(f"{alias}.{field} = ${pname}")
                params[pname] = raw_val

    if len(clauses) == 0:
        return "", params

    where = "WHERE " + " AND ".join(clauses)
    return where, params


def build_order_clause(query: Optional[QueryBase | dict], *, alias: str = "n") -> str:
    query = _normalize_query(query)
    if query is None or query.order_by is None:
        return ""
    assert isinstance(query.order_by, list), (
        "[Db] order_by for Neo4j must be a list of tuples (field, 'asc'|'desc')"
    )
    order_parts: List[str] = []
    for item in query.order_by:
        assert (
            isinstance(item, tuple)
            and len(item) == 2
            and isinstance(item[0], str)
            and isinstance(item[1], str)
        ), (
            "[Db] order_by expects tuples like ('field', 'asc'|'desc') for Neo4j"
        )
        direction = item[1].lower()
        assert direction in ["asc", "desc"], (
            "[Db] order_by direction must be 'asc' or 'desc' for Neo4j"
        )
        order_parts.append(f"{alias}.{item[0]} {direction.upper()}")
    if not order_parts:
        return ""
    return "ORDER BY " + ", ".join(order_parts)


def build_paging_clause(query: Optional[QueryBase | dict]) -> Tuple[str, str]:
    query = _normalize_query(query)
    if query is None:
        return "", ""
    skip_clause = ""
    limit_clause = ""
    if query.offset is not None:
        assert isinstance(query.offset, int), "[Db] offset must be int for Neo4j"
        skip_clause = "SKIP $skip"
    if query.limit is not None:
        assert isinstance(query.limit, int), "[Db] limit must be int for Neo4j"
        limit_clause = "LIMIT $limit"
    return skip_clause, limit_clause


def translate_query(
    query: Optional[QueryBase | dict],
    *,
    alias: str = "n",
    id_field: str = "id",
    use_internal_id: bool = False,
) -> Tuple[str, str, str, Dict[str, Any]]:
    where, params = build_where_clause(
        query, alias=alias, id_field=id_field, use_internal_id=use_internal_id
    )
    order_clause = build_order_clause(query, alias=alias)
    skip_clause, limit_clause = build_paging_clause(query)

    q = _normalize_query(query)
    if q is not None:
        if q.offset is not None:
            params["skip"] = q.offset
        if q.limit is not None:
            params["limit"] = q.limit

    return where, order_clause, " ".join([c for c in [skip_clause, limit_clause] if c]), params


def node_to_dict(
    node: Any,
    *,
    id_field: str,
    use_internal_id: bool,
) -> Dict[str, Any]:
    data = dict(node)
    if use_internal_id:
        internal_id = None
        # Prefer a stored id_field if it was set on the node (e.g., via elementId(n))
        if id_field in data:
            internal_id = data[id_field]
        if hasattr(node, "element_id"):
            internal_id = getattr(node, "element_id")
        if internal_id is None and hasattr(node, "id"):
            internal_id = getattr(node, "id")
        if internal_id is None and isinstance(node, dict):
            internal_id = (
                node.get(id_field)
                or node.get("element_id")
                or node.get("_id")
                or node.get("id")
            )
        if internal_id is None:
            raise ValueError("[Db] Could not determine internal id from node")
        data[id_field] = str(internal_id)
    return data
