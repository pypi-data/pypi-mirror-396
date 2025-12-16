from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

from neo4j import AsyncSession as Neo4jAsyncSession
from neo4j import Session as Neo4jSession
from pydantic import BaseModel

from ..schemas import QueryBase
from .neo4j_util import node_to_dict, translate_query

ModelType = TypeVar("ModelType", bound=BaseModel)


class Neo4jCRUDBase(Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        label: Union[str, Sequence[str]],
        *,
        id_field: str = "id",
        use_internal_id: bool = False,
    ):
        self.model = model
        self.labels: List[str] = [label] if isinstance(label, str) else list(label)
        self.label_fragment = ":" + ":".join(self.labels)
        self.id_field = id_field
        self.use_internal_id = use_internal_id

    # Helpers
    def _hydrate(self, node: Any) -> ModelType:
        data = node_to_dict(
            node, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        obj = self.model(**data)
        if self.use_internal_id:
            val = data.get(self.id_field)
            if val is not None:
                try:
                    setattr(obj, self.id_field, val)
                except Exception:
                    try:
                        object.__setattr__(obj, self.id_field, val)
                    except Exception:
                        # if all else fails, store on __dict__ for access
                        try:
                            obj.__dict__[self.id_field] = val
                        except Exception:
                            pass
        return obj

    def _normalize_payload(
        self, obj: Union[ModelType, BaseModel, Dict[str, Any]]
    ) -> Dict[str, Any]:
        if isinstance(obj, BaseModel):
            payload = obj.model_dump(exclude_none=True)
        else:
            payload = {k: v for k, v in obj.items() if v is not None}
        if self.use_internal_id and self.id_field in payload:
            # internal id is managed by Neo4j, avoid conflicting property writes
            payload = {k: v for k, v in payload.items() if k != self.id_field}
        return payload

    def _match_fragment(self) -> str:
        return f"MATCH (n{self.label_fragment})"

    # CRUD
    def create(
        self, session: Neo4jSession, *, obj_in: Union[ModelType, BaseModel]
    ) -> ModelType:
        payload = self._normalize_payload(obj_in)
        if self.use_internal_id:
            cypher = (
                f"CREATE (n{self.label_fragment} $props) "
                f"SET n.{self.id_field} = elementId(n) "
                "RETURN n"
            )
        else:
            cypher = f"CREATE (n{self.label_fragment} $props) RETURN n"

        def work(tx):
            result = tx.run(cypher, {"props": payload})
            data = result.data()
            return data[0]["n"] if data else None

        node = session.execute_write(work)
        if node is None:
            raise ValueError("[Db] Failed to create Neo4j node")
        return self._hydrate(node)

    async def acreate(
        self, session: Neo4jAsyncSession, *, obj_in: Union[ModelType, BaseModel]
    ) -> ModelType:
        payload = self._normalize_payload(obj_in)
        if self.use_internal_id:
            cypher = (
                f"CREATE (n{self.label_fragment} $props) "
                f"SET n.{self.id_field} = elementId(n) "
                "RETURN n"
            )
        else:
            cypher = f"CREATE (n{self.label_fragment} $props) RETURN n"

        async def work(tx):
            result = await tx.run(cypher, {"props": payload})
            data = await result.data()
            return data[0]["n"] if data else None

        node = await session.execute_write(work)
        if node is None:
            raise ValueError("[Db] Failed to create Neo4j node")
        return self._hydrate(node)

    def create_multi(
        self,
        session: Neo4jSession,
        *,
        obj_in_list: Iterable[Union[ModelType, BaseModel]],
    ) -> List[ModelType]:
        payloads = [self._normalize_payload(obj) for obj in obj_in_list]
        if len(payloads) == 0:
            return []
        if self.use_internal_id:
            cypher = (
                f"UNWIND $rows AS row CREATE (n{self.label_fragment}) "
                "SET n += row "
                f"SET n.{self.id_field} = elementId(n) "
                "RETURN n"
            )
        else:
            cypher = (
                f"UNWIND $rows AS row CREATE (n{self.label_fragment}) SET n += row RETURN n"
            )

        def work(tx):
            result = tx.run(cypher, {"rows": payloads})
            data = result.data()
            return [record["n"] for record in data]

        nodes = session.execute_write(work)
        return [self._hydrate(n) for n in nodes]

    async def acreate_multi(
        self,
        session: Neo4jAsyncSession,
        *,
        obj_in_list: Iterable[Union[ModelType, BaseModel]],
    ) -> List[ModelType]:
        payloads = [self._normalize_payload(obj) for obj in obj_in_list]
        if len(payloads) == 0:
            return []
        if self.use_internal_id:
            cypher = (
                f"UNWIND $rows AS row CREATE (n{self.label_fragment}) "
                "SET n += row "
                f"SET n.{self.id_field} = elementId(n) "
                "RETURN n"
            )
        else:
            cypher = (
                f"UNWIND $rows AS row CREATE (n{self.label_fragment}) SET n += row RETURN n"
            )

        async def work(tx):
            result = await tx.run(cypher, {"rows": payloads})
            data = await result.data()
            return [record["n"] for record in data]

        nodes = await session.execute_write(work)
        return [self._hydrate(n) for n in nodes]

    def first(
        self, session: Neo4jSession, *, query: Optional[QueryBase | dict] = None
    ) -> Optional[ModelType]:
        where, order_clause, paging, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        clauses = [self._match_fragment(), where, "RETURN n", order_clause, "LIMIT 1"]
        cypher = " ".join([c for c in clauses if c])

        def work(tx):
            result = tx.run(cypher, params)
            data = result.data()
            return data[0]["n"] if data else None

        node = session.execute_read(work)
        return self._hydrate(node) if node is not None else None

    async def afirst(
        self, session: Neo4jAsyncSession, *, query: Optional[QueryBase | dict] = None
    ) -> Optional[ModelType]:
        where, order_clause, paging, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        clauses = [self._match_fragment(), where, "RETURN n", order_clause, "LIMIT 1"]
        cypher = " ".join([c for c in clauses if c])

        async def work(tx):
            result = await tx.run(cypher, params)
            data = await result.data()
            return data[0]["n"] if data else None

        node = await session.execute_read(work)
        return self._hydrate(node) if node is not None else None

    def get_multi(
        self, session: Neo4jSession, *, query: Optional[QueryBase | dict] = None
    ) -> List[ModelType]:
        where, order_clause, paging, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        clauses = [self._match_fragment(), where, "RETURN n", order_clause, paging]
        cypher = " ".join([c for c in clauses if c])

        def work(tx):
            result = tx.run(cypher, params)
            data = result.data()
            return [record["n"] for record in data]

        nodes = session.execute_read(work)
        return [self._hydrate(node) for node in nodes]

    async def aget_multi(
        self, session: Neo4jAsyncSession, *, query: Optional[QueryBase | dict] = None
    ) -> List[ModelType]:
        where, order_clause, paging, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        clauses = [self._match_fragment(), where, "RETURN n", order_clause, paging]
        cypher = " ".join([c for c in clauses if c])

        async def work(tx):
            result = await tx.run(cypher, params)
            data = await result.data()
            return [record["n"] for record in data]

        nodes = await session.execute_read(work)
        return [self._hydrate(node) for node in nodes]

    def update(
        self,
        session: Neo4jSession,
        *,
        _id: Any,
        obj_in: Union[ModelType, BaseModel, Dict[str, Any]],
    ) -> Optional[ModelType]:
        payload = self._normalize_payload(obj_in)
        query = QueryBase(id=_id)
        where, _, _, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        cypher = f"{self._match_fragment()} {where} SET n += $props RETURN n"
        params = {**params, "props": payload}

        def work(tx):
            result = tx.run(cypher, params)
            data = result.data()
            return data[0]["n"] if data else None

        node = session.execute_write(work)
        return self._hydrate(node) if node is not None else None

    async def aupdate(
        self,
        session: Neo4jAsyncSession,
        *,
        _id: Any,
        obj_in: Union[ModelType, BaseModel, Dict[str, Any]],
    ) -> Optional[ModelType]:
        payload = self._normalize_payload(obj_in)
        query = QueryBase(id=_id)
        where, _, _, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        cypher = f"{self._match_fragment()} {where} SET n += $props RETURN n"
        params = {**params, "props": payload}

        async def work(tx):
            result = await tx.run(cypher, params)
            data = await result.data()
            return data[0]["n"] if data else None

        node = await session.execute_write(work)
        return self._hydrate(node) if node is not None else None

    def delete(self, session: Neo4jSession, *, _id: Any) -> int:
        query = QueryBase(id=_id)
        where, _, _, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        cypher = f"{self._match_fragment()} {where} WITH n DETACH DELETE n RETURN count(*) AS deleted"

        def work(tx):
            result = tx.run(cypher, params)
            data = result.data()
            return data[0]["deleted"] if data else 0

        return session.execute_write(work)

    async def adelete(self, session: Neo4jAsyncSession, *, _id: Any) -> int:
        query = QueryBase(id=_id)
        where, _, _, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        cypher = f"{self._match_fragment()} {where} WITH n DETACH DELETE n RETURN count(*) AS deleted"

        async def work(tx):
            result = await tx.run(cypher, params)
            data = await result.data()
            return data[0]["deleted"] if data else 0

        return await session.execute_write(work)

    def count(
        self, session: Neo4jSession, *, query: Optional[QueryBase | dict] = None
    ) -> int:
        where, _, _, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        cypher = f"{self._match_fragment()} {where} RETURN count(n) AS count"

        def work(tx):
            result = tx.run(cypher, params)
            data = result.data()
            return data[0]["count"] if data else 0

        return session.execute_read(work)

    async def acount(
        self, session: Neo4jAsyncSession, *, query: Optional[QueryBase | dict] = None
    ) -> int:
        where, _, _, params = translate_query(
            query, id_field=self.id_field, use_internal_id=self.use_internal_id
        )
        cypher = f"{self._match_fragment()} {where} RETURN count(n) AS count"

        async def work(tx):
            result = await tx.run(cypher, params)
            data = await result.data()
            return data[0]["count"] if data else 0

        return await session.execute_read(work)

    # Graph helpers
    def merge(
        self,
        session: Neo4jSession,
        *,
        key_value: Any,
        obj_in: Union[ModelType, BaseModel, Dict[str, Any]],
    ) -> ModelType:
        payload = self._normalize_payload(obj_in)
        cypher = (
            f"MERGE (n{self.label_fragment} {{{self.id_field}: $key}}) "
            "SET n += $props RETURN n"
        )

        def work(tx):
            result = tx.run(cypher, {"key": key_value, "props": payload})
            data = result.data()
            return data[0]["n"] if data else None

        node = session.execute_write(work)
        if node is None:
            raise ValueError("[Db] Failed to merge Neo4j node")
        return self._hydrate(node)

    async def amerge(
        self,
        session: Neo4jAsyncSession,
        *,
        key_value: Any,
        obj_in: Union[ModelType, BaseModel, Dict[str, Any]],
    ) -> ModelType:
        payload = self._normalize_payload(obj_in)
        cypher = (
            f"MERGE (n{self.label_fragment} {{{self.id_field}: $key}}) "
            "SET n += $props RETURN n"
        )

        async def work(tx):
            result = await tx.run(cypher, {"key": key_value, "props": payload})
            data = await result.data()
            return data[0]["n"] if data else None

        node = await session.execute_write(work)
        if node is None:
            raise ValueError("[Db] Failed to merge Neo4j node")
        return self._hydrate(node)

    def create_relationship(
        self,
        session: Neo4jSession,
        *,
        from_id: Any,
        to_id: Any,
        rel_type: str,
        to_label: Optional[Union[str, Sequence[str]]] = None,
        rel_properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        to_labels_raw = (
            [to_label]
            if isinstance(to_label, str) or to_label is None
            else list(to_label)
        )
        to_labels: List[str] = [lbl for lbl in to_labels_raw if lbl is not None]
        to_fragment = ":" + ":".join(self.labels if to_label is None else to_labels)
        auth_props = rel_properties or {}
        from_match = (
            f"MATCH (a{self.label_fragment}) WHERE "
            f"{'elementId(a)' if self.use_internal_id else f'a.{self.id_field}'} = $from_id"
        )
        to_match = (
            f"MATCH (b{to_fragment}) WHERE "
            f"{'elementId(b)' if self.use_internal_id else f'b.{self.id_field}'} = $to_id"
        )
        cypher = (
            f"{from_match} {to_match} MERGE (a)-[r:{rel_type}]->(b) SET r += $rel_props"
        )
        params: Dict[str, Any] = {
            "from_id": str(from_id) if self.use_internal_id else from_id,
            "to_id": str(to_id) if self.use_internal_id else to_id,
            "rel_props": auth_props,
        }
        if self.use_internal_id and str(from_id).isdigit():
            params["from_id_int"] = int(str(from_id))
            cypher = cypher.replace(
                "elementId(a) = $from_id",
                "(elementId(a) = $from_id OR id(a) = $from_id_int)",
            )
        if self.use_internal_id and str(to_id).isdigit():
            params["to_id_int"] = int(str(to_id))
            cypher = cypher.replace(
                "elementId(b) = $to_id",
                "(elementId(b) = $to_id OR id(b) = $to_id_int)",
            )

        def work(tx):
            tx.run(cypher, params)

        session.execute_write(work)

    async def acreate_relationship(
        self,
        session: Neo4jAsyncSession,
        *,
        from_id: Any,
        to_id: Any,
        rel_type: str,
        to_label: Optional[Union[str, Sequence[str]]] = None,
        rel_properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        to_labels_raw = (
            [to_label]
            if isinstance(to_label, str) or to_label is None
            else list(to_label)
        )
        to_labels: List[str] = [lbl for lbl in to_labels_raw if lbl is not None]
        to_fragment = ":" + ":".join(self.labels if to_label is None else to_labels)
        auth_props = rel_properties or {}
        from_match = (
            f"MATCH (a{self.label_fragment}) WHERE "
            f"{'elementId(a)' if self.use_internal_id else f'a.{self.id_field}'} = $from_id"
        )
        to_match = (
            f"MATCH (b{to_fragment}) WHERE "
            f"{'elementId(b)' if self.use_internal_id else f'b.{self.id_field}'} = $to_id"
        )
        cypher = (
            f"{from_match} {to_match} MERGE (a)-[r:{rel_type}]->(b) SET r += $rel_props"
        )
        params: Dict[str, Any] = {
            "from_id": str(from_id) if self.use_internal_id else from_id,
            "to_id": str(to_id) if self.use_internal_id else to_id,
            "rel_props": auth_props,
        }
        if self.use_internal_id and str(from_id).isdigit():
            params["from_id_int"] = int(str(from_id))
            cypher = cypher.replace(
                "elementId(a) = $from_id",
                "(elementId(a) = $from_id OR id(a) = $from_id_int)",
            )
        if self.use_internal_id and str(to_id).isdigit():
            params["to_id_int"] = int(str(to_id))
            cypher = cypher.replace(
                "elementId(b) = $to_id",
                "(elementId(b) = $to_id OR id(b) = $to_id_int)",
            )

        async def work(tx):
            await tx.run(cypher, params)

        await session.execute_write(work)

    def get_related(
        self,
        session: Neo4jSession,
        *,
        _id: Any,
        rel_type: str,
        direction: str = "out",
        related_label: Optional[Union[str, Sequence[str]]] = None,
        query: Optional[QueryBase | dict] = None,
    ) -> List[ModelType]:
        where, order_clause, paging, params = translate_query(
            query,
            alias="m",
            id_field=self.id_field,
            use_internal_id=self.use_internal_id,
        )
        params["from_id"] = str(_id) if self.use_internal_id else _id
        if self.use_internal_id and str(_id).isdigit():
            params["from_id_int"] = int(str(_id))
        if self.use_internal_id and str(_id).isdigit():
            params["from_id_int"] = int(str(_id))
        if self.use_internal_id and str(_id).isdigit():
            params["from_id_int"] = int(str(_id))
        related_labels_raw = (
            [related_label]
            if isinstance(related_label, str) or related_label is None
            else list(related_label)
        )
        related_labels: List[str] = [
            lbl for lbl in related_labels_raw if lbl is not None
        ]
        related_fragment = ":" + ":".join(
            self.labels if related_label is None else related_labels
        )
        if direction == "out":
            pattern = f"(n{self.label_fragment})-[:{rel_type}]->(m{related_fragment})"
        elif direction == "in":
            pattern = f"(n{self.label_fragment})<-[:{rel_type}]-(m{related_fragment})"
        else:
            pattern = f"(n{self.label_fragment})-[:{rel_type}]-(m{related_fragment})"
        if self.use_internal_id:
            base_parts = ["elementId(n) = $from_id", f"n.{self.id_field} = $from_id"]
            if "from_id_int" in params:
                base_parts.append("id(n) = $from_id_int")
            base_condition = "(" + " OR ".join(base_parts) + ")"
        else:
            base_condition = f"n.{self.id_field} = $from_id"
        extra = where.replace("WHERE", "", 1).strip() if where else ""
        if extra:
            where_clause = f"WHERE {base_condition} AND {extra}"
        else:
            where_clause = f"WHERE {base_condition}"
        match = f"MATCH {pattern} {where_clause}"
        cypher = " ".join([match, "RETURN m", order_clause, paging])

        def work(tx):
            result = tx.run(cypher, params)
            data = result.data()
            return [record["m"] for record in data]

        nodes = session.execute_read(work)
        return [self._hydrate(node) for node in nodes]

    async def aget_related(
        self,
        session: Neo4jAsyncSession,
        *,
        _id: Any,
        rel_type: str,
        direction: str = "out",
        related_label: Optional[Union[str, Sequence[str]]] = None,
        query: Optional[QueryBase | dict] = None,
    ) -> List[ModelType]:
        where, order_clause, paging, params = translate_query(
            query,
            alias="m",
            id_field=self.id_field,
            use_internal_id=self.use_internal_id,
        )
        params["from_id"] = str(_id) if self.use_internal_id else _id
        related_labels_raw = (
            [related_label]
            if isinstance(related_label, str) or related_label is None
            else list(related_label)
        )
        related_labels: List[str] = [
            lbl for lbl in related_labels_raw if lbl is not None
        ]
        related_fragment = ":" + ":".join(
            self.labels if related_label is None else related_labels
        )
        if direction == "out":
            pattern = f"(n{self.label_fragment})-[:{rel_type}]->(m{related_fragment})"
        elif direction == "in":
            pattern = f"(n{self.label_fragment})<-[:{rel_type}]-(m{related_fragment})"
        else:
            pattern = f"(n{self.label_fragment})-[:{rel_type}]-(m{related_fragment})"
        if self.use_internal_id:
            base_parts = ["elementId(n) = $from_id", f"n.{self.id_field} = $from_id"]
            if "from_id_int" in params:
                base_parts.append("id(n) = $from_id_int")
            base_condition = "(" + " OR ".join(base_parts) + ")"
        else:
            base_condition = f"n.{self.id_field} = $from_id"
        extra = where.replace("WHERE", "", 1).strip() if where else ""
        if extra:
            where_clause = f"WHERE {base_condition} AND {extra}"
        else:
            where_clause = f"WHERE {base_condition}"
        match = f"MATCH {pattern} {where_clause}"
        cypher = " ".join([match, "RETURN m", order_clause, paging])

        async def work(tx):
            result = await tx.run(cypher, params)
            data = await result.data()
            return [record["m"] for record in data]

        nodes = await session.execute_read(work)
        return [self._hydrate(node) for node in nodes]

    def delete_relationship(
        self,
        session: Neo4jSession,
        *,
        from_id: Any,
        to_id: Any,
        rel_type: str,
    ) -> int:
        match = (
            f"MATCH (a{self.label_fragment})-[r:{rel_type}]-(b) "
            f"WHERE {'elementId(a)' if self.use_internal_id else f'a.{self.id_field}'} = $from_id "
            f"AND {'elementId(b)' if self.use_internal_id else f'b.{self.id_field}'} = $to_id "
            "DELETE r RETURN count(r) AS deleted"
        )
        from_param = str(from_id) if self.use_internal_id else from_id
        to_param = str(to_id) if self.use_internal_id else to_id
        params: Dict[str, Any] = {"from_id": from_param, "to_id": to_param}
        if self.use_internal_id and str(from_id).isdigit():
            params["from_id_int"] = int(str(from_id))
            match = match.replace(
                "elementId(a) = $from_id",
                "(elementId(a) = $from_id OR id(a) = $from_id_int)",
            )
        if self.use_internal_id and str(to_id).isdigit():
            params["to_id_int"] = int(str(to_id))
            match = match.replace(
                "elementId(b) = $to_id",
                "(elementId(b) = $to_id OR id(b) = $to_id_int)",
            )

        def work(tx):
            result = tx.run(match, params)
            data = result.data()
            return data[0]["deleted"] if data else 0

        return session.execute_write(work)

    async def adelete_relationship(
        self,
        session: Neo4jAsyncSession,
        *,
        from_id: Any,
        to_id: Any,
        rel_type: str,
    ) -> int:
        match = (
            f"MATCH (a{self.label_fragment})-[r:{rel_type}]-(b) "
            f"WHERE {'elementId(a)' if self.use_internal_id else f'a.{self.id_field}'} = $from_id "
            f"AND {'elementId(b)' if self.use_internal_id else f'b.{self.id_field}'} = $to_id "
            "DELETE r RETURN count(r) AS deleted"
        )
        from_param = str(from_id) if self.use_internal_id else from_id
        to_param = str(to_id) if self.use_internal_id else to_id
        params: Dict[str, Any] = {"from_id": from_param, "to_id": to_param}
        if self.use_internal_id and str(from_id).isdigit():
            params["from_id_int"] = int(str(from_id))
            match = match.replace(
                "elementId(a) = $from_id",
                "(elementId(a) = $from_id OR id(a) = $from_id_int)",
            )
        if self.use_internal_id and str(to_id).isdigit():
            params["to_id_int"] = int(str(to_id))
            match = match.replace(
                "elementId(b) = $to_id",
                "(elementId(b) = $to_id OR id(b) = $to_id_int)",
            )

        async def work(tx):
            result = await tx.run(match, params)
            data = await result.data()
            return data[0]["deleted"] if data else 0

        return await session.execute_write(work)
