import uuid
from abc import ABC, abstractmethod
from typing import Annotated, Any, List, Optional, Type, Union, get_args, get_origin
from uuid import UUID as _UUID

from bson import Binary
from bson import ObjectId as _ObjectId
from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from qdrant_client.conversions.common_types import PointId


def is_optional(field):
    return get_origin(field) is Union and type(None) in get_args(field)


class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(cls, v: Any, handler) -> _ObjectId:
        if isinstance(v, _ObjectId):
            return v

        s = handler(v)
        if _ObjectId.is_valid(s):
            return _ObjectId(s)
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, _handler
    ) -> core_schema.CoreSchema:
        assert source_type is _ObjectId or (
            is_optional(source_type) and _ObjectId in get_args(source_type)
        ), (
            "[Db] Internal error, expected source_type is _ObjectId or (is_optional(source_type) and _ObjectId in get_args(source_type))"
        )
        return core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


ObjectId = Annotated[_ObjectId, ObjectIdPydanticAnnotation]


class Uuid(_UUID):
    @classmethod
    def new(cls) -> _UUID:
        return uuid.uuid4()

    @classmethod
    def validate_uuid(cls, v: Any) -> _UUID:
        if isinstance(v, _UUID):
            return v
        if isinstance(v, str):
            return _UUID(v)
        if isinstance(v, Binary):
            return v.as_uuid()
        raise ValueError(f"[Db] Unidentifieable UUID data type: {v}")

    # def to_binary(self):
    #     return Binary.from_uuid(self)

    @classmethod
    def from_uuid(cls, payload) -> Binary:
        if isinstance(payload, Binary):
            return payload
        return Binary.from_uuid(payload)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate_uuid,
            core_schema.uuid_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=cls.from_uuid
            ),
        )


# add json plain serializer to Uuid
# Uuid = Annotated[
#     Uuid, PlainSerializer(lambda x: str(x), return_type=str, when_used='json') # this will override the __get_pydantic_core_schema__ declared above.
# ]

MaybeUuid = Union[Uuid, _UUID, Binary]


def to_binary_uuid(uuid_: Union[MaybeUuid, List[MaybeUuid]]):
    if isinstance(uuid_, list):
        return [to_binary_uuid(u) for u in uuid_]
    if isinstance(uuid_, Binary):
        return uuid_
    return Binary.from_uuid(uuid_)


def serialize_object_ids_in_dict(mey_be_dict: Any):
    if not isinstance(mey_be_dict, dict):
        return
    for key, val in mey_be_dict.items():
        if isinstance(val, _ObjectId):
            mey_be_dict[key] = str(val)
        elif isinstance(val, dict):
            serialize_object_ids_in_dict(val)
        elif isinstance(val, list):
            for item in val:
                serialize_object_ids_in_dict(item)


class DbSettingsABC(ABC):
    @property
    @abstractmethod
    def qdrant_host(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def qdrant_port(self) -> Optional[int]: ...

    @property
    @abstractmethod
    def mongo_db_uri(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def redis_uri(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def sql_write_uri(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def sql_read_uri(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def sql_uri(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def neo4j_uri(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def neo4j_user(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def neo4j_password(self) -> Optional[str]: ...

    @property
    @abstractmethod
    def neo4j_database(self) -> Optional[str]: ...


class QueryBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    offset: Optional[int | str | PointId] = None
    limit: Optional[int] = None
    filters: Optional[Union[dict, List[Any]]] = None
    order_by: Optional[Any] = None

    id: Optional[Union[ObjectId, Uuid, str, int]] = None
    ids: Optional[List[Union[ObjectId, Uuid, str, int]]] = None

    def __init__(
        self,
        offset: Optional[Union[int, str, PointId]] = None,
        limit: Optional[int] = None,
        filters: Optional[Union[dict, List[Any]]] = None,
        order_by: Optional[Any] = None,
        id: Optional[Union[ObjectId, Uuid, str, int]] = None,
        ids: Optional[List[Union[ObjectId, Uuid, str, int]]] = None,
    ):
        # Perform custom initialization logic if necessary

        # Call the Pydantic BaseModel initializer to perform the standard model validation and initialization
        super().__init__(
            offset=offset,
            limit=limit,
            filters=filters,
            order_by=order_by,
            id=id,
            ids=ids,
        )

    @classmethod
    def loop(cls, func, *args, **kwargs) -> List[Any]:
        page = 0
        page_size = 100
        res = []
        has_more = True
        base_query: QueryBase | None = kwargs.get("query")
        if "query" in kwargs:
            del kwargs["query"]
        base_query_dict: dict = (
            base_query.model_dump() if base_query is not None else {}
        )
        if "offset" in base_query_dict:
            del base_query_dict["offset"]
        if "limit" in base_query_dict:
            del base_query_dict["limit"]
        while page < 10000 and has_more:
            query = QueryBase(
                **base_query_dict, limit=page_size, offset=page * page_size
            )

            output = func(*args, **kwargs, query=query)
            if len(output) == 0:
                break
            has_more = len(output) == page_size
            res += output
            page += 1
        return res

    @classmethod
    async def aloop(cls, afunc, *args, **kwargs) -> List[Any]:
        page = 0
        page_size = 100
        res = []
        has_more = True
        base_query: QueryBase | None = kwargs.get("query")
        if "query" in kwargs:
            del kwargs["query"]
        base_query_dict: dict = (
            base_query.model_dump() if base_query is not None else {}
        )
        if "offset" in base_query_dict:
            del base_query_dict["offset"]
        if "limit" in base_query_dict:
            del base_query_dict["limit"]
        while page < 10000 and has_more:
            query = QueryBase(
                **base_query_dict, limit=page_size, offset=page * page_size
            )

            output = await afunc(*args, **kwargs, query=query)
            if len(output) == 0:
                break
            has_more = len(output) == page_size
            res += output
            page += 1
        return res

    @classmethod
    def qdrant_scroll(cls, func, *args, **kwargs) -> List[Any]:
        page = 0
        page_size = 100
        offset = None  # point id
        res = []
        has_more = True
        base_query: QueryBase | None = kwargs.get("query")
        if "query" in kwargs:
            del kwargs["query"]

        base_query_dict: dict = (
            base_query.model_dump() if base_query is not None else {}
        )
        if "offset" in base_query_dict:
            del base_query_dict["offset"]
        if "limit" in base_query_dict:
            del base_query_dict["limit"]
        while page < 10000 and has_more:
            query = QueryBase(**base_query_dict, limit=page_size, offset=offset)
            output, next_point_id = func(*args, **kwargs, query=query)
            if len(output) == 0:
                break
            has_more = next_point_id is not None
            res += output
            page += 1
            offset = next_point_id
        return res
