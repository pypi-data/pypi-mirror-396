from typing import Any, Generic, List, Optional, Sequence, Tuple, Type, TypeVar, cast

from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client import models as qdrant_models
from qdrant_client.conversions import common_types as qdrant_types
from qdrant_client.models import UpdateResult

from ..schemas import QueryBase
from .qdrant_util import cleanse_query_for_search

ModelType = TypeVar("ModelType", bound=BaseModel)
VectorModelType = TypeVar("VectorModelType", bound=BaseModel)


class Record(qdrant_types.Record, Generic[VectorModelType]):
    payload: Optional[Any] = None
    score: Optional[float] = None
    vector: Optional[VectorModelType] = None


class QdrantCRUDBase(Generic[ModelType, VectorModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        vector_model: Type[VectorModelType],
        collection: str,
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD) in Qdrant

        **Parameters**
        * `model`: A Qdrant Alchemy model class
        """
        self.model: Type[ModelType] = model
        self.vector_model: Type[VectorModelType] = vector_model
        self.collection = collection

    def __is_result_success(self, result: qdrant_types.UpdateResult):
        return (
            result.status.lower() == qdrant_models.UpdateStatus.COMPLETED.value.lower()
        )

    def __convert_record(self, record: qdrant_types.Record) -> Record[VectorModelType]:
        assert record.vector is None or isinstance(record.vector, dict), (
            f"[Db] Expected record.vector to be a dict or None, but got {record.vector}"
        )
        return Record(
            **record.model_dump(exclude={"payload", "vector"}),
            payload=self.model(**record.payload)
            if record.payload is not None
            else None,
            vector=self.vector_model(**record.vector)
            if record.vector is not None
            else None,
        )

    def __convert_records(self, records: List[qdrant_types.Record]) -> List[Record]:
        return [self.__convert_record(record=record) for record in records]

    def get_multi_records_by_ids(
        self, client: QdrantClient, *, _ids: Sequence[qdrant_types.PointId], **kwargs
    ) -> List[Record]:
        return self.__convert_records(
            client.retrieve(self.collection, ids=_ids, **kwargs)
        )

    async def aget_multi_records_by_ids(
        self,
        client: AsyncQdrantClient,
        *,
        _ids: Sequence[qdrant_types.PointId],
        **kwargs,
    ) -> List[Record]:
        return self.__convert_records(
            await client.retrieve(self.collection, ids=_ids, **kwargs)
        )

    def get_multi_by_ids(
        self, client: QdrantClient, *, _ids: Sequence[qdrant_types.PointId], **kwargs
    ) -> List[ModelType]:
        records = self.get_multi_records_by_ids(client, _ids=_ids, **kwargs)
        return [r.payload for r in records if r.payload is not None]

    async def aget_multi_by_ids(
        self,
        client: AsyncQdrantClient,
        *,
        _ids: Sequence[qdrant_types.PointId],
        **kwargs,
    ) -> List[ModelType]:
        records = await self.aget_multi_records_by_ids(client, _ids=_ids, **kwargs)
        return [r.payload for r in records if r.payload is not None]

    def first_record_by_id(
        self, client: QdrantClient, *, _id: qdrant_types.PointId, **kwargs
    ) -> Optional[Record]:
        records: List[Record] = self.get_multi_records_by_ids(
            client, _ids=[_id], **kwargs
        )
        if len(records) < 1:
            return None
        return records[0]

    async def afirst_record_by_id(
        self, client: AsyncQdrantClient, *, _id: qdrant_types.PointId, **kwargs
    ) -> Optional[Record]:
        records: List[Record] = await self.aget_multi_records_by_ids(
            client, _ids=[_id], **kwargs
        )
        if len(records) < 1:
            return None
        return records[0]

    def first_by_id(
        self, client: QdrantClient, *, _id: qdrant_types.PointId, **kwargs
    ) -> Optional[ModelType]:
        record = self.first_record_by_id(client, _id=_id, **kwargs)
        if record is not None:
            return record.payload

    async def afirst_by_id(
        self, client: AsyncQdrantClient, *, _id: qdrant_types.PointId, **kwargs
    ) -> Optional[ModelType]:
        record = await self.afirst_record_by_id(client, _id=_id, **kwargs)
        if record is not None:
            return record.payload

    @classmethod
    def _build_search_kwargs(cls, query: Optional[QueryBase | dict] = None):
        filter_ = cleanse_query_for_search(query, offset_type="int")
        offset = None
        if isinstance(query, dict):
            query = QueryBase(**query)
        if query is not None and query.offset is not None:
            assert isinstance(query.offset, int), (
                f"[Db] Expected search in qdrant with int or None type offset, but got {query.offset}"
            )
            offset = query.offset
        return {
            "query_filter": filter_,
            "limit": query.limit
            if query is not None and query.limit is not None
            else 100,  # by default 100
            "offset": offset,
        }

    def search(
        self,
        client: QdrantClient,
        *,
        vector: List[float],
        vector_key: str,
        query: Optional[QueryBase | dict] = None,
        score_threshold: float = 0.76,
        # 0.76 ~ 0.8 is a decent threshold base on our test, among different languages
        **kwargs,
    ) -> List[Record]:
        search_kwargs = self._build_search_kwargs(query)
        if hasattr(client, "search"):
            scored_points: List[qdrant_types.ScoredPoint] = client.search(  # type: ignore
                self.collection,
                query_vector=(vector_key, vector),
                score_threshold=score_threshold,
                **search_kwargs,
                **kwargs,
            )
        else:
            resp = client.query_points(
                collection_name=self.collection,
                query=vector,
                using=vector_key,
                score_threshold=score_threshold,
                with_vectors=True,
                **search_kwargs,
                **kwargs,
            )
            scored_points = resp.points if hasattr(resp, "points") else []
        return [
            Record(
                **sp.model_dump(include={"score", "shard_key", "id"}),
                payload=self.model(**sp.payload) if sp.payload is not None else None,
                vector=self.vector_model(**sp.vector)  # type: ignore
                if sp.vector is not None
                else None,
            )
            for sp in scored_points
        ]

    async def asearch(
        self,
        client: AsyncQdrantClient,
        *,
        vector: List[float],
        vector_key: str,
        query: Optional[QueryBase | dict] = None,
        score_threshold: float = 0.76,
        # 0.76 ~ 0.8 is a decent threshold base on our test, among different languages
        **kwargs,
    ) -> List[Record]:
        search_kwargs = self._build_search_kwargs(query)
        if hasattr(client, "search"):
            scored_points: List[qdrant_types.ScoredPoint] = await client.search(  # type: ignore
                self.collection,
                query_vector=(vector_key, vector),
                score_threshold=score_threshold,
                **search_kwargs,
                **kwargs,
            )
        else:
            resp = await client.query_points(
                collection_name=self.collection,
                query=vector,
                using=vector_key,
                score_threshold=score_threshold,
                with_vectors=True,
                **search_kwargs,
                **kwargs,
            )
            scored_points = resp.points if hasattr(resp, "points") else []
        return [
            Record(
                **sp.model_dump(include={"score", "shard_key", "id"}),
                payload=self.model(**sp.payload) if sp.payload is not None else None,
                vector=self.vector_model(**sp.vector)  # type: ignore
                if sp.vector is not None
                else None,
            )
            for sp in scored_points
        ]

    @classmethod
    def _build_scroll_kwargs(cls, query: Optional[QueryBase | dict] = None):
        if isinstance(query, dict):
            query = QueryBase(**query)
        filter_ = cleanse_query_for_search(query, offset_type="str")
        assert query is None or query.limit is not None, (
            "[Db] You need to provide limit to perform a scroll in Qdrant"
        )
        offset = None
        if query is not None and query.offset is not None:
            assert isinstance(query.offset, str), (
                f"[Db] Expected str or None type query offset when scrolling records in qdrant, but got {query.offset}"
            )
            offset = query.offset

        return {
            "scroll_filter": filter_,
            "limit": query.limit
            if query is not None and query.limit is not None
            else 100,
            "offset": offset,
        }

    def scroll_records(
        self, client: QdrantClient, *, query: QueryBase | dict | None, **kwargs
    ) -> Tuple[List[Record], Optional[qdrant_types.PointId]]:
        records, next_point_id = client.scroll(
            self.collection, **self._build_scroll_kwargs(query), **kwargs
        )
        return self.__convert_records(records), next_point_id

    async def ascroll_records(
        self, client: AsyncQdrantClient, *, query: QueryBase | dict | None, **kwargs
    ) -> Tuple[List[Record], Optional[qdrant_types.PointId]]:
        records, next_point_id = await client.scroll(
            self.collection, **self._build_scroll_kwargs(query), **kwargs
        )
        return self.__convert_records(records), next_point_id

    def scroll(
        self, client: QdrantClient, *, query: QueryBase | dict | None, **kwargs
    ) -> Tuple[List[ModelType], Optional[qdrant_types.PointId]]:
        records, next_point_id = self.scroll_records(client, query=query, **kwargs)
        return [
            record.payload for record in records if record.payload is not None
        ], next_point_id

    async def ascroll(
        self, client: AsyncQdrantClient, *, query: QueryBase | dict | None, **kwargs
    ) -> Tuple[List[ModelType], Optional[qdrant_types.PointId]]:
        records, next_point_id = await self.ascroll_records(
            client, query=query, **kwargs
        )
        return [
            record.payload for record in records if record.payload is not None
        ], next_point_id

    def _return_create_response(self, response: UpdateResult):
        _, status = response
        status = status[1] if isinstance(status, tuple) and len(status) > 1 else status
        return str(status).lower() == qdrant_models.UpdateStatus.COMPLETED.value.lower()

    def create(
        self,
        client: QdrantClient,
        vector: VectorModelType,
        payload: ModelType,
        _id: qdrant_types.PointId,
        **kwargs,
    ) -> bool:
        vector_dict = vector.model_dump(exclude_none=True, exclude_unset=True)
        return self._return_create_response(
            client.upsert(
                collection_name=self.collection,
                points=[
                    qdrant_models.PointStruct(
                        id=cast(qdrant_models.ExtendedPointId, _id),
                        vector=vector_dict,
                        payload=payload.model_dump(),
                    )
                ],
                **kwargs,
            )
        )

    async def acreate(
        self,
        client: AsyncQdrantClient,
        vector: VectorModelType,
        payload: ModelType,
        _id: qdrant_types.PointId,
        **kwargs,
    ) -> bool:
        vector_dict = vector.model_dump(exclude_none=True, exclude_unset=True)
        return self._return_create_response(
            await client.upsert(
                collection_name=self.collection,
                points=[
                    qdrant_models.PointStruct(
                        id=cast(qdrant_models.ExtendedPointId, _id),
                        vector=vector_dict,
                        payload=payload.model_dump(),
                    )
                ],
                **kwargs,
            )
        )

    def create_multi(
        self,
        client: QdrantClient,
        *,
        payloads_and_vectors: List[Tuple[str, ModelType, VectorModelType]],
        **kwargs,
    ) -> bool:
        points: List[qdrant_models.PointStruct] = [
            qdrant_models.PointStruct(
                id=_id,
                vector=vector.model_dump(exclude_none=True, exclude_unset=True),
                payload=payload.model_dump(),
            )
            for _id, payload, vector in payloads_and_vectors
        ]
        return self._return_create_response(
            client.upsert(collection_name=self.collection, points=points, **kwargs)
        )

    async def acreate_multi(
        self,
        client: AsyncQdrantClient,
        *,
        payloads_and_vectors: List[Tuple[str, ModelType, VectorModelType]],
        **kwargs,
    ) -> bool:
        points: List[qdrant_models.PointStruct] = [
            qdrant_models.PointStruct(
                id=_id,
                vector=vector.model_dump(exclude_none=True, exclude_unset=True),
                payload=payload.model_dump(),
            )
            for _id, payload, vector in payloads_and_vectors
        ]
        return self._return_create_response(
            await client.upsert(
                collection_name=self.collection, points=points, **kwargs
            )
        )

    def delete(
        self, client: QdrantClient, *, _id: qdrant_types.PointId, **kwargs
    ) -> bool:
        update_result: qdrant_types.UpdateResult = client.delete(
            self.collection, points_selector=[_id], **kwargs
        )
        return self.__is_result_success(update_result)

    async def adelete(
        self, client: AsyncQdrantClient, *, _id: qdrant_types.PointId, **kwargs
    ) -> bool:
        update_result: qdrant_types.UpdateResult = await client.delete(
            self.collection, points_selector=[_id], **kwargs
        )
        return self.__is_result_success(update_result)

    def _get_points_selector_by_delete_query(
        self,
        query: QueryBase | dict | None,
    ) -> qdrant_models.PointIdsList | qdrant_models.FilterSelector:
        if query is None:
            query_dict: dict = {}
        else:
            if isinstance(query, dict):
                query = QueryBase(**query)
            query_dict: dict = query.model_dump(
                exclude_none=True, exclude_unset=True, exclude_defaults=True
            )
        filters_exist = "filters" in query_dict and query_dict["filters"] is not None
        ids_exist = "ids" in query_dict and query_dict["ids"] is not None
        if not (filters_exist or ids_exist):
            raise ValueError(
                "[Db] you must set query.ids or query.filters to delete_multi in qdrant"
            )
        if ids_exist:
            points_selector = qdrant_models.PointIdsList(points=query_dict["ids"])
        elif filters_exist:
            points_selector = qdrant_models.FilterSelector(filter=query_dict["filters"])
        else:
            raise Exception(
                "[Db] you must set query.ids or query.filters to delete_multi in qdrant"
            )
        return points_selector

    def delete_multi(
        self, client: QdrantClient, *, query: QueryBase | dict | None, **kwargs
    ):
        points_selector = self._get_points_selector_by_delete_query(query)
        update_result: qdrant_types.UpdateResult = client.delete(
            self.collection, points_selector=points_selector, **kwargs
        )
        return self.__is_result_success(update_result)

    async def adelete_multi(
        self, client: AsyncQdrantClient, *, query: QueryBase | dict | None, **kwargs
    ):
        points_selector = self._get_points_selector_by_delete_query(query)
        update_result: qdrant_types.UpdateResult = await client.delete(
            self.collection, points_selector=points_selector, **kwargs
        )
        return self.__is_result_success(update_result)

    def update_payload(
        self,
        client: QdrantClient,
        *,
        _id: qdrant_types.PointId,
        payload: ModelType,
        **kwargs,
    ):
        """Set Payload key value, not completely override entire payload object"""
        old_payload = self.first_by_id(client, _id=_id)
        if old_payload is not None:
            obj_dict = old_payload.model_dump()
            obj_dict.update(payload.model_dump())
            res = client.set_payload(
                collection_name=self.collection,
                payload=self.model(**obj_dict).model_dump(),
                points=[_id],
                **kwargs,
            )
            return self.__is_result_success(res)
        return False

    async def aupdate_payload(
        self,
        client: AsyncQdrantClient,
        *,
        _id: qdrant_types.PointId,
        payload: ModelType,
        **kwargs,
    ):
        """Set Payload key value, not completely override entire payload object"""
        old_payload = await self.afirst_by_id(client, _id=_id)
        if old_payload is not None:
            obj_dict = old_payload.model_dump()
            obj_dict.update(payload.model_dump())
            res = await client.set_payload(
                collection_name=self.collection,
                payload=self.model(**obj_dict).model_dump(),
                points=[_id],
                **kwargs,
            )
            return self.__is_result_success(res)
        return False

    def overwrite_payload(
        self,
        client: QdrantClient,
        *,
        _id: qdrant_types.PointId,
        payload: ModelType,
        **kwargs,
    ):
        """Completely override entire payload object, replace entire old payload"""
        res = client.overwrite_payload(
            collection_name=self.collection,
            payload=payload.model_dump(),
            points=[_id],
            **kwargs,
        )
        return self.__is_result_success(res)

    async def aoverwrite_payload(
        self,
        client: AsyncQdrantClient,
        *,
        _id: qdrant_types.PointId,
        payload: ModelType,
        **kwargs,
    ):
        """Completely override entire payload object, replace entire old payload"""
        res = await client.overwrite_payload(
            collection_name=self.collection,
            payload=payload.model_dump(),
            points=[_id],
            **kwargs,
        )
        return self.__is_result_success(res)

    def update_vector(
        self,
        client: QdrantClient,
        *,
        _id: qdrant_types.PointId,
        vector: VectorModelType,
        **kwargs,
    ) -> bool:
        res = client.update_vectors(
            collection_name=self.collection,
            points=[
                qdrant_models.PointVectors(
                    id=cast(qdrant_models.ExtendedPointId, _id),
                    vector=vector.model_dump(exclude_none=True, exclude_unset=True),
                )
            ],
            **kwargs,
        )
        return self.__is_result_success(res)

    async def aupdate_vector(
        self,
        client: AsyncQdrantClient,
        *,
        _id: qdrant_types.PointId,
        vector: VectorModelType,
        **kwargs,
    ) -> bool:
        res = await client.update_vectors(
            collection_name=self.collection,
            points=[
                qdrant_models.PointVectors(
                    id=cast(qdrant_models.ExtendedPointId, _id),
                    vector=vector.model_dump(exclude_none=True, exclude_unset=True),
                )
            ],
            **kwargs,
        )
        return self.__is_result_success(res)

    def count(
        self, client: QdrantClient, *, query: Optional[QueryBase | dict] = None
    ) -> int:
        filter_ = cleanse_query_for_search(query, offset_type="int")
        return client.count(
            collection_name=self.collection,
            count_filter=filter_,
            exact=True,
        ).count

    async def acount(
        self, client: AsyncQdrantClient, *, query: Optional[QueryBase | dict] = None
    ) -> int:
        filter_ = cleanse_query_for_search(query, offset_type="int")
        result = await client.count(
            collection_name=self.collection,
            count_filter=filter_,
            exact=True,
        )
        return result.count
