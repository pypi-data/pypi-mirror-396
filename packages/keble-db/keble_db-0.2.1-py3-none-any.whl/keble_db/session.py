import inspect
import logging
from typing import Dict, List, Mapping, Optional, Union

from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncDriver, AsyncGraphDatabase, Driver, GraphDatabase
from neo4j import AsyncSession as Neo4jAsyncSession
from neo4j import Session as Neo4jSession
from pymongo import IndexModel, MongoClient
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import PayloadSchemaType
from redis import ConnectionPool
from redis import Redis as R
from redis.asyncio import ConnectionPool as AsyncConnectionPool
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from keble_db.wrapper import ExtendedAsyncRedis
from keble_db.wrapper.redis import ExtendedRedis

from .schemas import DbSettingsABC

logger = logging.getLogger(__name__)


class Db:
    def __init__(self, settings: DbSettingsABC):
        self.__settings = settings
        self.__redis_pool = (
            ConnectionPool.from_url(settings.redis_uri, decode_responses=True)
            if settings.redis_uri is not None
            else None
        )
        self.__aredis_pool = (
            AsyncConnectionPool.from_url(settings.redis_uri, decode_responses=True)
            if settings.redis_uri is not None
            else None
        )
        self.__sql_read_engine = (
            create_engine(
                str(
                    settings.sql_read_uri
                    if settings.sql_read_uri is not None
                    else settings.sql_uri
                ),
                pool_pre_ping=True,
                pool_size=1000,
                max_overflow=10,
                pool_recycle=3600,
                pool_use_lifo=True,
                echo=False,
            )
            if settings.sql_read_uri is not None or settings.sql_uri is not None
            else None
        )
        self.__sql_write_engine = (
            create_engine(
                str(
                    settings.sql_write_uri
                    if settings.sql_write_uri is not None
                    else settings.sql_uri
                ),
                pool_pre_ping=True,
                pool_size=1000,
                max_overflow=10,
                pool_recycle=3600,
                pool_use_lifo=True,
                echo=False,
            )
            if settings.sql_write_uri is not None or settings.sql_uri is not None
            else None
        )

        # New async engines
        self.__async_sql_read_engine = (
            create_async_engine(
                str(
                    settings.sql_read_uri
                    if settings.sql_read_uri is not None
                    else settings.sql_uri
                ),
                pool_pre_ping=True,
                pool_size=100,
                max_overflow=10,
                pool_recycle=3600,
                echo=False,
            )
            if settings.sql_read_uri is not None or settings.sql_uri is not None
            else None
        )
        self.__async_sql_write_engine = (
            create_async_engine(
                str(
                    settings.sql_write_uri
                    if settings.sql_write_uri is not None
                    else settings.sql_uri
                ),
                pool_pre_ping=True,
                pool_size=100,
                max_overflow=10,
                pool_recycle=3600,
                echo=False,
            )
            if settings.sql_write_uri is not None or settings.sql_uri is not None
            else None
        )

        self._sql_read_instance = None
        self._sql_write_instance = None
        self._async_sql_read_instance = None
        self._async_sql_write_instance = None
        self._redis_instance = None
        self._aredis_instance = None
        self._mongo_instance = None
        self._amongo_instance: Optional[AsyncIOMotorClient] = None
        self._aqdrant_instance: Optional[AsyncQdrantClient] = None
        self._qdrant_instance = None
        self._neo4j_driver: Optional[Driver] = None
        self._neo4j_async_driver: Optional[AsyncDriver] = None
        self._neo4j_session: Optional[Neo4jSession] = None
        self._neo4j_async_session: Optional[Neo4jAsyncSession] = None

    @property
    def sql_write_engine(self) -> Optional[Engine]:
        return self.__sql_write_engine

    @property
    def sql_read_engine(self) -> Optional[Engine]:
        return self.__sql_read_engine

    @property
    def async_sql_write_engine(self) -> Optional[AsyncEngine]:
        return self.__async_sql_write_engine

    @property
    def async_sql_read_engine(self) -> Optional[AsyncEngine]:
        return self.__async_sql_read_engine

    def get_redis(self, *, force_new_instance: bool = False) -> R:
        """Return conn to redis
        You do not need to explicitly close the redis conn"""
        if self.__redis_pool is None:
            raise ValueError("[Db] redis_pool required")
        if force_new_instance:
            return R(connection_pool=self.__redis_pool, decode_responses=True)
        if not force_new_instance and self._redis_instance is not None:
            return self._redis_instance
        self._redis_instance = R(
            connection_pool=self.__redis_pool, decode_responses=True
        )
        return self._redis_instance

    def get_aredis(self, *, new_instance: bool = True) -> AsyncRedis:
        if self.__aredis_pool is None:
            raise ValueError("[Db] aredis_pool required")
        if new_instance:
            return AsyncRedis(connection_pool=self.__aredis_pool, decode_responses=True)
        if not new_instance and self._aredis_instance is not None:
            return self._aredis_instance
        self._aredis_instance = AsyncRedis(
            connection_pool=self.__aredis_pool, decode_responses=True
        )
        return self._aredis_instance

    def get_extended_aredis(
        self, *, new_instance: bool = True, namespace: Optional[str] = None
    ) -> ExtendedAsyncRedis:
        return ExtendedAsyncRedis.extend(
            aredis=self.get_aredis(new_instance=new_instance), namespace=namespace
        )

    def get_extended_redis(
        self, *, force_new_instance: bool = False, namespace: Optional[str] = None
    ) -> ExtendedRedis:
        return ExtendedRedis.extend(
            redis=self.get_redis(force_new_instance=force_new_instance),
            namespace=namespace,
        )

    def get_mongo(self, *, new_instance: bool = True) -> MongoClient:
        """Return a mongo conn
        You do not need to close PyMongo connections. Leave them open so that PyMongo connection pooling gives you the most efficient performance"""
        if self.__settings.mongo_db_uri is None:
            raise ValueError("[Db] mongo_db_uri required")

        if new_instance:
            return MongoClient(
                self.__settings.mongo_db_uri, uuidRepresentation="standard"
            )

        if self._mongo_instance is not None:
            try:
                self._mongo_instance.server_info()
                return self._mongo_instance
            except Exception as e:
                logger.critical(
                    f"[Db] Old mongo instance has been closed, now create a new one and returned. Server info exception: {e}"
                )
                pass

        self._mongo_instance = MongoClient(
            self.__settings.mongo_db_uri, uuidRepresentation="standard"
        )
        return self._mongo_instance

    async def aget_amongo(self, *, new_instance: bool = True) -> AsyncIOMotorClient:
        """Return a async mongo conn
        You do not need to close PyMongo connections. Leave them open so that PyMongo connection pooling gives you the most efficient performance"""
        if self.__settings.mongo_db_uri is None:
            raise ValueError("[Db] mongo_db_uri required")

        if new_instance:
            # check new instance first, new instance is independent and will not save as self.instance
            return AsyncIOMotorClient(
                self.__settings.mongo_db_uri, uuidRepresentation="standard"
            )

        if self._amongo_instance is not None:
            try:
                await self._amongo_instance.server_info()
                return self._amongo_instance
            except Exception as e:
                logger.critical(
                    f"[Db] Old async mongo instance has been closed, now create a new one and returned. Server info exception: {e}"
                )
                pass

        self._amongo_instance = AsyncIOMotorClient(
            self.__settings.mongo_db_uri, uuidRepresentation="standard"
        )
        return self._amongo_instance

    def get_amongo(self) -> AsyncIOMotorClient:
        """Return a async mongo conn
        without checking old instance, use with caustious to prevent creating too many session/conn to mongo at the same time.
        """
        if self.__settings.mongo_db_uri is None:
            raise ValueError("[Db] mongo_db_uri required")

        return AsyncIOMotorClient(
            self.__settings.mongo_db_uri, uuidRepresentation="standard"
        )

    def get_qdrant_client(self, *, new_instance: bool = True) -> QdrantClient:
        if self.__settings.qdrant_host is None or self.__settings.qdrant_port is None:
            raise ValueError("[Db] qdrant_host and qdrant_port required")
        if new_instance:
            # check new instance first, new instance is independent and will not save as self.instance
            return QdrantClient(
                host=self.__settings.qdrant_host,
                port=self.__settings.qdrant_port,
                timeout=120,
            )
        if not new_instance and self._qdrant_instance is not None:
            return self._qdrant_instance
        self._qdrant_instance = QdrantClient(
            host=self.__settings.qdrant_host,
            port=self.__settings.qdrant_port,
            timeout=120,
        )
        return self._qdrant_instance

    def get_aqdrant_client(self, *, new_instance: bool = True) -> AsyncQdrantClient:
        if self.__settings.qdrant_host is None or self.__settings.qdrant_port is None:
            raise ValueError("[Db] qdrant_host and qdrant_port required")
        if new_instance:
            # check new instance first, new instance is independent and will not save as self.instance
            return AsyncQdrantClient(
                host=self.__settings.qdrant_host,
                port=self.__settings.qdrant_port,
                timeout=120,
            )
        if not new_instance and self._aqdrant_instance is not None:
            return self._aqdrant_instance
        self._aqdrant_instance = AsyncQdrantClient(
            host=self.__settings.qdrant_host,
            port=self.__settings.qdrant_port,
            timeout=120,
        )
        return self._aqdrant_instance

    def get_neo4j_driver(self, *, new_instance: bool = True) -> Driver:
        if self.__settings.neo4j_uri is None:
            raise ValueError("[Db] neo4j_uri required")
        if self._neo4j_driver is None or new_instance:
            auth = None
            if (
                self.__settings.neo4j_user is not None
                and self.__settings.neo4j_password is not None
            ):
                auth = (self.__settings.neo4j_user, self.__settings.neo4j_password)
            self._neo4j_driver = GraphDatabase.driver(
                self.__settings.neo4j_uri,
                auth=auth,
            )
        return self._neo4j_driver

    def get_async_neo4j_driver(self, *, new_instance: bool = True) -> AsyncDriver:
        if self.__settings.neo4j_uri is None:
            raise ValueError("[Db] neo4j_uri required")
        if self._neo4j_async_driver is None or new_instance:
            auth = None
            if (
                self.__settings.neo4j_user is not None
                and self.__settings.neo4j_password is not None
            ):
                auth = (self.__settings.neo4j_user, self.__settings.neo4j_password)
            self._neo4j_async_driver = AsyncGraphDatabase.driver(
                self.__settings.neo4j_uri,
                auth=auth,
            )
        return self._neo4j_async_driver

    def get_neo4j_session(
        self,
        *,
        new_instance: bool = True,
        database: Optional[str] = None,
    ) -> Neo4jSession:
        driver = self.get_neo4j_driver(new_instance=new_instance)
        target_db = database if database is not None else self.__settings.neo4j_database
        if new_instance or self._neo4j_session is None:
            self._neo4j_session = driver.session(database=target_db)
        return self._neo4j_session

    def get_async_neo4j_session(
        self,
        *,
        new_instance: bool = True,
        database: Optional[str] = None,
    ) -> Neo4jAsyncSession:
        driver = self.get_async_neo4j_driver(new_instance=new_instance)
        target_db = database if database is not None else self.__settings.neo4j_database
        if new_instance or self._neo4j_async_session is None:
            self._neo4j_async_session = driver.session(database=target_db)
        return self._neo4j_async_session

    def get_sql_write_client(self, *, new_instance: bool = True) -> Session:
        if self.sql_write_engine is None:
            raise ValueError("[Db] sql_write_engine required")
        if new_instance:
            return Session(self.sql_write_engine)
        if not new_instance and self._sql_write_instance is not None:
            return self._sql_write_instance
        self._sql_write_instance = Session(self.sql_write_engine)
        return self._sql_write_instance

    def get_sql_read_client(self, *, new_instance: bool = True) -> Session:
        if self.sql_read_engine is None:
            raise ValueError("[Db] sql_read_engine required")
        if new_instance:
            return Session(self.sql_read_engine)
        if not new_instance and self._sql_read_instance is not None:
            return self._sql_read_instance
        self._sql_read_instance = Session(self.sql_read_engine)
        return self._sql_read_instance

    # def get_async_sql_write_client(
    #     self, *, new_instance: bool = True
    # ) -> SQLModelAsyncSession:
    #     """Get an async SQL session for writing operations."""
    #     if self.async_sql_write_engine is None:
    #         raise ValueError("[Db] async_sql_write_engine required")
    #     if new_instance:
    #         return SQLModelAsyncSession(self.async_sql_write_engine, expire_on_commit=False)
    #     if not new_instance and self._async_sql_write_instance is not None:
    #         return self._async_sql_write_instance
    #     self._async_sql_write_instance = SQLModelAsyncSession(
    #         self.async_sql_write_engine,
    #         expire_on_commit=False  # Prevent greenlet_spawn error on attribute access after commit
    #     )
    #     return self._async_sql_write_instance

    # def get_async_sql_read_client(
    #     self, *, new_instance: bool = True
    # ) -> SQLModelAsyncSession:
    #     """Get an async SQL session for reading operations."""
    #     if self.async_sql_read_engine is None:
    #         raise ValueError("[Db] async_sql_read_engine required")
    #     if new_instance:
    #         return SQLModelAsyncSession(self.async_sql_read_engine, expire_on_commit=False)
    #     if not new_instance and self._async_sql_read_instance is not None:
    #         return self._async_sql_read_instance
    #     self._async_sql_read_instance = SQLModelAsyncSession(
    #         self.async_sql_read_engine,
    #         expire_on_commit=False  # Prevent greenlet_spawn error on attribute access after commit
    #     )
    #     return self._async_sql_read_instance

    @staticmethod
    def ready_mongo(client: MongoClient):
        # check by list
        client.list_databases()

    @staticmethod
    def ready_mongo_indexes(
        client: MongoClient,
        db_name: str,
        collection_name: str,
        indexes: List[Dict[str, Union[int, str]]],
    ) -> None:
        """
        Ensure MongoDB indexes exist. Creates them if not.

        :param client: MongoClient instance
        :param db_name: Name of the MongoDB database
        :param collection_name: Name of the MongoDB collection
        :param indexes: List of dictionaries defining the index fields and their types.
                        - For normal ascending/descending indexes, use 1 (ascending) or -1 (descending).
                        - For text search indexes, use "text".
                        Example: [{"field1": 1, "field2": -1}, {"field3": "text"}]
        """
        collection = client[db_name][collection_name]
        existing_indexes = collection.index_information()

        # Create index models based on the input
        indexes_need_to_create = []
        for index in indexes:
            compound_index_key = [(field, order) for field, order in index.items()]

            # Check if the index already exists in the collection
            if not any(
                compound_index_key == idx.get("key")
                for idx in existing_indexes.values()
            ):
                index_model = IndexModel(compound_index_key)
                indexes_need_to_create.append(index_model)
        if len(indexes_need_to_create) > 0:
            collection.create_indexes(indexes_need_to_create)

    @staticmethod
    def ready_redis(redis: R):
        # check by get key
        redis.get("k")

    @staticmethod
    def ready_qdrant(
        client: QdrantClient,
        collection: str,
        vectors_config: Union[
            qdrant_models.VectorParams, Mapping[str, qdrant_models.VectorParams]
        ],
    ):
        # need to check database exist or not
        try:
            client.get_collection(collection_name=collection)
        except (AssertionError, UnexpectedResponse):
            # collection not found, or connection error. Try to create
            client.create_collection(
                collection_name=collection,
                vectors_config=vectors_config,
            )

    @staticmethod
    def ready_neo4j(driver: Driver):
        # Verify connectivity; raises if misconfigured
        driver.verify_connectivity()

    @staticmethod
    def ready_qdrant_indexes(
        client: QdrantClient,
        collection_name: str,
        indexes: List[Dict[str, PayloadSchemaType]],
    ) -> None:
        """
        Ensure Qdrant payload indexes exist. Creates them if not.

        :param client: QdrantClient instance
        :param collection_name: Name of the Qdrant collection
        :param indexes: List of dictionaries where keys are field names and values are their corresponding types (PayloadSchemaType).
                        Example: [{"field1": PayloadSchemaType.INTEGER}, {"field2": PayloadSchemaType.KEYWORD}]
        """
        try:
            collection_info = client.get_collection(collection_name)
            existing_indexes = collection_info.payload_schema or {}

            for index in indexes:
                for field_name, schema_type in index.items():
                    if field_name not in existing_indexes:
                        client.create_payload_index(
                            collection_name=collection_name,
                            field_name=field_name,
                            field_schema=qdrant_models.PayloadSchemaType(schema_type),
                        )
        except (AssertionError, UnexpectedResponse):
            logger.critical(
                f"[Db] Collection {collection_name} does not exist or failed to retrieve collection info."
            )

    @staticmethod
    def try_close(
        *sessions: Optional[
            MongoClient
            | R
            | Session
            | QdrantClient
            | AsyncIOMotorClient
            | AsyncQdrantClient
            | AsyncRedis
            | SQLModelAsyncSession
            | AsyncEngine
            | Driver
            | AsyncDriver
            | Neo4jSession
            | Neo4jAsyncSession
        ],
    ):
        import asyncio

        for session in sessions:
            if session is None:
                continue

            try:
                # Call close() method
                close_method = getattr(session, "close", None)
                if close_method is None:
                    continue

                # Check if it's an async method
                if inspect.iscoroutinefunction(close_method):
                    # Create a coroutine
                    coro = close_method()

                    # Try to run it or create a task based on context
                    try:
                        # Check if we're in an event loop
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Create a task - we can't await here
                            # Type ignores for linter errors - these are valid operations
                            asyncio.create_task(coro)  # type: ignore
                        else:
                            # No running loop, create one and run
                            asyncio.run(coro)  # type: ignore
                    except RuntimeError:
                        # No event loop exists, create one
                        try:
                            asyncio.run(coro)  # type: ignore
                        except Exception as e:
                            logger.error(f"[Db] Failed to run async close: {e}")
                else:
                    # Regular synchronous close
                    result = close_method()

                    # Check if the result is awaitable
                    if inspect.isawaitable(result):
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.create_task(result)  # type: ignore
                            else:
                                asyncio.run(result)  # type: ignore
                        except RuntimeError:
                            try:
                                asyncio.run(result)  # type: ignore
                            except Exception as e:
                                logger.error(f"[Db] Failed to run awaitable: {e}")

            except Exception as e:
                # Log errors but don't raise
                logger.error(f"[Db] Failed to close a db session due to {e}")

    @staticmethod
    async def try_close_async(
        *sessions: Optional[
            MongoClient
            | R
            | Session
            | QdrantClient
            | AsyncIOMotorClient
            | AsyncQdrantClient
            | AsyncRedis
            | SQLModelAsyncSession
            | AsyncEngine
            | Driver
            | AsyncDriver
            | Neo4jSession
            | Neo4jAsyncSession
        ],
    ):
        """Async version of try_close that can properly await async close methods."""
        for session in sessions:
            if session is None:
                continue

            try:
                close_method = getattr(session, "close", None)
                if close_method is None:
                    continue

                if inspect.iscoroutinefunction(close_method):
                    await close_method()
                else:
                    result = close_method()
                    if inspect.isawaitable(result):
                        await result

            except Exception as e:
                logger.error(f"[Db] Failed to close async session due to {e}")
