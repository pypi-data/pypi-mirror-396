from typing import AsyncGenerator, Generator, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncSession as Neo4jAsyncSession
from neo4j import Session as Neo4jSession
from pymongo import MongoClient
from qdrant_client import AsyncQdrantClient, QdrantClient
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from keble_db.wrapper import ExtendedAsyncRedis
from keble_db.wrapper.redis import ExtendedRedis

from ..session import Db


class ApiDbDeps:
    def __init__(self, db: Db):
        self.__db = db

        # 1) Create your session factory once, ideally at module import, not per-request
        self.self_asql_write_session_maker = (
            async_sessionmaker(
                self.__db.async_sql_write_engine,
                class_=SQLModelAsyncSession,
                expire_on_commit=False,  # keep attributes loaded after commit
            )
            if self.__db.async_sql_write_engine is not None
            else None
        )

        self.self_asql_read_session_maker = (
            async_sessionmaker(
                self.__db.async_sql_read_engine,
                class_=SQLModelAsyncSession,
                expire_on_commit=False,  # keep attributes loaded after commit
            )
            if self.__db.async_sql_read_engine is not None
            else None
        )

    def get_redis(self) -> Generator[Redis | None, None, None]:
        r = None
        try:
            r = self.__db.get_redis(force_new_instance=True)
            yield r
        finally:
            self.__db.try_close(r)

    def get_aredis(self) -> Generator[AsyncRedis, None, None]:
        """Get an async Redis client."""
        r = None
        r = self.__db.get_aredis(new_instance=True)
        yield r  # no need to close redis, it will manage itself

    def get_extended_redis(
        self, *, namespace: Optional[str] = None
    ) -> Generator[ExtendedRedis | None, None, None]:
        r = None
        try:
            r = ExtendedRedis.extend(redis=self.__db.get_redis(), namespace=namespace)
            yield r
        finally:
            pass

    def get_mongo(self) -> Generator[MongoClient | None, None, None]:
        m = None
        try:
            m = self.__db.get_mongo(new_instance=True)
            yield m
        finally:
            self.__db.try_close(m)

    def get_amongo(self) -> Generator[AsyncIOMotorClient, None, None]:
        """Get an async MongoDB client."""
        m = None
        try:
            m = self.__db.get_amongo()
            yield m
        finally:
            self.__db.try_close(m)

    def get_write_sql(self) -> Generator[Session | None, None, None]:
        s = None
        try:
            s = self.__db.get_sql_write_client(new_instance=True)
            yield s
        finally:
            self.__db.try_close(s)

    def get_read_sql(self) -> Generator[Session | None, None, None]:
        """Get a SQL session for reading operations."""
        s = None
        try:
            s = self.__db.get_sql_read_client(new_instance=True)
            yield s
        finally:
            self.__db.try_close(s)

    async def get_async_write_sql(
        self,
    ) -> AsyncGenerator[SQLModelAsyncSession | None, None]:
        """Get an async SQL session for writing operations."""
        if self.self_asql_write_session_maker is None:
            raise ValueError("[Db] async_sql_write_engine is not set")

        # 2) Use an async-generator dependency to yield and then close
        async with self.self_asql_write_session_maker() as session:
            yield session
            # async with already calls session.close() for you

        # s = None
        # try:
        #     s = self.__db.get_async_sql_write_client(new_instance=True)
        #     yield s
        # finally:
        #     await self.__db.try_close_async(s)

    async def get_async_read_sql(
        self,
    ) -> AsyncGenerator[SQLModelAsyncSession | None, None]:
        """Get an async SQL session for reading operations."""
        if self.self_asql_read_session_maker is None:
            raise ValueError("[Db] async_sql_read_engine is not set")

        # 2) Use an async-generator dependency to yield and then close
        async with self.self_asql_read_session_maker() as session:
            yield session
            # async with already calls session.close() for you
        # s = None
        # try:
        #     s = self.__db.get_async_sql_read_client(new_instance=True)
        #     yield s
        # finally:
        #     await self.__db.try_close_async(s)

    def get_qdrant(self) -> Generator[QdrantClient | None, None, None]:
        q = None
        try:
            q = self.__db.get_qdrant_client(new_instance=True)
            yield q
        finally:
            self.__db.try_close(q)

    def get_aqdrant(self) -> Generator[AsyncQdrantClient | None, None, None]:
        """Get an async Qdrant client."""
        q = None
        try:
            q = self.__db.get_aqdrant_client(new_instance=True)
            yield q
        finally:
            self.__db.try_close(q)

    def get_extended_aredis(
        self, *, namespace: Optional[str] = None
    ) -> Generator[ExtendedAsyncRedis | None, None, None]:
        """Get an extended async Redis client with namespace support."""
        r = None
        r = ExtendedAsyncRedis.extend(
            aredis=self.__db.get_aredis(new_instance=True), namespace=namespace
        )
        yield r

    def get_neo4j_session(self) -> Generator[Neo4jSession | None, None, None]:
        session = None
        try:
            session = self.__db.get_neo4j_session(new_instance=True)
            yield session
        finally:
            self.__db.try_close(session)

    async def get_async_neo4j_session(
        self,
    ) -> AsyncGenerator[Neo4jAsyncSession | None, None]:
        session = None
        try:
            session = self.__db.get_async_neo4j_session(new_instance=True)
            yield session
        finally:
            await self.__db.try_close_async(session)
