from typing import Any, Generic, List, Mapping, Optional, Sequence, Type, TypeVar

from deprecated import deprecated
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)

from ..schemas import QueryBase
from .mongo_util import (
    MaybeObjectId,
    build_object_id,
    cleanse_query_for_first,
    cleanse_query_for_list,
    cleanse_query_order_by,
)

ModelType = TypeVar("ModelType", bound=BaseModel)


class MongoCRUDBase(Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        collection: str,
        database: str,
        *,
        searchable: Optional[List[str]] = None,
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD), in Mongo
        """
        self.model = model
        self.collection = collection
        self.searchable = searchable
        self.database = database

    def first(
        self,
        m: MongoClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
        **kwargs,
    ) -> Optional[ModelType]:
        doc = self.first_doc(m, query=query, project=project, **kwargs)
        return self.model(**doc) if doc is not None else None

    async def afirst(
        self,
        m: AsyncIOMotorClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
        **kwargs,
    ) -> Optional[ModelType]:
        """Asynchronously fetch the first document and parse it into a Pydantic model."""
        doc = await self.afirst_doc(m, query=query, project=project, **kwargs)
        return self.model(**doc) if doc else None

    def first_doc(
        self,
        m: MongoClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
        **kwargs,
    ) -> Optional[dict]:
        doc: Optional[dict] = m[self.database][self.collection].find_one(
            {**cleanse_query_for_first(query)},
            project,
            **kwargs,
            sort=cleanse_query_order_by(query),
        )
        return doc

    async def afirst_doc(
        self,
        m: AsyncIOMotorClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
        **kwargs,
    ) -> Optional[dict]:
        """Asynchronously fetch the first document matching the query."""
        doc = await m[self.database][self.collection].find_one(
            {**cleanse_query_for_first(query)},
            project,
            **kwargs,
            sort=cleanse_query_order_by(query),
        )
        return doc

    def get_multi(
        self,
        m: MongoClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
    ) -> List[ModelType]:
        docs = self.get_multi_docs(m, query=query, project=project)
        return [self.model(**doc) for doc in docs]

    async def aget_multi(
        self,
        m: AsyncIOMotorClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
    ) -> List[ModelType]:
        """Asynchronously fetch multiple documents and parse them into Pydantic models."""
        docs = await self.aget_multi_docs(m, query=query, project=project)
        return [self.model(**doc) for doc in docs]

    def get_multi_docs(
        self,
        m: MongoClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
    ) -> List[dict]:
        if isinstance(query, dict):
            query = QueryBase(**query)
        _sort = cleanse_query_order_by(query)
        cursor = m[self.database][self.collection].find(
            {**cleanse_query_for_list(query)}, project
        )
        if _sort is not None and len(_sort) > 0:
            cursor = cursor.sort(_sort)
        if query is not None and query.offset is not None:
            if not isinstance(query.offset, int):
                raise ValueError(
                    f"[Db] Expected query offset to be type int, but got {query.offset}"
                )
            cursor = cursor.skip(int(query.offset))
        if query is not None and query.limit is not None:
            assert isinstance(query.limit, int), (
                f"[Db] Expected query limit to be type int, but got {query.limit}"
            )
            cursor = cursor.limit(query.limit)
        docs: List[dict] = list(cursor)
        return docs

    async def aget_multi_docs(
        self,
        m: AsyncIOMotorClient,
        *,
        query: Optional[QueryBase | dict] = None,
        project: Optional[dict] = None,
    ) -> List[dict]:
        """Asynchronously fetch multiple documents as raw dictionaries."""
        if isinstance(query, dict):
            query = QueryBase(**query)
        _sort = cleanse_query_order_by(query)
        cursor = m[self.database][self.collection].find(
            {**cleanse_query_for_list(query)}, project
        )
        if _sort:
            cursor = cursor.sort(_sort)
        if query and query.offset is not None:
            if not isinstance(query.offset, int):
                raise ValueError(
                    f"[Db] Expected query offset to be type int, but got {query.offset}"
                )
            cursor = cursor.skip(query.offset)
        if query and query.limit is not None:
            cursor = cursor.limit(query.limit)
        docs = [doc async for doc in cursor]
        return docs

    def create(self, m: MongoClient, *, obj_in: ModelType) -> InsertOneResult:
        return m[self.database][self.collection].insert_one(obj_in.model_dump())

    async def acreate(
        self, m: AsyncIOMotorClient, *, obj_in: ModelType
    ) -> InsertOneResult:
        """Asynchronously create a single document."""
        return await m[self.database][self.collection].insert_one(obj_in.model_dump())

    def create_multi(
        self, m: MongoClient, *, obj_in_list: List[ModelType]
    ) -> InsertManyResult:
        return m[self.database][self.collection].insert_many(
            [obj_in.model_dump() for obj_in in obj_in_list]
        )

    async def acreate_multi(
        self, m: AsyncIOMotorClient, *, obj_in_list: List[ModelType]
    ) -> InsertManyResult:
        """Asynchronously create multiple documents."""
        return await m[self.database][self.collection].insert_many(
            [obj.model_dump() for obj in obj_in_list]
        )

    def update(
        self,
        m: MongoClient,
        *,
        _id: MaybeObjectId,
        obj_in: dict,
    ) -> UpdateResult:
        return m[self.database][self.collection].update_one(
            {"_id": build_object_id(_id)}, {"$set": obj_in}
        )

    async def aupdate(
        self, m: AsyncIOMotorClient, *, _id: MaybeObjectId, obj_in: dict
    ) -> UpdateResult:
        """Asynchronously update a document by ID."""
        return await m[self.database][self.collection].update_one(
            {"_id": build_object_id(_id)}, {"$set": obj_in}
        )

    @deprecated(
        reason="remove in next version, this method does nothing but setting a optional value in the mongo object dict, 'update' as True, which is inappropriate."
    )
    def hide(
        self,
        m: MongoClient,
        *,
        _id: MaybeObjectId,
    ) -> UpdateResult:
        return self.update(m, _id=_id, obj_in={"update": True})

    def delete(
        self,
        m: MongoClient,
        *,
        _id: MaybeObjectId,
    ) -> DeleteResult:
        return m[self.database][self.collection].delete_one(
            {"_id": build_object_id(_id)}
        )

    async def adelete(
        self, m: AsyncIOMotorClient, *, _id: MaybeObjectId
    ) -> DeleteResult:
        """Asynchronously delete a document by ID."""
        return await m[self.database][self.collection].delete_one(
            {"_id": build_object_id(_id)}
        )

    def delete_multi(
        self, m: MongoClient, *, query: Optional[QueryBase | dict]
    ) -> DeleteResult:
        if query is None:
            query_dict = {}
        else:
            if isinstance(query, dict):
                query = QueryBase(**query)
            query_dict: dict = query.model_dump(
                exclude_none=True, exclude_unset=True, exclude_defaults=True
            )
        if not ("filters" in query_dict and query_dict["filters"] is not None):
            raise ValueError(
                "[Db] You must set, and only set query.filters to delete_multi in mongodb"
            )
        return m[self.database][self.collection].delete_many(query_dict["filters"])

    async def adelete_multi(
        self, m: AsyncIOMotorClient, *, query: Optional[QueryBase | dict]
    ) -> DeleteResult:
        """Asynchronously delete multiple documents based on a query."""
        if query is None:
            query_dict = {}
        else:
            if isinstance(query, dict):
                query = QueryBase(**query)
            query_dict = query.model_dump(
                exclude_none=True, exclude_unset=True, exclude_defaults=True
            )
        if not ("filters" in query_dict and query_dict["filters"] is not None):
            raise ValueError(
                "[Db] You must set, and only set query.filters to adelete_multi in mongodb"
            )
        return await m[self.database][self.collection].delete_many(
            query_dict["filters"]
        )

    def first_by_id(
        self, m: MongoClient, *, _id: MaybeObjectId, **kwargs
    ) -> Optional[ModelType]:
        return self.first(
            m, query=QueryBase(id=_id if isinstance(_id, str) else str(_id)), **kwargs
        )  # convert type for inserted_id

    async def afirst_by_id(
        self, m: AsyncIOMotorClient, *, _id: MaybeObjectId, **kwargs
    ) -> Optional[ModelType]:
        """Asynchronously fetch the first document by ID and parse it into a Pydantic model."""
        return await self.afirst(
            m, query=QueryBase(id=_id if isinstance(_id, str) else str(_id)), **kwargs
        )

    def first_doc_by_id(
        self, m: MongoClient, *, _id: MaybeObjectId, **kwargs
    ) -> Optional[dict]:
        return self.first_doc(
            m, query=QueryBase(id=_id if isinstance(_id, str) else str(_id)), **kwargs
        )  # convert type for inserted_id

    async def afirst_doc_by_id(
        self, m: AsyncIOMotorClient, *, _id: MaybeObjectId, **kwargs
    ) -> Optional[dict]:
        """Asynchronously fetch the first document by ID."""
        return await self.afirst_doc(
            m, query=QueryBase(id=_id if isinstance(_id, str) else str(_id)), **kwargs
        )

    def aggregate(
        self,
        m: MongoClient,
        *,
        pipelines: Sequence[Mapping[str, Any]],
        model: Type[BaseModel],
        let: Optional[Mapping[str, Any]] = None,
    ) -> List[BaseModel]:
        docs = m[self.database][self.collection].aggregate(pipelines, let=let)
        return [model(**d) for d in docs]

    async def aaggregate(
        self,
        m: AsyncIOMotorClient,
        *,
        pipelines: Sequence[Mapping[str, Any]],
        model: Type[BaseModel],
        let: Optional[Mapping[str, Any]] = None,
    ) -> List[BaseModel]:
        """Asynchronously perform an aggregation query and parse results into Pydantic models."""
        cursor = m[self.database][self.collection].aggregate(pipelines, let=let)
        results = []
        async for doc in cursor:
            results.append(model(**doc))
        return results

    def count(
        self,
        m: MongoClient,
        *,
        query: Optional[QueryBase | dict] = None,
    ) -> int:
        """Count documents matching the query."""
        return m[self.database][self.collection].count_documents(
            {**cleanse_query_for_list(query)}
        )

    async def acount(
        self,
        m: AsyncIOMotorClient,
        *,
        query: Optional[QueryBase | dict] = None,
    ) -> int:
        """Asynchronously count documents matching the query."""
        return await m[self.database][self.collection].count_documents(
            {**cleanse_query_for_list(query)}
        )
